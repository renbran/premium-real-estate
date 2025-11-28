from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import json
import logging
import base64

_logger = logging.getLogger(__name__)


class QRVerificationController(http.Controller):
    """QR Code Verification Controller for Payment Vouchers"""

    @http.route('/payment/verify/<string:token>', type='http', auth='public', website=True, csrf=False)
    def verify_payment_page(self, token, **kwargs):
        """
        Public page for QR payment verification
        """
        try:
            # Find payment by verification token
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return request.render('account_payment_approval.qr_verification_invalid', {
                    'error_message': _("Invalid verification token. Payment not found."),
                    'error_code': 'INVALID_TOKEN'
                })

            # Check payment state
            if payment.voucher_state not in ['authorized', 'posted']:
                return request.render('account_payment_approval.qr_verification_invalid', {
                    'error_message': _("Payment is not yet authorized for verification."),
                    'error_code': 'NOT_AUTHORIZED'
                })

            # Prepare payment data
            payment_data = {
                'voucher_number': payment.voucher_number,
                'amount': payment.amount,
                'currency_symbol': payment.currency_id.symbol,
                'partner_name': payment.partner_id.name if payment.partner_id else 'N/A',
                'date': payment.date.strftime('%d %B %Y') if payment.date else 'N/A',
                'state_display': dict(payment._fields['voucher_state'].selection).get(payment.voucher_state, 'Unknown'),
                'memo': payment.memo or '',
                'payment_method': payment.payment_method_line_id.name if payment.payment_method_line_id else 'N/A',
                'journal_name': payment.journal_id.name if payment.journal_id else 'N/A',
                'company_name': payment.company_id.name,
            }

            # Check if already validated
            validation_status = 'pending'
            if payment.qr_validated:
                validation_status = 'validated'

            return request.render('account_payment_approval.qr_verification_page', {
                'payment': payment,
                'payment_data': payment_data,
                'validation_status': validation_status,
                'token': token,
                'scan_count': payment.qr_scan_count,
            })

        except Exception as e:
            _logger.error("Error in QR verification page: %s", str(e))
            return request.render('account_payment_approval.qr_verification_error', {
                'error_message': _("An error occurred while processing your request."),
                'error_code': 'SYSTEM_ERROR'
            })

    @http.route('/payment/verify/api/<string:token>', type='json', auth='public', csrf=False)
    def api_verify_payment(self, token, **kwargs):
        """
        AJAX API endpoint for QR verification
        """
        try:
            # Get client info for logging
            client_info = {
                'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', '')[:200],
            }

            # Find payment
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return {
                    'success': False,
                    'message': _("Invalid verification token."),
                    'code': 'INVALID_TOKEN'
                }

            # Validate payment
            result = payment.action_validate_qr_payment(client_info)

            # Log verification attempt
            _logger.info("QR verification attempt for payment %s from IP %s: %s",
                        payment.voucher_number, client_info['ip_address'],
                        'SUCCESS' if result['success'] else result.get('code', 'FAILED'))

            return result

        except Exception as e:
            _logger.error("QR verification API error: %s", str(e))
            return {
                'success': False,
                'message': _("System error occurred. Please try again later."),
                'code': 'SYSTEM_ERROR'
            }

    @http.route('/payment/qr/scanner', type='http', auth='user', website=True)
    def qr_scanner_page(self, **kwargs):
        """
        QR Scanner page for internal users
        """
        # Check if user has permission
        if not request.env.user.has_group('account_payment_approval.group_payment_qr_verifier'):
            return request.render('website.403')

        return request.render('account_payment_approval.qr_scanner_page', {
            'user_name': request.env.user.name,
            'can_validate': request.env.user.has_group('account_payment_approval.group_payment_voucher_reviewer'),
        })

    @http.route('/payment/qr/validate', type='json', auth='user', csrf=False)
    def validate_scanned_qr(self, qr_data, **kwargs):
        """
        Validate QR code scanned by internal user
        """
        try:
            # Extract token from QR data
            token = qr_data
            if '/payment/verify/' in qr_data:
                token = qr_data.split('/payment/verify/')[-1].split('?')[0]

            # Get client info
            client_info = {
                'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                'user_agent': f"Odoo Internal Scanner - {request.env.user.name}",
            }

            # Find and validate payment
            payment = request.env['account.payment'].search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return {
                    'success': False,
                    'message': _("Invalid QR code. Payment not found."),
                    'code': 'INVALID_TOKEN'
                }

            # Validate payment
            result = payment.action_validate_qr_payment(client_info)

            # Log internal validation
            _logger.info("Internal QR validation by user %s for payment %s: %s",
                        request.env.user.name, payment.voucher_number,
                        'SUCCESS' if result['success'] else result.get('code', 'FAILED'))

            return result

        except Exception as e:
            _logger.error("Internal QR validation error by user %s: %s", request.env.user.name, str(e))
            return {
                'success': False,
                'message': _("Validation failed. Please try again."),
                'code': 'VALIDATION_ERROR'
            }

    @http.route('/payment/qr/status/<string:token>', type='json', auth='public', csrf=False)
    def get_verification_status(self, token, **kwargs):
        """
        Get current verification status without validating
        """
        try:
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return {'status': 'invalid', 'message': _("Payment not found")}

            return {
                'status': 'validated' if payment.qr_validated else 'pending',
                'validated': payment.qr_validated,
                'scan_count': payment.qr_scan_count,
                'payment_state': payment.voucher_state,
                'validated_date': payment.qr_validation_date.strftime('%d/%m/%Y %H:%M') if payment.qr_validation_date else None,
                'validator': payment.qr_validator_id.name if payment.qr_validator_id else 'System'
            }

        except Exception as e:
            _logger.error("Error getting verification status: %s", str(e))
            return {'status': 'error', 'message': _("Unable to check status")}