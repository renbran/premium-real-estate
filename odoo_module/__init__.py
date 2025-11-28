# -*- coding: utf-8 -*-
from . import models
from . import controllers

def post_init_hook(cr, registry):
    """Post-installation hook to set up default configuration"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create default webhook configuration if it doesn't exist
    config = env['bill.automation.config'].search([], limit=1)
    if not config:
        env['bill.automation.config'].create({
            'name': 'Default Bill Automation Config',
            'webhook_enabled': True,
            'auto_create_vendors': True,
            'duplicate_detection': True,
            'file_attachment_enabled': True,
            'api_key_required': False,
        })

def uninstall_hook(cr, registry):
    """Pre-uninstallation hook to clean up"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clean up any remaining webhook logs older than 30 days
    import datetime
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
    old_logs = env['webhook.log'].search([
        ('create_date', '<', cutoff_date)
    ])
    if old_logs:
        old_logs.unlink()