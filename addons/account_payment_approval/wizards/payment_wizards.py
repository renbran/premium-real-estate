# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PaymentRejectionWizard(models.TransientModel):
    """Wizard for rejecting payments with reason"""
    _name = 'payment.rejection.wizard'
    _description = 'Payment Rejection Wizard'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        readonly=True
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        required=True,
        help="Please provide a detailed reason for rejection"
    )
    
    notify_submitter = fields.Boolean(
        string='Notify Submitter',
        default=True,
        help="Send email notification to the payment submitter"
    )
    
    rejection_category = fields.Selection([
        ('incomplete_docs', 'Incomplete Documentation'),
        ('invalid_amount', 'Invalid Amount'),
        ('unauthorized', 'Unauthorized Payment'),
        ('duplicate', 'Duplicate Payment'),
        ('budget_exceeded', 'Budget Exceeded'),
        ('policy_violation', 'Policy Violation'),
        ('other', 'Other')
    ], string='Rejection Category', required=True, default='other')

    def action_reject_payment(self):
        """Execute payment rejection"""
        self.ensure_one()
        
        if not self.rejection_reason:
            raise ValidationError(_("Rejection reason is required"))
        
        # Check if user has permission to reject
        if not self.env.user.has_group('account_payment_approval.group_payment_approval_reviewer'):
            raise UserError(_("You don't have permission to reject payments"))
        
        # Update payment state
        payment = self.payment_id
        if payment.voucher_state not in ['submitted', 'under_review']:
            raise UserError(_("Payment cannot be rejected in current state: %s") % payment.voucher_state)
        
        # Add rejection comment
        rejection_message = _("Payment rejected by %s\nReason: %s\nCategory: %s") % (
            self.env.user.name,
            self.rejection_reason,
            dict(self._fields['rejection_category'].selection)[self.rejection_category]
        )
        
        payment.message_post(
            body=rejection_message,
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )
        
        # Set rejection details
        payment.write({
            'voucher_state': 'rejected',
            'rejection_reason': self.rejection_reason,
            'rejection_category': self.rejection_category,
            'rejected_by': self.env.user.id,
            'rejection_date': fields.Datetime.now()
        })
        
        # Send notification if requested
        if self.notify_submitter and payment.create_uid:
            self._send_rejection_notification(payment)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Payment Rejected'),
                'message': _('Payment %s has been rejected successfully') % payment.name,
                'type': 'success',
                'sticky': False,
            }
        }

    def _send_rejection_notification(self, payment):
        """Send email notification about rejection"""
        template = self.env.ref('account_payment_approval.email_template_payment_rejected', False)
        if template:
            template.send_mail(payment.id, force_send=True)


class PaymentBulkApprovalWizard(models.TransientModel):
    """Wizard for bulk payment approval operations"""
    _name = 'payment.bulk.approval.wizard'
    _description = 'Payment Bulk Approval Wizard'

    payment_ids = fields.Many2many(
        'account.payment',
        string='Payments',
        required=True,
        readonly=True
    )
    
    action_type = fields.Selection([
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('authorize', 'Authorize'),
        ('submit_review', 'Submit for Review')
    ], string='Action', required=True)
    
    reason = fields.Text(
        string='Reason/Comments',
        help="Optional reason or comments for this bulk action"
    )
    
    force_action = fields.Boolean(
        string='Force Action',
        default=False,
        help="Force action even if some payments are in invalid state"
    )

    @api.model
    def default_get(self, fields_list):
        """Set default payment_ids from context"""
        defaults = super().default_get(fields_list)
        
        # Get payment IDs from context
        payment_ids = self.env.context.get('active_ids', [])
        if payment_ids:
            defaults['payment_ids'] = [(6, 0, payment_ids)]
        
        return defaults

    def action_execute_bulk_operation(self):
        """Execute the bulk operation"""
        self.ensure_one()
        
        if not self.payment_ids:
            raise ValidationError(_("No payments selected"))
        
        # Check permissions
        if not self._check_bulk_permissions():
            raise UserError(_("Insufficient permissions for bulk operations"))
        
        success_count = 0
        failed_count = 0
        messages = []
        
        for payment in self.payment_ids:
            try:
                if self.action_type == 'approve':
                    if payment.voucher_state == 'under_review' or self.force_action:
                        payment.action_approve()
                        success_count += 1
                    else:
                        failed_count += 1
                        messages.append(_("Payment %s: Invalid state for approval") % payment.name)
                
                elif self.action_type == 'reject':
                    if payment.voucher_state in ['submitted', 'under_review'] or self.force_action:
                        payment.write({
                            'voucher_state': 'rejected',
                            'rejection_reason': self.reason or 'Bulk rejection',
                            'rejected_by': self.env.user.id,
                            'rejection_date': fields.Datetime.now()
                        })
                        success_count += 1
                    else:
                        failed_count += 1
                        messages.append(_("Payment %s: Invalid state for rejection") % payment.name)
                
                elif self.action_type == 'authorize':
                    if payment.voucher_state == 'approved' or self.force_action:
                        payment.action_authorize()
                        success_count += 1
                    else:
                        failed_count += 1
                        messages.append(_("Payment %s: Invalid state for authorization") % payment.name)
                
                elif self.action_type == 'submit_review':
                    if payment.voucher_state == 'draft' or self.force_action:
                        payment.action_submit_for_approval()
                        success_count += 1
                    else:
                        failed_count += 1
                        messages.append(_("Payment %s: Invalid state for submission") % payment.name)
                
                # Add comment if reason provided
                if self.reason:
                    payment.message_post(
                        body=_("Bulk operation: %s\nReason: %s") % (
                            dict(self._fields['action_type'].selection)[self.action_type],
                            self.reason
                        ),
                        message_type='comment'
                    )
            
            except Exception as e:
                failed_count += 1
                messages.append(_("Payment %s: %s") % (payment.name, str(e)))
        
        # Prepare result message
        result_message = _("Bulk operation completed:\n- Successful: %d\n- Failed: %d") % (
            success_count, failed_count
        )
        
        if messages:
            result_message += "\n\nErrors:\n" + "\n".join(messages)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Operation Complete'),
                'message': result_message,
                'type': 'success' if failed_count == 0 else 'warning',
                'sticky': True,
            }
        }

    def _check_bulk_permissions(self):
        """Check if user has permissions for bulk operations"""
        user = self.env.user
        
        if self.action_type in ['approve', 'reject']:
            return user.has_group('account_payment_approval.group_payment_approval_reviewer')
        elif self.action_type == 'authorize':
            return user.has_group('account_payment_approval.group_payment_approval_manager')
        elif self.action_type == 'submit_review':
            return user.has_group('account_payment_approval.group_payment_approval_user')
        
        return False


