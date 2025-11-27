from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import logging
import qrcode
import io
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Unified Status Field - Updated Professional Workflow per Requirements
    order_status = fields.Selection([
        ('draft', 'Draft'),
        ('document_review', 'Document Review'),
        ('commission_calculation', 'Commission Calculation'),
        ('allocation', 'Allocation'),
        ('final_review', 'Final Review'),
        ('approved', 'Approved'),
        ('post', 'Post'),
    ], string='Order Status', default='draft', tracking=True, copy=False,
       help="Current status of the order in the professional workflow")
    
    # Legacy field (kept for backward compatibility)
    custom_status_id = fields.Many2one('order.status', string='Custom Status', 
                                      tracking=True, copy=False, readonly=True)
    custom_status_history_ids = fields.One2many('order.status.history', 'order_id', 
                                            string='Status History', copy=False)
    
    # Enhanced user assignments for each stage with automatic group-based assignment
    documentation_user_id = fields.Many2one('res.users', string='Documentation Responsible',
                                           help="User responsible for document review stage")
    allocation_user_id = fields.Many2one('res.users', string='Allocation Responsible',
                                        help="User responsible for allocation stage")
    commission_user_id = fields.Many2one('res.users', string='Commission Responsible',
                                        help="User responsible for commission calculations")
    final_review_user_id = fields.Many2one('res.users', string='Final Review Responsible',
                                          help="User responsible for final review stage")
    approval_user_id = fields.Many2one('res.users', string='Approval Responsible',
                                          help="User responsible for final approval")
    posting_user_id = fields.Many2one('res.users', string='Posting Responsible',
                                     help="User responsible for posting approved orders")
    
    # Enhanced stage visibility computed fields with new workflow
    show_document_review_button = fields.Boolean(compute='_compute_workflow_buttons')
    show_commission_calculation_button = fields.Boolean(compute='_compute_workflow_buttons')
    show_commission_calc_button = fields.Boolean(compute='_compute_workflow_buttons', 
                                                string='Commission Calc Button',
                                                help='Alias for show_commission_calculation_button for backward compatibility')
    show_allocation_button = fields.Boolean(compute='_compute_workflow_buttons')
    show_final_review_button = fields.Boolean(compute='_compute_workflow_buttons')
    show_approve_button = fields.Boolean(compute='_compute_workflow_buttons')
    show_post_button = fields.Boolean(compute='_compute_workflow_buttons')
    show_reject_button = fields.Boolean(compute='_compute_workflow_buttons')
    
    # Group-based assignment tracking
    auto_assigned_users = fields.Boolean(string='Auto-assigned Users', default=False,
                                        help="Indicates if users were automatically assigned based on groups")
    
    # Real Estate specific fields
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today, tracking=True, 
                              help="Date when the property was booked/reserved")
    project_id = fields.Many2one('product.template', string='Project', tracking=True)
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True)
    
    # Commission fields - External
    broker_partner_id = fields.Many2one('res.partner', string="Broker Partner", tracking=True)
    broker_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Broker Commission Type", default='percent_unit_price')
    broker_rate = fields.Float(string="Broker Rate (%)", default=0.0, digits=(5, 2))
    broker_amount = fields.Monetary(string="Broker Commission Amount", 
                                  compute="_compute_commissions", store=True)
    
    referrer_partner_id = fields.Many2one('res.partner', string="Referrer Partner", tracking=True)
    referrer_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Referrer Commission Type", default='percent_unit_price')
    referrer_rate = fields.Float(string="Referrer Rate (%)", default=0.0, digits=(5, 2))
    referrer_amount = fields.Monetary(string="Referrer Commission Amount", 
                                    compute="_compute_commissions", store=True)
    
    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Partner", tracking=True)
    cashback_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Cashback Type", default='percent_unit_price')
    cashback_rate = fields.Float(string="Cashback Rate (%)", default=0.0, digits=(5, 2))
    cashback_amount = fields.Monetary(string="Cashback Amount", 
                                    compute="_compute_commissions", store=True)
    
    # Commission fields - Internal
    agent1_partner_id = fields.Many2one('res.partner', string="Agent 1", tracking=True)
    agent1_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 1 Commission Type", default='percent_unit_price')
    agent1_rate = fields.Float(string="Agent 1 Rate (%)", default=0.0, digits=(5, 2))
    agent1_amount = fields.Monetary(string="Agent 1 Commission", 
                                  compute="_compute_commissions", store=True)
    
    agent2_partner_id = fields.Many2one('res.partner', string="Agent 2", tracking=True)
    agent2_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 2 Commission Type", default='percent_unit_price')
    agent2_rate = fields.Float(string="Agent 2 Rate (%)", default=0.0, digits=(5, 2))
    agent2_amount = fields.Monetary(string="Agent 2 Commission", 
                                  compute="_compute_commissions", store=True)
    
    manager_partner_id = fields.Many2one('res.partner', string="Manager Partner", tracking=True)
    manager_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Manager Commission Type", default='percent_unit_price')
    manager_rate = fields.Float(string="Manager Rate (%)", default=0.0, digits=(5, 2))
    manager_amount = fields.Monetary(string="Manager Commission Amount", 
                                   compute="_compute_commissions", store=True)
    
    director_partner_id = fields.Many2one('res.partner', string="Director Partner", tracking=True)
    director_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Director Commission Type", default='percent_unit_price')
    director_rate = fields.Float(string="Director Rate (%)", default=3.0, digits=(5, 2))
    director_amount = fields.Monetary(string="Director Commission Amount", 
                                    compute="_compute_commissions", store=True)
    
    # Summary fields
    total_external_commission_amount = fields.Monetary(string="Total External Commissions", 
                                                     compute="_compute_commissions", store=True)
    total_internal_commission_amount = fields.Monetary(string="Total Internal Commissions", 
                                                     compute="_compute_commissions", store=True)
    total_commission_amount = fields.Monetary(string="Total Commission Amount", 
                                            compute="_compute_commissions", store=True)
    
    # QR Code for verification
    qr_code = fields.Binary(string="QR Code", compute="_compute_qr_code", store=True)
    
    # Report fields - Legacy compatibility
    related_purchase_orders = fields.One2many(
        'purchase.order', 
        compute='_compute_related_documents',
        string='Related Purchase Orders'
    )
    related_vendor_bills = fields.One2many(
        'account.move',
        compute='_compute_related_documents', 
        string='Related Vendor Bills'
    )
    total_payment_out = fields.Monetary(
        string='Total Payment Out',
        compute='_compute_total_payment_out',
        currency_field='currency_id'
    )
    
    @api.depends('broker_rate', 'broker_commission_type', 'referrer_rate', 'referrer_commission_type',
                 'cashback_rate', 'cashback_commission_type', 'agent1_rate', 'agent1_commission_type',
                 'agent2_rate', 'agent2_commission_type', 'manager_rate', 'manager_commission_type',
                 'director_rate', 'director_commission_type', 'amount_untaxed', 'order_line.price_unit')
    def _compute_commissions(self):
        """Calculate all commission amounts based on configured rates and types"""
        for order in self:
            # External commissions
            order.broker_amount = order._calculate_commission_amount(
                order.broker_rate, order.broker_commission_type, order)
            order.referrer_amount = order._calculate_commission_amount(
                order.referrer_rate, order.referrer_commission_type, order)
            order.cashback_amount = order._calculate_commission_amount(
                order.cashback_rate, order.cashback_commission_type, order)
            
            # Internal commissions
            order.agent1_amount = order._calculate_commission_amount(
                order.agent1_rate, order.agent1_commission_type, order)
            order.agent2_amount = order._calculate_commission_amount(
                order.agent2_rate, order.agent2_commission_type, order)
            order.manager_amount = order._calculate_commission_amount(
                order.manager_rate, order.manager_commission_type, order)
            order.director_amount = order._calculate_commission_amount(
                order.director_rate, order.director_commission_type, order)
            
            # Summary totals
            order.total_external_commission_amount = (
                order.broker_amount + order.referrer_amount + order.cashback_amount)
            order.total_internal_commission_amount = (
                order.agent1_amount + order.agent2_amount + 
                order.manager_amount + order.director_amount)
            order.total_commission_amount = (
                order.total_external_commission_amount + order.total_internal_commission_amount)

    def _calculate_commission_amount(self, rate, commission_type, order):
        """Calculate commission amount based on rate and type"""
        if not rate or rate <= 0:
            return 0.0
        
        if commission_type == 'fixed':
            return rate
        elif commission_type == 'percent_unit_price':
            # Calculate based on unit price of first line
            if order.order_line:
                unit_price = order.order_line[0].price_unit
                return (rate / 100) * unit_price
            return 0.0
        elif commission_type == 'percent_untaxed_total':
            return (rate / 100) * order.amount_untaxed
        
        return 0.0

    @api.depends('name', 'partner_id.name')
    def _compute_qr_code(self):
        """Generate QR code for order verification"""
        for order in self:
            if order.name:
                qr_data = f"Order: {order.name}\nCustomer: {order.partner_id.name}\nAmount: {order.amount_total} {order.currency_id.name}"
                
                try:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    order.qr_code = base64.b64encode(buffer.getvalue())
                except Exception as e:
                    _logger.warning(f"Failed to generate QR code for order {order.name}: {e}")
                    order.qr_code = False
            else:
                order.qr_code = False
    
    @api.depends('order_status', 'state')
    def _compute_workflow_buttons(self):
        """Compute visibility of workflow transition buttons with new workflow"""
        for order in self:
            # Default all buttons to hidden
            order.show_document_review_button = False
            order.show_commission_calculation_button = False
            order.show_commission_calc_button = False  # Alias field
            order.show_allocation_button = False
            order.show_final_review_button = False
            order.show_approve_button = False
            order.show_post_button = False
            order.show_reject_button = False
            
            # Show buttons based on current status and user groups
            current_user = self.env.user
            
            # Check if user is admin or has system access (CloudPepper compatibility)
            is_admin = (current_user.has_group('base.group_system') or 
                       current_user.has_group('base.group_erp_manager') or
                       current_user.has_group('order_status_override.group_order_status_admin'))
            
            if order.order_status == 'draft':
                # Can move to document review if user has documentation rights or is admin
                if (current_user.has_group('order_status_override.group_order_documentation_reviewer') or is_admin):
                    order.show_document_review_button = True
                order.show_reject_button = False  # No reject from draft
                
            elif order.order_status == 'document_review':
                # Can move to commission calculation if user has commission rights or is admin
                if (current_user.has_group('order_status_override.group_order_commission_calculator') or is_admin):
                    order.show_commission_calculation_button = True
                    order.show_commission_calc_button = True  # Alias for compatibility
                order.show_reject_button = True
                
            elif order.order_status == 'commission_calculation':
                # Can move to allocation if user has allocation rights or is admin
                if (current_user.has_group('order_status_override.group_order_allocation_manager') or is_admin):
                    order.show_allocation_button = True
                order.show_reject_button = True
                
            elif order.order_status == 'allocation':
                # Can move to final review if user has allocation rights or is admin
                if (current_user.has_group('order_status_override.group_order_allocation_manager') or is_admin):
                    order.show_final_review_button = True
                order.show_reject_button = True
                
            elif order.order_status == 'final_review':
                # Can move to approved if user has approval rights or is admin
                if (current_user.has_group('order_status_override.group_order_approval_manager_enhanced') or
                    current_user.id == order.final_review_user_id.id or is_admin):
                    order.show_approve_button = True
                order.show_reject_button = True
                
            elif order.order_status == 'approved':
                # Can post if user has posting rights or is admin
                if (current_user.has_group('order_status_override.group_order_posting_manager') or is_admin):
                    order.show_post_button = True
                order.show_reject_button = False  # Cannot reject approved orders
                
            # Post status - no further actions needed

    @api.depends('partner_id', 'order_line', 'order_line.product_id')
    def _compute_related_documents(self):
        """Compute related purchase orders and vendor bills"""
        for order in self:
            # Find related purchase orders (by partner or project reference)
            purchase_orders = self.env['purchase.order'].search([
                '|',
                ('partner_id', '=', order.partner_id.id),
                ('origin', 'ilike', order.name)
            ])
            order.related_purchase_orders = purchase_orders
            
            # Find related vendor bills
            vendor_bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                '|',
                ('partner_id', '=', order.partner_id.id),
                ('ref', 'ilike', order.name)
            ])
            order.related_vendor_bills = vendor_bills

    @api.depends('related_vendor_bills', 'total_commission_amount')
    def _compute_total_payment_out(self):
        """Calculate total payment out (vendor bills + commissions)"""
        for order in self:
            vendor_total = sum(order.related_vendor_bills.mapped('amount_total'))
            order.total_payment_out = vendor_total + order.total_commission_amount

    @api.model_create_multi
    def create(self, vals_list):
        """Enhanced create method with auto-assignment based on groups"""
        records = super(SaleOrder, self).create(vals_list)
        
        for record in records:
            # Auto-assign users based on groups
            record._auto_assign_workflow_users()
            
            # Set initial status
            initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
            if initial_status:
                record.custom_status_id = initial_status.id
                self.env['order.status.history'].create({
                    'order_id': record.id,
                    'status_id': initial_status.id,
                    'notes': _('Initial status automatically set to %s') % initial_status.name
                })
        
        return records

    def _auto_assign_workflow_users(self):
        """Automatically assign users based on security groups"""
        self.ensure_one()
        
        # Find users for each workflow stage based on groups
        
        # Documentation reviewers
        if not self.documentation_user_id:
            doc_users = self.env['res.users'].search([
                ('groups_id', 'in', [self.env.ref('order_status_override.group_order_documentation_reviewer').id]),
                ('active', '=', True)
            ], limit=1)
            if doc_users:
                self.documentation_user_id = doc_users[0].id
        
        # Commission calculators -> Allocation managers
        if not self.allocation_user_id:
            allocation_users = self.env['res.users'].search([
                ('groups_id', 'in', [self.env.ref('order_status_override.group_order_allocation_manager').id]),
                ('active', '=', True)
            ], limit=1)
            if allocation_users:
                self.allocation_user_id = allocation_users[0].id
        
        # Final review managers -> Approval managers
        if not self.approval_user_id:
            approval_users = self.env['res.users'].search([
                ('groups_id', 'in', [self.env.ref('order_status_override.group_order_approval_manager_enhanced').id]),
                ('active', '=', True)
            ], limit=1)
            if approval_users:
                self.approval_user_id = approval_users[0].id
        
        # Posting managers
        if not self.posting_user_id:
            posting_users = self.env['res.users'].search([
                ('groups_id', 'in', [self.env.ref('order_status_override.group_order_posting_manager').id]),
                ('active', '=', True)
            ], limit=1)
            if posting_users:
                self.posting_user_id = posting_users[0].id
        
        # Mark as auto-assigned
        self.auto_assigned_users = True
        
        _logger.info(f"Auto-assigned workflow users for order {self.name}: "
                    f"Doc: {self.documentation_user_id.name if self.documentation_user_id else 'None'}, "
                    f"Allocation: {self.allocation_user_id.name if self.allocation_user_id else 'None'}, "
                    f"Approval: {self.approval_user_id.name if self.approval_user_id else 'None'}, "
                    f"Post: {self.posting_user_id.name if self.posting_user_id else 'None'}")

    def action_reassign_workflow_users(self):
        """Manual action to reassign workflow users based on current groups"""
        self.ensure_one()
        self._auto_assign_workflow_users()
        self.message_post(
            body=_("Workflow users have been automatically reassigned based on current group memberships."),
            subject=_("Users Reassigned")
        )
        return True
    
    def action_change_status(self):
        """
        Open the status change wizard
        :return: Action dictionary
        """
        self.ensure_one()
        return {
            'name': _('Change Order Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_current_status_id': self.custom_status_id.id,
            }
        }


    def action_start_documentation_review(self):
        """Start documentation review process"""
        self.ensure_one()
        if not self.documentation_user_id:
            raise UserError(_("Please assign a user for documentation review before starting the process."))
        
        # Find the documentation status
        doc_status = self.env['order.status'].search([('code', '=', 'documentation_review')], limit=1)
        if not doc_status:
            raise UserError(_("Documentation Review status not found in the system."))
        
        # Change to documentation status
        self._change_status(doc_status.id, _("Documentation review started by %s") % self.env.user.name)
        
        # Create activity for documentation user
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Review Documentation for Order %s") % self.name,
            note=_("Please review and prepare all required documentation for this order."),
            user_id=self.documentation_user_id.id
        )
        
        # Send notification email
        self._send_workflow_notification('documentation_review')
        
        return True

    def action_start_allocation(self):
        """Start allocation process (replaces commission calculation)"""
        self.ensure_one()
        if not self.allocation_user_id:
            raise UserError(_("Please assign a user for allocation before proceeding."))
        
        # Update order status to allocation
        self.order_status = 'allocation'
        
        # Create activity for allocation user
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Handle Allocation for Order %s") % self.name,
            note=_("Please process allocation and commission calculations for this order."),
            user_id=self.allocation_user_id.id
        )
        
        # Send notification email
        self._send_workflow_notification('allocation')
        
        return True

    def action_approve_and_post_order(self):
        """Approve the order and post as Sales Order"""
        self.ensure_one()
        
        # Validate commission calculations are complete
        if not self.total_commission_amount:
            raise UserError(_("Please complete commission calculations before approving the order."))
        
        # Find the approved status
        approved_status = self.env['order.status'].search([('code', '=', 'approved')], limit=1)
        if not approved_status:
            raise UserError(_("Approved status not found in the system."))
        
        # Change to approved status
        self._change_status(approved_status.id, _("Order approved and posted by %s") % self.env.user.name)
        
        # Confirm the sales order if not already confirmed
        if self.state == 'draft':
            self.action_confirm()
        
        # Send approval notification
        self._send_workflow_notification('approved')
        
        # Create success message
        self.message_post(
            body=_("Order has been approved and posted as Sales Order. Total commission amount: %s") % 
                 self.currency_id.symbol + str(self.total_commission_amount),
            subject=_("Order Approved and Posted"),
            message_type='notification'
        )
        
        return True

    def _send_workflow_notification(self, stage):
        """Send automated email notification for workflow stages"""
        email_template = None
        recipient_user = None
        
        if stage == 'documentation_review':
            email_template = self.env.ref('order_status_override.email_template_documentation_review', raise_if_not_found=False)
            recipient_user = self.documentation_user_id
        elif stage == 'allocation':
            email_template = self.env.ref('order_status_override.email_template_allocation', raise_if_not_found=False)
            recipient_user = self.allocation_user_id
        elif stage == 'approved':
            email_template = self.env.ref('order_status_override.email_template_order_approved', raise_if_not_found=False)
            # Send to the order creator and sales team
            
        if email_template and recipient_user:
            try:
                email_template.send_mail(self.id, force_send=True)
                _logger.info(f"Workflow notification sent for {stage} to user {recipient_user.name}")
            except Exception as e:
                _logger.warning(f"Failed to send workflow notification: {str(e)}")
    
    def action_reject_order(self):
        """Reject the order and return to draft"""
        self.ensure_one()
        # Check if current user can reject
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can reject orders."))
        
        # Find the draft status
        draft_status = self.env['order.status'].search([('code', '=', 'draft')], limit=1)
        if not draft_status:
            raise UserError(_("Draft status not found in the system."))
        
        # Change to draft status
        self._change_status(draft_status.id, _("Order rejected by %s and returned to draft") % self.env.user.name)
        
        # Send rejection notification
        self.message_post(
            body=_("Order has been rejected and returned to draft status for revision."),
            subject=_("Order Rejected"),
            message_type='notification'
        )
        
        return True

    def action_view_order_reports(self):
        """Open the order reports wizard with current order context"""
        return {
            'name': _('Generate Order Reports'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.report',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_date_from': self.date_order.date() if self.date_order else fields.Date.today(),
                'default_date_to': self.date_order.date() if self.date_order else fields.Date.today(),
                'default_partner_ids': [(6, 0, [self.partner_id.id])],
                'default_report_type': 'comprehensive',
            }
        }

    def action_submit_for_review(self):
        """Submit order for final review"""
        self.ensure_one()
        if not self.final_review_user_id:
            raise UserError(_("Please assign a user for final review before submitting."))
        
        # Find the final review status
        review_status = self.env['order.status'].search([('code', '=', 'final_review')], limit=1)
        if not review_status:
            raise UserError(_("Final review status not found in the system."))
        
        # Change to final review status
        self._change_status(review_status.id, _("Order submitted for final review by %s") % self.env.user.name)
        
        # Create activity for reviewer
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Review Order %s") % self.name,
            note=_("This order is ready for final review and approval/rejection."),
            user_id=self.final_review_user_id.id
        )
        
        return True
    
    def action_return_to_previous(self):
        """Return order to previous stage"""
        self.ensure_one()
        # Get previous status from history
        last_history = self.env['order.status.history'].search([
            ('order_id', '=', self.id)
        ], order='create_date desc', limit=2)
        
        if len(last_history) < 2:
            raise UserError(_("No previous status found to return to."))
        
        previous_status = last_history[1].status_id
        
        # Change to previous status
        self._change_status(previous_status.id, _("Order returned to previous stage by %s") % self.env.user.name)
        
        return True
    
    def action_request_documentation(self):
        """Start documentation process"""
        self.ensure_one()
        if not self.documentation_user_id:
            raise UserError(_("Please assign a user for documentation before starting the process."))
        
        # Find the documentation status
        doc_status = self.env['order.status'].search([('code', '=', 'documentation_progress')], limit=1)
        if not doc_status:
            raise UserError(_("Documentation progress status not found in the system."))
        
        # Change to documentation status
        self._change_status(doc_status.id, _("Documentation process started by %s") % self.env.user.name)
        
        # Create activity for documentation user
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_("Prepare Documentation for Order %s") % self.name,
            note=_("Please prepare all required documentation for this order."),
            user_id=self.documentation_user_id.id
        )
        
        return True
    
    # === ENHANCED UNIFIED WORKFLOW ACTIONS ===
    def action_move_to_document_review(self):
        """Move order to document review stage"""
        self.ensure_one()
        if self.order_status != 'draft':
            raise UserError(_("Order must be in draft status to move to document review."))
        
        # Check user permissions
        if not self.env.user.has_group('order_status_override.group_order_documentation_reviewer'):
            raise UserError(_("You don't have permission to move orders to document review stage."))
        
        self.order_status = 'document_review'
        self._create_workflow_activity('document_review')
        self.message_post(
            body=_("Order moved to Document Review stage by %s") % self.env.user.name,
            subject=_("Status Changed: Document Review"),
        )
        return True

    def action_move_to_commission_calculation(self):
        """Move order from Document Review to Commission Calculation"""
        self.ensure_one()
        if self.order_status != 'document_review':
            raise UserError(_("Order must be in Document Review status to move to Commission Calculation."))
        
        # Check user permissions
        if not self.env.user.has_group('order_status_override.group_order_commission_calculator'):
            raise UserError(_("You don't have permission to move orders to commission calculation stage."))
        
        self.order_status = 'commission_calculation'
        self._create_workflow_activity('commission_calculation')
        self.message_post(
            body=_("Order moved to Commission Calculation stage by %s") % self.env.user.name,
            subject=_("Status Changed: Commission Calculation"),
        )
        return True

    def action_move_to_allocation(self):
        """Move order from Commission Calculation to allocation stage"""
        self.ensure_one()
        if self.order_status != 'commission_calculation':
            raise UserError(_("Order must be in commission calculation status to move to allocation."))
        
        # Check user permissions
        if not self.env.user.has_group('order_status_override.group_order_commission_calculator'):
            raise UserError(_("You don't have permission to move orders to allocation stage."))
        
        self.order_status = 'allocation'
        self._create_workflow_activity('allocation')
        self.message_post(
            body=_("Order moved to Allocation stage by %s") % self.env.user.name,
            subject=_("Status Changed: Allocation"),
        )
        return True

    def action_move_to_final_review(self):
        """Move order from Allocation to Final Review"""
        self.ensure_one()
        if self.order_status != 'allocation':
            raise UserError(_("Order must be in Allocation status to move to Final Review."))
        
        # Check user permissions
        if not self.env.user.has_group('order_status_override.group_order_allocation_manager'):
            raise UserError(_("You don't have permission to move orders to final review stage."))
        
        self.order_status = 'final_review'
        self._create_workflow_activity('final_review')
        self.message_post(
            body=_("Order moved to Final Review stage by %s") % self.env.user.name,
            subject=_("Status Changed: Final Review"),
        )
        return True

    def action_approve_order(self):
        """Move order from Final Review to Approved stage"""
        self.ensure_one()
        if self.order_status != 'final_review':
            raise UserError(_("Order must be in final review status to approve."))
        
        # Check user permissions
        current_user = self.env.user
        if not (current_user.has_group('order_status_override.group_order_approval_manager_enhanced') or
                current_user.id == self.approval_user_id.id):
            raise UserError(_("You don't have permission to approve orders."))
        
        self.order_status = 'approved'
        self._create_workflow_activity('approved')
        self.message_post(
            body=_("Order approved by %s") % self.env.user.name,
            subject=_("Status Changed: Approved"),
        )
        return True

    def action_move_to_post(self):
        """Move order from Approved to Post stage"""
        self.ensure_one()
        if self.order_status != 'approved':
            raise UserError(_("Order must be approved before posting."))
        
        # Check user permissions
        current_user = self.env.user
        if not current_user.has_group('order_status_override.group_order_posting_manager'):
            raise UserError(_("You don't have permission to post orders."))
        
        self.order_status = 'post'
        self._create_workflow_activity('post')
        self.message_post(
            body=_("Order moved to posting stage by %s") % self.env.user.name,
            subject=_("Status Changed: Post"),
        )
        return True

    def action_post_order(self):
        """Post the approved order as sales order (replaces confirm to post)"""
        self.ensure_one()
        if self.order_status != 'approved':
            raise UserError(_("Order must be approved before posting."))
        
        # Check user permissions
        if not self.env.user.has_group('order_status_override.group_order_posting_manager'):
            raise UserError(_("You don't have permission to post orders."))
        
        # Confirm the sales order in Odoo (standard workflow)
        if self.state == 'draft':
            self.action_confirm()
        
        self.order_status = 'posted'
        self.message_post(
            body=_("Order posted as Sales Order by %s") % self.env.user.name,
            subject=_("Status Changed: Posted"),
        )
        return True

    def _create_workflow_activity(self, stage):
        """Create activities for workflow stages with enhanced targeting"""
        self.ensure_one()
        
        user_id = False
        summary = _("Process Sale Order: %s") % self.name
        note = ""
        
        if stage == 'document_review':
            user_id = self.documentation_user_id.id
            note = _("Please review and prepare all required documentation for this order.")
            summary = _("Document Review Required: %s") % self.name
            
        elif stage == 'allocation':
            user_id = self.allocation_user_id.id
            note = _("Please process allocation for this order.")
            summary = _("Allocation Required: %s") % self.name
            
        elif stage == 'approved':
            user_id = self.posting_user_id.id
            note = _("Order has been approved and is ready for posting as Sales Order.")
            summary = _("Order Ready for Posting: %s") % self.name
        
        if user_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=summary,
                note=note,
                user_id=user_id
            )
    
    def _change_status(self, new_status_id, notes=False):
        """Helper method to change status and create history entry"""
        old_status_id = self.custom_status_id.id
        self.custom_status_id = new_status_id
        
        # Create history entry
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': new_status_id,
            'previous_status_id': old_status_id,
            'notes': notes or _('Status changed')
        })
        
        # Create activity based on the responsible type
        new_status = self.env['order.status'].browse(new_status_id)
        self._create_activity_for_status(new_status)
        
        return True
    
    def _create_activity_for_status(self, status):
        """Create an activity for the responsible user based on status"""
        user_id = False
        summary = _("Process Sale Order ") + self.name
        note = _("Please process the sale order as per the '%s' stage.") % status.name
        
        if status.responsible_type == 'documentation':
            user_id = self.documentation_user_id.id
        elif status.responsible_type == 'commission':
            user_id = self.commission_user_id.id
        elif status.responsible_type == 'final_review':
            user_id = self.final_review_user_id.id
        
        if user_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=summary,
                note=note,
                user_id=user_id
            )
    
    def action_confirm(self):
        """Override the standard confirm action to include custom status workflow"""
        result = super(SaleOrder, self).action_confirm()
        
        # Update to next appropriate status if configured
        if self.custom_status_id and self.custom_status_id.stage == 'quotation':
            # Find next status in sequence or set to 'confirmed' stage
            next_status = self.env['order.status'].search([
                ('stage', '=', 'confirmed'),
                ('active', '=', True)
            ], limit=1)
            
            if next_status:
                self._change_status(
                    next_status.id,
                    _("Order confirmed and moved to next stage")
                )
        
        # Log confirmation activity
        self.message_post(
            body=_("Sale Order %s has been confirmed") % self.name,
            message_type='notification'
        )
        
        return result
    
    def action_quotation_send(self):
        """Override the standard quotation send action to update status if needed"""
        result = super(SaleOrder, self).action_quotation_send()
        
        # Update status to 'sent' if we have a quotation status
        if self.custom_status_id and self.custom_status_id.stage == 'quotation':
            sent_status = self.env['order.status'].search([
                ('stage', '=', 'quotation'),
                ('name', 'ilike', 'sent'),
                ('active', '=', True)
            ], limit=1)
            
            if sent_status:
                self._change_status(
                    sent_status.id,
                    _("Quotation sent to customer")
                )
        
        # Log send activity
        self.message_post(
            body=_("Quotation for %s has been sent") % self.name,
            message_type='notification'
        )
        
        return result
