# -*- coding: utf-8 -*-
"""
API Logging Model
"""

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class APIUsageLog(models.Model):
    _name = 'enhanced.api.usage.log'
    _description = 'API Usage Statistics'
    _order = 'date desc'

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
    )
    
    endpoint_path = fields.Char(
        string='Endpoint Path',
        required=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User'
    )
    
    total_requests = fields.Integer(
        string='Total Requests',
        default=0
    )
    
    successful_requests = fields.Integer(
        string='Successful Requests',
        default=0
    )
    
    failed_requests = fields.Integer(
        string='Failed Requests',
        default=0
    )
    
    avg_response_time = fields.Float(
        string='Average Response Time (ms)',
        default=0.0
    )
    
    @api.depends('successful_requests', 'total_requests')
    def _compute_success_rate(self):
        for record in self:
            if record.total_requests > 0:
                record.success_rate = (record.successful_requests / record.total_requests) * 100
            else:
                record.success_rate = 0.0
    
    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_success_rate',
        store=True
    )