class PaymentApprovalConfigWizard(models.TransientModel):
    """Wizard for configuring payment approval settings"""
    _name = 'payment.approval.config.wizard'
    _description = 'Payment Approval Configuration Wizard'

    approval_amount_limit = fields.Float(
        string='Approval Amount Limit',
        help="Maximum amount that can be approved without higher authorization"
    )
    
    authorization_amount_limit = fields.Float(
        string='Authorization Amount Limit',
        help="Maximum amount that can be authorized"
    )
    
    require_dual_approval = fields.Boolean(
        string='Require Dual Approval',
        default=True,
        help="Require two different users for approval and authorization"
    )
    
    auto_notify_reviewers = fields.Boolean(
        string='Auto Notify Reviewers',
        default=True,
        help="Automatically notify reviewers when payments are submitted"
    )
    
    enable_qr_verification = fields.Boolean(
        string='Enable QR Verification',
        default=True,
        help="Enable QR code verification for payments"
    )
    
    enable_digital_signature = fields.Boolean(
        string='Enable Digital Signature',
        default=True,
        help="Enable digital signature for payment authorization"
    )

    @api.model
    def default_get(self, fields_list):
        """Load current configuration values"""
        defaults = super().default_get(fields_list)
        
        # Get current config parameters
        defaults.update({
            'approval_amount_limit': float(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.approval_amount_limit', 10000.0)),
            'authorization_amount_limit': float(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.authorization_amount_limit', 50000.0)),
            'require_dual_approval': self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.require_dual_approval', 'True') == 'True',
            'auto_notify_reviewers': self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.auto_notify_reviewers', 'True') == 'True',
            'enable_qr_verification': self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.enable_qr_verification', 'True') == 'True',
            'enable_digital_signature': self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.enable_digital_signature', 'True') == 'True',
        })
        
        return defaults

    def action_save_config(self):
        """Save configuration parameters"""
        self.ensure_one()
        
        # Check permissions
        if not self.env.user.has_group('account_payment_approval.group_payment_approval_administrator'):
            raise UserError(_("Only administrators can modify payment approval configuration"))
        
        # Save configuration parameters
        config_params = [
            ('account_payment_approval.approval_amount_limit', str(self.approval_amount_limit)),
            ('account_payment_approval.authorization_amount_limit', str(self.authorization_amount_limit)),
            ('account_payment_approval.require_dual_approval', str(self.require_dual_approval)),
            ('account_payment_approval.auto_notify_reviewers', str(self.auto_notify_reviewers)),
            ('account_payment_approval.enable_qr_verification', str(self.enable_qr_verification)),
            ('account_payment_approval.enable_digital_signature', str(self.enable_digital_signature)),
        ]
        
        for key, value in config_params:
            self.env['ir.config_parameter'].sudo().set_param(key, value)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuration Saved'),
                'message': _('Payment approval configuration has been updated successfully'),
                'type': 'success',
                'sticky': False,
            }
        }
