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

    @http.route('/payment/test', type='http', auth='public', website=True, csrf=False)
    def test_controller(self, **kwargs):
        """Simple test endpoint to verify controller routing works"""
        return "<html><body><h1>Payment Controller Test - Working!</h1></body></html>"

    @http.route('/payment/verify/<string:access_token>', type='http', auth='public', website=True, csrf=False)
    def verify_payment_by_token(self, access_token, **kwargs):
        """Public payment verification page accessible via QR code with access token"""
        try:
            _logger.info("Payment verification attempt for token: %s", access_token)
            
            # Find payment by access token
            payment = request.env['account.payment'].sudo().search([
                ('access_token', '=', access_token)
            ], limit=1)
            
            if not payment:
                _logger.warning("Payment not found for access token: %s", access_token)
                # Use simple HTML response if template fails
                return """
                <html>
                <head><title>Payment Not Found</title></head>
                <body style="font-family: Arial; margin: 40px; text-align: center;">
                    <h1>Payment Not Found</h1>
                    <p>The payment voucher you are trying to verify does not exist or has been removed.</p>
                    <p>Access Token: %s</p>
                </body>
                </html>
                """ % access_token
            
            _logger.info("Payment found: %s for token: %s", payment.voucher_number or payment.name, access_token)
            
            # Try to log verification attempt (but don't fail if it breaks)
            try:
                verification_log = self._log_verification_attempt(payment, 'qr_scan', request.httprequest)
            except Exception as log_error:
                _logger.warning("Could not log verification attempt: %s", str(log_error))
                verification_log = None
            
            # Get basic status info (simplified)
            try:
                status_info = self._get_payment_status_info(payment)
            except Exception as status_error:
                _logger.warning("Could not get status info: %s", str(status_error))
                status_info = {
                    'status': 'info',
                    'message': 'Verified',
                    'css_class': 'bg-info'
                }
            
            # Simplified context for template
            context = {
                'payment': payment,
                'verification_status': status_info.get('status', 'info'),
                'status_message': status_info.get('message', 'Verified'),
                'status_class': status_info.get('css_class', 'bg-info'),
                'company': payment.company_id,
                'verification_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'verification_code': verification_log.verification_code if verification_log else access_token[:8].upper(),
            }
            
            # Try to render template, fall back to simple HTML if it fails
            try:
                return request.render('payment_account_enhanced.payment_verification_success', context)
            except Exception as template_error:
                _logger.error("Template rendering failed: %s", str(template_error))
                # Fallback to simple HTML response
                return f"""
                <html>
                <head><title>Payment Verified - {payment.voucher_number or payment.name}</title></head>
                <body style="font-family: Arial; margin: 40px;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                        <h1 style="color: green;">✓ Payment Verification Successful</h1>
                        <p><strong>Payment Number:</strong> {payment.voucher_number or payment.name}</p>
                        <p><strong>Partner:</strong> {payment.partner_id.name or 'N/A'}</p>
                        <p><strong>Amount:</strong> {payment.currency_id.symbol or ''} {payment.amount:,.2f}</p>
                        <p><strong>Date:</strong> {payment.date.strftime('%Y-%m-%d') if payment.date else 'N/A'}</p>
                        <p><strong>Status:</strong> {payment.approval_state.replace('_', ' ').title() if payment.approval_state else 'Draft'}</p>
                        <p><strong>Company:</strong> {payment.company_id.name}</p>
                        <p><strong>Verified:</strong> {context['verification_time']}</p>
                        <p style="margin-top: 30px; color: #666; font-size: 12px;">This payment has been verified through secure QR code authentication.</p>
                    </div>
                </body>
                </html>
                """
            
        except Exception as e:
            _logger.error("Critical error in token payment verification for token %s: %s", access_token, str(e))
            # Always return something, even if everything fails
            return f"""
            <html>
            <head><title>Verification Error</title></head>
            <body style="font-family: Arial; margin: 40px; text-align: center;">
                <h1>Verification Error</h1>
                <p>An error occurred while verifying the payment.</p>
                <p>Error: {str(e)}</p>
                <p>Access Token: {access_token}</p>
                <p>Please contact support for assistance.</p>
            </body>
            </html>
            """

    @http.route('/payment/verify/json/<string:access_token>', type='json', auth='public', website=True, csrf=False)
    def verify_payment_token_json(self, access_token, **kwargs):
        """JSON API endpoint for payment verification by access token"""
        try:
            # Find payment by access token
            payment = request.env['account.payment'].sudo().search([
                ('access_token', '=', access_token)
            ], limit=1)
            
            if not payment:
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
            _logger.error("Error in JSON token payment verification for token %s: %s", access_token, str(e))
            return {
                'success': False,
                'error': 'verification_error',
                'message': _('An error occurred during verification')
            }

    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', website=True, csrf=False)
    def verify_payment(self, payment_id, **kwargs):
        """Backward compatibility: Public payment verification page by payment ID"""
        try:
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return request.render('payment_account_enhanced.payment_not_found', {
                    'error_message': _('Payment Not Found'),
                    'error_details': _('The payment voucher you are trying to verify does not exist or has been removed.'),
                })
            
            # Log verification attempt
            verification_log = self._log_verification_attempt(payment, 'qr_scan', request.httprequest)
            
            # Determine verification status
            status_info = self._get_payment_status_info(payment)
            
            # Get verification history
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
            
            return request.render('payment_account_enhanced.payment_verification_success', context)
            
        except Exception as e:
            _logger.error("Error in payment verification for payment_id %s: %s", payment_id, str(e))
            return request.render('payment_account_enhanced.payment_verification_error', {
                'error_message': _('Verification Error'),
                'error_details': _('An error occurred while verifying the payment. Please try again later.'),
            })

    @http.route('/payment/bulk-verify', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def bulk_verify_payments(self, **kwargs):
        """Bulk verification page for authorized users"""
        if not request.env.user.has_group('payment_account_enhanced.group_payment_verifier'):
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
            
            return request.render('payment_account_enhanced.bulk_verification_results', {
                'results': results,
                'total_checked': len([r for r in results if r.get('voucher_number')]),
                'found_count': len([r for r in results if r.get('found')]),
            })
        
        return request.render('payment_account_enhanced.bulk_verification_form')

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
            _logger.error("Error logging verification attempt: %s", str(e))
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
