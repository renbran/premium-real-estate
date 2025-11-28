# -*- coding: utf-8 -*-
"""
Extended User Model for Enhanced REST API
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import secrets
import string
import logging

_logger = logging.getLogger(__name__)


class ResUsersExtended(models.Model):
    _inherit = 'res.users'

    # Enhanced API fields
    enhanced_api_key = fields.Char(
        string='Enhanced API Key',
        help="Enhanced API key for REST API access",
        copy=False
    )
    
    api_key_expiry = fields.Datetime(
        string='API Key Expiry',
        help="When the API key expires"
    )
    
    api_rate_limit = fields.Integer(
        string='API Rate Limit (per minute)',
        default=60,
        help="Maximum API requests per minute for this user"
    )
    
    api_last_used = fields.Datetime(
        string='API Last Used',
        help="Last time this user accessed the API"
    )
    
    api_usage_count = fields.Integer(
        string='API Usage Count',
        default=0,
        help="Total number of API requests made by this user"
    )
    
    is_api_user = fields.Boolean(
        string='API User',
        default=False,
        help="Whether this user can access the REST API"
    )

    def generate_enhanced_api_key(self):
        """Generate a new enhanced API key for the user"""
        self.ensure_one()
        
        # Generate a secure random API key
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(40))
        
        self.enhanced_api_key = api_key
        self.api_key_expiry = fields.Datetime.now().replace(year=fields.Datetime.now().year + 1)
        self.is_api_user = True
        
        _logger.info(f"Generated new enhanced API key for user {self.name}")
        
        return api_key

    def revoke_api_key(self):
        """Revoke the current API key"""
        self.ensure_one()
        self.enhanced_api_key = False
        self.api_key_expiry = False
        self.is_api_user = False
        
        _logger.info(f"Revoked API key for user {self.name}")

    @api.model
    def authenticate_api_key(self, api_key):
        """Authenticate a user by API key"""
        if not api_key:
            return False
            
        user = self.search([
            ('enhanced_api_key', '=', api_key),
            ('is_api_user', '=', True),
            ('active', '=', True)
        ], limit=1)
        
        if not user:
            return False
            
        # Check if API key is expired
        if user.api_key_expiry and user.api_key_expiry < fields.Datetime.now():
            _logger.warning(f"Expired API key used for user {user.name}")
            return False
            
        # Update last used timestamp
        user.sudo().write({
            'api_last_used': fields.Datetime.now(),
            'api_usage_count': user.api_usage_count + 1
        })
        
        return user

    @api.constrains('api_rate_limit')
    def _check_api_rate_limit(self):
        for user in self:
            if user.api_rate_limit < 1:
                raise ValidationError(_("API rate limit must be at least 1 request per minute"))
