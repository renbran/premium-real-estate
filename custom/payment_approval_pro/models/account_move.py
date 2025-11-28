# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import qrcode
import base64
from io import BytesIO
import json

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ============================================================================
    # APPROVAL WORKFLOW FIELDS
    # ============================================================================

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Approval State', default='draft', tracking=True, copy=False,
       help="Current approval state of the invoice/bill")

    # Legacy verification status for compatibility
    verification_status = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], default='pending', string="Verification Status", copy=False, tracking=True,
       help="External verification status of the invoice/bill")

    # Approval tracking fields
    reviewer_id = fields.Many2one('res.users', string='Reviewed By', copy=False)
    reviewer_date = fields.Datetime(string='Review Date', copy=False)
    approver_id = fields.Many2one('res.users', string='Approved By', copy=False)
    approver_date = fields.Datetime(string='Approval Date', copy=False)

    # QR Code for invoice verification
    qr_code_invoice = fields.Binary(
        string='Invoice QR Code',
        compute='_compute_qr_code_invoice',
        store=True,
        help="QR code for invoice/bill verification"
    )

    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================

    can_submit_for_review = fields.Boolean(
        compute='_compute_workflow_buttons',
        help="Whether user can submit this document for review"
    )

    can_review = fields.Boolean(
        compute='_compute_workflow_buttons',
        help="Whether user can review this document"
    )

    can_approve = fields.Boolean(
        compute='_compute_workflow_buttons',
        help="Whether user can approve this document"
    )

    can_post_manual = fields.Boolean(
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

    @api.depends('name', 'amount_total', 'approval_state', 'verification_status', 'partner_id', 'invoice_date')
    def _compute_qr_code_invoice(self):
        """Generate QR code for invoice/bill verification"""
        for record in self:
            if (record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'] and 
                record.name and record.id):
                try:
                    # Create comprehensive verification data
                    qr_data = {
                        'type': 'invoice_verification',
                        'number': record.name,
                        'amount': str(record.amount_total),
                        'currency': record.currency_id.name,
                        'partner': record.partner_id.name,
                        'date': str(record.invoice_date) if record.invoice_date else '',
                        'approval_state': record.approval_state,
                        'verification_status': record.verification_status,
                        'company': record.company_id.name,
                        'move_type': record.move_type,
                    }
                    
                    # Convert to JSON for QR code
                    qr_text = json.dumps(qr_data, ensure_ascii=False)
                    
                    # Generate QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_text)
                    qr.make(fit=True)
                    
                    # Create image
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    qr_img.save(buffer, format='PNG')
                    record.qr_code_invoice = base64.b64encode(buffer.getvalue())
                    
                except Exception as e:
                    _logger.error("Error generating QR code for invoice %s: %s", record.name, str(e))
                    record.qr_code_invoice = False
            else:
                record.qr_code_invoice = False

    # ============================================================================
    # WORKFLOW METHODS
    # ============================================================================

    def action_submit_for_review(self):
        """Submit invoice/bill for review"""
        for record in self:
            if record.approval_state != 'draft':
                raise UserError(_("Only draft invoices/bills can be submitted for review"))
            
            if record.move_type not in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                raise UserError(_("Only invoices and bills can use approval workflow"))
            
            record.approval_state = 'under_review'
            record._post_approval_message("submitted for review")
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_review_approve(self):
        """Review and approve invoice/bill"""
        for record in self:
            if record.approval_state != 'under_review':
                raise UserError(_("Only invoices/bills under review can be approved"))
            
            if not record._check_approval_permissions('review'):
                raise UserError(_("You do not have permission to review this invoice/bill"))
            
            record.reviewer_id = self.env.user
            record.reviewer_date = fields.Datetime.now()
            record.approval_state = 'for_approval'
            record._post_approval_message("reviewed and forwarded for approval")
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_final_approve(self):
        """Final approval and auto-post invoice/bill"""
        for record in self:
            if record.approval_state != 'for_approval':
                raise UserError(_("Only invoices/bills pending approval can be finally approved"))
            
            if not record._check_approval_permissions('approve'):
                raise UserError(_("You do not have permission to approve this invoice/bill"))
            
            record.approver_id = self.env.user
            record.approver_date = fields.Datetime.now()
            record.approval_state = 'approved'
            record._post_approval_message("approved and ready for posting")
            
            # Auto-post the invoice/bill after approval
            try:
                record.action_post()
            except Exception as e:
                _logger.warning(f"Auto-posting failed for invoice/bill {record.name}: {str(e)}")

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_reject_invoice_bill(self):
        """Reject invoice/bill and return to draft"""
        for record in self:
            if record.approval_state not in ['under_review', 'for_approval']:
                raise UserError(_("Only invoices/bills in review/approval stages can be rejected"))
            
            record._clear_approval_fields()
            record.approval_state = 'draft'
            record._post_approval_message("rejected and returned to draft for revision")
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_post(self):
        """Override posting to enforce approval workflow for invoices/bills"""
        for record in self:
            # Apply approval workflow only to invoices and bills
            if record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                if (hasattr(record, 'approval_state') and 
                    record.approval_state not in ['approved', 'posted']):
                    
                    # Check if user can bypass
                    if not record._can_bypass_approval():
                        raise UserError(_("Invoice/Bill must be approved before posting. Please complete the approval workflow first."))
                
                # Post and update approval state
                result = super(AccountMove, record).action_post()
                if hasattr(record, 'approval_state'):
                    record.approval_state = 'posted'
                    record._post_approval_message("posted to ledger")
                return result
            else:
                # For other move types, use standard behavior
                return super(AccountMove, record).action_post()

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _check_approval_permissions(self, stage):
        """Check if user has permission for specific approval stage"""
        permission_map = {
            'review': ['account.group_account_user', 'account_payment_final.group_payment_reviewer'],
            'approve': ['account.group_account_manager', 'account_payment_final.group_payment_approver']
        }
        
        required_groups = permission_map.get(stage, [])
        return any(self.env.user.has_group(group) for group in required_groups)

    def _check_posting_permissions(self):
        """Check if user has permission to post invoices/bills"""
        return (self.env.user.has_group('account.group_account_manager') or 
               self.env.user.has_group('account_payment_final.group_payment_poster'))

    def _can_bypass_approval(self):
        """Check if user can bypass approval workflow"""
        return (self.env.user.has_group('account.group_account_manager') or
                self.env.user.has_group('account_payment_final.group_payment_manager'))

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
