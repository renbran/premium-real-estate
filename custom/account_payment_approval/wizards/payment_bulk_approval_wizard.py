# -*- coding: utf-8 -*-
#############################################################################
#
#    Bulk Payment Approval Wizard
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class PaymentBulkApprovalWizard(models.TransientModel):
    """Wizard for bulk approval of multiple payments"""
    _name = 'payment.bulk.approval.wizard'
    _description = 'Bulk Payment Approval Wizard'
    
    # ========================================
    # Wizard Fields
    # ========================================
    
    action_type = fields.Selection([
        ('submit', 'Submit for Review'),
        ('review', 'Mark as Reviewed'),
        ('approve', 'Approve Payments'),
        ('authorize', 'Authorize Payments'),
        ('post', 'Post Payments'),
        ('reject', 'Reject Payments'),
        ('cancel', 'Cancel Payments'),
    ], string='Action', required=True, default='approve')
    
    payment_ids = fields.Many2many(
        'account.payment',
        string='Selected Payments',
        required=True,
        help="Payments to perform bulk action on"
    )
    
    eligible_payment_ids = fields.Many2many(
        'account.payment',
        'payment_bulk_eligible_rel',
        string='Eligible Payments',
        compute='_compute_eligible_payments',
        help="Payments that can be processed with the selected action"
    )
    
    ineligible_payment_ids = fields.Many2many(
        'account.payment',
        'payment_bulk_ineligible_rel', 
        string='Ineligible Payments',
        compute='_compute_eligible_payments',
        help="Payments that cannot be processed with the selected action"
    )
    
    notes = fields.Text(
        string='Notes',
        help="Notes to add to all processed payments"
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        help="Reason for rejection (required for reject action)"
    )
    
    require_signature = fields.Boolean(
        string='Require Digital Signature',
        default=True,
        help="Require digital signature for this bulk action"
    )
    
    signature_data = fields.Text(
        string='Digital Signature',
        help="Digital signature data for bulk approval"
    )
    
    urgency_filter = fields.Selection([
        ('all', 'All Urgencies'),
        ('urgent', 'Urgent Only'),
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ], string='Urgency Filter', default='all')
    
    amount_threshold = fields.Float(
        string='Amount Threshold',
        help="Only process payments above this amount (leave 0 for all)"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_totals',
        help="Total amount of selected payments"
    )
    
    total_count = fields.Integer(
        string='Total Count',
        compute='_compute_totals',
        help="Total number of selected payments"
    )
    
    eligible_amount = fields.Float(
        string='Eligible Amount',
        compute='_compute_totals',
        help="Total amount of eligible payments"
    )
    
    eligible_count = fields.Integer(
        string='Eligible Count',
        compute='_compute_totals',
        help="Total number of eligible payments"
    )
    
    # ========================================
    # Computed Fields
    # ========================================
    
    @api.depends('payment_ids', 'action_type', 'urgency_filter', 'amount_threshold')
    def _compute_eligible_payments(self):
        """Compute which payments are eligible for the selected action"""
        for wizard in self:
            eligible_payments = self.env['account.payment']
            ineligible_payments = self.env['account.payment']
            
            for payment in wizard.payment_ids:
                # Check if payment can perform the action
                can_perform = False
                
                if wizard.action_type == 'submit':
                    can_perform = payment.approval_state == 'draft'
                elif wizard.action_type == 'review':
                    can_perform = payment.approval_state == 'submitted'
                elif wizard.action_type == 'approve':
                    can_perform = payment.approval_state == 'under_review'
                elif wizard.action_type == 'authorize':
                    can_perform = payment.approval_state == 'approved'
                elif wizard.action_type == 'post':
                    can_perform = payment.approval_state == 'authorized'
                elif wizard.action_type == 'reject':
                    can_perform = payment.approval_state in ['submitted', 'under_review', 'approved']
                elif wizard.action_type == 'cancel':
                    can_perform = payment.approval_state not in ['posted', 'cancelled']
                
                # Apply urgency filter
                if can_perform and wizard.urgency_filter != 'all':
                    can_perform = payment.urgency == wizard.urgency_filter
                
                # Apply amount threshold
                if can_perform and wizard.amount_threshold > 0:
                    can_perform = payment.amount >= wizard.amount_threshold
                
                # Check user permissions
                if can_perform:
                    if wizard.action_type == 'approve':
                        can_perform = payment._can_user_approve()
                    elif wizard.action_type == 'authorize':
                        can_perform = payment._can_user_authorize()
                    elif wizard.action_type == 'post':
                        can_perform = payment._can_user_post()
                
                if can_perform:
                    eligible_payments |= payment
                else:
                    ineligible_payments |= payment
            
            wizard.eligible_payment_ids = eligible_payments
            wizard.ineligible_payment_ids = ineligible_payments
    
    @api.depends('payment_ids', 'eligible_payment_ids')
    def _compute_totals(self):
        """Compute total amounts and counts"""
        for wizard in self:
            wizard.total_count = len(wizard.payment_ids)
            wizard.total_amount = sum(wizard.payment_ids.mapped('amount'))
            wizard.eligible_count = len(wizard.eligible_payment_ids)
            wizard.eligible_amount = sum(wizard.eligible_payment_ids.mapped('amount'))
    
    # ========================================
    # Constraint Methods
    # ========================================
    
    @api.constrains('rejection_reason', 'action_type')
    def _check_rejection_reason(self):
        """Ensure rejection reason is provided for reject action"""
        for wizard in self:
            if wizard.action_type == 'reject' and not wizard.rejection_reason:
                raise ValidationError(_("Rejection reason is required when rejecting payments."))
    
    @api.constrains('signature_data', 'require_signature', 'action_type')
    def _check_signature_requirement(self):
        """Check signature requirements for certain actions"""
        for wizard in self:
            if (wizard.require_signature and 
                wizard.action_type in ['approve', 'authorize', 'post'] and
                not wizard.signature_data):
                raise ValidationError(_("Digital signature is required for this action."))
    
    # ========================================
    # Default Methods
    # ========================================
    
    @api.model
    def default_get(self, fields_list):
        """Set default values based on context"""
        defaults = super().default_get(fields_list)
        
        # Get payments from context
        payment_ids = self.env.context.get('active_ids', [])
        if payment_ids:
            defaults['payment_ids'] = [(6, 0, payment_ids)]
        
        # Set default action based on payments state
        if payment_ids:
            payments = self.env['account.payment'].browse(payment_ids)
            states = payments.mapped('approval_state')
            
            # Determine most common next action
            if 'under_review' in states:
                defaults['action_type'] = 'approve'
            elif 'approved' in states:
                defaults['action_type'] = 'authorize'
            elif 'authorized' in states:
                defaults['action_type'] = 'post'
            elif 'submitted' in states:
                defaults['action_type'] = 'review'
            elif 'draft' in states:
                defaults['action_type'] = 'submit'
        
        return defaults
    
    # ========================================
    # Action Methods
    # ========================================
    
    def action_process_bulk(self):
        """Process the bulk action on eligible payments"""
        if not self.eligible_payment_ids:
            raise UserError(_("No eligible payments found for the selected action."))
        
        # Validate bulk limits
        config = self.env['payment.approval.config']._get_company_config(self.company_id.id)
        if config and config.max_bulk_approval_count > 0:
            if len(self.eligible_payment_ids) > config.max_bulk_approval_count:
                raise UserError(_(
                    "Cannot process more than %d payments in bulk. "
                    "Please select fewer payments or increase the limit in configuration."
                ) % config.max_bulk_approval_count)
        
        # Process each eligible payment
        processed_count = 0
        failed_payments = []
        
        for payment in self.eligible_payment_ids:
            try:
                # Perform the action
                if self.action_type == 'submit':
                    payment.action_submit_for_approval()
                elif self.action_type == 'review':
                    payment.action_mark_reviewed()
                elif self.action_type == 'approve':
                    payment.action_approve_payment()
                elif self.action_type == 'authorize':
                    payment.action_authorize_payment()
                elif self.action_type == 'post':
                    payment.action_post_payment()
                elif self.action_type == 'reject':
                    payment.action_reject_payment(self.rejection_reason)
                elif self.action_type == 'cancel':
                    payment.action_cancel_payment()
                
                # Add notes if provided
                if self.notes:
                    payment.approval_notes = (payment.approval_notes or '') + '\n' + self.notes
                
                # Add signature data if provided
                if self.signature_data and self.require_signature:
                    payment._add_digital_signature(self.signature_data, f'Bulk {self.action_type}')
                
                processed_count += 1
                
            except Exception as e:
                failed_payments.append((payment, str(e)))
        
        # Create approval history entry for bulk action
        self._create_bulk_approval_history(processed_count, failed_payments)
        
        # Prepare result message
        if failed_payments:
            message = _(
                "Bulk action completed. %d payments processed successfully. %d payments failed."
            ) % (processed_count, len(failed_payments))
            
            # Show failed payments details
            if len(failed_payments) <= 5:  # Show details for few failures
                failed_details = '\n'.join([
                    f"â€¢ {p.name}: {error}" for p, error in failed_payments
                ])
                message += f"\n\nFailed payments:\n{failed_details}"
        else:
            message = _("Bulk action completed successfully. %d payments processed.") % processed_count
        
        # Return result action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Action Completed'),
                'message': message,
                'type': 'success' if not failed_payments else 'warning',
                'sticky': True,
            }
        }
    
    def action_preview_changes(self):
        """Preview what changes will be made"""
        if not self.eligible_payment_ids:
            raise UserError(_("No eligible payments found for preview."))
        
        # Create preview data
        preview_lines = []
        for payment in self.eligible_payment_ids:
            preview_lines.append({
                'payment_id': payment.id,
                'payment_name': payment.name or payment.ref,
                'partner_name': payment.partner_id.name,
                'amount': payment.amount,
                'currency_id': payment.currency_id.id,
                'current_state': payment.approval_state,
                'new_state': self._get_target_state(payment),
            })
        
        # Create preview wizard
        preview_wizard = self.env['payment.bulk.preview.wizard'].create({
            'bulk_wizard_id': self.id,
            'preview_line_ids': [(0, 0, line) for line in preview_lines],
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Preview Bulk Changes'),
            'res_model': 'payment.bulk.preview.wizard',
            'res_id': preview_wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_filter_payments(self):
        """Apply filters to payment selection"""
        self._compute_eligible_payments()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Payment Approval'),
            'res_model': 'payment.bulk.approval.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    # ========================================
    # Helper Methods
    # ========================================
    
    def _get_target_state(self, payment):
        """Get the target state after action"""
        if self.action_type == 'submit':
            return 'submitted'
        elif self.action_type == 'review':
            return 'under_review'
        elif self.action_type == 'approve':
            return 'approved'
        elif self.action_type == 'authorize':
            return 'authorized'
        elif self.action_type == 'post':
            return 'posted'
        elif self.action_type == 'reject':
            return 'rejected'
        elif self.action_type == 'cancel':
            return 'cancelled'
        return payment.approval_state
    
    def _create_bulk_approval_history(self, processed_count, failed_payments):
        """Create history entry for bulk action"""
        history_vals = {
            'action': f'bulk_{self.action_type}',
            'user_id': self.env.user.id,
            'timestamp': fields.Datetime.now(),
            'notes': f"Bulk {self.action_type}: {processed_count} payments processed",
            'company_id': self.company_id.id,
        }
        
        if failed_payments:
            failed_info = f"{len(failed_payments)} payments failed"
            history_vals['notes'] += f", {failed_info}"
        
        if self.notes:
            history_vals['notes'] += f"\nNotes: {self.notes}"
        
        # Create history for each processed payment
        for payment in self.eligible_payment_ids:
            payment_history = history_vals.copy()
            payment_history['payment_id'] = payment.id
            self.env['payment.approval.history'].create(payment_history)


class PaymentBulkPreviewWizard(models.TransientModel):
    """Preview wizard for bulk payment changes"""
    _name = 'payment.bulk.preview.wizard'
    _description = 'Payment Bulk Preview Wizard'
    
    bulk_wizard_id = fields.Many2one(
        'payment.bulk.approval.wizard',
        string='Bulk Wizard',
        required=True
    )
    
    preview_line_ids = fields.One2many(
        'payment.bulk.preview.line',
        'preview_wizard_id',
        string='Preview Lines'
    )
    
    def action_confirm_bulk(self):
        """Confirm and execute the bulk action"""
        return self.bulk_wizard_id.action_process_bulk()
    
    def action_back_to_wizard(self):
        """Go back to the bulk wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Payment Approval'),
            'res_model': 'payment.bulk.approval.wizard',
            'res_id': self.bulk_wizard_id.id,
            'view_mode': 'form',
            'target': 'new',
        }


class PaymentBulkPreviewLine(models.TransientModel):
    """Preview line for bulk payment changes"""
    _name = 'payment.bulk.preview.line'
    _description = 'Payment Bulk Preview Line'
    
    preview_wizard_id = fields.Many2one(
        'payment.bulk.preview.wizard',
        string='Preview Wizard',
        required=True
    )
    
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True
    )
    
    payment_name = fields.Char(string='Payment Reference')
    partner_name = fields.Char(string='Partner')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    current_state = fields.Char(string='Current State')
    new_state = fields.Char(string='New State')
    
    currency_id = fields.Many2one(
        related='payment_id.currency_id',
        string='Currency'
    )
