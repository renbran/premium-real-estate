# -*- coding: utf-8 -*-
"""
Enhanced API Configuration Model
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class APIConfig(models.Model):
    _name = 'enhanced.api.config'
    _description = 'Enhanced API Configuration'
    _rec_name = 'endpoint_name'
    _order = 'endpoint_name'

    endpoint_name = fields.Char(
        string='Endpoint Name',
        required=True,
        help="Name of the API endpoint"
    )
    
    endpoint_path = fields.Char(
        string='Endpoint Path',
        required=True,
        help="URL path for the API endpoint (e.g., /api/v1/crm/leads)"
    )
    
    model_name = fields.Char(
        string='Model Name',
        required=True,
        help="Odoo model name this endpoint operates on"
    )
    
    http_methods = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH')
    ], string='HTTP Method', required=True, default='GET')
    
    authentication_type = fields.Selection([
        ('none', 'No Authentication'),
        ('user', 'User Authentication'),
        ('api_key', 'API Key'),
        ('jwt', 'JWT Token'),
        ('oauth', 'OAuth2')
    ], string='Authentication Type', default='api_key', required=True)
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this endpoint is active and available"
    )
    
    rate_limit = fields.Integer(
        string='Rate Limit (per minute)',
        default=60,
        help="Maximum number of requests per minute for this endpoint"
    )
    
    allowed_groups = fields.Many2many(
        'res.groups',
        string='Allowed Groups',
        help="User groups that can access this endpoint"
    )
    
    description = fields.Text(
        string='Description',
        help="Description of what this endpoint does"
    )
    
    version = fields.Char(
        string='API Version',
        default='v1',
        help="API version for this endpoint"
    )
    
    @api.constrains('endpoint_path')
    def _check_endpoint_path(self):
        for record in self:
            if not record.endpoint_path.startswith('/'):
                raise ValidationError(_("Endpoint path must start with '/'"))
    
    @api.constrains('rate_limit')
    def _check_rate_limit(self):
        for record in self:
            if record.rate_limit < 1:
                raise ValidationError(_("Rate limit must be at least 1 request per minute"))


class APIEndpointLog(models.Model):
    _name = 'enhanced.api.log'
    _description = 'API Endpoint Usage Log'
    _order = 'create_date desc'
    _rec_name = 'endpoint_name'

    endpoint_name = fields.Char(
        string='Endpoint',
        required=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True
    )
    
    ip_address = fields.Char(
        string='IP Address'
    )
    
    http_method = fields.Char(
        string='HTTP Method'
    )
    
    request_data = fields.Text(
        string='Request Data'
    )
    
    response_code = fields.Char(
        string='Response Code'
    )
    
    response_time = fields.Float(
        string='Response Time (ms)',
        help="Response time in milliseconds"
    )
    
    error_message = fields.Text(
        string='Error Message'
    )
    
    is_success = fields.Boolean(
        string='Success',
        default=True
    )
