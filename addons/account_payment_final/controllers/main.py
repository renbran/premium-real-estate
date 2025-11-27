# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, AccessError
import logging
import json
import hashlib
import datetime

_logger = logging.getLogger(__name__)


class PaymentVerificationController(http.Controller):
    """Web controller for payment verification through QR codes"""

    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', website=True, csrf=False)
    def verify_payment(self, payment_id, **kwargs):
        """Public payment verification page accessible via QR code"""
        try:
            # Find the payment record
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return request.render('account_payment_final.payment_verification_not_found', {
                    'error_message': _('Payment not found'),
                    'error_details': _('The payment voucher you are trying to verify does not exist.'),
                })
            
            # Log verification attempt
            self._log_verification_attempt(payment, 'qr_scan', request.httprequest)
            
            # Check if payment is in a verifiable state
            if payment.approval_state in ['cancelled']:
                verification_status = 'cancelled'
                status_message = _('This payment has been cancelled')
                status_class = 'text-danger'
            elif payment.approval_state == 'draft':
                verification_status = 'draft'
                status_message = _('This payment is still in draft state')
                status_class = 'text-warning'
            elif payment.approval_state == 'posted':
                verification_status = 'posted'
                status_message = _('Payment completed successfully')
                status_class = 'text-success'
            elif payment.approval_state in ['under_review', 'for_approval', 'for_authorization', 'approved']:
                verification_status = 'processing'
                status_message = _('Payment is being processed')
                status_class = 'text-info'
            else:
                verification_status = 'unknown'
                status_message = _('Payment status unknown')
                status_class = 'text-muted'
            
            # Get verification history
            verifications = request.env['payment.qr.verification'].sudo().search([
                ('payment_id', '=', payment.id)
            ], limit=10, order='verification_date desc')
            
            # Prepare context for template
            context = {
                'payment': payment,
                'verification_status': verification_status,
                'status_message': status_message,
                'status_class': status_class,
                'verifications': verifications,
                'company': payment.company_id,
                'verification_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'qr_verification_count': len(verifications) + 1,
            }
            
            return request.render('account_payment_final.payment_verification_page', context)
            
        except Exception as e:
            _logger.error(f"Error in payment verification: {e}")
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
            
            return {
                'success': True,
                'payment_data': {
                    'voucher_number': payment.voucher_number,
                    'partner_name': payment.partner_id.name,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'date': payment.date.strftime('%Y-%m-%d') if payment.date else None,
                    'approval_state': payment.approval_state,
                    'state': payment.state,
                    'company': payment.company_id.name,
                },
                'verification_time': datetime.datetime.now().isoformat(),
            }
            
        except Exception as e:
            _logger.error(f"Error in JSON payment verification: {e}")
            return {
                'success': False,
                'error': 'verification_error',
                'message': _('An error occurred during verification')
            }

    @http.route('/payment/qr-guide', type='http', auth='public', website=True, sitemap=False)
    def qr_verification_guide(self, **kwargs):
        """Guide page for manual QR verification when URL is not available"""
        return request.render('account_payment_final.payment_qr_guide', {
            'company_name': request.env.company.name,
        })

    @http.route('/payment/bulk-verify', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def bulk_verify_payments(self, **kwargs):
        """Bulk verification page for authorized users"""
        if not request.env.user.has_group('account.group_account_user'):
            raise AccessError(_('You do not have permission to access this page'))
        
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
                        results.append({
                            'voucher_number': voucher_num,
                            'found': True,
                            'partner': payment.partner_id.name,
                            'amount': payment.amount,
                            'currency': payment.currency_id.name,
                            'status': payment.approval_state,
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
        """Log verification attempt for audit trail"""
        try:
            # Generate verification code
            verification_code = hashlib.md5(
                f"{payment.id}-{datetime.datetime.now().isoformat()}".encode()
            ).hexdigest()[:12].upper()
            
            # Get IP and user agent
            verifier_ip = http_request.environ.get('REMOTE_ADDR', 'Unknown')
            user_agent = http_request.environ.get('HTTP_USER_AGENT', 'Unknown')
            
            # Create verification record
            request.env['payment.qr.verification'].sudo().create({
                'payment_id': payment.id,
                'verification_code': verification_code,
                'verification_date': datetime.datetime.now(),
                'verifier_ip': verifier_ip,
                'verifier_user_agent': user_agent,
                'verification_method': method,
                'verification_status': 'success',
                'additional_data': json.dumps({
                    'payment_state': payment.approval_state,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'partner': payment.partner_id.name,
                })
            })
            
        except Exception as e:
            _logger.error(f"Error logging verification attempt: {e}")
