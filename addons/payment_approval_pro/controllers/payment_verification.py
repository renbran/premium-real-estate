# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import UserError, AccessError
import logging
import json
import hashlib
import datetime

_logger = logging.getLogger(__name__)


class PaymentVerificationController(http.Controller):
    """Professional payment verification controller with comprehensive security"""

    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', website=True, csrf=False)
    def verify_payment(self, payment_id, **kwargs):
        """Public payment verification page accessible via QR code"""
        try:
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return request.render('account_payment_final.payment_not_found', {
                    'error_message': _('Payment Not Found'),
                    'error_details': _('The payment voucher you are trying to verify does not exist or has been removed.'),
                })
            
            # Log verification attempt with comprehensive data
            verification_log = self._log_verification_attempt(payment, 'qr_scan', request.httprequest)
            
            # Determine verification status and display information
            status_info = self._get_payment_status_info(payment)
            
            # Get verification history for audit trail
            verifications = request.env['payment.qr.verification'].sudo().search([
                ('payment_id', '=', payment.id)
            ], limit=10, order='verification_date desc')
            
            context = {
                'payment': payment,
                'verification_status': status_info['status'],
                'status_message': status_info['message'],
                'status_class': status_info['css_class'],
                'verifications': verifications,
                'company': payment.company_id,
                'verification_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'qr_verification_count': len(verifications),
                'verification_code': verification_log.verification_code if verification_log else None,
            }
            
            return request.render('account_payment_final.payment_verification_page', context)
            
        except Exception as e:
            _logger.error(f"Error in payment verification for payment_id {payment_id}: {e}")
            return request.render('account_payment_final.payment_verification_error', {
                'error_message': _('Verification Error'),
                'error_details': _('An error occurred while verifying the payment. Please try again later.'),
            })

    @http.route('/payment/verify/json/<int:payment_id>', type='json', auth='public', website=True, csrf=False)
    def verify_payment_json(self, payment_id, **kwargs):
        """JSON API endpoint for payment verification"""
        try:
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return {
                    'success': False,
                    'error': 'payment_not_found',
                    'message': _('Payment not found')
                }
            
            # Log verification attempt
            self._log_verification_attempt(payment, 'api_call', request.httprequest)
            
            # Get comprehensive payment data
            status_info = self._get_payment_status_info(payment)
            
            return {
                'success': True,
                'payment_data': {
                    'voucher_number': payment.voucher_number,
                    'name': payment.name,
                    'partner_name': payment.partner_id.name,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'currency_symbol': payment.currency_id.symbol,
                    'date': payment.date.strftime('%Y-%m-%d') if payment.date else None,
                    'payment_type': payment.payment_type,
                    'approval_state': payment.approval_state,
                    'verification_status': payment.verification_status,
                    'journal_name': payment.journal_id.name,
                    'company_name': payment.company_id.name,
                    'status_info': status_info,
                },
                'verification_time': datetime.datetime.now().isoformat(),
            }
            
        except Exception as e:
            _logger.error(f"Error in JSON payment verification for payment_id {payment_id}: {e}")
            return {
                'success': False,
                'error': 'verification_error',
                'message': _('An error occurred during verification')
            }

    @http.route('/payment/bulk-verify', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def bulk_verify_payments(self, **kwargs):
        """Bulk verification page for authorized users"""
        if not request.env.user.has_group('account_payment_final.group_payment_verifier'):
            raise AccessError(_('You do not have permission to access bulk verification'))
        
        if request.httprequest.method == 'POST':
            # Process bulk verification
            voucher_numbers = kwargs.get('voucher_numbers', '').strip().split('\n')
            results = []
            
            for voucher_num in voucher_numbers:
                voucher_num = voucher_num.strip()
                if voucher_num:
                    payment = request.env['account.payment'].search([
                        ('voucher_number', '=', voucher_num)
                    ], limit=1)
                    
                    if payment:
                        status_info = self._get_payment_status_info(payment)
                        results.append({
                            'voucher_number': voucher_num,
                            'found': True,
                            'partner': payment.partner_id.name,
                            'amount': payment.amount,
                            'currency': payment.currency_id.name,
                            'status': status_info['message'],
                            'date': payment.date,
                        })
                    else:
                        results.append({
                            'voucher_number': voucher_num,
                            'found': False,
                            'error': _('Voucher not found'),
                        })
            
            return request.render('account_payment_final.bulk_verification_results', {
                'results': results,
                'total_checked': len([r for r in results if r.get('voucher_number')]),
                'found_count': len([r for r in results if r.get('found')]),
            })
        
        return request.render('account_payment_final.bulk_verification_form')

    def _log_verification_attempt(self, payment, method, http_request):
        """Log verification attempt for comprehensive audit trail"""
        try:
            # Generate unique verification code
            verification_code = hashlib.md5(
                f"{payment.id}-{datetime.datetime.now().isoformat()}".encode()
            ).hexdigest()[:12].upper()
            
            # Extract request information
            verifier_ip = http_request.environ.get('REMOTE_ADDR', 'Unknown')
            user_agent = http_request.environ.get('HTTP_USER_AGENT', 'Unknown')
            
            # Create comprehensive verification record
            verification_record = request.env['payment.qr.verification'].sudo().create({
                'payment_id': payment.id,
                'verification_code': verification_code,
                'verification_date': datetime.datetime.now(),
                'verifier_ip': verifier_ip,
                'verifier_user_agent': user_agent,
                'verification_method': method,
                'verification_status': 'success',
                'additional_data': json.dumps({
                    'payment_state': payment.approval_state,
                    'verification_status': payment.verification_status,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'partner': payment.partner_id.name,
                    'journal': payment.journal_id.name,
                })
            })
            
            return verification_record
            
        except Exception as e:
            _logger.error(f"Error logging verification attempt: {e}")
            return None

    def _get_payment_status_info(self, payment):
        """Get comprehensive payment status information"""
        # Combined status from both approval_state and verification_status
        approval_status_map = {
            'draft': ('secondary', 'Draft - Not Processed'),
            'under_review': ('info', 'Under Review'),
            'for_approval': ('warning', 'Pending Approval'),
            'for_authorization': ('warning', 'Pending Authorization'),
            'approved': ('success', 'Approved - Ready to Post'),
            'posted': ('success', 'Posted to Ledger'),
            'cancelled': ('danger', 'Cancelled'),
        }
        
        verification_status_map = {
            'pending': ('info', 'Pending Verification'),
            'verified': ('success', 'VERIFIED'),
            'rejected': ('danger', 'Verification Rejected'),
        }
        
        # Primary status from approval_state if available, otherwise verification_status
        if hasattr(payment, 'approval_state') and payment.approval_state:
            primary_status = approval_status_map.get(payment.approval_state, ('secondary', 'Unknown'))
        else:
            primary_status = verification_status_map.get(payment.verification_status, ('secondary', 'Unknown'))
        
        return {
            'status': primary_status[0],
            'message': primary_status[1],
            'css_class': f'bg-{primary_status[0]}',
            'approval_state': getattr(payment, 'approval_state', None),
            'verification_status': payment.verification_status,
        }
