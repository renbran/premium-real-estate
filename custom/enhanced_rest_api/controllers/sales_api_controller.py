# -*- coding: utf-8 -*-
"""
Sales REST API Controller
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


class SalesAPIController(http.Controller):
    """Sales-specific REST API endpoints"""

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

    @http.route('/api/v1/sales/orders', type='http', auth='none', methods=['GET'], csrf=False)
    def get_sale_orders(self, **kwargs):
        """Get sale orders with filtering options"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse parameters
            state = kwargs.get('state')
            partner_id = kwargs.get('partner_id')
            user_id = kwargs.get('user_id')
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
            if user_id:
                domain.append(('user_id', '=', int(user_id)))
            if date_from:
                domain.append(('date_order', '>=', date_from))
            if date_to:
                domain.append(('date_order', '<=', date_to))
            
            # Get sale orders
            orders = request.env['sale.order'].search_read(
                domain=domain,
                fields=[
                    'id', 'name', 'partner_id', 'user_id', 'date_order',
                    'state', 'amount_total', 'amount_untaxed', 'currency_id'
                ],
                limit=limit,
                offset=offset,
                order='date_order desc'
            )
            
            total_count = request.env['sale.order'].search_count(domain)
            
            return self._make_response({
                'orders': orders,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/sales/orders', type='http', auth='none', methods=['POST'], csrf=False)
    def create_sale_order(self, **kwargs):
        """Create a new sale order"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse JSON data
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['partner_id']
            for field in required_fields:
                if field not in data:
                    return self._make_response({'error': f'Missing required field: {field}'}, 400)
            
            # Create sale order
            order = request.env['sale.order'].create(data)
            
            return self._make_response({
                'id': order.id,
                'name': order.name,
                'state': order.state,
                'amount_total': order.amount_total,
                'message': 'Sale order created successfully'
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/sales/dashboard', type='http', auth='none', methods=['GET'], csrf=False)
    def get_sales_dashboard_data(self, **kwargs):
        """Get sales dashboard data"""
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
                ('date_order', '>=', date_from),
                ('date_order', '<=', date_to)
            ]
            
            # Get statistics
            total_orders = request.env['sale.order'].search_count(domain)
            confirmed_orders = request.env['sale.order'].search_count(domain + [('state', 'in', ['sale', 'done'])])
            draft_orders = request.env['sale.order'].search_count(domain + [('state', '=', 'draft')])
            
            # Revenue data
            confirmed_orders_data = request.env['sale.order'].search_read(
                domain + [('state', 'in', ['sale', 'done'])],
                fields=['amount_total']
            )
            total_revenue = sum(order.get('amount_total', 0) for order in confirmed_orders_data)
            
            # Monthly trend
            monthly_data = []
            for i in range(12):
                month_start = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime('%Y-%m-01')
                month_end = (datetime.now().replace(day=1) - timedelta(days=(i-1)*30)).strftime('%Y-%m-01')
                
                month_orders = request.env['sale.order'].search_read(
                    [('date_order', '>=', month_start), ('date_order', '<', month_end), ('state', 'in', ['sale', 'done'])],
                    fields=['amount_total']
                )
                month_revenue = sum(order.get('amount_total', 0) for order in month_orders)
                
                monthly_data.append({
                    'month': month_start[:7],  # YYYY-MM format
                    'revenue': month_revenue,
                    'orders': len(month_orders)
                })
            
            # Top customers
            top_customers = request.env['sale.order'].read_group(
                domain + [('state', 'in', ['sale', 'done'])],
                fields=['partner_id', 'amount_total:sum'],
                groupby=['partner_id'],
                limit=10,
                orderby='amount_total desc'
            )
            
            return self._make_response({
                'period': {'from': date_from, 'to': date_to},
                'summary': {
                    'total_orders': total_orders,
                    'confirmed_orders': confirmed_orders,
                    'draft_orders': draft_orders,
                    'total_revenue': total_revenue,
                    'conversion_rate': (confirmed_orders / total_orders * 100) if total_orders > 0 else 0
                },
                'monthly_trend': monthly_data,
                'top_customers': top_customers
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/sales/orders/<int:order_id>/confirm', type='http', auth='none', methods=['POST'], csrf=False)
    def confirm_sale_order(self, order_id, **kwargs):
        """Confirm a sale order"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Get order
            order = request.env['sale.order'].browse(order_id)
            if not order.exists():
                return self._make_response({'error': 'Order not found'}, 404)
            
            # Confirm order
            order.action_confirm()
            
            return self._make_response({
                'id': order.id,
                'name': order.name,
                'state': order.state,
                'message': 'Sale order confirmed successfully'
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/sales/products', type='http', auth='none', methods=['GET'], csrf=False)
    def get_products(self, **kwargs):
        """Get product list"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse parameters
            category_id = kwargs.get('category_id')
            active_only = kwargs.get('active_only', 'true').lower() == 'true'
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))
            
            # Build domain
            domain = [('sale_ok', '=', True)]
            if active_only:
                domain.append(('active', '=', True))
            if category_id:
                domain.append(('categ_id', '=', int(category_id)))
            
            # Get products
            products = request.env['product.template'].search_read(
                domain=domain,
                fields=[
                    'id', 'name', 'list_price', 'standard_price', 
                    'categ_id', 'uom_id', 'active', 'sale_ok'
                ],
                limit=limit,
                offset=offset,
                order='name'
            )
            
            total_count = request.env['product.template'].search_count(domain)
            
            return self._make_response({
                'products': products,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)
