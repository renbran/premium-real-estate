# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountJournal(models.Model):
    """
    Account Journal Extension for Payment Workflow
    
    Extends account.journal with payment workflow specific settings.
    """
    _inherit = 'account.journal'
    
    # Payment workflow settings
    payment_approval_required = fields.Boolean(
        string='Require Payment Approval',
        default=True,
        help="Require approval workflow for payments in this journal"
    )
    
    payment_approval_threshold = fields.Monetary(
        string='Approval Threshold',
        currency_field='currency_id',
        help="Amount above which approval is required (0 = always require approval)"
    )
    
    payment_auto_approve_limit = fields.Monetary(
        string='Auto Approve Limit',
        currency_field='currency_id',
        help="Amount below which payments are automatically approved"
    )
    
    # QR Code settings
    payment_qr_enabled = fields.Boolean(
        string='Enable QR Codes',
        default=True,
        help="Generate QR codes for payments in this journal"
    )
    
    payment_qr_template_id = fields.Many2one(
        'payment.qr.template',
        string='QR Code Template',
        help="Template for QR code generation"
    )
    
    # Notification settings
    payment_notification_enabled = fields.Boolean(
        string='Enable Notifications',
        default=True,
        help="Send email notifications for payment workflow events"
    )
    
    payment_notification_recipients = fields.Text(
        string='Notification Recipients',
        help="Additional email addresses for notifications (comma separated)"
    )
    
    # Workflow stage overrides
    custom_workflow_enabled = fields.Boolean(
        string='Use Custom Workflow',
        default=False,
        help="Use journal-specific workflow stages instead of company default"
    )
    
    workflow_stage_ids = fields.Many2many(
        'payment.workflow.stage',
        string='Custom Workflow Stages',
        help="Custom workflow stages for this journal"
    )
    
    # Security settings
    require_dual_approval = fields.Boolean(
        string='Require Dual Approval',
        default=False,
        help="Require two different users for approval"
    )
    
    restrict_approval_to_groups = fields.Boolean(
        string='Restrict to Groups',
        default=True,
        help="Restrict approval to specific user groups"
    )
    
    approval_group_ids = fields.Many2many(
        'res.groups',
        'journal_approval_group_rel',
        string='Approval Groups',
        help="Groups allowed to approve payments in this journal"
    )
    
    # Computed fields
    pending_payment_count = fields.Integer(
        string='Pending Payments',
        compute='_compute_pending_payment_count',
        help="Number of payments pending approval"
    )
    
    @api.depends('code')
    def _compute_pending_payment_count(self):
        """Compute number of pending payments"""
        for journal in self:
            count = self.env['account.payment'].search_count([
                ('journal_id', '=', journal.id),
                ('state', 'in', ['review', 'approve', 'authorize']),
            ])
            journal.pending_payment_count = count
    
    def get_workflow_stages(self):
        """Get workflow stages for this journal"""
        if self.custom_workflow_enabled and self.workflow_stage_ids:
            return self.workflow_stage_ids.sorted('sequence')
        else:
            # Use company default stages
            return self.env['payment.workflow.stage'].search([
                ('company_id', '=', self.company_id.id)
            ], order='sequence')
    
    def can_user_approve_payments(self, user=None):
        """Check if user can approve payments in this journal"""
        if not user:
            user = self.env.user
        
        # Super user can always approve
        if user._is_superuser():
            return True
        
        # Check if restrictions are enabled
        if not self.restrict_approval_to_groups:
            return True
        
        # Check if user is in approval groups
        if self.approval_group_ids:
            user_groups = user.groups_id
            return any(group in user_groups for group in self.approval_group_ids)
        
        return False
    
    def should_require_approval(self, amount):
        """Check if payment amount requires approval"""
        if not self.payment_approval_required:
            return False
        
        # Auto approve if below limit
        if self.payment_auto_approve_limit and amount <= self.payment_auto_approve_limit:
            return False
        
        # Always require approval if threshold is 0
        if self.payment_approval_threshold == 0:
            return True
        
        # Require approval if above threshold
        return amount > self.payment_approval_threshold
    
    def get_notification_recipients(self, stage=None):
        """Get email recipients for notifications"""
        recipients = []
        
        # Add journal-specific recipients
        if self.payment_notification_recipients:
            emails = [email.strip() for email in self.payment_notification_recipients.split(',')]
            recipients.extend(emails)
        
        # Add stage-specific recipients
        if stage and stage.approval_group_ids:
            group_users = stage.approval_group_ids.mapped('users')
            group_emails = group_users.mapped('email')
            recipients.extend(filter(None, group_emails))
        
        # Add journal approvers
        if self.approval_group_ids:
            approver_users = self.approval_group_ids.mapped('users')
            approver_emails = approver_users.mapped('email')
            recipients.extend(filter(None, approver_emails))
        
        # Remove duplicates and return
        return list(set(recipients))
    
    def action_view_pending_payments(self):
        """Action to view pending payments"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pending Payments - %s') % self.name,
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [
                ('journal_id', '=', self.id),
                ('state', 'in', ['review', 'approve', 'authorize']),
            ],
            'context': {'default_journal_id': self.id},
        }
