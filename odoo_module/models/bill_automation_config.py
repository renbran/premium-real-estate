# -*- coding: utf-8 -*-
"""
Bill Automation Configuration Model
===================================

This model stores configuration settings for the bill automation webhook system.
It allows administrators to control various aspects of the automation process
including security, processing options, and feature toggles.

Features:
- Webhook enable/disable toggle
- API key authentication settings
- Vendor auto-creation control
- Duplicate detection settings
- File attachment configuration
- Error notification settings
- Processing limits and timeouts

Author: Bill Automation Project Team
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BillAutomationConfig(models.Model):
    """Configuration settings for bill automation webhook"""
    
    _name = 'bill.automation.config'
    _description = 'Bill Automation Configuration'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(
        string='Configuration Name',
        required=True,
        default='Bill Automation Config'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this configuration is active'
    )
    
    # Webhook Settings
    webhook_enabled = fields.Boolean(
        string='Webhook Enabled',
        default=True,
        help='Enable or disable webhook processing'
    )
    
    webhook_url = fields.Char(
        string='Webhook URL',
        compute='_compute_webhook_url',
        help='The URL for webhook calls'
    )
    
    # Security Settings
    api_key_required = fields.Boolean(
        string='Require API Key',
        default=False,
        help='Require API key authentication for webhook calls'
    )
    
    api_key = fields.Char(
        string='API Key',
        help='API key for webhook authentication (leave empty to auto-generate)'
    )
    
    allowed_ips = fields.Text(
        string='Allowed IP Addresses',
        help='Comma-separated list of allowed IP addresses (leave empty to allow all)'
    )
    
    # Processing Settings
    auto_create_vendors = fields.Boolean(
        string='Auto-create Vendors',
        default=True,
        help='Automatically create new vendors if not found'
    )
    
    duplicate_detection = fields.Boolean(
        string='Duplicate Detection',
        default=True,
        help='Prevent creation of duplicate bills'
    )
    
    file_attachment_enabled = fields.Boolean(
        string='File Attachment',
        default=True,
        help='Download and attach files from webhook requests'
    )
    
    # Default Values
    default_journal_id = fields.Many2one(
        'account.journal',
        string='Default Journal',
        domain="[('type', '=', 'purchase')]",
        help='Default journal for created bills'
    )
    
    default_expense_account_id = fields.Many2one(
        'account.account',
        string='Default Expense Account',
        domain="[('account_type', '=', 'expense')]",
        help='Default expense account for bill lines'
    )
    
    default_currency_id = fields.Many2one(
        'res.currency',
        string='Default Currency',
        default=lambda self: self.env.company.currency_id,
        help='Default currency for bills'
    )
    
    # Processing Limits
    max_file_size_mb = fields.Float(
        string='Max File Size (MB)',
        default=10.0,
        help='Maximum file size for attachments in megabytes'
    )
    
    request_timeout = fields.Integer(
        string='Request Timeout (seconds)',
        default=30,
        help='Timeout for file downloads and external requests'
    )
    
    # Notification Settings
    error_notification_enabled = fields.Boolean(
        string='Error Notifications',
        default=True,
        help='Send notifications when webhook processing fails'
    )
    
    notification_email = fields.Char(
        string='Notification Email',
        help='Email address for error notifications'
    )
    
    # Statistics
    total_requests = fields.Integer(
        string='Total Requests',
        compute='_compute_statistics',
        help='Total number of webhook requests processed'
    )
    
    successful_requests = fields.Integer(
        string='Successful Requests',
        compute='_compute_statistics',
        help='Number of successfully processed requests'
    )
    
    failed_requests = fields.Integer(
        string='Failed Requests',
        compute='_compute_statistics',
        help='Number of failed requests'
    )
    
    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_statistics',
        help='Success rate percentage'
    )
    
    last_request_date = fields.Datetime(
        string='Last Request',
        compute='_compute_statistics',
        help='Date of the last webhook request'
    )

    @api.depends('webhook_enabled')
    def _compute_webhook_url(self):
        """Generate the webhook URL"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if base_url:
                record.webhook_url = f"{base_url}/api/v1/bills/create"
            else:
                record.webhook_url = "/api/v1/bills/create"

    @api.depends('webhook_enabled')
    def _compute_statistics(self):
        """Compute processing statistics"""
        for record in self:
            if record.webhook_enabled:
                logs = self.env['webhook.log'].search([])
                
                record.total_requests = len(logs)
                record.successful_requests = len(logs.filtered(lambda l: l.status == 'success'))
                record.failed_requests = len(logs.filtered(lambda l: l.status == 'failed'))
                
                if record.total_requests > 0:
                    record.success_rate = (record.successful_requests / record.total_requests) * 100
                else:
                    record.success_rate = 0.0
                
                if logs:
                    record.last_request_date = max(logs.mapped('create_date'))
                else:
                    record.last_request_date = False
            else:
                record.total_requests = 0
                record.successful_requests = 0
                record.failed_requests = 0
                record.success_rate = 0.0
                record.last_request_date = False

    @api.model
    def create(self, vals):
        """Override create to ensure only one active config exists"""
        if vals.get('active', True):
            # Deactivate other configs
            self.search([('active', '=', True)]).write({'active': False})
        
        # Generate API key if not provided
        if vals.get('api_key_required', False) and not vals.get('api_key'):
            vals['api_key'] = self._generate_api_key()
        
        return super().create(vals)

    def write(self, vals):
        """Override write to handle active config logic"""
        if vals.get('active', False):
            # Deactivate other configs
            other_configs = self.search([('id', '!=', self.id), ('active', '=', True)])
            if other_configs:
                other_configs.write({'active': False})
        
        # Generate API key if required but not set
        if vals.get('api_key_required', False) and not self.api_key and not vals.get('api_key'):
            vals['api_key'] = self._generate_api_key()
        
        return super().write(vals)

    @api.constrains('max_file_size_mb')
    def _check_file_size(self):
        """Validate file size limit"""
        for record in self:
            if record.max_file_size_mb <= 0:
                raise ValidationError(_('Maximum file size must be greater than 0'))
            if record.max_file_size_mb > 100:
                raise ValidationError(_('Maximum file size cannot exceed 100 MB'))

    @api.constrains('request_timeout')
    def _check_timeout(self):
        """Validate request timeout"""
        for record in self:
            if record.request_timeout < 5:
                raise ValidationError(_('Request timeout must be at least 5 seconds'))
            if record.request_timeout > 300:
                raise ValidationError(_('Request timeout cannot exceed 300 seconds'))

    @api.constrains('notification_email')
    def _check_notification_email(self):
        """Validate notification email format"""
        import re
        for record in self:
            if record.notification_email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, record.notification_email):
                    raise ValidationError(_('Please enter a valid email address'))

    def _generate_api_key(self):
        """Generate a random API key"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    def action_regenerate_api_key(self):
        """Action to regenerate API key"""
        self.ensure_one()
        new_key = self._generate_api_key()
        self.write({'api_key': new_key})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('API key regenerated successfully'),
                'type': 'success',
            }
        }

    def action_test_webhook(self):
        """Action to test webhook configuration"""
        self.ensure_one()
        
        try:
            # Run basic configuration checks
            errors = []
            
            if not self.webhook_enabled:
                errors.append(_('Webhook is disabled'))
            
            if not self.default_journal_id:
                journals = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
                if not journals:
                    errors.append(_('No purchase journal found'))
            
            if not self.default_expense_account_id:
                accounts = self.env['account.account'].search([('account_type', '=', 'expense')], limit=1)
                if not accounts:
                    errors.append(_('No expense account found'))
            
            if errors:
                message = _('Configuration issues found:\\n') + '\\n'.join(errors)
                notification_type = 'danger'
            else:
                message = _('Webhook configuration is valid and ready to use')
                notification_type = 'success'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': notification_type,
                }
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Test failed: %s') % str(e),
                    'type': 'danger',
                }
            }

    def action_view_webhook_logs(self):
        """Action to view webhook logs"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Webhook Logs'),
            'res_model': 'webhook.log',
            'view_mode': 'tree,form,kanban',
            'target': 'current',
            'context': {'create': False}
        }

    def action_view_statistics(self):
        """Action to view detailed statistics"""
        self.ensure_one()
        
        stats = self.env['webhook.log'].get_statistics()
        
        message = _(
            'Webhook Statistics:\\n\\n'
            'Last 24 hours: %s requests (%s%% success)\\n'
            'Last 7 days: %s requests (%s%% success)\\n'
            'All time: %s requests (%s%% success)'
        ) % (
            stats['last_24h']['total'], stats['last_24h']['success_rate'],
            stats['last_7d']['total'], stats['last_7d']['success_rate'],
            stats['all_time']['total'], stats['all_time']['success_rate']
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'info',
            }
        }

    @api.model
    def get_active_config(self):
        """Get the active configuration"""
        return self.search([('active', '=', True)], limit=1)

    def is_ip_allowed(self, ip_address):
        """Check if IP address is allowed"""
        self.ensure_one()
        
        if not self.allowed_ips:
            return True  # No restrictions
        
        allowed_list = [ip.strip() for ip in self.allowed_ips.split(',') if ip.strip()]
        return ip_address in allowed_list

    def send_error_notification(self, error_message, request_data=None):
        """Send error notification email"""
        self.ensure_one()
        
        if not self.error_notification_enabled or not self.notification_email:
            return False
        
        try:
            mail_template = self.env.ref('bill_automation.email_template_webhook_error', raise_if_not_found=False)
            if mail_template:
                mail_template.with_context(
                    error_message=error_message,
                    request_data=request_data,
                    config_name=self.name
                ).send_mail(self.id, force_send=True)
                return True
        except Exception as e:
            # Log the error but don't fail the main process
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f'Failed to send error notification: {str(e)}')
        
        return False