# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
import logging
import time

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Basic Commission Fields
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string="Commission Status", default='draft', tracking=True)
    
    commission_processed = fields.Boolean(
        string="Commission Processed", 
        default=False,
        tracking=True
    )
    
    use_commission_lines = fields.Boolean(
        string="Use Commission Lines",
        default=True,
        help="Enable enhanced commission line processing"
    )
    
    commission_calculation_time = fields.Float(
        string="Commission Calculation Time (ms)",
        readonly=True,
        help="Time taken for last commission calculation in milliseconds"
    )
    
    commission_blocked_reason = fields.Text(
        string="Commission Blocked Reason",
        readonly=True
    )

    # Count Fields for Smart Buttons
    commission_statement_count = fields.Integer(
        string="Commission Statement Count",
        compute="_compute_commission_counts",
        store=True
    )
    
    commission_lines_count = fields.Integer(
        string="Commission Lines Count",
        compute="_compute_commission_counts",
        store=True
    )
    
    purchase_order_count = fields.Integer(
        string="Purchase Order Count",
        compute="_compute_purchase_order_count",
        store=True
    )

    # Commission Amount Fields
    total_commission_amount = fields.Monetary(
        string="Total Commission Amount",
        compute="_compute_commission_amounts",
        store=True,
        currency_field='currency_id'
    )
    
    total_external_commission_amount = fields.Monetary(
        string="Total External Commission",
        compute="_compute_commission_amounts",
        store=True,
        currency_field='currency_id'
    )
    
    total_internal_commission_amount = fields.Monetary(
        string="Total Internal Commission",
        compute="_compute_commission_amounts",
        store=True,
        currency_field='currency_id'
    )
    
    company_share = fields.Monetary(
        string="Company Share",
        compute="_compute_commission_amounts",
        store=True,
        currency_field='currency_id'
    )
    
    net_company_share = fields.Monetary(
        string="Net Company Share",
        compute="_compute_commission_amounts",
        store=True,
        currency_field='currency_id'
    )
    
    sales_value = fields.Monetary(
        string="Unit Price (Sales Value)",
        compute="_compute_sales_value",
        store=True,
        currency_field='currency_id',
        help="Actual unit price from the single sales order line"
    )

    # Legacy Commission Fields
    consultant_id = fields.Many2one('res.partner', string="Consultant")
    consultant_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Consultant Commission Type", default='percentage')
    consultant_comm_percentage = fields.Float(string="Consultant Commission %")
    salesperson_commission = fields.Monetary(string="Salesperson Commission", currency_field='currency_id')
    
    manager_id = fields.Many2one('res.partner', string="Manager")
    manager_legacy_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Manager Commission Type", default='percentage')
    manager_comm_percentage = fields.Float(string="Manager Commission %")
    manager_commission = fields.Monetary(string="Manager Commission", currency_field='currency_id')
    
    second_agent_id = fields.Many2one('res.partner', string="Second Agent")
    second_agent_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Second Agent Commission Type", default='percentage')
    second_agent_comm_percentage = fields.Float(string="Second Agent Commission %")
    second_agent_commission = fields.Monetary(string="Second Agent Commission", currency_field='currency_id')
    
    director_id = fields.Many2one('res.partner', string="Director")
    director_legacy_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Director Commission Type", default='percentage')
    director_comm_percentage = fields.Float(string="Director Commission %")
    director_commission = fields.Monetary(string="Director Commission", currency_field='currency_id')

    # External Commission Fields
    broker_partner_id = fields.Many2one('res.partner', string="Broker Partner")
    broker_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Broker Commission Type", default='percentage')
    broker_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Broker Calculation Base', default='unit_price')
    broker_rate = fields.Float(string="Broker Rate %")
    broker_amount = fields.Monetary(string="Broker Amount", currency_field='currency_id')
    
    referrer_partner_id = fields.Many2one('res.partner', string="Referrer Partner")
    referrer_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Referrer Commission Type", default='percentage')
    referrer_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Referrer Calculation Base', default='unit_price')
    referrer_rate = fields.Float(string="Referrer Rate %")
    referrer_amount = fields.Monetary(string="Referrer Amount", currency_field='currency_id')

    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Partner")
    cashback_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Cashback Commission Type", default='percentage')
    cashback_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Cashback Calculation Base', default='unit_price')
    cashback_rate = fields.Float(string="Cashback Rate %")
    cashback_amount = fields.Monetary(string="Cashback Amount", currency_field='currency_id')

    other_external_partner_id = fields.Many2one('res.partner', string="Other External Partner")
    other_external_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Other External Commission Type", default='percentage')
    other_external_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Other External Calculation Base', default='unit_price')
    other_external_rate = fields.Float(string="Other External Rate %")
    other_external_amount = fields.Monetary(string="Other External Amount", currency_field='currency_id')

    # Internal Commission Fields
    agent1_partner_id = fields.Many2one('res.partner', string="Agent 1")
    agent1_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Agent 1 Commission Type", default='percentage')
    agent1_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Agent 1 Calculation Base', default='order_total_untaxed')
    agent1_rate = fields.Float(string="Agent 1 Rate %")
    agent1_amount = fields.Monetary(string="Agent 1 Amount", currency_field='currency_id')

    agent2_partner_id = fields.Many2one('res.partner', string="Agent 2")
    agent2_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Agent 2 Commission Type", default='percentage')
    agent2_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Agent 2 Calculation Base', default='order_total_untaxed')
    agent2_rate = fields.Float(string="Agent 2 Rate %")
    agent2_amount = fields.Monetary(string="Agent 2 Amount", currency_field='currency_id')

    manager_partner_id = fields.Many2one('res.partner', string="Manager Partner")
    manager_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Manager Commission Type", default='percentage')
    manager_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Manager Calculation Base', default='order_total_untaxed')
    manager_rate = fields.Float(string="Manager Rate %")
    manager_amount = fields.Monetary(string="Manager Amount", currency_field='currency_id')

    director_partner_id = fields.Many2one('res.partner', string="Director Partner")
    director_commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Director Commission Type", default='percentage')
    director_calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Director Calculation Base', default='unit_price')
    director_rate = fields.Float(string="Director Rate %")
    director_amount = fields.Monetary(string="Director Amount", currency_field='currency_id')

    # Invoice Status Fields
    is_fully_invoiced = fields.Boolean(
        string="Is Fully Invoiced",
        compute="_compute_invoice_status",
        store=True
    )
    
    has_posted_invoices = fields.Boolean(
        string="Has Posted Invoices",
        compute="_compute_invoice_status",
        store=True
    )

    # Relational Fields
    commission_line_ids = fields.One2many(
        'commission.line',
        'sale_order_id',
        string="Commission Lines"
    )
    
    purchase_order_ids = fields.One2many(
        'purchase.order',
        'commission_sale_order_id',
        string="Commission Purchase Orders"
    )

    @api.depends('commission_line_ids')
    def _compute_commission_counts(self):
        """Compute commission-related counts for smart buttons"""
        for record in self:
            record.commission_lines_count = len(record.commission_line_ids)
            record.commission_statement_count = len(record.commission_line_ids.filtered(lambda l: l.state != 'draft'))

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        """Compute purchase order count"""
        for record in self:
            record.purchase_order_count = len(record.purchase_order_ids)

    @api.depends('order_line', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_sales_value(self):
        """Compute sales_value as the actual unit price from the single order line
        
        Since sales orders are constrained to have only one line,
        sales_value represents the actual unit price of that line.
        """
        for record in self:
            if record.order_line:
                # Get the first (and only) line
                line = record.order_line[0]
                # sales_value = unit price
                record.sales_value = line.price_unit
            else:
                record.sales_value = 0.0

    @api.depends('commission_line_ids', 'commission_line_ids.commission_amount', 'amount_total')
    def _compute_commission_amounts(self):
        """Compute all commission amounts based on order and commission lines"""
        for record in self:
            commission_lines = record.commission_line_ids
            
            # Calculate total commission from all commission lines
            record.total_commission_amount = sum(commission_lines.mapped('commission_amount'))
            
            # Calculate external commissions (from external partners)
            record.total_external_commission_amount = sum(
                commission_lines.filtered(lambda l: l.commission_category == 'external').mapped('commission_amount')
            )
            
            # Calculate internal commissions (from internal agents/managers)
            record.total_internal_commission_amount = sum(
                commission_lines.filtered(lambda l: l.commission_category == 'internal').mapped('commission_amount')
            )
            
            # Company share = Order Total - Total Commissions
            record.company_share = record.amount_total - record.total_commission_amount
            
            # Net company share (same as company_share at order level)
            record.net_company_share = record.company_share

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_status')
    def _compute_invoice_status(self):
        """Compute invoice status fields with enhanced debugging"""
        for record in self:
            invoices = record.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice')
            posted_invoices = invoices.filtered(lambda inv: inv.state == 'posted')
            
            record.has_posted_invoices = bool(posted_invoices)
            record.is_fully_invoiced = record.invoice_status == 'invoiced'
            
            # Debug logging
            if record.invoice_ids and not record.has_posted_invoices:
                _logger.info("SO %s - Total Invoices: %s, Out Invoices: %s, Posted: %s, States: %s", 
                            record.name, 
                            len(record.invoice_ids),
                            len(invoices),
                            len(posted_invoices),
                            [inv.state for inv in invoices])

    # ===== ONCHANGE METHODS FOR AUTO-CALCULATION =====

    def _get_calculation_base_amount(self, calculation_base):
        """Helper to get the base amount for a given calculation base"""
        self.ensure_one()
        if calculation_base == 'unit_price':
            if self.order_line:
                return self.order_line[0].price_unit
            return 0.0
        elif calculation_base == 'order_total_untaxed':
            return self.amount_untaxed
        elif calculation_base == 'order_total':
            return self.amount_total
        return 0.0

    @api.onchange('broker_rate', 'broker_calculation_base', 'broker_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_broker_commission(self):
        """Auto-calculate broker commission amount"""
        if self.broker_commission_type == 'percentage' and self.broker_rate:
            base = self._get_calculation_base_amount(self.broker_calculation_base)
            self.broker_amount = base * (self.broker_rate / 100)

    @api.onchange('referrer_rate', 'referrer_calculation_base', 'referrer_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_referrer_commission(self):
        """Auto-calculate referrer commission amount"""
        if self.referrer_commission_type == 'percentage' and self.referrer_rate:
            base = self._get_calculation_base_amount(self.referrer_calculation_base)
            self.referrer_amount = base * (self.referrer_rate / 100)

    @api.onchange('cashback_rate', 'cashback_calculation_base', 'cashback_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_cashback_commission(self):
        """Auto-calculate cashback commission amount"""
        if self.cashback_commission_type == 'percentage' and self.cashback_rate:
            base = self._get_calculation_base_amount(self.cashback_calculation_base)
            self.cashback_amount = base * (self.cashback_rate / 100)

    @api.onchange('other_external_rate', 'other_external_calculation_base', 'other_external_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_other_external_commission(self):
        """Auto-calculate other external commission amount"""
        if self.other_external_commission_type == 'percentage' and self.other_external_rate:
            base = self._get_calculation_base_amount(self.other_external_calculation_base)
            self.other_external_amount = base * (self.other_external_rate / 100)

    @api.onchange('agent1_rate', 'agent1_calculation_base', 'agent1_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_agent1_commission(self):
        """Auto-calculate agent1 commission amount"""
        if self.agent1_commission_type == 'percentage' and self.agent1_rate:
            base = self._get_calculation_base_amount(self.agent1_calculation_base)
            self.agent1_amount = base * (self.agent1_rate / 100)

    @api.onchange('agent2_rate', 'agent2_calculation_base', 'agent2_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_agent2_commission(self):
        """Auto-calculate agent2 commission amount"""
        if self.agent2_commission_type == 'percentage' and self.agent2_rate:
            base = self._get_calculation_base_amount(self.agent2_calculation_base)
            self.agent2_amount = base * (self.agent2_rate / 100)

    @api.onchange('manager_rate', 'manager_calculation_base', 'manager_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_manager_commission(self):
        """Auto-calculate manager commission amount"""
        if self.manager_commission_type == 'percentage' and self.manager_rate:
            base = self._get_calculation_base_amount(self.manager_calculation_base)
            self.manager_amount = base * (self.manager_rate / 100)

    @api.onchange('director_rate', 'director_calculation_base', 'director_commission_type', 'amount_untaxed', 'amount_total')
    def _onchange_director_commission(self):
        """Auto-calculate director commission amount"""
        if self.director_commission_type == 'percentage' and self.director_rate:
            base = self._get_calculation_base_amount(self.director_calculation_base)
            self.director_amount = base * (self.director_rate / 100)

    def action_view_commission_statement(self):
        """Open commission lines for this sale order as a 'statement' view.
        If multiple partners are involved, action opens a tree view filtered to this order.
        """
        self.ensure_one()
        action = {
            'name': f'Commission Statements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }
        return action

    def action_view_commission_lines(self):
        """Action to view commission lines"""
        self.ensure_one()
        action = self.env.ref('commission_ax.action_commission_line_tree').read()[0]
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {
            'default_sale_order_id': self.id,
            'search_default_sale_order_id': self.id,
        }
        return action

    def action_view_commission_dashboard(self):
        """Action to view commission dashboard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Dashboard'),
            'res_model': 'commission.dashboard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'active_id': self.id,
                'active_model': 'sale.order'
            }
        }

    def action_process_commissions(self):
        """Process commissions for this sale order"""
        self.ensure_one()
        
        # Check if already processed
        if self.commission_processed:
            raise UserError(_("Commissions have already been processed for this order."))
        
        # Check if order is confirmed
        if self.state not in ['sale', 'done']:
            raise UserError(_("Order must be confirmed before processing commissions."))
        
        # Check invoice requirement
        if not self.has_posted_invoices:
            raise UserError(_("Order must have at least one posted invoice before processing commissions."))
        
        try:
            start_time = time.time()
            
            _logger.info("="*60)
            _logger.info("Starting commission processing for Sale Order: %s", self.name)
            _logger.info("="*60)
            
            # Create commission lines
            self._create_commission_lines()
            
            _logger.info("Commission lines created: %s total, %s external", 
                        len(self.commission_line_ids), 
                        len(self.commission_line_ids.filtered(lambda l: l.commission_category == 'external')))
            
            # Create purchase orders for external commissions
            self._create_commission_purchase_orders()
            
            # Record performance metric
            calculation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update status
            self.commission_processed = True
            self.commission_status = 'processed'
            self.commission_calculation_time = calculation_time
            
            _logger.info("="*60)
            _logger.info("Commissions processed successfully for Sale Order: %s (Time: %.2fms)", 
                        self.name, calculation_time)
            _logger.info("="*60)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Commissions processed successfully!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error processing commissions for Sale Order {self.name}: {str(e)}")
            raise UserError(_("Error processing commissions: %s") % str(e))

    def action_force_process_commissions(self):
        """Force process commissions (override invoice check)"""
        self.ensure_one()
        
        # Check if already processed
        if self.commission_processed:
            raise UserError(_("Commissions have already been processed for this order."))
        
        # Check if order is confirmed
        if self.state not in ['sale', 'done']:
            raise UserError(_("Order must be confirmed before processing commissions."))
        
        try:
            start_time = time.time()
            
            # Create commission lines
            self._create_commission_lines()
            
            # Create purchase orders for external commissions
            self._create_commission_purchase_orders()
            
            # Record performance metric
            calculation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update status
            self.commission_processed = True
            self.commission_status = 'processed'
            self.commission_calculation_time = calculation_time
            
            _logger.info(f"Commissions force processed for Sale Order {self.name}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Commissions force processed successfully!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error force processing commissions for Sale Order {self.name}: {str(e)}")
            raise UserError(_("Error force processing commissions: %s") % str(e))

    def action_confirm_commissions(self):
        """Confirm calculated commissions"""
        self.ensure_one()
        
        if self.commission_status != 'calculated':
            raise UserError(_("Only calculated commissions can be confirmed."))
        
        self.commission_status = 'confirmed'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commissions confirmed successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reset_commissions(self):
        """Reset commissions to draft"""
        self.ensure_one()
        
        # Delete existing commission lines
        self.commission_line_ids.unlink()
        
        # Reset status
        self.commission_processed = False
        self.commission_status = 'draft'
        self.commission_calculation_time = False
        self.commission_blocked_reason = False
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commissions reset to draft successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_create_commission_lines(self):
        """Create commission lines manually"""
        self.ensure_one()
        self._create_commission_lines()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission lines created successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _create_commission_lines(self):
        """Create commission lines based on configured partners and rates"""
        self.ensure_one()
        
        # Clear existing lines
        self.commission_line_ids.unlink()
        
        commission_lines = []
        
        # External Commission Lines
        external_partners = [
            ('broker', self.broker_partner_id, self.broker_commission_type, self.broker_calculation_base, self.broker_rate, self.broker_amount),
            ('referrer', self.referrer_partner_id, self.referrer_commission_type, self.referrer_calculation_base, self.referrer_rate, self.referrer_amount),
            ('cashback', self.cashback_partner_id, self.cashback_commission_type, self.cashback_calculation_base, self.cashback_rate, self.cashback_amount),
            ('other_external', self.other_external_partner_id, self.other_external_commission_type, self.other_external_calculation_base, self.other_external_rate, self.other_external_amount),
        ]

        for role, partner, comm_type, calc_base, rate, amount in external_partners:
            if partner:
                commission_lines.append(self._create_commission_line_data(
                    partner, role, 'external', comm_type, calc_base, rate, amount
                ))

        # Internal Commission Lines
        internal_partners = [
            ('agent1', self.agent1_partner_id, self.agent1_commission_type, self.agent1_calculation_base, self.agent1_rate, self.agent1_amount),
            ('agent2', self.agent2_partner_id, self.agent2_commission_type, self.agent2_calculation_base, self.agent2_rate, self.agent2_amount),
            ('manager', self.manager_partner_id, self.manager_commission_type, self.manager_calculation_base, self.manager_rate, self.manager_amount),
            ('director', self.director_partner_id, self.director_commission_type, self.director_calculation_base, self.director_rate, self.director_amount),
        ]

        for role, partner, comm_type, calc_base, rate, amount in internal_partners:
            if partner:
                commission_lines.append(self._create_commission_line_data(
                    partner, role, 'internal', comm_type, calc_base, rate, amount
                ))
        
        # Create all commission lines at once
        if commission_lines:
            self.env['commission.line'].create(commission_lines)
            self.commission_status = 'calculated'
            _logger.info(f"Created {len(commission_lines)} commission lines for Sale Order {self.name}")

    def _create_commission_line_data(self, partner, role, category, comm_type, calc_base, rate, amount):
        """Create commission line data dict

        All three calculation types are available for all partner types:
        - unit_price: Based on product unit price
        - order_total_untaxed: Based on order total without tax
        - fixed: Fixed commission amount (via calculation_method)
        """
        # Get the first (and typically only) sale order line
        sale_order_line = self.order_line[0] if self.order_line else False
        
        return {
            'sale_order_id': self.id,
            'sale_order_line_id': sale_order_line.id if sale_order_line else False,
            'partner_id': partner.id,
            'role': role,
            'commission_category': category,
            'calculation_method': 'percentage' if comm_type == 'percentage' else 'fixed',
            'calculation_base': calc_base,  # Directly use the selected calculation base
            'rate': rate if comm_type == 'percentage' else 0,
            'commission_amount': amount,
            'state': 'confirmed',  # Start in confirmed state for automatic PO creation
            'calculation_date': fields.Datetime.now(),
            'confirmation_date': fields.Datetime.now(),
            # base_amount will be computed automatically based on calculation_base and sale_order_line_id
        }

    def _create_commission_purchase_orders(self):
        """Create purchase orders for ALL commission lines (external, internal, legacy) for verification"""
        self.ensure_one()
        
        _logger.info(">>> " + "=" * 60)
        _logger.info(">>> Starting Purchase Order Creation for SO: %s", self.name)
        _logger.info(">>> " + "=" * 60)
        
        # Process ALL commission lines regardless of category
        eligible_lines = self.commission_line_ids.filtered(
            lambda l: l.state == 'confirmed' and not l.purchase_order_id
        )
        
        _logger.info(">>> Total commission lines: %s", len(self.commission_line_ids))
        _logger.info(">>> Eligible for PO creation: %s", len(eligible_lines))
        _logger.info(">>> Categories breakdown:")
        for category in ['external', 'internal', 'legacy']:
            count = len(self.commission_line_ids.filtered(lambda l: l.commission_category == category))
            if count > 0:
                _logger.info(">>>   - %s: %s lines", category.capitalize(), count)
        
        _logger.info(">>> Line details:")
        for line in self.commission_line_ids:
            _logger.info(">>>   Line ID %s: Partner=%s, Category=%s, State=%s, Amount=%s, Has PO=%s", 
                        line.id, line.partner_id.name, line.commission_category, 
                        line.state, line.commission_amount, bool(line.purchase_order_id))

        # Don't process if no commission lines exist
        if not eligible_lines:
            _logger.warning(">>> No eligible commission lines found for sale order %s. Skipping PO creation.", self.name)
            return

        _logger.info(">>> " + "=" * 60)
        _logger.info(">>> Processing %s commission lines for PO creation", len(eligible_lines))
        _logger.info(">>> " + "=" * 60)

        po_created_count = 0
        po_skipped_count = 0
        po_failed_count = 0
        
        for idx, line in enumerate(eligible_lines, 1):
            _logger.info(">>> " + "-" * 40)
            _logger.info(">>> Processing Line %s/%s", idx, len(eligible_lines))
            _logger.info(">>> " + "-" * 40)
            _logger.info(">>> Commission Line ID: %s", line.id)
            _logger.info(">>> Partner: %s (ID: %s)", line.partner_id.name, line.partner_id.id)
            _logger.info(">>> Category: %s", line.commission_category)
            _logger.info(">>> Role: %s", line.role)
            _logger.info(">>> Amount: %s %s", line.commission_amount, line.currency_id.name)
            _logger.info(">>> State: %s", line.state)
            
            if line.purchase_order_id:
                _logger.info(">>> ⊘ Line already has PO %s, skipping", line.purchase_order_id.name)
                po_skipped_count += 1
                continue
            
            # Ensure partner is marked as vendor (auto-fix if needed)
            if not line.partner_id.supplier_rank or line.partner_id.supplier_rank == 0:
                _logger.info(">>> Partner not marked as vendor. Auto-marking as vendor...")
                try:
                    line.partner_id.write({'supplier_rank': 1})
                    _logger.info(">>> ✓ Partner marked as vendor")
                except Exception as e:
                    _logger.error(">>> ✗ Failed to mark partner as vendor: %s", str(e))
                    po_failed_count += 1
                    continue
            else:
                _logger.info(">>> ✓ Partner is vendor (rank: %s)", line.partner_id.supplier_rank)
                
            try:
                _logger.info(">>> Calling _create_purchase_order()...")
                po = line._create_purchase_order()
                
                if po:
                    _logger.info(">>> ✓✓✓ Successfully created PO %s for line %s", po.name, line.id)
                    po_created_count += 1
                else:
                    _logger.warning(">>> ✗✗✗ PO creation returned None for line %s", line.id)
                    po_failed_count += 1
                    
            except Exception as e:
                _logger.error(">>> ✗✗✗ Failed to create PO for line %s: %s", line.id, str(e), exc_info=True)
                po_failed_count += 1
                # Continue with other lines instead of failing the entire process
                continue
        
        _logger.info(">>> " + "=" * 60)
        _logger.info(">>> PO CREATION SUMMARY for SO %s:", self.name)
        _logger.info(">>> " + "=" * 60)
        _logger.info(">>>   Created: %s", po_created_count)
        _logger.info(">>>   Skipped (already has PO): %s", po_skipped_count)
        _logger.info(">>>   Failed: %s", po_failed_count)
        _logger.info(">>> " + "=" * 60)

    def _get_commission_product(self):
        """Get or create commission product for purchase orders

        Returns the product to use for commission purchase orders.
        Creates a default commission product if one doesn't exist.
        """
        self.ensure_one()

        # Try to find existing commission product
        commission_product = self.env['product.product'].search([
            ('default_code', '=', 'COMMISSION'),
            ('type', '=', 'service')
        ], limit=1)

        # If not found, create one
        if not commission_product:
            commission_product = self.env['product.product'].create({
                'name': 'Commission Service',
                'default_code': 'COMMISSION',
                'type': 'service',
                'categ_id': self.env.ref('product.product_category_all').id,
                'sale_ok': False,
                'purchase_ok': True,
                'list_price': 0.0,
                'standard_price': 0.0,
                'description': 'Service product for commission payments',
            })
            _logger.info(f"Created commission product: {commission_product.name}")

        return commission_product
