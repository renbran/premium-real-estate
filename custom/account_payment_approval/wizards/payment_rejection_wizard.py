# -*- coding: utf-8 -*-
#############################################################################
#
#    Payment Rejection Wizard
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class PaymentRejectionWizard(models.TransientModel):
    """Wizard for rejecting payments with detailed reasons"""
    _name = 'payment.rejection.wizard'
    _description = 'Payment Rejection Wizard'
    
    # ========================================
    # Wizard Fields
    # ========================================
    
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        help="Payment to be rejected"
    )
    
    rejection_category = fields.Selection([
        ('documentation', 'Incomplete Documentation'),
        ('authorization', 'Insufficient Authorization'),
        ('compliance', 'Compliance Issues'),
        ('duplicate', 'Duplicate Payment'),
        ('incorrect_amount', 'Incorrect Amount'),
        ('incorrect_vendor', 'Incorrect Vendor'),
        ('budget', 'Budget Constraints'),
        ('approval_limit', 'Exceeds Approval Limit'),
        ('policy_violation', 'Policy Violation'),
        ('technical', 'Technical Issues'),
        ('other', 'Other Reason'),
    ], string='Rejection Category', required=True, default='other')
    
    rejection_reason = fields.Text(
        string='Detailed Reason',
        required=True,
        help="Detailed explanation for the rejection"
    )
    
    required_actions = fields.Text(
        string='Required Actions',
        help="Actions required to resolve the issues and resubmit"
    )
    
    return_to_creator = fields.Boolean(
        string='Return to Creator',
        default=True,
        help="Return payment to creator for corrections"
    )
    
    notify_stakeholders = fields.Boolean(
        string='Notify Stakeholders',
        default=True,
        help="Send notification to all relevant stakeholders"
    )
    
    allow_resubmission = fields.Boolean(
        string='Allow Resubmission',
        default=True,
        help="Allow creator to resubmit after corrections"
    )
    
    escalate_to_manager = fields.Boolean(
        string='Escalate to Manager',
        default=False,
        help="Escalate rejection to manager for review"
    )
    
    signature_required = fields.Boolean(
        string='Digital Signature Required',
        default=True,
        help="Require digital signature for rejection"
    )
    
    signature_data = fields.Text(
        string='Digital Signature',
        help="Digital signature data for rejection approval"
    )
    
    # Payment information (read-only)
    payment_reference = fields.Char(
        related='payment_id.name',
        string='Payment Reference',
        readonly=True
    )
    
    payment_amount = fields.Monetary(
        related='payment_id.amount',
        string='Payment Amount',
        currency_field='payment_currency_id',
        readonly=True
    )
    
    payment_currency_id = fields.Many2one(
        related='payment_id.currency_id',
        string='Currency',
        readonly=True
    )
    
    payment_partner = fields.Char(
        related='payment_id.partner_id.name',
        string='Partner',
        readonly=True
    )
    
    payment_state = fields.Selection(
        related='payment_id.voucher_state',
        string='Current State',
        readonly=True
    )
    
    currency_id = fields.Many2one(
        related='payment_id.currency_id',
        string='Currency',
        readonly=True
    )
    
    # ========================================
    # Validation Methods
    # ========================================
    
    @api.constrains('signature_data', 'signature_required')
    def _check_signature_requirement(self):
        """Check if signature is required"""
        for wizard in self:
            if wizard.signature_required and not wizard.signature_data:
                raise ValidationError(_("Digital signature is required for payment rejection."))
    
    @api.constrains('payment_id')
    def _check_payment_state(self):
        """Validate that payment can be rejected"""
        for wizard in self:
            if wizard.payment_id.voucher_state not in ['submitted', 'under_review', 'approved']:
                raise ValidationError(_(
                    "Payment cannot be rejected in current state: %s"
                ) % dict(wizard.payment_id._fields['voucher_state'].selection)[wizard.payment_id.voucher_state])
    
    # ========================================
    # Default Methods
    # ========================================
    
    @api.model
    def default_get(self, fields_list):
        """Set default values based on context"""
        defaults = super().default_get(fields_list)
        
        # Get payment from context
        payment_id = self.env.context.get('active_id')
        if payment_id:
            defaults['payment_id'] = payment_id
            
            # Set default category based on payment characteristics
            payment = self.env['account.payment'].browse(payment_id)
            if payment.exists():
                # Analyze payment to suggest category
                if payment.amount > 50000:
                    defaults['rejection_category'] = 'approval_limit'
                elif not payment.ref:
                    defaults['rejection_category'] = 'documentation'
                else:
                    defaults['rejection_category'] = 'other'
        
        return defaults
    
    # ========================================
    # Action Methods
    # ========================================
    
    def action_confirm_rejection(self):
        """Confirm and process the payment rejection"""
        self.ensure_one()
        
        # Validate user permissions
        if not self.payment_id._can_user_reject():
            raise UserError(_("You don't have permission to reject this payment."))
        
        # Prepare rejection data
        rejection_data = {
            'rejection_category': self.rejection_category,
            'rejection_reason': self.rejection_reason,
            'required_actions': self.required_actions,
            'rejected_by_id': self.env.user.id,
            'rejection_date': fields.Datetime.now(),
            'allow_resubmission': self.allow_resubmission,
        }
        
        # Update payment with rejection data
        self.payment_id.write(rejection_data)
        
        # Process the rejection
        self.payment_id.action_reject_payment(self.rejection_reason)
        
        # Add digital signature if provided
        if self.signature_data:
            self.payment_id._add_digital_signature(
                self.signature_data, 
                f'Payment Rejection - {self.rejection_category}'
            )
        
        # Create detailed rejection history
        self._create_rejection_history()
        
        # Handle return to creator
        if self.return_to_creator:
            self.payment_id.voucher_state = 'draft'
            self.payment_id.message_post(
                body=_("Payment returned to creator for corrections."),
                subtype_xmlid='mail.mt_note'
            )
        
        # Send notifications
        if self.notify_stakeholders:
            self._send_rejection_notifications()
        
        # Handle escalation
        if self.escalate_to_manager:
            self._escalate_to_manager()
        
        # Return to payment form
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Rejected'),
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'form_view_initial_mode': 'readonly'},
        }
    
    def action_preview_rejection(self):
        """Preview the rejection notification"""
        template = self._get_rejection_template()
        if not template:
            raise UserError(_("No rejection email template found."))
        
        # Generate preview
        preview_vals = template.generate_email(self.payment_id.id)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Preview Rejection Email'),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'account.payment',
                'default_res_id': self.payment_id.id,
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                'default_subject': preview_vals.get('subject', ''),
                'default_body': preview_vals.get('body', ''),
            }
        }
    
    # ========================================
    # Helper Methods
    # ========================================
    
    def _create_rejection_history(self):
        """Create detailed rejection history entry"""
        history_vals = {
            'payment_id': self.payment_id.id,
            'action': 'rejected',
            'user_id': self.env.user.id,
            'timestamp': fields.Datetime.now(),
            'notes': f"Rejection Category: {dict(self._fields['rejection_category'].selection)[self.rejection_category]}\n"
                    f"Reason: {self.rejection_reason}",
            'stage_from': self.payment_id.voucher_state,
            'stage_to': 'rejected',
        }
        
        if self.required_actions:
            history_vals['notes'] += f"\nRequired Actions: {self.required_actions}"
        
        if self.escalate_to_manager:
            history_vals['notes'] += "\nEscalated to manager for review"
        
        self.env['payment.approval.history'].create(history_vals)
    
    def _send_rejection_notifications(self):
        """Send rejection notifications to stakeholders"""
        template = self._get_rejection_template()
        if not template:
            return
        
        # Send to creator
        if self.payment_id.create_uid:
            template.send_mail(self.payment_id.id, force_send=True)
        
        # Send to approvers if they were involved
        approvers = self.env['res.users']
        if self.payment_id.approved_by_id:
            approvers |= self.payment_id.approved_by_id
        if self.payment_id.authorized_by_id:
            approvers |= self.payment_id.authorized_by_id
        
        for approver in approvers:
            if approver != self.env.user:  # Don't send to current user
                template.with_context(
                    recipient_id=approver.partner_id.id
                ).send_mail(self.payment_id.id, force_send=True)
    
    def _escalate_to_manager(self):
        """Escalate rejection to manager"""
        manager = self.env.user.employee_id.parent_id.user_id
        if not manager:
            # Find manager through approval configuration
            config = self.payment_id._get_approval_config()
            if config and config.escalation_manager_id:
                manager = config.escalation_manager_id
        
        if manager:
            # Create escalation record
            escalation_vals = {
                'payment_id': self.payment_id.id,
                'escalated_by_id': self.env.user.id,
                'escalated_to_id': manager.id,
                'escalation_date': fields.Datetime.now(),
                'escalation_reason': f"Payment rejection escalation: {self.rejection_category}",
                'original_rejection_reason': self.rejection_reason,
                'status': 'pending',
            }
            
            escalation = self.env['payment.approval.escalation'].create(escalation_vals)
            
            # Send escalation notification
            self._send_escalation_notification(escalation, manager)
    
    def _send_escalation_notification(self, escalation, manager):
        """Send escalation notification to manager"""
        subject = f"Payment Rejection Escalation: {self.payment_id.name}"
        body = f"""
        <p>Dear {manager.name},</p>
        
        <p>A payment rejection has been escalated to you for review:</p>
        
        <ul>
            <li><strong>Payment:</strong> {self.payment_id.name}</li>
            <li><strong>Amount:</strong> {self.payment_id.currency_id.format(self.payment_id.amount)}</li>
            <li><strong>Partner:</strong> {self.payment_id.partner_id.name}</li>
            <li><strong>Rejection Category:</strong> {dict(self._fields['rejection_category'].selection)[self.rejection_category]}</li>
            <li><strong>Rejected By:</strong> {self.env.user.name}</li>
        </ul>
        
        <p><strong>Rejection Reason:</strong><br/>{self.rejection_reason}</p>
        
        {f'<p><strong>Required Actions:</strong><br/>{self.required_actions}</p>' if self.required_actions else ''}
        
        <p>Please review this escalation and take appropriate action.</p>
        """
        
        self.payment_id.message_post(
            body=body,
            subject=subject,
            partner_ids=[manager.partner_id.id],
            subtype_xmlid='mail.mt_comment'
        )
    
    def _get_rejection_template(self):
        """Get the rejection email template"""
        return self.env.ref('account_payment_approval.email_template_payment_rejected', False)
    
    # ========================================
    # Onchange Methods
    # ========================================
    
    @api.onchange('rejection_category')
    def _onchange_rejection_category(self):
        """Update suggested actions based on category"""
        if self.rejection_category:
            suggestions = {
                'documentation': 'Please provide complete supporting documentation including invoices, contracts, and approval forms.',
                'authorization': 'Obtain proper authorization from the appropriate authority before resubmitting.',
                'compliance': 'Ensure payment complies with company policies and regulatory requirements.',
                'duplicate': 'Verify this is not a duplicate payment and provide justification if legitimate.',
                'incorrect_amount': 'Verify and correct the payment amount before resubmitting.',
                'incorrect_vendor': 'Verify vendor details and update if necessary.',
                'budget': 'Ensure sufficient budget allocation or obtain budget approval.',
                'approval_limit': 'Obtain higher-level approval or split payment if appropriate.',
                'policy_violation': 'Review company policies and ensure compliance before resubmitting.',
                'technical': 'Resolve technical issues and resubmit payment.',
            }
            
            self.required_actions = suggestions.get(self.rejection_category, '')
    
    @api.onchange('escalate_to_manager')
    def _onchange_escalate_to_manager(self):
        """Update notification settings when escalating"""
        if self.escalate_to_manager:
            self.notify_stakeholders = True
