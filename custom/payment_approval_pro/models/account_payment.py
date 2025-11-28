# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
import qrcode
import base64
from io import BytesIO
import logging
import datetime

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # ============================================================================
    # CORE WORKFLOW FIELDS
    # ============================================================================

    # Enhanced 4-Stage Approval Workflow State
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('for_authorization', 'For Authorization'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Approval State', default='draft', tracking=True, copy=False, index=True,
       help="Current approval state of the payment voucher")

    # Legacy verification status for backward compatibility
    verification_status = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], string='Verification Status', default='pending', copy=False, tracking=True,
       help="Current verification status of the payment")

    # Voucher number with automatic generation
    voucher_number = fields.Char(
        string='Voucher Number',
        copy=False,
        readonly=True,
        index=True,
        help="Unique voucher number generated automatically"
    )

    # QR Code fields
    qr_code = fields.Binary(
        string="Payment QR Code",
        compute='_compute_payment_qr_code',
        store=True,
        help="QR code containing payment verification URL"
    )
    
    qr_in_report = fields.Boolean(
        string='Display QR Code in Report',
        default=True,
        help="Whether to display QR code in payment voucher report"
    )

    # Enhanced fields for voucher system
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks or memo for this payment voucher"
    )

    # ============================================================================
    # APPROVAL WORKFLOW TRACKING FIELDS
    # ============================================================================

    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        copy=False,
        help="User who reviewed the payment (Stage 1)"
    )

    reviewer_date = fields.Datetime(
        string='Review Date',
        copy=False,
        help="Date when the payment was reviewed"
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        copy=False,
        help="User who approved the payment (Stage 2)"
    )

    approver_date = fields.Datetime(
        string='Approval Date',
        copy=False,
        help="Date when the payment was approved"
    )

    authorizer_id = fields.Many2one(
        'res.users',
        string='Authorized By',
        copy=False,
        help="User who authorized the payment (Stage 3)"
    )

    authorizer_date = fields.Datetime(
        string='Authorization Date',
        copy=False,
        help="Date when the payment was authorized"
    )

    actual_approver_id = fields.Many2one(
        'res.users',
        string='Posted By User',
        copy=False,
        help="User who actually posted the payment",
        readonly=True
    )

    # ============================================================================
    # RELATIONSHIP FIELDS
    # ============================================================================

    approval_history_ids = fields.One2many(
        'payment.approval.history',
        'payment_id',
        string='Approval History',
        help="Complete history of approval actions"
    )

    qr_verification_ids = fields.One2many(
        'payment.qr.verification',
        'payment_id',
        string='QR Verifications',
        help="Log of QR code verification attempts"
    )

    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================

    can_verify = fields.Boolean(
        compute='_compute_workflow_permissions',
        help="Whether current user can verify this payment"
    )

    can_submit_for_review = fields.Boolean(
        compute='_compute_workflow_permissions',
        help="Whether current user can submit for review"
    )

    can_review = fields.Boolean(
        compute='_compute_workflow_permissions',
        help="Whether current user can review"
    )

    can_approve = fields.Boolean(
        compute='_compute_workflow_permissions',
        help="Whether current user can approve"
    )

    can_authorize = fields.Boolean(
        compute='_compute_workflow_permissions',
        help="Whether current user can authorize"
    )

    @api.depends('approval_state', 'verification_status')
    def _compute_workflow_permissions(self):
        """Compute workflow permissions for current user"""
        for record in self:
            user = self.env.user
            
            # Basic verification permission
            record.can_verify = (
                record.verification_status == 'pending' and
                user.has_group('account_payment_final.group_payment_verifier')
            )
            
            # Workflow permissions based on approval_state
            record.can_submit_for_review = (
                record.approval_state == 'draft' and
                user.has_group('account.group_account_user')
            )
            
            record.can_review = (
                record.approval_state == 'under_review' and
                user.has_group('account_payment_final.group_payment_reviewer')
            )
            
            record.can_approve = (
                record.approval_state == 'for_approval' and
                user.has_group('account_payment_final.group_payment_approver')
            )
            
            record.can_authorize = (
                record.approval_state == 'for_authorization' and
                record.payment_type == 'outbound' and
                user.has_group('account_payment_final.group_payment_authorizer')
            )

    @api.depends('name', 'amount', 'partner_id', 'approval_state', 'verification_status', 'qr_in_report', 'id')
    def _compute_payment_qr_code(self):
        """Generate QR code for payment voucher verification"""
        for record in self:
            if record.qr_in_report and record.id:
                try:
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
                    
                    if base_url:
                        qr_data = f"{base_url}/payment/verify/{record.id}"
                        record.qr_code = record._generate_qr_image(qr_data)
                    else:
                        # Fallback: structured data for manual verification
                        qr_data = self._create_fallback_qr_data(record)
                        record.qr_code = record._generate_qr_image(qr_data)
                        
                except Exception as e:
                    _logger.error("Error generating QR code for payment %s: %s", record.voucher_number or 'Draft', e)
                    record.qr_code = False
            else:
                record.qr_code = False

    def _generate_qr_image(self, data):
        """Generate QR code image with error handling"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            stream = BytesIO()
            img.save(stream, format="PNG")
            return base64.b64encode(stream.getvalue())
            
        except Exception as e:
            _logger.error("Error generating QR image: %s", e)
            return False

    def _create_fallback_qr_data(self, record):
        """Create structured QR data for manual verification when URL not available"""
        voucher_ref = record.voucher_number or record.name or 'Draft Payment'
        partner_name = record.partner_id.name if record.partner_id else 'Unknown Partner'
        amount_str = f"{record.amount:.2f} {record.currency_id.name if record.currency_id else 'USD'}"
        date_str = record.date.strftime('%Y-%m-%d') if record.date else 'Draft'
        
        return f"""PAYMENT VERIFICATION
