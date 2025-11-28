# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import wizard


def post_init_hook(cr, registry):
    """Post-installation hook to set up default data"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create default workflow stages if they don't exist
    stages = env['payment.workflow.stage'].search([])
    if not stages:
        env['payment.workflow.stage']._create_default_stages()
    
    # Set up default sequences if they don't exist
    sequences_to_create = [
        ('payment.voucher', 'Payment Voucher', 'PV'),
        ('receipt.voucher', 'Receipt Voucher', 'RV'),
    ]
    
    for code, name, prefix in sequences_to_create:
        existing = env['ir.sequence'].search([('code', '=', code)], limit=1)
        if not existing:
            env['ir.sequence'].create({
                'name': name,
                'code': code,
                'prefix': prefix,
                'padding': 5,
            })


def uninstall_hook(cr, registry):
    """Pre-uninstallation hook to clean up data"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clean up verification logs older than 1 year
    import datetime
    old_date = datetime.datetime.now() - datetime.timedelta(days=365)
    old_verifications = env['payment.qr.verification'].search([
        ('verification_date', '<', old_date)
    ])
    old_verifications.unlink()
