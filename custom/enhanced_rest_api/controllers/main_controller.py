# -*- coding: utf-8 -*-
"""
Enhanced REST API Main Controller
"""

import json
import time
import logging
from datetime import datetime

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class EnhancedRestAPIController(http.Controller):
    """Enhanced REST API Controller with advanced features"""

    def _authenticate_request(self):
        """Authenticate API request using enhanced API key"""
        api_key = request.httprequest.headers.get('X-API-Key') or request.httprequest.headers.get('api-key')
        
        if not api_key:
            return {
                'error': 'API key required',
                'code': 401,
                'message': 'Please provide an API key in X-API-Key header'
            }
        
        user = request.env['res.users'].sudo().authenticate_api_key(api_key)
        if not user:
            return {
                'error': 'Invalid API key',
                'code': 401,
                'message': 'The provided API key is invalid or expired'
            }
        
        # Set the user in request context
        request.uid = user.id
        return user

    def _log_api_request(self, endpoint, method, response_time, success=True, error_msg=None):
        """Log API request for monitoring and analytics"""
        try:
            request.env['enhanced.api.log'].sudo().create({
                'endpoint_name': endpoint,
                'user_id': request.uid,
                'ip_address': request.httprequest.remote_addr,
                'http_method': method,
                'response_time': response_time,
                'is_success': success,
                'error_message': error_msg or '',
                'response_code': '200' if success else '500'
            })
        except Exception as e:
            _logger.error(f"Failed to log API request: {str(e)}")

    def _make_response(self, data, status=200):
        """Create standardized API response"""
        response_data = {
            'success': status < 400,
            'timestamp': datetime.now().isoformat(),
            'data': data if status < 400 else None,
            'error': data if status >= 400 else None
        }
        
        response = request.make_response(
            data=json.dumps(response_data, default=str),
            headers={'Content-Type': 'application/json'}
        )
        response.status_code = status
        return response

    @http.route('/api/v1/auth/generate-key', type='http', auth='user', methods=['POST'], csrf=False)
    def generate_api_key(self, **kwargs):
        """Generate a new API key for the authenticated user"""
        start_time = time.time()
        
        try:
            user = request.env.user
            api_key = user.generate_enhanced_api_key()
            
            response_time = (time.time() - start_time) * 1000
            self._log_api_request('/api/v1/auth/generate-key', 'POST', response_time)
            
            return self._make_response({
                'api_key': api_key,
                'expires_at': user.api_key_expiry.isoformat() if user.api_key_expiry else None,
                'rate_limit': user.api_rate_limit
            })
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self._log_api_request('/api/v1/auth/generate-key', 'POST', response_time, False, str(e))
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/auth/revoke-key', type='http', auth='none', methods=['POST'], csrf=False)
    def revoke_api_key(self, **kwargs):
        """Revoke the current API key"""
        start_time = time.time()
        
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            user = auth_result
            user.revoke_api_key()
            
            response_time = (time.time() - start_time) * 1000
            self._log_api_request('/api/v1/auth/revoke-key', 'POST', response_time)
            
            return self._make_response({'message': 'API key revoked successfully'})
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self._log_api_request('/api/v1/auth/revoke-key', 'POST', response_time, False, str(e))
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/status', type='http', auth='none', methods=['GET'], csrf=False)
    def api_status(self, **kwargs):
        """Get API status and health check"""
        start_time = time.time()
        
        try:
            response_time = (time.time() - start_time) * 1000
            
            return self._make_response({
                'status': 'healthy',
                'version': '1.0.0',
                'server_time': datetime.now().isoformat(),
                'response_time_ms': response_time
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/user/profile', type='http', auth='none', methods=['GET'], csrf=False)
    def get_user_profile(self, **kwargs):
        """Get current user profile information"""
        start_time = time.time()
        
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            user = auth_result
            
            response_time = (time.time() - start_time) * 1000
            self._log_api_request('/api/v1/user/profile', 'GET', response_time)
            
            return self._make_response({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'login': user.login,
                'api_usage_count': user.api_usage_count,
                'api_last_used': user.api_last_used.isoformat() if user.api_last_used else None,
                'api_rate_limit': user.api_rate_limit
            })
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self._log_api_request('/api/v1/user/profile', 'GET', response_time, False, str(e))
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/models/<string:model_name>/search', type='http', auth='none', methods=['GET'], csrf=False)
    def search_records(self, model_name, **kwargs):
        """Generic search endpoint for any model"""
        start_time = time.time()
        
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse query parameters
            domain = json.loads(kwargs.get('domain', '[]'))
            fields = kwargs.get('fields', '').split(',') if kwargs.get('fields') else []
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))
            order = kwargs.get('order', 'id')
            
            # Security check - verify user has access to the model
            try:
                request.env[model_name].check_access_rights('read')
            except AccessError:
                return self._make_response({'error': f'Access denied to model {model_name}'}, 403)
            
            # Search records
            records = request.env[model_name].search_read(
                domain=domain,
                fields=fields or None,
                limit=limit,
                offset=offset,
                order=order
            )
            
            # Get total count
            total_count = request.env[model_name].search_count(domain)
            
            response_time = (time.time() - start_time) * 1000
            self._log_api_request(f'/api/v1/models/{model_name}/search', 'GET', response_time)
            
            return self._make_response({
                'records': records,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self._log_api_request(f'/api/v1/models/{model_name}/search', 'GET', response_time, False, str(e))
            return self._make_response({'error': str(e)}, 500)
