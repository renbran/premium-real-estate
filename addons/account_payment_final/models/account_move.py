from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ============================================================================
    # FIELDS
    # ============================================================================

    # Enhanced approval workflow for invoices and bills
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Approval State', default='draft', tracking=True, copy=False,
       help="Current approval state of the invoice/bill")

    # Approval workflow fields
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        copy=False,
        help="User who reviewed the invoice/bill"
    )

    reviewer_date = fields.Datetime(
        string='Review Date',
        copy=False,
        help="Date when the invoice/bill was reviewed"
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        copy=False,
        help="User who approved the invoice/bill"
    )

    approver_date = fields.Datetime(
        string='Approval Date',
        copy=False,
        help="Date when the invoice/bill was approved"
    )

    # ============================================================================
    # COMPUTED FIELDS FOR UI ENHANCEMENT
    # ============================================================================

    can_submit_for_review = fields.Boolean(
        string='Can Submit for Review',
        compute='_compute_workflow_buttons',
        help="Whether user can submit this document for review"
    )

    can_review = fields.Boolean(
        string='Can Review',
        compute='_compute_workflow_buttons',
        help="Whether user can review this document"
    )

    can_approve = fields.Boolean(
        string='Can Approve',
        compute='_compute_workflow_buttons',
        help="Whether user can approve this document"
    )

    can_post_manual = fields.Boolean(
        string='Can Post Manually',
        compute='_compute_workflow_buttons',
        help="Whether user can manually post this document"
    )

    @api.depends('approval_state', 'move_type', 'state')
    def _compute_workflow_buttons(self):
        """Compute button visibility and permissions"""
        for record in self:
            # Check if this is an invoice/bill
            is_invoice_bill = record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']
            
            # Initialize all as False
            record.can_submit_for_review = False
            record.can_review = False
            record.can_approve = False
            record.can_post_manual = False
            
            if is_invoice_bill:
                # Can submit for review
                record.can_submit_for_review = (
                    record.approval_state == 'draft' and
                    record.state == 'draft'
                )
                
                # Can review
                record.can_review = (
                    record.approval_state == 'under_review' and
                    record._check_approval_permissions('review')
                )
                
                # Can approve
                record.can_approve = (
                    record.approval_state == 'for_approval' and
                    record._check_approval_permissions('approve')
                )
                
                # Can post manually
                record.can_post_manual = (
                    record.approval_state == 'approved' and
                    record.state == 'draft' and
                    record._check_posting_permissions()
                )

    @api.onchange('approval_state', 'move_type')
    def _onchange_approval_state(self):
        """Update UI when approval state changes"""
        if self.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            # Trigger button recomputation
            self._compute_workflow_buttons()
            
            # Show helpful messages
            if self.approval_state == 'under_review':
                return {
                    'warning': {
                        'title': _('Under Review'),
                        'message': _('This invoice/bill is now under review. A reviewer will need to approve it before it can proceed.')
                    }
                }
            elif self.approval_state == 'approved':
                return {
                    'warning': {
                        'title': _('Approved'),
                        'message': _('This invoice/bill has been approved and is ready for posting.')
                    }
                }

    # ============================================================================
    # WORKFLOW METHODS
    # ============================================================================

    def action_submit_for_review(self):
        """Submit invoice/bill for review"""
        for record in self:
            if record.approval_state != 'draft':
                raise UserError(_("Only draft invoices/bills can be submitted for review."))
            
            if record.move_type not in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                raise UserError(_("Only invoices and bills can use approval workflow."))
            
            record.approval_state = 'under_review'
            record._post_approval_message("submitted for review")
        
        return self._return_success_message(_('Invoice/Bill has been submitted for review.'))

    def action_review_approve(self):
        """Approve invoice/bill from review stage"""
        for record in self:
            if record.approval_state != 'under_review':
                raise UserError(_("Only invoices/bills under review can be approved."))
            
            # Check user permissions
            if not record._check_approval_permissions('review'):
                raise UserError(_("You do not have permission to review this invoice/bill."))
            
            record.reviewer_id = self.env.user
            record.reviewer_date = fields.Datetime.now()
            record.approval_state = 'for_approval'
            record._post_approval_message("reviewed and forwarded for approval")
        
        return self._return_success_message(_('Invoice/Bill has been reviewed and forwarded for approval.'))

    def action_final_approve(self):
        """Final approval and auto-post invoice/bill"""
        for record in self:
            if record.approval_state != 'for_approval':
                raise UserError(_("Only invoices/bills pending approval can be finally approved."))
            
            # Check user permissions
            if not record._check_approval_permissions('approve'):
                raise UserError(_("You do not have permission to approve this invoice/bill."))
            
            record.approver_id = self.env.user
            record.approver_date = fields.Datetime.now()
            record.approval_state = 'approved'
            record._post_approval_message("approved and ready for posting")
            
            # Auto-post the invoice/bill after approval
            try:
                record.action_post_invoice_bill()
                return self._return_success_message(_('Invoice/Bill has been approved and posted successfully.'))
            except Exception as e:
                # If auto-posting fails, keep it approved for manual posting
                _logger.warning(f"Auto-posting failed for invoice/bill {record.name}: {str(e)}")
                return self._return_success_message(_('Invoice/Bill has been approved. Please post manually due to technical issue.'))
        
        return self._return_success_message(_('Invoice/Bill has been approved and is ready for posting.'))

    def action_post_invoice_bill(self):
        """Post invoice/bill after approval (overrides default post button)"""
        for record in self:
            # Check if invoice/bill is approved
            if hasattr(record, 'approval_state') and record.approval_state != 'approved':
                raise UserError(_("Only approved invoices/bills can be posted. Current state: %s") % record.approval_state)
            
            # Check user permissions
            if not record._check_posting_permissions():
                raise UserError(_("You do not have permission to post invoices/bills."))
        
        try:
            # Call the original post method
            result = super(AccountMove, self).action_post()
            
            # Update approval state after successful posting
            for record in self:
                if hasattr(record, 'approval_state'):
                    record.approval_state = 'posted'
                    record._post_approval_message("posted to ledger")
            
            return result
            
        except Exception as e:
            # Rollback approval state if posting fails
            for record in self:
                if hasattr(record, 'approval_state'):
                    record.approval_state = 'approved'
            _logger.error(f"Failed to post invoice/bill: {str(e)}")
            raise UserError(_("Failed to post invoice/bill: %s") % str(e))

    def action_reject_invoice_bill(self):
        """Reject invoice/bill and return to draft"""
        for record in self:
            if record.approval_state not in ['under_review', 'for_approval']:
                raise UserError(_("Only invoices/bills in review/approval stages can be rejected."))
            
            # Clear approval fields
            record._clear_approval_fields()
            record.approval_state = 'draft'
            record._post_approval_message("rejected and returned to draft for revision")
        
        return self._return_success_message(_('Invoice/Bill has been rejected and returned to draft.'))

    # ============================================================================
    # OVERRIDE METHODS
    # ============================================================================

    def action_post(self):
        """Override core action_post to enforce approval workflow for invoices/bills"""
        for record in self:
            # Only apply approval workflow to invoices and bills
            if record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                # If this is an approved invoice/bill being posted through workflow
                if hasattr(record, 'approval_state') and record.approval_state == 'approved':
                    # Check if user has permission to post
                    if not record._check_posting_permissions():
                        raise UserError(_("You do not have permission to post this invoice/bill."))
                    
                    # Call the original post method and update state
                    result = super(AccountMove, record).action_post()
                    record.approval_state = 'posted'
                    record._post_approval_message("posted to ledger")
                    return result
                
                # If invoice/bill has approval workflow but is not approved
                elif hasattr(record, 'approval_state') and record.approval_state:
                    if record.approval_state == 'draft':
                        raise UserError(_("Invoice/Bill must go through approval workflow. Please submit for review first."))
                    elif record.approval_state in ['under_review', 'for_approval']:
                        raise UserError(_("Invoice/Bill is still under approval workflow. Current state: %s. Please complete the approval process first.") % record.approval_state)
                    elif record.approval_state == 'posted':
                        raise UserError(_("Invoice/Bill is already posted."))
                    elif record.approval_state == 'cancelled':
                        raise UserError(_("Cannot post cancelled invoice/bill."))
                    else:
                        raise UserError(_("Invoice/Bill state is invalid for posting: %s") % record.approval_state)
            
            # For other move types (journal entries, etc.), use default behavior
            else:
                return super(AccountMove, record).action_post()

    @api.model
    def create(self, vals):
        """Initialize approval state for new invoices/bills"""
        move = super(AccountMove, self).create(vals)
        
        # Initialize approval workflow for invoices and bills
        if move.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            if not move.approval_state:
                move.approval_state = 'draft'
        
        return move

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _check_approval_permissions(self, stage):
        """Check if user has permission for specific approval stage"""
        if stage == 'review':
            return (self.env.user.has_group('account.group_account_user') or 
                   self.env.user.has_group('account_payment_final.group_payment_reviewer'))
        elif stage == 'approve':
            return (self.env.user.has_group('account.group_account_manager') or 
                   self.env.user.has_group('account_payment_final.group_payment_approver'))
        return False

    def _check_posting_permissions(self):
        """Check if user has permission to post invoices/bills"""
        return (self.env.user.has_group('account.group_account_manager') or 
               self.env.user.has_group('account_payment_final.group_payment_poster'))

    def _post_approval_message(self, action):
        """Post message to chatter about approval action"""
        if self.env.context.get('skip_approval_message'):
            return
        
        user_name = self.env.user.display_name
        message = _("Invoice/Bill %s by %s") % (action, user_name)
        
        self.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    def _clear_approval_fields(self):
        """Clear approval workflow fields"""
        self.write({
            'reviewer_id': False,
            'reviewer_date': False,
            'approver_id': False,
            'approver_date': False,
        })

    def _return_success_message(self, message):
        """Return success message for UI feedback"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': message,
                'sticky': False,
            }
        }

    # ============================================================================
    # REGISTER PAYMENT INTEGRATION
    # ============================================================================

    def action_register_payment(self):
        """Override register payment to enforce approval workflow for all payments"""
        for record in self:
            # Only check approval for invoices and bills
            if record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                # Check if invoice/bill is posted
                if record.state != 'posted':
                    raise UserError(_("Cannot register payment for unposted invoice/bill. Please post the invoice/bill first."))
                
                # Check if invoice/bill went through approval workflow
                if hasattr(record, 'approval_state') and record.approval_state != 'posted':
                    raise UserError(_("Cannot register payment for unapproved invoice/bill. Current approval state: %s") % record.approval_state)
        
        # Get the original register payment action
        action = super(AccountMove, self).action_register_payment()
        
        # Modify context to ensure payment goes through approval workflow
        if isinstance(action, dict) and 'context' in action:
            # Add context flags to force approval workflow
            action['context'].update({
                'from_invoice_payment': True,
                'force_approval_workflow': True,
                'default_approval_state': 'draft',
                'payment_requires_approval': True,
            })
        
        return action

    @api.onchange('approval_state')
    def _onchange_approval_state_move(self):
        """Real-time status updates for invoice/bill approval workflow"""
        if self.approval_state == 'posted' and self.state != 'posted':
            # Don't automatically post - require explicit action
            return {
                'warning': {
                    'title': _('Ready to Post'),
                    'message': _('This invoice/bill has been approved and is ready to be posted. Please use the Post button to complete the process.')
                }
            }
        
        # Trigger UI refresh for real-time updates
        return {
            'domain': {},
            'value': {},
        }

    @api.onchange('state')
    def _onchange_state_move_sync(self):
        """Synchronize move state with approval state"""
        if self.state == 'posted' and hasattr(self, 'approval_state') and self.approval_state != 'posted':
            if self.env.user.has_group('account.group_account_manager'):
                self.approval_state = 'posted'

    @api.onchange('amount_total', 'partner_id')
    def _onchange_invoice_validation(self):
        """Real-time validation for invoice/bill amounts and partners"""
        if self.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            # Validate amount
            if self.amount_total <= 0:
                return {
                    'warning': {
                        'title': _('Invalid Amount'),
                        'message': _('Invoice/bill amount must be greater than zero.')
                    }
                }
            
            # Check if high amount requires special approval
            if self.amount_total > 50000:  # High amount threshold
                return {
                    'warning': {
                        'title': _('High Amount Invoice/Bill'),
                        'message': _('This invoice/bill amount is high and may require enhanced approval workflow.')
                    }
                }
            
            # Validate partner
            if not self.partner_id:
                return {
                    'warning': {
                        'title': _('Partner Required'),
                        'message': _('Please select a partner for this invoice/bill.')
                    }
                }