Voucher: {voucher_ref}
Amount: {amount_str}
Partner: {partner_name}
Date: {date_str}
Status: {record.approval_state.upper() if hasattr(record, 'approval_state') else record.verification_status.upper()}
Company: {record.company_id.name}"""

    # ============================================================================
    # CORE BUSINESS METHODS
    # ============================================================================

    @api.model
    def create(self, vals):
        """Enhanced create method with voucher number generation and workflow setup"""
        # Generate voucher number immediately
        if not vals.get('voucher_number'):
            payment_type = vals.get('payment_type', 'outbound')
            sequence_code = 'receipt.voucher' if payment_type == 'inbound' else 'payment.voucher'
            vals['voucher_number'] = self.env['ir.sequence'].next_by_code(sequence_code) or '/'
        
        # Set initial verification status
        if 'verification_status' not in vals:
            vals['verification_status'] = 'pending'
        
        # Enforce approval workflow unless explicitly bypassed
        if not self.env.context.get('bypass_approval_workflow'):
            vals.update({
                'approval_state': 'draft',
                'state': 'draft'
            })
        
        # Validate amount
        if vals.get('amount', 0) <= 0:
            raise ValidationError(_('Payment amount must be positive'))
        
        payment = super().create(vals)
        
        # Log creation in approval history
        self.env['payment.approval.history'].sudo().create({
            'payment_id': payment.id,
            'action_type': 'create',
            'stage_from': 'draft',
            'stage_to': 'draft',
            'user_id': self.env.user.id,
            'comments': f'Payment created with voucher number {payment.voucher_number}'
        })
        
        payment.message_post(body=_("Payment voucher %s created") % payment.voucher_number)
        return payment

    # ============================================================================
    # VERIFICATION METHODS (Legacy Support)
    # ============================================================================

    def action_verify_payment(self):
        """Verify payment and update verification status"""
        self.ensure_one()
        
        if self.verification_status != 'pending':
            raise UserError(_('Only payments in "Pending" status can be verified'))
        
        if not self.env.user.has_group('account_payment_final.group_payment_verifier'):
            raise AccessError(_("You don't have permission to verify payments"))
        
        try:
            self.verification_status = 'verified'
            
            # Create approval history record
            self.env['payment.approval.history'].create({
                'payment_id': self.id,
                'action_type': 'verify',
                'stage_from': 'pending',
                'stage_to': 'verified',
                'user_id': self.env.user.id,
                'comments': 'Payment verification completed'
            })
            
            # Send notification email if configured
            if self.company_id.send_approval_notifications:
                template = self.env.ref('account_payment_final.mail_template_payment_verified', False)
                if template:
                    template.send_mail(self.id, force_send=True)
            
            self.message_post(body=_("Payment %s verified by %s") % (self.voucher_number, self.env.user.name))
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Payment Verified!'),
                    'message': _('Payment %s has been successfully verified.') % (self.voucher_number or self.name),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error during payment verification for {self.name}: {e}")
            raise UserError(_('Error during payment verification: %s') % str(e))

    def action_reject_payment_verification(self):
        """Reject payment verification"""
        self.ensure_one()
        
        if self.verification_status not in ['pending', 'verified']:
            raise UserError(_('Only payments in "Pending" or "Verified" status can be rejected'))
        
        if not self.env.user.has_group('account_payment_final.group_payment_verifier'):
            raise AccessError(_("You don't have permission to reject payment verification"))
        
        try:
            old_status = self.verification_status
            self.verification_status = 'rejected'
            
            # Create approval history record
            self.env['payment.approval.history'].create({
                'payment_id': self.id,
                'action_type': 'reject',
                'stage_from': old_status,
                'stage_to': 'rejected',
                'user_id': self.env.user.id,
                'comments': 'Payment verification rejected'
            })
            
            # Send notification email if configured
            if self.company_id.send_approval_notifications:
                template = self.env.ref('account_payment_final.mail_template_payment_rejected', False)
                if template:
                    template.send_mail(self.id, force_send=True)
            
            self.message_post(body=_("Payment %s verification rejected by %s") % (self.voucher_number, self.env.user.name))
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Payment Verification Rejected'),
                    'message': _('Payment %s verification has been rejected.') % (self.voucher_number or self.name),
                    'type': 'warning',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error during payment rejection for {self.name}: {e}")
            raise UserError(_('Error during payment rejection: %s') % str(e))

    # ============================================================================
    # 4-STAGE APPROVAL WORKFLOW METHODS
    # ============================================================================

    def action_submit_for_review(self):
        """Submit payment for initial review (Stage 1)"""
        self.ensure_one()
        
        if self.approval_state != 'draft':
            raise UserError(_("Only draft payments can be submitted for review"))
        
        # Validate minimum required data
        self._validate_payment_data()
        
        # Update state and tracking
        self.approval_state = 'under_review'
        
        # Log in approval history
        self._log_approval_action('draft', 'under_review', 'submit')
        
        self.message_post(body=_("Payment submitted for review by %s") % self.env.user.name)
        
        return self._return_success_message(_('Payment has been submitted for review.'))

    def action_review_payment(self):
        """Review payment and move to next stage (Stage 1 → Stage 2)"""
        self.ensure_one()
        
        if self.approval_state != 'under_review':
            raise UserError(_("Only payments under review can be processed"))
        
        if not self.env.user.has_group('account_payment_final.group_payment_reviewer'):
            raise AccessError(_("You don't have permission to review payments"))
        
        # Set review fields
        self.reviewer_id = self.env.user
        self.reviewer_date = fields.Datetime.now()
        
        # Determine next stage based on payment type
        if self.payment_type == 'outbound':  # Vendor payment
            self.approval_state = 'for_approval'
            next_stage_msg = "sent for approval"
        else:  # Customer receipt - can skip to approved
            self.approval_state = 'approved'
            next_stage_msg = "approved and ready for posting"
        
        # Log in approval history
        self._log_approval_action('under_review', self.approval_state, 'review')
        
        self.message_post(body=_("Payment reviewed and %s by %s") % (next_stage_msg, self.env.user.name))
        
        # Auto-post if enabled and appropriate
        if self.approval_state == 'approved' and self.company_id.auto_post_approved_payments:
            return self._attempt_auto_post()
        
        return self._return_success_message(_('Payment has been reviewed successfully.'))

    def action_approve_payment(self):
        """Approve payment (Stage 2 → Stage 3)"""
        self.ensure_one()
        
        if self.approval_state != 'for_approval':
            raise UserError(_("Only payments pending approval can be approved"))
        
        if not self.env.user.has_group('account_payment_final.group_payment_approver'):
            raise AccessError(_("You don't have permission to approve payments"))
        
        # Set approval fields
        self.approver_id = self.env.user
        self.approver_date = fields.Datetime.now()
        
        # Determine next stage
        if self.payment_type == 'outbound':  # Vendor payment needs authorization
            self.approval_state = 'for_authorization'
            next_stage_msg = "sent for authorization"
        else:  # Customer receipt can go directly to approved
            self.approval_state = 'approved'
            next_stage_msg = "approved and ready for posting"
        
        # Log in approval history
        self._log_approval_action('for_approval', self.approval_state, 'approve')
        
        self.message_post(body=_("Payment approved and %s by %s") % (next_stage_msg, self.env.user.name))
        
        # Auto-post if enabled and appropriate
        if self.approval_state == 'approved' and self.company_id.auto_post_approved_payments:
            return self._attempt_auto_post()
        
        return self._return_success_message(_('Payment has been approved successfully.'))

    def action_authorize_payment(self):
        """Authorize vendor payment (Stage 3 → Final)"""
        self.ensure_one()
        
        if self.payment_type != 'outbound':
            raise UserError(_("Authorization stage only applies to vendor payments"))
        
        if self.approval_state != 'for_authorization':
            raise UserError(_("Only vendor payments waiting for authorization can be authorized"))
        
        if not self.env.user.has_group('account_payment_final.group_payment_authorizer'):
            raise AccessError(_("You don't have permission to authorize payments"))
        
        # Set authorization fields
        self.authorizer_id = self.env.user
        self.authorizer_date = fields.Datetime.now()
        self.approval_state = 'approved'
        
        # Log in approval history
        self._log_approval_action('for_authorization', 'approved', 'authorize')
        
        self.message_post(body=_("Payment authorized and ready for posting by %s") % self.env.user.name)
        
        # Auto-post if enabled
        if self.company_id.auto_post_approved_payments:
            return self._attempt_auto_post()
        
        return self._return_success_message(_('Payment has been authorized successfully.'))

    def action_post(self):
        """Enhanced posting with approval validation"""
        for record in self:
            # Check approval requirements
            if hasattr(record, 'approval_state') and record.approval_state != 'approved':
                if not record._can_bypass_approval():
                    raise UserError(_('Payment must be approved before posting. Current state: %s') % record.approval_state)
            
            # Set posting user
            record.actual_approver_id = self.env.user
            
            # Call parent post method
            result = super(AccountPayment, record).action_post()
            
            # Update approval state and log
            if hasattr(record, 'approval_state'):
                record.approval_state = 'posted'
                record._log_approval_action('approved', 'posted', 'post')
                record.message_post(body=_("Payment posted by %s") % self.env.user.name)
            
            return result

    def action_reject_payment(self):
        """Reject payment and return to draft"""
        self.ensure_one()
        
        if self.approval_state not in ['under_review', 'for_approval', 'for_authorization']:
            raise UserError(_("Only payments in review/approval stages can be rejected"))
        
        # Check permissions based on current stage
        self._check_rejection_permissions()
        
        old_state = self.approval_state
        
        # Clear relevant fields and return to draft
        self._clear_workflow_fields()
        self.approval_state = 'draft'
        
        # Log rejection
        self._log_approval_action(old_state, 'draft', 'reject')
        
        self.message_post(body=_("Payment rejected and returned to draft by %s") % self.env.user.name)
        
        return self._return_success_message(_('Payment has been rejected and returned to draft.'))

    # ============================================================================
    # UTILITY AND HELPER METHODS
    # ============================================================================

    def _validate_payment_data(self):
        """Validate essential payment data"""
        required_fields = [
            ('partner_id', 'Partner'),
            ('amount', 'Amount'),
            ('currency_id', 'Currency'),
            ('journal_id', 'Journal')
        ]
        
        for field, label in required_fields:
            value = getattr(self, field)
            if not value or (field == 'amount' and value <= 0):
                raise ValidationError(_('%s is required and must be valid.') % label)

    def _can_bypass_approval(self):
        """Determine if approval workflow can be bypassed"""
        return (
            self.env.user.has_group('account.group_account_manager') or
            self.env.context.get('bypass_approval_workflow') or
            self.env.user.has_group('account_payment_final.group_payment_manager')
        )

    def _check_rejection_permissions(self):
        """Check if user can reject at current stage"""
        permission_map = {
            'under_review': 'account_payment_final.group_payment_reviewer',
            'for_approval': 'account_payment_final.group_payment_approver',
            'for_authorization': 'account_payment_final.group_payment_authorizer'
        }
        
        required_group = permission_map.get(self.approval_state)
        if required_group and not self.env.user.has_group(required_group):
            raise AccessError(_("You don't have permission to reject payments at %s stage") % self.approval_state)

    def _clear_workflow_fields(self):
        """Clear workflow fields based on current stage"""
        if self.approval_state == 'under_review':
            self.reviewer_id = False
            self.reviewer_date = False
        elif self.approval_state == 'for_approval':
            self.approver_id = False
            self.approver_date = False
        elif self.approval_state == 'for_authorization':
            self.authorizer_id = False
            self.authorizer_date = False

    def _log_approval_action(self, stage_from, stage_to, action_type, comments=None):
        """Log approval action in history"""
        self.env['payment.approval.history'].create({
            'payment_id': self.id,
            'stage_from': stage_from,
            'stage_to': stage_to,
            'action_type': action_type,
            'user_id': self.env.user.id,
            'comments': comments
        })

    def _attempt_auto_post(self):
        """Attempt to auto-post approved payment"""
        try:
            self.action_post()
            return self._return_success_message(_('Payment approved and posted successfully.'))
        except Exception as e:
            _logger.warning(f"Auto-posting failed for payment {self.voucher_number}: {str(e)}")
            return self._return_success_message(_('Payment approved. Please post manually due to technical issue.'))

    def _return_success_message(self, message):
        """Return standardized success message"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    def get_amount_in_words(self):
        """Convert payment amount to words for voucher"""
        self.ensure_one()
        try:
            # Try built-in Odoo method first
            if hasattr(self.currency_id, 'amount_to_text'):
                return self.currency_id.amount_to_text(self.amount)
            
            # Fallback to simple conversion
            return self._simple_amount_to_words()
            
        except Exception as e:
            _logger.warning("Error converting amount to words: %s", e)
            return f"{self.currency_id.name} {self.amount:,.2f} Only"

    def _simple_amount_to_words(self):
        """Basic amount to words conversion"""
        integer_part = int(self.amount)
        decimal_part = int((self.amount - integer_part) * 100)
        
        if integer_part == 0:
            result = "Zero"
        elif integer_part < 1000:
            result = str(integer_part)
        elif integer_part < 1000000:
            thousands = integer_part // 1000
            remainder = integer_part % 1000
            result = f"{thousands} Thousand"
            if remainder > 0:
                result += f" {remainder}"
        else:
            result = f"{integer_part:,}"
        
        result += f" {self.currency_id.name}"
        if decimal_part > 0:
            result += f" and {decimal_part:02d}/100"
        
        return result + " Only"

    def get_verification_url(self):
        """Get public verification URL for this payment"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        return f"{base_url}/payment/verify/{self.id}" if self.id else False

    # ============================================================================
    # CONSTRAINTS AND VALIDATION
    # ============================================================================

    @api.constrains('approval_state', 'state')
    def _check_approval_constraints(self):
        """Ensure payments follow approval workflow before posting"""
        for payment in self:
            if (payment.state == 'posted' and 
                hasattr(payment, 'approval_state') and 
                payment.approval_state not in ['approved', 'posted'] and
                not payment._can_bypass_approval()):
                raise ValidationError(_('Payment cannot be posted without proper approval workflow completion'))

    @api.constrains('amount')
    def _check_amount_positive(self):
        """Ensure payment amount is positive"""
        for payment in self:
            if payment.amount <= 0:
                raise ValidationError(_('Payment amount must be positive'))

    def unlink(self):
        """Enhanced unlink with proper validation"""
        for record in self:
            if hasattr(record, 'approval_state') and record.approval_state not in ['draft', 'cancelled']:
                if not self.env.user.has_group('account_payment_final.group_payment_manager'):
                    raise UserError(_("You can only delete draft or cancelled payments"))
            if record.state == 'posted':
                raise UserError(_("You cannot delete posted payments"))
        
        return super().unlink()
