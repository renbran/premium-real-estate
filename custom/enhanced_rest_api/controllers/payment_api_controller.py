# -*- coding: utf-8 -*-
"""
Payment Account Enhanced REST API Controller
"""

import json
import time
import logging
from datetime import datetime, timedelta

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class PaymentAPIController(http.Controller):
    """Payment-specific REST API endpoints"""

    def _authenticate_request(self):
        """Authenticate API request using enhanced API key"""
        api_key = request.httprequest.headers.get('X-API-Key') or request.httprequest.headers.get('api-key')
        
        if not api_key:
            return {'error': 'API key required', 'code': 401}
        
        user = request.env['res.users'].sudo().authenticate_api_key(api_key)
        if not user:
            return {'error': 'Invalid API key', 'code': 401}
        
        request.uid = user.id
        return user

    def _make_response(self, data, status=200):
        """Create standardized API response"""
        response_data = {
            'success': status < 400,
            'timestamp': datetime.now().isoformat(),
            'data': data if status < 400 else None,
            'error': data if status >= 400 else None
        }
        
        return request.make_response(
            data=json.dumps(response_data, default=str),
            headers={'Content-Type': 'application/json'}
        )

    @http.route('/api/v1/payments/voucher/<int:payment_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def generate_payment_voucher(self, payment_id, **kwargs):
        """Generate payment voucher report"""
        try:
            # Authenticate
            user = self._authenticate_request()
            if isinstance(user, dict):
                return self._make_response(user, 401)

            # Get payment record
            payment = request.env['account.payment'].browse(payment_id)
            if not payment.exists():
                return self._make_response({'error': 'Payment not found', 'code': 404}, 404)

            # Check access rights
            try:
                payment.check_access_rights('read')
                payment.check_access_rule('read')
            except AccessError:
                return self._make_response({'error': 'Access denied', 'code': 403}, 403)

            # Generate report
            report = request.env.ref('enhanced_rest_api.action_report_payment_voucher')
            pdf_content, _ = report._render_qweb_pdf([payment.id])
            
            # Create response
            response = request.make_response(
                pdf_content,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="Payment_Voucher_{payment.name or payment.id}.pdf"'),
                    ('Content-Length', len(pdf_content)),
                ]
            )
            
            return response

        except Exception as e:
            _logger.error(f"Error generating payment voucher: {str(e)}")
            return self._make_response({'error': str(e), 'code': 500}, 500)

    @http.route('/api/v1/payments/voucher/html/<int:payment_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_payment_voucher_html(self, payment_id, **kwargs):
        """Get payment voucher as HTML for preview"""
        try:
            # Authenticate
            user = self._authenticate_request()
            if isinstance(user, dict):
                return self._make_response(user, 401)

            # Get payment record
            payment = request.env['account.payment'].browse(payment_id)
            if not payment.exists():
                return self._make_response({'error': 'Payment not found', 'code': 404}, 404)

            # Check access rights
            try:
                payment.check_access_rights('read')
                payment.check_access_rule('read')
            except AccessError:
                return self._make_response({'error': 'Access denied', 'code': 403}, 403)

            # Render HTML template
            template = request.env.ref('enhanced_rest_api.payment_voucher_document')
            html_content = template._render({'docs': [payment]})
            
            return request.make_response(
                html_content,
                headers=[('Content-Type', 'text/html')]
            )

        except Exception as e:
            _logger.error(f"Error generating payment voucher HTML: {str(e)}")
            return self._make_response({'error': str(e), 'code': 500}, 500)

    @http.route('/api/v1/payments/voucher/data/<int:payment_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_payment_voucher_data(self, payment_id, **kwargs):
        """Get payment voucher data as JSON"""
        try:
            # Authenticate
            user = self._authenticate_request()
            if isinstance(user, dict):
                return self._make_response(user, 401)

            # Get payment record
            payment = request.env['account.payment'].browse(payment_id)
            if not payment.exists():
                return self._make_response({'error': 'Payment not found', 'code': 404}, 404)

            # Check access rights
            try:
                payment.check_access_rights('read')
                payment.check_access_rule('read')
            except AccessError:
                return self._make_response({'error': 'Access denied', 'code': 403}, 403)

            # Get voucher data
            voucher_data = payment.get_voucher_data()
            
            return self._make_response(voucher_data)

        except Exception as e:
            _logger.error(f"Error getting payment voucher data: {str(e)}")
            return self._make_response({'error': str(e), 'code': 500}, 500)

    @http.route('/api/v1/payments', type='http', auth='none', methods=['GET'], csrf=False)
    def get_payments(self, **kwargs):
        """Get payment records with filtering options"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse parameters
            state = kwargs.get('state')
            partner_id = kwargs.get('partner_id')
            payment_type = kwargs.get('payment_type')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))
            
            # Build domain
            domain = []
            if state:
                domain.append(('state', '=', state))
            if partner_id:
                domain.append(('partner_id', '=', int(partner_id)))
            if payment_type:
                domain.append(('payment_type', '=', payment_type))
            if date_from:
                domain.append(('date', '>=', date_from))
            if date_to:
                domain.append(('date', '<=', date_to))
            
            # Get payments
            payments = request.env['account.payment'].search_read(
                domain=domain,
                fields=[
                    'id', 'name', 'partner_id', 'amount', 'currency_id',
                    'date', 'state', 'payment_type', 'payment_method_id',
                    'voucher_number', 'qr_code_image'
                ],
                limit=limit,
                offset=offset,
                order='date desc'
            )
            
            total_count = request.env['account.payment'].search_count(domain)
            
            return self._make_response({
                'payments': payments,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/payments', type='http', auth='none', methods=['POST'], csrf=False)
    def create_payment(self, **kwargs):
        """Create a new payment"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse JSON data
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['amount', 'partner_id', 'payment_type']
            for field in required_fields:
                if field not in data:
                    return self._make_response({'error': f'Missing required field: {field}'}, 400)
            
            # Create payment
            payment = request.env['account.payment'].create(data)
            
            return self._make_response({
                'id': payment.id,
                'name': payment.name,
                'voucher_number': payment.voucher_number,
                'state': payment.state,
                'amount': payment.amount,
                'qr_verification_url': payment.qr_verification_url,
                'message': 'Payment created successfully'
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/payments/<int:payment_id>/verify', type='http', auth='none', methods=['GET'], csrf=False)
    def verify_payment(self, payment_id, **kwargs):
        """Verify a payment using QR code"""
        try:
            # Get payment
            payment = request.env['account.payment'].sudo().browse(payment_id)
            if not payment.exists():
                return self._make_response({'error': 'Payment not found'}, 404)
            
            return self._make_response({
                'id': payment.id,
                'voucher_number': payment.voucher_number,
                'partner_name': payment.partner_id.name,
                'amount': payment.amount,
                'currency': payment.currency_id.name,
                'date': payment.date.isoformat() if payment.date else None,
                'state': payment.state,
                'payment_type': payment.payment_type,
                'is_valid': True
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/payments/dashboard', type='http', auth='none', methods=['GET'], csrf=False)
    def get_payment_dashboard_data(self, **kwargs):
        """Get payment dashboard data"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Date range
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            
            if not date_from:
                date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not date_to:
                date_to = datetime.now().strftime('%Y-%m-%d')
            
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to)
            ]
            
            # Get statistics
            total_payments = request.env['account.payment'].search_count(domain)
            posted_payments = request.env['account.payment'].search_count(domain + [('state', '=', 'posted')])
            draft_payments = request.env['account.payment'].search_count(domain + [('state', '=', 'draft')])
            
            # Amount totals
            inbound_payments = request.env['account.payment'].search_read(
                domain + [('payment_type', '=', 'inbound'), ('state', '=', 'posted')],
                fields=['amount']
            )
            outbound_payments = request.env['account.payment'].search_read(
                domain + [('payment_type', '=', 'outbound'), ('state', '=', 'posted')],
                fields=['amount']
            )
            
            total_inbound = sum(payment.get('amount', 0) for payment in inbound_payments)
            total_outbound = sum(payment.get('amount', 0) for payment in outbound_payments)
            
            # Payment methods breakdown
            payment_methods = request.env['account.payment'].read_group(
                domain + [('state', '=', 'posted')],
                fields=['payment_method_id', 'amount:sum'],
                groupby=['payment_method_id']
            )
            
            return self._make_response({
                'period': {'from': date_from, 'to': date_to},
                'summary': {
                    'total_payments': total_payments,
                    'posted_payments': posted_payments,
                    'draft_payments': draft_payments,
                    'total_inbound': total_inbound,
                    'total_outbound': total_outbound,
                    'net_amount': total_inbound - total_outbound
                },
                'payment_methods': payment_methods
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/payments/<int:payment_id>/confirm', type='http', auth='none', methods=['POST'], csrf=False)
    def confirm_payment(self, payment_id, **kwargs):
        """Confirm/post a payment"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Get payment
            payment = request.env['account.payment'].browse(payment_id)
            if not payment.exists():
                return self._make_response({'error': 'Payment not found'}, 404)
            
            # Post payment
            payment.action_post()
            
            return self._make_response({
                'id': payment.id,
                'name': payment.name,
                'state': payment.state,
                'message': 'Payment confirmed successfully'
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/payments/voucher/<string:voucher_number>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_payment_by_voucher(self, voucher_number, **kwargs):
        """Get payment by voucher number"""
        try:
            # Get payment
            payment = request.env['account.payment'].sudo().search([
                ('voucher_number', '=', voucher_number)
            ], limit=1)
            
            if not payment:
                return self._make_response({'error': 'Payment voucher not found'}, 404)
            
            return self._make_response({
                'id': payment.id,
                'voucher_number': payment.voucher_number,
                'partner_name': payment.partner_id.name,
                'amount': payment.amount,
                'currency': payment.currency_id.name,
                'date': payment.date.isoformat() if payment.date else None,
                'state': payment.state,
                'payment_type': payment.payment_type,
                'initiated_by': payment.initiated_by.name if payment.initiated_by else None,
                'reviewed_by': payment.reviewed_by.name if payment.reviewed_by else None,
                'approved_by': payment.approved_by.name if payment.approved_by else None
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)
