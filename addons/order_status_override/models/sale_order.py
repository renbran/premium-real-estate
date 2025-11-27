from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Add custom status fields if they don't exist
    order_status = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('commission', 'Commission'),
        ('final_review', 'Final Review'),
        ('approved', 'Approved'),
        ('implementation', 'Implementation'),
        ('completed', 'Completed'),
    ], string='Order Status', default='draft', tracking=True,
       help="Current status of the order in the workflow")
    
    order_status_id = fields.Many2one(
        'order.status', 
        string='Order Status Record',
        tracking=True,
        help="Custom order status for workflow management"
    )
    
    # Legacy field for backward compatibility (CloudPepper fix)
    custom_status_id = fields.Many2one(
        'order.status', 
        string='Custom Status',
        tracking=True,
        help="Custom order status for workflow management (legacy field for compatibility)"
    )
    documentation_user_id = fields.Many2one(
        'res.users',
        string='Documentation User',
        tracking=True,
        help="User responsible for documentation stage"
    )
    commission_user_id = fields.Many2one(
        'res.users',
        string='Commission User',
        tracking=True,
        help="User responsible for commission calculation"
    )
    allocation_user_id = fields.Many2one(
        'res.users',
        string='Allocation User',
        tracking=True,
        help="User responsible for allocation stage"
    )
    final_review_user_id = fields.Many2one(
        'res.users',
        string='Final Review User',
        tracking=True,
        help="User responsible for final review"
    )
    
    # Computed fields for button visibility
    show_document_review_button = fields.Boolean(
        string='Show Document Review Button',
        compute='_compute_button_visibility',
        help="Determines if document review button should be visible"
    )
    show_commission_calculation_button = fields.Boolean(
        string='Show Commission Calculation Button',
        compute='_compute_button_visibility',
        help="Determines if commission calculation button should be visible"
    )
    show_allocation_button = fields.Boolean(
        string='Show Allocation Button',
        compute='_compute_button_visibility',
        help="Determines if allocation button should be visible"
    )
    show_final_review_button = fields.Boolean(
        string='Show Final Review Button',
        compute='_compute_button_visibility',
        help="Determines if final review button should be visible"
    )
    show_approve_button = fields.Boolean(
        string='Show Approve Button',
        compute='_compute_button_visibility',
        help="Determines if approve button should be visible"
    )
    show_post_button = fields.Boolean(
        string='Show Post Button',
        compute='_compute_button_visibility',
        help="Determines if post button should be visible"
    )
    show_reject_button = fields.Boolean(
        string='Show Reject Button',
        compute='_compute_button_visibility',
        help="Determines if reject button should be visible"
    )
    auto_assigned_users = fields.Boolean(
        string='Auto Assigned Users',
        compute='_compute_auto_assigned_users',
        help="Indicates if users have been automatically assigned"
    )
    
    # Commission Configuration Fields
    # External Commission Fields
    broker_partner_id = fields.Many2one(
        'res.partner',
        string='Broker Partner',
        tracking=True,
        help="Partner receiving broker commission"
    )
    broker_commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Broker Commission Type', default='percentage')
    broker_rate = fields.Float(
        string='Broker Rate (%)',
        help="Broker commission percentage or fixed amount"
    )
    broker_amount = fields.Monetary(
        string='Broker Amount',
        compute='_compute_commission_amounts',
        store=True,
        help="Calculated broker commission amount"
    )
    
    referrer_partner_id = fields.Many2one(
        'res.partner',
        string='Referrer Partner',
        tracking=True,
        help="Partner receiving referrer commission"
    )
    referrer_commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Referrer Commission Type', default='percentage')
    referrer_rate = fields.Float(
        string='Referrer Rate (%)',
        help="Referrer commission percentage or fixed amount"
    )
    referrer_amount = fields.Monetary(
        string='Referrer Amount',
        compute='_compute_commission_amounts',
        store=True,
        help="Calculated referrer commission amount"
    )
    
    cashback_partner_id = fields.Many2one(
        'res.partner',
        string='Cashback Partner',
        tracking=True,
        help="Partner receiving cashback commission"
    )
    cashback_commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Cashback Commission Type', default='percentage')
    cashback_rate = fields.Float(
        string='Cashback Rate (%)',
        help="Cashback commission percentage or fixed amount"
    )
    cashback_amount = fields.Monetary(
        string='Cashback Amount',
        compute='_compute_commission_amounts',
        store=True,
        help="Calculated cashback commission amount"
    )
    
    # Internal Commission Fields
    agent1_partner_id = fields.Many2one(
        'res.partner',
        string='Agent 1 Partner',
        tracking=True,
        help="First agent receiving commission"
    )
    agent1_commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Agent 1 Commission Type', default='percentage')
    agent1_rate = fields.Float(
        string='Agent 1 Rate (%)',
        help="Agent 1 commission percentage or fixed amount"
    )
    agent1_amount = fields.Monetary(
        string='Agent 1 Amount',
        compute='_compute_commission_amounts',
        store=True,
        help="Calculated agent 1 commission amount"
    )
    
    agent2_partner_id = fields.Many2one(
        'res.partner',
        string='Agent 2 Partner',
        tracking=True,
        help="Second agent receiving commission"
    )
    agent2_commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Agent 2 Commission Type', default='percentage')
    agent2_rate = fields.Float(
        string='Agent 2 Rate (%)',
        help="Agent 2 commission percentage or fixed amount"
    )
    agent2_amount = fields.Monetary(
        string='Agent 2 Amount',
        compute='_compute_commission_amounts',
        store=True,
        help="Calculated agent 2 commission amount"
    )
    
    manager_partner_id = fields.Many2one(
        'res.partner',
        string='Manager Partner',
        tracking=True,
        help="Manager receiving commission"
    )
    manager_commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Manager Commission Type', default='percentage')
    manager_rate = fields.Float(
        string='Manager Rate (%)',
        help="Manager commission percentage or fixed amount"
    )
    manager_amount = fields.Monetary(
        string='Manager Amount',
        compute='_compute_commission_amounts',
        store=True,
        help="Calculated manager commission amount"
    )
    
    director_partner_id = fields.Many2one(
        'res.partner',
        string='Director Partner',
        tracking=True,
        help="Director receiving commission"
    )
    director_commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Director Commission Type', default='percentage')
    director_rate = fields.Float(
        string='Director Rate (%)',
        help="Director commission percentage or fixed amount"
    )
    director_amount = fields.Monetary(
        string='Director Amount',
        compute='_compute_commission_amounts',
        store=True,
        help="Calculated director commission amount"
    )
    
    # Commission Summary Fields
    total_external_commission_amount = fields.Monetary(
        string='Total External Commission',
        compute='_compute_commission_totals',
        store=True,
        help="Total of all external commissions (broker + referrer + cashback)"
    )
    total_internal_commission_amount = fields.Monetary(
        string='Total Internal Commission',
        compute='_compute_commission_totals',
        store=True,
        help="Total of all internal commissions (agents + manager + director)"
    )
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_totals',
        store=True,
        help="Total of all commissions (internal + external)"
    )
    
    # New Net Commission Field based on the specified formula
    net_commission_amount = fields.Monetary(
        string='Net Commission',
        compute='_compute_net_commission',
        store=True,
        help="Net commission calculated as: amount_total - (total_internal - total_external)"
    )
    
    # Real Estate specific fields referenced in views
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="Date when the booking was made"
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        tracking=True,
        help="Related project for real estate"
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        help="Specific unit/product being sold"
    )
    
    # Additional workflow user assignments
    approval_user_id = fields.Many2one(
        'res.users',
        string='Approval User',
        tracking=True,
        help="User responsible for final approval"
    )
    posting_user_id = fields.Many2one(
        'res.users',
        string='Posting User',
        tracking=True,
        help="User responsible for posting approved orders"
    )
    
    # Status history for tracking
    custom_status_history_ids = fields.One2many(
        'order.status.history',
        'order_id',
        string='Status History',
        help="History of status changes for this order"
    )
    
    @api.model
    def create(self, vals):
        """Set initial status when creating order"""
        order = super().create(vals)
        
        # Set initial status if not provided
        if not order.order_status_id:
            initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
            if initial_status:
                order.order_status_id = initial_status.id
                order.custom_status_id = initial_status.id  # Sync legacy field
        
        # Ensure both fields are synchronized
        if order.order_status_id and not order.custom_status_id:
            order.custom_status_id = order.order_status_id.id
        elif order.custom_status_id and not order.order_status_id:
            order.order_status_id = order.custom_status_id.id
        
        return order
    
    @api.onchange('order_status_id')
    def _onchange_order_status_id(self):
        """Sync custom_status_id when order_status_id changes"""
        if self.order_status_id:
            self.custom_status_id = self.order_status_id
    
    @api.onchange('custom_status_id')
    def _onchange_custom_status_id(self):
        """Sync order_status_id when custom_status_id changes"""
        if self.custom_status_id:
            self.order_status_id = self.custom_status_id
    
    @api.depends('order_status_id', 'custom_status_id', 'state')
    def _compute_button_visibility(self):
        """Compute visibility of workflow buttons based on current status"""
        for record in self:
            current_status = record.order_status_id or record.custom_status_id
            
            # Default all to False
            record.show_document_review_button = False
            record.show_commission_calculation_button = False
            record.show_allocation_button = False
            record.show_final_review_button = False
            record.show_approve_button = False
            record.show_post_button = False
            record.show_reject_button = False
            
            if not current_status:
                continue
                
            # Logic for button visibility based on status
            if current_status == 'draft':
                record.show_document_review_button = True
            elif current_status == 'document_review':
                record.show_commission_calculation_button = True
                record.show_reject_button = True
            elif current_status == 'commission_calculation':
                record.show_allocation_button = True
                record.show_reject_button = True
            elif current_status == 'allocation':
                record.show_final_review_button = True
                record.show_reject_button = True
            elif current_status == 'final_review':
                record.show_approve_button = True
                record.show_reject_button = True
            elif current_status in ['approved', 'sale']:
                record.show_post_button = True
    
    @api.depends('documentation_user_id', 'commission_user_id', 'allocation_user_id', 'final_review_user_id')
    def _compute_auto_assigned_users(self):
        """Compute if users have been automatically assigned"""
        for record in self:
            record.auto_assigned_users = bool(
                record.documentation_user_id or 
                record.commission_user_id or 
                record.allocation_user_id or 
                record.final_review_user_id
            )
    
    @api.depends('amount_total', 'broker_rate', 'broker_commission_type', 'referrer_rate', 'referrer_commission_type',
                 'cashback_rate', 'cashback_commission_type', 'agent1_rate', 'agent1_commission_type',
                 'agent2_rate', 'agent2_commission_type', 'manager_rate', 'manager_commission_type',
                 'director_rate', 'director_commission_type')
    def _compute_commission_amounts(self):
        """Compute individual commission amounts based on type and rate"""
        for record in self:
            base_amount = record.amount_total
            
            # External Commissions
            record.broker_amount = record._calculate_commission_amount(
                base_amount, record.broker_rate, record.broker_commission_type
            )
            record.referrer_amount = record._calculate_commission_amount(
                base_amount, record.referrer_rate, record.referrer_commission_type
            )
            record.cashback_amount = record._calculate_commission_amount(
                base_amount, record.cashback_rate, record.cashback_commission_type
            )
            
            # Internal Commissions
            record.agent1_amount = record._calculate_commission_amount(
                base_amount, record.agent1_rate, record.agent1_commission_type
            )
            record.agent2_amount = record._calculate_commission_amount(
                base_amount, record.agent2_rate, record.agent2_commission_type
            )
            record.manager_amount = record._calculate_commission_amount(
                base_amount, record.manager_rate, record.manager_commission_type
            )
            record.director_amount = record._calculate_commission_amount(
                base_amount, record.director_rate, record.director_commission_type
            )
    
    @api.depends('broker_amount', 'referrer_amount', 'cashback_amount',
                 'agent1_amount', 'agent2_amount', 'manager_amount', 'director_amount')
    def _compute_commission_totals(self):
        """Compute total commission amounts"""
        for record in self:
            # Total External Commission (broker + referrer + cashback)
            record.total_external_commission_amount = (
                record.broker_amount + 
                record.referrer_amount + 
                record.cashback_amount
            )
            
            # Total Internal Commission (agents + manager + director)
            record.total_internal_commission_amount = (
                record.agent1_amount + 
                record.agent2_amount + 
                record.manager_amount + 
                record.director_amount
            )
            
            # Total Commission Amount
            record.total_commission_amount = (
                record.total_external_commission_amount + 
                record.total_internal_commission_amount
            )
    
    @api.depends('amount_total', 'total_internal_commission_amount', 'total_external_commission_amount')
    def _compute_net_commission(self):
        """Compute net commission using the specified formula:
        net commission = amount_total - (total internal - total external)
        """
        for record in self:
            # Apply the new formula: amount_total - (total internal - total external)
            total_internal = record.total_internal_commission_amount
            total_external = record.total_external_commission_amount
            
            record.net_commission_amount = record.amount_total - (total_internal - total_external)
    
    def _calculate_commission_amount(self, base_amount, rate, commission_type):
        """Helper method to calculate commission amount based on type"""
        if not rate or not commission_type:
            return 0.0
        
        if commission_type == 'percentage':
            return base_amount * (rate / 100.0)
        elif commission_type == 'fixed':
            return rate
        else:
            return 0.0
    
    def _change_status(self, new_status_id, notes=None):
        """Change order status with proper validation and logging"""
        self.ensure_one()
        
        try:
            new_status = self.env['order.status'].browse(new_status_id)
            if not new_status.exists():
                raise ValidationError(_("Invalid status specified."))
            
            old_status = self.order_status_id
            
            # Update the status
            self.order_status_id = new_status.id
            self.custom_status_id = new_status.id  # Sync legacy field
            
            # Handle Odoo state mapping
            self._update_state_from_status(new_status)
            
            # Log the change
            message = _("Status changed from '%s' to '%s'") % (
                old_status.name if old_status else _('None'),
                new_status.name
            )
            if notes:
                message += _("\nNotes: %s") % notes
            
            self.message_post(body=message)
            
            _logger.info("Order %s status changed from %s to %s by user %s", 
                        self.name, 
                        old_status.name if old_status else 'None',
                        new_status.name,
                        self.env.user.name)
            
            return True
            
        except Exception as e:
            _logger.error("Failed to change status for order %s: %s", self.name, str(e))
            raise
    
    def _update_state_from_status(self, status):
        """Update Odoo standard state based on custom status"""
        state_mapping = {
            'draft': 'draft',
            'documentation_progress': 'sent',
            'commission_progress': 'sale',
            'final_review': 'sale',
            'approved': 'sale',
        }
        
        new_state = state_mapping.get(status.code)
        if new_state and new_state != self.state:
            if new_state == 'sale' and self.state in ['draft', 'sent']:
                self.action_confirm()
            elif new_state == 'sent' and self.state == 'draft':
                self.state = 'sent'
            else:
                self.state = new_state
    
    @api.model
    def get_order_status(self, order_id):
        """Get order status information for the widget"""
        try:
            order = self.browse(order_id)
            if not order.exists():
                return {'error': 'Order not found'}
            
            return {
                'status': order.state,
                'status_display': dict(order._fields['state'].selection).get(order.state, order.state),
                'order_id': order.id,
                'name': order.name,
                'partner_name': order.partner_id.name,
                'amount_total': order.amount_total,
                'currency': order.currency_id.name,
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_status(self, new_status):
        """Update order status safely"""
        try:
            self.ensure_one()
            
            # Map widget statuses to Odoo states
            status_mapping = {
                'approved': 'sale',
                'rejected': 'cancel',
                'draft': 'draft',
                'confirmed': 'sale'
            }
            
            if new_status in status_mapping:
                odoo_state = status_mapping[new_status]
                
                # Validate state transition
                if odoo_state == 'sale' and self.state == 'draft':
                    self.action_confirm()
                elif odoo_state == 'cancel':
                    self.action_cancel()
                else:
                    self.state = odoo_state
                
                return {'success': True, 'new_status': self.state}
            else:
                raise ValidationError(f"Invalid status: {new_status}")
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Missing action methods from validation
    def action_post_order(self):
        """Post the order (mark as confirmed)"""
        self.ensure_one()
        if self.state == 'draft':
            self.action_confirm()
        return True
    
    def action_change_status(self):
        """Open status change wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Order Status',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_move_to_final_review(self):
        """Move order to final review stage"""
        self.ensure_one()
        # Custom logic for final review
        return True
    
    def action_approve_order(self):
        """Approve the order"""
        self.ensure_one()
        if self.state in ['draft', 'sent']:
            self.action_confirm()
        return True
    
    def action_quotation_send(self):
        """Send quotation email"""
        self.ensure_one()
        return self.action_quotation_send() if hasattr(super(), 'action_quotation_send') else True
    
    def action_reassign_workflow_users(self):
        """Reassign workflow users"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reassign Users',
            'res_model': 'order.user.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_move_to_post(self):
        """Move to post stage"""
        self.ensure_one()
        return self.action_confirm()
    
    def action_move_to_commission_calculation(self):
        """Move to commission calculation stage"""
        self.ensure_one()
        
        # Find commission calculation status
        commission_status = self.env['order.status'].search([
            ('code', '=', 'commission_calculation')
        ], limit=1)
        
        if commission_status:
            self._change_status(commission_status.id, "Moved to commission calculation")
        
        # Auto-calculate commissions if rates are already set
        if any([
            self.broker_rate, self.referrer_rate, self.cashback_rate,
            self.agent1_rate, self.agent2_rate, self.manager_rate, self.director_rate
        ]):
            # Trigger commission recalculation
            self._compute_commission_amounts()
            self._compute_commission_totals()
            self._compute_net_commission()
            
            _logger.info("Commission calculation completed for order %s. Net commission: %s", 
                        self.name, self.net_commission_amount)
        
        return True
    
    def action_view_order_reports(self):
        """View order reports"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order Reports',
            'res_model': 'order.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_reject_order(self):
        """Reject the order"""
        self.ensure_one()
        self.action_cancel()
        return True
    
    def action_move_to_allocation(self):
        """Move to allocation stage"""
        self.ensure_one()
        # Custom allocation logic
        return True
    
    def action_move_to_document_review(self):
        """Move to document review stage"""
        self.ensure_one()
        # Custom document review logic
        return True
    
    def action_confirm(self):
        """Confirm the sale order"""
        self.ensure_one()
        try:
            # Call the parent action_confirm
            result = super().action_confirm()
            
            # Update status to confirmed/sale if we have status management
            if self.order_status_id:
                confirmed_status = self.env['order.status'].search([
                    ('code', '=', 'confirmed')
                ], limit=1)
                if confirmed_status:
                    self._change_status(confirmed_status.id, "Order confirmed")
            
            return result
        except Exception as e:
            _logger.error("Error in action_confirm: %s", str(e))
            raise
    
    def action_move_to_final_review(self):
        """Move to final review stage"""
        self.ensure_one()
        final_review_status = self.env['order.status'].search([
            ('code', '=', 'final_review')
        ], limit=1)
        if final_review_status:
            self._change_status(final_review_status.id, "Moved to final review")
        return True
    
    def action_approve_order(self):
        """Approve the order"""
        self.ensure_one()
        approved_status = self.env['order.status'].search([
            ('code', '=', 'approved')
        ], limit=1)
        if approved_status:
            self._change_status(approved_status.id, "Order approved")
        return True
    
    def action_generate_payment_voucher(self):
        """Generate payment voucher"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Payment Voucher',
            'res_model': 'payment.voucher.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_view_payment_vouchers(self):
        """View payment vouchers"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Vouchers',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('ref', 'ilike', self.name)],
            'context': {'create': False}
        }
    
    def action_print_payment_voucher(self):
        """Print payment voucher"""
        self.ensure_one()
        return self.env.ref('account.action_report_payment_receipt').report_action(self)
    
    def action_send_commission_email(self):
        """Send commission email"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Commission Email',
            'res_model': 'commission.email.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
