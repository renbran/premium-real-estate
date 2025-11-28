# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    """
    Partner Extension for Payment Workflow
    
    Extends res.partner with payment-related information and approval settings.
    """
    _inherit = 'res.partner'
    
    # Payment approval settings
    payment_approval_required = fields.Boolean(
        string='Require Payment Approval',
        help="Always require approval for payments to/from this partner"
    )
    
    payment_approval_threshold = fields.Monetary(
        string='Approval Threshold',
        currency_field='currency_id',
        help="Amount above which approval is required for this partner"
    )
    
    payment_auto_approve = fields.Boolean(
        string='Auto Approve Payments',
        default=False,
        help="Automatically approve payments to this partner (trusted partners)"
    )
    
    # Payment limits
    daily_payment_limit = fields.Monetary(
        string='Daily Payment Limit',
        currency_field='currency_id',
        help="Maximum amount that can be paid to this partner per day"
    )
    
    monthly_payment_limit = fields.Monetary(
        string='Monthly Payment Limit', 
        currency_field='currency_id',
        help="Maximum amount that can be paid to this partner per month"
    )
    
    # QR Code settings
    qr_verification_enabled = fields.Boolean(
        string='Enable QR Verification',
        default=True,
        help="Enable QR code verification for payments to this partner"
    )
    
    # Payment history and statistics
    total_payments_sent = fields.Monetary(
        string='Total Payments Sent',
        compute='_compute_payment_statistics',
        currency_field='currency_id',
        help="Total amount of payments sent to this partner"
    )
    
    total_payments_received = fields.Monetary(
        string='Total Payments Received',
        compute='_compute_payment_statistics', 
        currency_field='currency_id',
        help="Total amount of payments received from this partner"
    )
    
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_statistics',
        help="Total number of payments with this partner"
    )
    
    last_payment_date = fields.Date(
        string='Last Payment Date',
        compute='_compute_payment_statistics',
        help="Date of last payment with this partner"
    )
    
    # Risk assessment
    payment_risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('blocked', 'Blocked'),
    ], string='Payment Risk Level', default='low',
       help="Risk level for payments to this partner")
    
    payment_notes = fields.Text(
        string='Payment Notes',
        help="Special instructions or notes for payments to this partner"
    )
    
    # Approval routing
    preferred_approver_ids = fields.Many2many(
        'res.users',
        'partner_preferred_approver_rel',
        string='Preferred Approvers',
        help="Preferred users for approving payments to this partner"
    )
    
    requires_specific_approver = fields.Boolean(
        string='Requires Specific Approver',
        default=False,
        help="Payments to this partner must be approved by specific users"
    )
    
    @api.depends('name')
    def _compute_payment_statistics(self):
        """Compute payment statistics for this partner"""
        for partner in self:
            # Get all payments related to this partner
            outbound_payments = self.env['account.payment'].search([
                ('partner_id', '=', partner.id),
                ('payment_type', '=', 'outbound'),
                ('state', 'in', ['post', 'authorize']),
            ])
            
            inbound_payments = self.env['account.payment'].search([
                ('partner_id', '=', partner.id),
                ('payment_type', '=', 'inbound'),
                ('state', 'in', ['post', 'authorize']),
            ])
            
            all_payments = outbound_payments + inbound_payments
            
            # Calculate totals
            partner.total_payments_sent = sum(outbound_payments.mapped('amount'))
            partner.total_payments_received = sum(inbound_payments.mapped('amount'))
            partner.payment_count = len(all_payments)
            
            # Get last payment date
            if all_payments:
                partner.last_payment_date = max(all_payments.mapped('date'))
            else:
                partner.last_payment_date = False
    
    def check_payment_limits(self, amount, payment_date=None):
        """
        Check if payment amount exceeds partner limits
        
        Args:
            amount (float): Payment amount
            payment_date (date, optional): Payment date (default: today)
            
        Returns:
            dict: Result with success status and message
        """
        if not payment_date:
            payment_date = fields.Date.today()
        
        # Check daily limit
        if self.daily_payment_limit > 0:
            daily_payments = self.env['account.payment'].search([
                ('partner_id', '=', self.id),
                ('payment_type', '=', 'outbound'),
                ('date', '=', payment_date),
                ('state', 'in', ['post', 'authorize']),
            ])
            daily_total = sum(daily_payments.mapped('amount')) + amount
            
            if daily_total > self.daily_payment_limit:
                return {
                    'success': False,
                    'message': _('Payment exceeds daily limit of %s for partner %s') % (
                        self.daily_payment_limit, self.name
                    )
                }
        
        # Check monthly limit
        if self.monthly_payment_limit > 0:
            month_start = payment_date.replace(day=1)
            monthly_payments = self.env['account.payment'].search([
                ('partner_id', '=', self.id),
                ('payment_type', '=', 'outbound'),
                ('date', '>=', month_start),
                ('date', '<=', payment_date),
                ('state', 'in', ['post', 'authorize']),
            ])
            monthly_total = sum(monthly_payments.mapped('amount')) + amount
            
            if monthly_total > self.monthly_payment_limit:
                return {
                    'success': False,
                    'message': _('Payment exceeds monthly limit of %s for partner %s') % (
                        self.monthly_payment_limit, self.name
                    )
                }
        
        return {'success': True, 'message': 'Payment within limits'}
    
    def get_payment_approval_requirements(self, amount):
        """
        Get approval requirements for payment to this partner
        
        Args:
            amount (float): Payment amount
            
        Returns:
            dict: Approval requirements
        """
        requirements = {
            'approval_required': False,
            'auto_approve': False,
            'specific_approver_required': False,
            'preferred_approvers': [],
            'risk_level': self.payment_risk_level,
        }
        
        # Check if approval is always required
        if self.payment_approval_required:
            requirements['approval_required'] = True
        
        # Check threshold
        if self.payment_approval_threshold > 0 and amount > self.payment_approval_threshold:
            requirements['approval_required'] = True
        
        # Check auto approve
        if self.payment_auto_approve and self.payment_risk_level == 'low':
            requirements['auto_approve'] = True
            requirements['approval_required'] = False
        
        # Block if high risk
        if self.payment_risk_level == 'blocked':
            requirements['approval_required'] = True
            requirements['auto_approve'] = False
        
        # Check specific approver requirement
        if self.requires_specific_approver:
            requirements['specific_approver_required'] = True
            requirements['preferred_approvers'] = self.preferred_approver_ids.ids
        
        return requirements
    
    def action_view_payments(self):
        """Action to view payments for this partner"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payments - %s') % self.name,
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
    
    def action_view_payment_history(self):
        """Action to view payment approval history for this partner"""
        payment_ids = self.env['account.payment'].search([
            ('partner_id', '=', self.id)
        ]).ids
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment History - %s') % self.name,
            'res_model': 'payment.approval.history',
            'view_mode': 'tree,form',
            'domain': [('payment_id', 'in', payment_ids)],
            'context': {'default_partner_id': self.id},
        }
    
    @api.model
    def get_payment_risk_partners(self, risk_level='high'):
        """Get partners with specific risk level"""
        return self.search([('payment_risk_level', '=', risk_level)])
    
    def update_risk_level(self, new_risk_level, reason=None):
        """Update partner risk level with audit trail"""
        old_risk_level = self.payment_risk_level
        self.payment_risk_level = new_risk_level
        
        # Log the change
        message = _("Payment risk level changed from %s to %s") % (
            old_risk_level, new_risk_level
        )
        if reason:
            message += _("\nReason: %s") % reason
        
        self.message_post(body=message, subtype_xmlid='mail.mt_note')
        
        return True
