# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # ============================================================================
    # ENHANCED PAYMENT REGISTRATION WITH APPROVAL WORKFLOW
    # ============================================================================

    force_approval_workflow = fields.Boolean(
        string='Force Approval Workflow',
        default=True,
        help="If checked, the payment will go through the approval workflow instead of being posted immediately"
    )

    approval_required_reason = fields.Text(
        string='Approval Required Reason',
        default="Payment registered from invoice/bill - approval workflow required",
        readonly=True,
        help="Reason why this payment requires approval workflow"
    )

    def _create_payment_vals_from_wizard(self, batch_result):
        """Override to enforce approval workflow for invoice payments"""
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        # Get the context and invoice information
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        
        # If this is payment registration from invoices/bills
        if active_model == 'account.move' and active_ids:
            # Get the invoices/bills
            invoices = self.env['account.move'].browse(active_ids)
            
            # Check if any invoice/bill requires approval workflow
            requires_approval = False
            approval_reasons = []
            
            for invoice in invoices:
                if invoice.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                    requires_approval = True
                    approval_reasons.append(f"Payment for {invoice.name} ({invoice.move_type})")
            
            if requires_approval or self.force_approval_workflow:
                # Force approval workflow
                payment_vals.update({
                    'approval_state': 'draft',
                    'state': 'draft',  # Ensure payment is in draft state
                })
                
                # Add to context that this payment is from invoice registration
                self = self.with_context(
                    from_invoice_payment=True,
                    force_approval_workflow=True,
                    payment_requires_approval=True,
                    approval_reason='; '.join(approval_reasons),
                )
                
                _logger.info(f"Payment registration: Forcing approval workflow for invoice payment")
        
        return payment_vals

    def _create_payments(self):
        """Override payment creation to ensure approval workflow"""
        # Add context flags to ensure approval workflow
        self = self.with_context(
            from_invoice_payment=True,
            force_approval_workflow=True,
            payment_requires_approval=True,
        )
        
        # Call parent method to create payments
        payments = super()._create_payments()
        
        # Ensure all created payments are in draft state for approval
        for payment in payments:
            if payment.approval_state != 'draft':
                payment.approval_state = 'draft'
            
            if payment.state != 'draft':
                payment.state = 'draft'
            
            # Post message about approval requirement
            payment.message_post(
                body=_(
                    "Payment registered from invoice/bill. "
                    "This payment must go through the approval workflow before posting. "
                    "Please submit for review to continue."
                ),
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )
            
            _logger.info(f"Created payment {payment.name} in draft state for approval workflow")
        
        return payments

    def action_create_payments(self):
        """Override to show approval workflow notification"""
        # Check if we need to show approval workflow notification
        show_approval_notification = (
            self.force_approval_workflow and 
            self.env.context.get('active_model') == 'account.move'
        )
        
        # Create payments
        result = super().action_create_payments()
        
        # If payments were created and require approval, show notification
        if show_approval_notification and isinstance(result, dict):
            # Modify the result to include approval notification
            if 'context' not in result:
                result['context'] = {}
            
            result['context'].update({
                'show_approval_notification': True,
                'approval_message': _(
                    "Payment(s) created successfully and added to approval workflow. "
                    "Please go to Accounting > Payments to review and submit for approval."
                )
            })
        
        return result

    @api.onchange('force_approval_workflow')
    def _onchange_force_approval_workflow(self):
        """Update reason text when approval workflow setting changes"""
        if self.force_approval_workflow:
            self.approval_required_reason = "Payment registered from invoice/bill - approval workflow required"
        else:
            self.approval_required_reason = "Approval workflow bypassed - payment will be posted directly"

    @api.model
    def default_get(self, fields_list):
        """Set default values for approval workflow"""
        defaults = super().default_get(fields_list)
        
        # Check if this is from invoice/bill registration
        active_model = self.env.context.get('active_model')
        if active_model == 'account.move':
            # Force approval workflow for invoice payments by default
            defaults['force_approval_workflow'] = True
            defaults['approval_required_reason'] = "Payment registered from invoice/bill - approval workflow required"
        
        return defaults

    def _check_payment_approval_requirements(self):
        """Check if payment requires approval workflow based on amount and other factors"""
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            return False
        
        invoices = self.env['account.move'].browse(active_ids)
        total_amount = sum(invoices.mapped('amount_residual'))
        
        # Check amount thresholds
        small_payment_threshold = float(self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_final.small_payment_threshold', '100.0'))
        
        auto_approval_threshold = float(self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_final.auto_approval_threshold', '1000.0'))
        
        # Check user permissions
        user = self.env.user
        is_account_manager = user.has_group('account.group_account_manager')
        can_bypass_approval = user.has_group('account_payment_final.group_payment_bypass_approval')
        
        # Determine if approval is required
        if can_bypass_approval:
            return False
        elif is_account_manager and total_amount <= auto_approval_threshold:
            return False
        elif total_amount <= small_payment_threshold:
            return False
        else:
            return True
