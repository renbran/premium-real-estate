# -*- coding: utf-8 -*-
"""
CRM REST API Controller
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


class CRMAPIController(http.Controller):
    """CRM-specific REST API endpoints"""

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

    @http.route('/api/v1/crm/leads', type='http', auth='none', methods=['GET'], csrf=False)
    def get_leads(self, **kwargs):
        """Get CRM leads with filtering options"""
        start_time = time.time()
        
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse parameters
            stage = kwargs.get('stage')
            team_id = kwargs.get('team_id')
            user_id = kwargs.get('user_id')
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))
            
            # Build domain
            domain = []
            if stage:
                domain.append(('stage_id.name', 'ilike', stage))
            if team_id:
                domain.append(('team_id', '=', int(team_id)))
            if user_id:
                domain.append(('user_id', '=', int(user_id)))
            if date_from:
                domain.append(('create_date', '>=', date_from))
            if date_to:
                domain.append(('create_date', '<=', date_to))
            
            # Get leads
            leads = request.env['crm.lead'].search_read(
                domain=domain,
                fields=[
                    'id', 'name', 'partner_name', 'email_from', 'phone', 
                    'stage_id', 'user_id', 'team_id', 'expected_revenue',
                    'probability', 'create_date', 'date_deadline'
                ],
                limit=limit,
                offset=offset,
                order='create_date desc'
            )
            
            total_count = request.env['crm.lead'].search_count(domain)
            
            return self._make_response({
                'leads': leads,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/crm/leads', type='http', auth='none', methods=['POST'], csrf=False)
    def create_lead(self, **kwargs):
        """Create a new CRM lead"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Parse JSON data
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['name']
            for field in required_fields:
                if field not in data:
                    return self._make_response({'error': f'Missing required field: {field}'}, 400)
            
            # Create lead
            lead = request.env['crm.lead'].create(data)
            
            return self._make_response({
                'id': lead.id,
                'name': lead.name,
                'message': 'Lead created successfully'
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/crm/dashboard', type='http', auth='none', methods=['GET'], csrf=False)
    def get_crm_dashboard_data(self, **kwargs):
        """Get CRM dashboard data"""
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
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ]
            
            # Get statistics
            total_leads = request.env['crm.lead'].search_count(domain)
            won_leads = request.env['crm.lead'].search_count(domain + [('stage_id.is_won', '=', True)])
            lost_leads = request.env['crm.lead'].search_count(domain + [('active', '=', False)])
            
            # Revenue data
            won_leads_data = request.env['crm.lead'].search_read(
                domain + [('stage_id.is_won', '=', True)],
                fields=['expected_revenue']
            )
            total_revenue = sum(lead.get('expected_revenue', 0) for lead in won_leads_data)
            
            # Pipeline data by stage
            stages = request.env['crm.stage'].search_read(
                [],
                fields=['id', 'name', 'sequence']
            )
            
            pipeline_data = []
            for stage in stages:
                stage_leads = request.env['crm.lead'].search_count(
                    domain + [('stage_id', '=', stage['id'])]
                )
                pipeline_data.append({
                    'stage': stage['name'],
                    'count': stage_leads
                })
            
            return self._make_response({
                'period': {'from': date_from, 'to': date_to},
                'summary': {
                    'total_leads': total_leads,
                    'won_leads': won_leads,
                    'lost_leads': lost_leads,
                    'total_revenue': total_revenue,
                    'conversion_rate': (won_leads / total_leads * 100) if total_leads > 0 else 0
                },
                'pipeline': pipeline_data
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)

    @http.route('/api/v1/crm/leads/<int:lead_id>', type='http', auth='none', methods=['PUT'], csrf=False)
    def update_lead(self, lead_id, **kwargs):
        """Update a CRM lead"""
        try:
            auth_result = self._authenticate_request()
            if isinstance(auth_result, dict) and 'error' in auth_result:
                return self._make_response(auth_result, auth_result['code'])
            
            # Get lead
            lead = request.env['crm.lead'].browse(lead_id)
            if not lead.exists():
                return self._make_response({'error': 'Lead not found'}, 404)
            
            # Parse JSON data
            data = json.loads(request.httprequest.data.decode('utf-8'))
            
            # Update lead
            lead.write(data)
            
            return self._make_response({
                'id': lead.id,
                'message': 'Lead updated successfully'
            })
            
        except Exception as e:
            return self._make_response({'error': str(e)}, 500)
