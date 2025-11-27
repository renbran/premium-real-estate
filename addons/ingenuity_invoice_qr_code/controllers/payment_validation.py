# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import ValidationError
import secrets
import hashlib
import logging

_logger = logging.getLogger(__name__)


class PaymentValidationController(http.Controller):
    """Controller for payment validation and QR code verification"""

    @http.route('/payment/validate/<string:token>', type='http', auth='public', website=True, sitemap=False)
    def validate_payment(self, token, **kwargs):
        """Public endpoint to validate payment using unique token"""
        try:
            # Find payment by validation token
            payment = request.env['account.payment'].sudo().search([
                ('validation_token', '=', token),
                ('state', '=', 'posted')
            ], limit=1)
            
            if not payment:
                return request.render('ingenuity_invoice_qr_code.payment_validation_error', {
                    'error_title': _('Payment Not Found'),
                    'error_message': _('The payment validation token is invalid or the payment does not exist.'),
                    'token': token
                })
            
            # Check if token is expired (optional - 30 days validity)
            if payment.validation_token_expiry and payment.validation_token_expiry < fields.Datetime.now():
                return request.render('ingenuity_invoice_qr_code.payment_validation_error', {
                    'error_title': _('Validation Token Expired'),
                    'error_message': _('This payment validation token has expired. Please contact the issuer for a new validation.'),
                    'token': token
                })
            
            # Log validation access
            _logger.info("Payment validation accessed for payment %s with token %s", payment.name, token)
            
            # Update validation access count
            payment.sudo().write({
                'validation_access_count': payment.validation_access_count + 1,
                'last_validation_access': fields.Datetime.now()
            })
            
            # Prepare validation data
            validation_data = {
                'payment': payment,
                'company': payment.company_id,
                'partner': payment.partner_id,
                'currency': payment.currency_id,
                'validation_token': token,
                'validation_url': request.httprequest.url,
                'is_receipt': payment.payment_type == 'inbound',
                'payment_status': 'Confirmed' if payment.state == 'posted' else payment.state.title(),
                'related_documents': payment.get_related_documents() if hasattr(payment, 'get_related_documents') else [],
            }
            
            return request.render('ingenuity_invoice_qr_code.payment_validation_page', validation_data)
            
        except Exception as e:
            _logger.error("Error validating payment with token %s: %s", token, str(e))
            return request.render('ingenuity_invoice_qr_code.payment_validation_error', {
                'error_title': _('Validation Error'),
                'error_message': _('An error occurred while validating the payment. Please try again later.'),
                'token': token
            })

    @http.route('/payment/validate/json/<string:token>', type='json', auth='public', csrf=False)
    def validate_payment_json(self, token, **kwargs):
        """JSON API endpoint for payment validation (for mobile apps, etc.)"""
        try:
            payment = request.env['account.payment'].sudo().search([
                ('validation_token', '=', token),
                ('state', '=', 'posted')
            ], limit=1)
            
            if not payment:
                return {
                    'success': False,
                    'error': 'Payment not found or invalid token',
                    'code': 'PAYMENT_NOT_FOUND'
                }
            
            # Check token expiry
            if payment.validation_token_expiry and payment.validation_token_expiry < fields.Datetime.now():
                return {
                    'success': False,
                    'error': 'Validation token expired',
                    'code': 'TOKEN_EXPIRED'
                }
            
            # Update access count
            payment.sudo().write({
                'validation_access_count': payment.validation_access_count + 1,
                'last_validation_access': fields.Datetime.now()
            })
            
            return {
                'success': True,
                'payment': {
                    'reference': payment.name,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'date': payment.date.isoformat() if payment.date else None,
                    'partner': payment.partner_id.name,
                    'company': payment.company_id.name,
                    'type': 'receipt' if payment.payment_type == 'inbound' else 'payment',
                    'status': 'confirmed',
                    'validation_count': payment.validation_access_count,
                    'validated_at': fields.Datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            _logger.error("JSON validation error for token %s: %s", token, str(e))
            return {
                'success': False,
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            }

    @http.route('/payment/validate/info', type='http', auth='public', website=True)
    def validation_info(self, **kwargs):
        """Information page about payment validation system"""
        return request.render('ingenuity_invoice_qr_code.payment_validation_info')
