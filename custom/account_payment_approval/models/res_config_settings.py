# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """Configuration settings for payment approval"""
    _inherit = 'res.config.settings'

    # Payment Approval Configuration
    approval_amount_limit = fields.Float(
        string='Approval Amount Limit',
        config_parameter='account_payment_approval.approval_amount_limit',
        default=10000.0,
        help="Maximum amount that can be approved without higher authorization"
    )
    
    authorization_amount_limit = fields.Float(
        string='Authorization Amount Limit',
        config_parameter='account_payment_approval.authorization_amount_limit',
        default=50000.0,
        help="Maximum amount that can be authorized"
    )
    
    require_dual_approval = fields.Boolean(
        string='Require Dual Approval',
        config_parameter='account_payment_approval.require_dual_approval',
        default=True,
        help="Require two different users for approval and authorization"
    )
    
    auto_notify_reviewers = fields.Boolean(
        string='Auto Notify Reviewers',
        config_parameter='account_payment_approval.auto_notify_reviewers',
        default=True,
        help="Automatically notify reviewers when payments are submitted"
    )
    
    enable_qr_verification = fields.Boolean(
        string='Enable QR Verification',
        config_parameter='account_payment_approval.enable_qr_verification',
        default=True,
        help="Enable QR code verification for payments"
    )
    
    enable_digital_signature = fields.Boolean(
        string='Enable Digital Signature',
        config_parameter='account_payment_approval.enable_digital_signature',
        default=True,
        help="Enable digital signature for payment authorization"
    )
    
    auto_assign_reviewers = fields.Boolean(
        string='Auto Assign Reviewers',
        config_parameter='account_payment_approval.auto_assign_reviewers',
        default=False,
        help="Automatically assign reviewers based on payment amount"
    )
    
    max_review_days = fields.Integer(
        string='Maximum Review Days',
        config_parameter='account_payment_approval.max_review_days',
        default=5,
        help="Maximum days allowed for payment review"
    )
    
    payment_approval_journal_ids = fields.Many2many(
        'account.journal',
        string='Approval Required Journals',
        help="Journals that require payment approval workflow"
    )

    @api.model
    def get_values(self):
        """Get configuration values"""
        res = super().get_values()
        
        # Get journal IDs from config parameter
        journal_ids = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval_journal_ids', ''
        )
        
        if journal_ids:
            try:
                journal_ids = [int(x) for x in journal_ids.split(',') if x.strip()]
                res['payment_approval_journal_ids'] = [(6, 0, journal_ids)]
            except ValueError:
                res['payment_approval_journal_ids'] = [(6, 0, [])]
        else:
            res['payment_approval_journal_ids'] = [(6, 0, [])]
        
        return res

    def set_values(self):
        """Set configuration values"""
        super().set_values()
        
        # Save journal IDs to config parameter
        journal_ids = ','.join(str(id) for id in self.payment_approval_journal_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'account_payment_approval.payment_approval_journal_ids', journal_ids
        )