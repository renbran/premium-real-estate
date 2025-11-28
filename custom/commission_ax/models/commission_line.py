from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class CommissionLine(models.Model):
    _name = 'commission.line'
    _description = 'Commission Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'
    _rec_name = 'display_name'
    _check_company_auto = True

    # Basic Fields
    sequence = fields.Integer(string="Sequence", default=10, index=True)
    name = fields.Char(string="Description", compute="_compute_name", store=True, index=True)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    
    # Related Sale Order
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        required=True,
        ondelete='cascade',
        index=True
    )
    
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string="Sale Order Line",
        ondelete='cascade'
    )
    
    # Partner Information
    partner_id = fields.Many2one(
        'res.partner',
        string="Commission Partner",
        required=True,
        index=True
    )
    
    # Commission Type and Configuration
    commission_type_id = fields.Many2one(
        'commission.type',
        string="Commission Type"
    )
    
    role = fields.Selection([
        ('broker', 'Broker'),
        ('referrer', 'Referrer'),
        ('cashback', 'Cashback'),
        ('other_external', 'Other External'),
        ('agent1', 'Agent 1'),
        ('agent2', 'Agent 2'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('consultant', 'Consultant'),
        ('second_agent', 'Second Agent'),
    ], string="Role", required=True)
    
    commission_category = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], string="Commission Category", required=True, default='external')
    
    # Calculation Fields
    calculation_method = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Calculation Method", default='percentage', required=True)

    calculation_base = fields.Selection([
        ('unit_price', 'Unit Price / Sales Value'),
        ('order_total_untaxed', 'Order Total (Without Tax)'),
        ('order_total', 'Order Total (With Tax)'),
    ], string='Calculation Base', default='order_total_untaxed', required=True,
       help='Determines what amount the commission is calculated on:\n'
            '- Unit Price: Based on the unit price of the product\n'
            '- Order Total (Without Tax): Based on total order amount excluding taxes\n'
            '- Order Total (With Tax): Based on total order amount including taxes')

    rate = fields.Float(
        string="Commission Rate (%)",
        digits=(16, 4),
        default=0.0
    )

    base_amount = fields.Monetary(
        string="Base Amount",
        currency_field='currency_id',
        compute='_compute_base_amount',
        store=True,
        readonly=False,
        help="Automatically calculated based on calculation_base selection"
    )
    
    commission_amount = fields.Monetary(
        string="Commission Amount",
        currency_field='currency_id',
        required=True,
        default=0.0
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related='sale_order_id.currency_id',
        store=True,
        readonly=True
    )
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string="State", default='draft', tracking=True)
    
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string="Payment Status", default='pending', tracking=True)
    
    # Purchase Order Integration
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string="Purchase Order",
        ondelete='set null'
    )
    
    # Tracking Fields
    calculation_date = fields.Datetime(string="Calculation Date", readonly=True)
    confirmation_date = fields.Datetime(string="Confirmation Date", readonly=True)
    processing_date = fields.Datetime(string="Processing Date", readonly=True)
    payment_date = fields.Datetime(string="Payment Date", readonly=True)
    
    # Notes
    notes = fields.Text(string="Notes")
    description = fields.Text(string="Description", tracking=True)

    # Company
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        related='sale_order_id.company_id',
        store=True,
        readonly=True
    )

    # ===== ADDITIONAL FIELDS FOR ENHANCED FUNCTIONALITY =====

    # Related fields from Sale Order Line
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        related='sale_order_line_id.product_id',
        store=True,
        readonly=True
    )

    product_uom_qty = fields.Float(
        string="Ordered Qty",
        related='sale_order_line_id.product_uom_qty',
        store=True,
        readonly=True,
        digits='Product Unit of Measure'
    )

    price_unit = fields.Float(
        string="Unit Price",
        related='sale_order_line_id.price_unit',
        store=True,
        readonly=True,
        digits='Product Price'
    )

    price_subtotal = fields.Monetary(
        string="Subtotal",
        related='sale_order_line_id.price_subtotal',
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    price_total = fields.Monetary(
        string="Total",
        related='sale_order_line_id.price_total',
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    # Commission Calculation Fields
    sales_value = fields.Float(
        string="Sales Value (Unit Price)",
        compute="_compute_sales_value",
        store=True,
        digits='Product Price',
        help="Unit price from order line (price per unit)"
    )

    commission_qty = fields.Float(
        string="Commission Quantity",
        compute="_compute_commission_qty",
        store=True,
        digits='Product Unit of Measure',
        help="Quantity for commission calculation"
    )

    invoiced_qty = fields.Float(
        string="Invoiced Quantity",
        compute="_compute_invoiced_qty",
        store=True,
        digits='Product Unit of Measure',
        help="Quantity already invoiced"
    )

    completion_percentage = fields.Float(
        string="Completion %",
        compute="_compute_completion_percentage",
        store=True,
        help="Commission completion based on invoicing"
    )

    # Payment Tracking Fields
    paid_amount = fields.Monetary(
        string="Paid Amount",
        default=0.0,
        currency_field='currency_id',
        tracking=True,
        help="Total amount already paid"
    )

    outstanding_amount = fields.Monetary(
        string="Outstanding Amount",
        compute="_compute_outstanding_amount",
        store=True,
        currency_field='currency_id',
        help="Remaining amount to be paid"
    )

    invoice_amount = fields.Monetary(
        string="Invoice Amount",
        currency_field='currency_id',
        default=0.0,
        help="Total invoiced amount"
    )

    expected_payment_date = fields.Date(
        string="Expected Payment Date",
        compute="_compute_expected_payment_date",
        store=True,
        help="Expected date for payment"
    )

    days_overdue = fields.Integer(
        string="Days Overdue",
        compute="_compute_days_overdue",
        store=True,
        help="Number of days payment is overdue"
    )

    # Related Purchase Order Fields
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string="Purchase Line",
        readonly=True,
        ondelete='set null'
    )

    vendor_bill_id = fields.Many2one(
        'account.move',
        string="Vendor Bill",
        domain="[('move_type', '=', 'in_invoice')]",
        ondelete='set null'
    )

    # Commission Processing Fields
    date_commission = fields.Date(
        string="Commission Date",
        default=fields.Date.context_today,
        help="Date when commission was earned"
    )

    # Counter Fields for Smart Buttons
    invoice_count = fields.Integer(
        string="Invoice Count",
        compute="_compute_invoice_count",
        store=True
    )

    payment_count = fields.Integer(
        string="Payment Count",
        compute="_compute_payment_count",
        store=True
    )

    # Aging Fields
    aging_days = fields.Integer(
        string="Aging Days",
        compute="_compute_aging",
        store=True,
        help="Number of days since commission was processed"
    )

    aging_category = fields.Selection([
        ('0_days', '0-30 Days'),
        ('30_days', '31-60 Days'),
        ('60_days', '61-90 Days'),
        ('90_days', '90+ Days')
    ], string="Aging Category", compute="_compute_aging", store=True)

    # Legacy Flag
    is_legacy = fields.Boolean(
        string="Is Legacy",
        default=False,
        help="Indicates if this is a legacy commission record"
    )

    # Company Currency Fields
    commission_amount_company_currency = fields.Monetary(
        string="Commission (Company Currency)",
        compute="_compute_company_currency_amount",
        store=True,
        currency_field='company_currency_id',
        help="Commission amount in company currency"
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        string="Company Currency",
        related='company_id.currency_id',
        store=True,
        readonly=True
    )

    @api.depends('partner_id', 'role', 'commission_amount')
    def _compute_name(self):
        """Compute commission line name"""
        for record in self:
            if record.partner_id and record.role:
                record.name = f"{record.partner_id.name} - {dict(record._fields['role'].selection).get(record.role)} Commission"
            else:
                record.name = "Commission Line"

    @api.depends('name', 'commission_amount', 'currency_id')
    def _compute_display_name(self):
        """Compute display name with amount"""
        for record in self:
            if record.name and record.commission_amount:
                currency_symbol = record.currency_id.symbol or ''
                record.display_name = f"{record.name} - {currency_symbol}{record.commission_amount:,.2f}"
            else:
                record.display_name = record.name or "Commission Line"

    @api.onchange('role')
    def _onchange_role(self):
        """Suggest calculation_base based on role (can be manually overridden by user)"""
        if self.role:
            # Suggest calculation base based on role
            # Exclusive sales roles typically use unit price
            exclusive_roles = ['broker', 'referrer', 'cashback', 'other_external']
            if self.role in exclusive_roles:
                self.calculation_base = 'unit_price'
            else:
                # Primary and internal roles typically use order total untaxed
                self.calculation_base = 'order_total_untaxed'

    @api.onchange('calculation_method', 'calculation_base', 'rate', 'base_amount', 'commission_amount')
    def _onchange_calculation_values(self):
        """Recalculate commission amount when method or values change"""
        if self.calculation_method == 'percentage' and self.rate and self.base_amount:
            self.commission_amount = self.base_amount * (self.rate / 100)
        # For fixed method, commission_amount should be set manually by user

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Update currency and auto-select first sale order line when sale order changes"""
        if self.sale_order_id:
            self.currency_id = self.sale_order_id.currency_id
            # Auto-select first sale order line if only one exists
            if len(self.sale_order_id.order_line) == 1:
                self.sale_order_line_id = self.sale_order_id.order_line[0]
            elif not self.sale_order_line_id and self.sale_order_id.order_line:
                # If no line selected and multiple lines exist, clear it to force selection
                self.sale_order_line_id = False
        else:
            self.sale_order_line_id = False

    @api.onchange('sale_order_line_id')
    def _onchange_sale_order_line_id(self):
        """Update related fields when sale order line changes"""
        if self.sale_order_line_id:
            # Force recomputation of related fields
            self._compute_base_amount()
            self._compute_sales_value()
            self._compute_commission_qty()
            
            # Auto-calculate commission if we have all required data
            if (self.calculation_method == 'percentage' and 
                self.rate and 
                self.base_amount and 
                self.state == 'draft'):
                self.commission_amount = self.base_amount * (self.rate / 100)

    # ===== NEW COMPUTE METHODS FOR ADDITIONAL FIELDS =====

    @api.depends('calculation_base', 'sale_order_id', 'sale_order_id.amount_untaxed',
                 'sale_order_id.amount_total', 'sale_order_line_id', 'sale_order_line_id.price_unit')
    def _compute_base_amount(self):
        """Compute base amount based on calculation_base selection"""
        for record in self:
            if not record.sale_order_id:
                record.base_amount = 0.0
                continue

            if record.calculation_base == 'unit_price':
                # Based on unit price/sales value
                if record.sale_order_line_id:
                    record.base_amount = record.sale_order_line_id.price_unit
                elif record.sale_order_id.order_line:
                    # Get first line if no specific line is set
                    record.base_amount = record.sale_order_id.order_line[0].price_unit
                else:
                    record.base_amount = 0.0
            elif record.calculation_base == 'order_total_untaxed':
                # Based on order total without tax
                record.base_amount = record.sale_order_id.amount_untaxed
            elif record.calculation_base == 'order_total':
                # Based on order total with tax
                record.base_amount = record.sale_order_id.amount_total
            else:
                record.base_amount = 0.0

    @api.depends('sale_order_line_id', 'sale_order_line_id.price_unit')
    def _compute_sales_value(self):
        """Compute sales value from order line"""
        for record in self:
            if record.sale_order_line_id:
                record.sales_value = record.sale_order_line_id.price_unit
            else:
                record.sales_value = 0.0

    @api.depends('sale_order_line_id', 'sale_order_line_id.product_uom_qty')
    def _compute_commission_qty(self):
        """Compute commission quantity from order line"""
        for record in self:
            if record.sale_order_line_id:
                record.commission_qty = record.sale_order_line_id.product_uom_qty
            else:
                record.commission_qty = 0.0

    @api.depends('sale_order_line_id', 'sale_order_line_id.qty_invoiced')
    def _compute_invoiced_qty(self):
        """Compute invoiced quantity from order line"""
        for record in self:
            if record.sale_order_line_id and hasattr(record.sale_order_line_id, 'qty_invoiced'):
                record.invoiced_qty = record.sale_order_line_id.qty_invoiced
            else:
                record.invoiced_qty = 0.0

    @api.depends('commission_qty', 'invoiced_qty')
    def _compute_completion_percentage(self):
        """Compute completion percentage based on invoiced quantity"""
        for record in self:
            if record.commission_qty and record.commission_qty > 0:
                record.completion_percentage = (record.invoiced_qty / record.commission_qty) * 100
            else:
                record.completion_percentage = 0.0

    @api.depends('commission_amount', 'paid_amount')
    def _compute_outstanding_amount(self):
        """Compute outstanding amount"""
        for record in self:
            record.outstanding_amount = record.commission_amount - record.paid_amount

    @api.depends('processing_date')
    def _compute_expected_payment_date(self):
        """Compute expected payment date (30 days after processing)"""
        for record in self:
            if record.processing_date:
                processing_date = fields.Date.from_string(record.processing_date.date())
                record.expected_payment_date = processing_date + timedelta(days=30)
            else:
                record.expected_payment_date = False

    @api.depends('expected_payment_date', 'payment_status', 'state')
    def _compute_days_overdue(self):
        """Compute days overdue"""
        today = fields.Date.context_today(self)
        for record in self:
            if record.expected_payment_date and record.state == 'processed' and record.payment_status != 'paid':
                if today > record.expected_payment_date:
                    delta = today - record.expected_payment_date
                    record.days_overdue = delta.days
                else:
                    record.days_overdue = 0
            else:
                record.days_overdue = 0

    @api.depends('vendor_bill_id', 'purchase_order_id')
    def _compute_invoice_count(self):
        """Compute invoice count"""
        for record in self:
            count = 0
            if record.vendor_bill_id:
                count += 1
            if record.purchase_order_id:
                # Count invoices related to purchase order
                invoice_lines = self.env['account.move.line'].search([
                    ('purchase_line_id', 'in', record.purchase_order_id.order_line.ids)
                ])
                count += len(invoice_lines.mapped('move_id').filtered(
                    lambda m: m.move_type == 'in_invoice'
                ))
            record.invoice_count = count

    @api.depends('paid_amount')
    def _compute_payment_count(self):
        """Compute payment count based on paid amount"""
        for record in self:
            # For now, simple logic: if partially paid = 1, if fully paid could be more
            if record.paid_amount > 0:
                if record.paid_amount >= record.commission_amount:
                    record.payment_count = 1  # At least one payment to full
                else:
                    record.payment_count = 1  # Partial payment
            else:
                record.payment_count = 0

    @api.depends('processing_date', 'state')
    def _compute_aging(self):
        """Compute aging days and category"""
        today = fields.Date.context_today(self)
        for record in self:
            if record.processing_date and record.state in ['processed', 'paid']:
                processing_date = fields.Date.from_string(record.processing_date.date())
                delta = today - processing_date
                record.aging_days = delta.days

                # Categorize aging
                if delta.days <= 30:
                    record.aging_category = '0_days'
                elif delta.days <= 60:
                    record.aging_category = '30_days'
                elif delta.days <= 90:
                    record.aging_category = '60_days'
                else:
                    record.aging_category = '90_days'
            else:
                record.aging_days = 0
                record.aging_category = '0_days'

    @api.depends('commission_amount', 'currency_id', 'company_currency_id')
    def _compute_company_currency_amount(self):
        """Compute commission amount in company currency"""
        for record in self:
            if record.currency_id and record.company_currency_id:
                if record.currency_id == record.company_currency_id:
                    record.commission_amount_company_currency = record.commission_amount
                else:
                    # Convert to company currency
                    date = record.date_commission or fields.Date.context_today(record)
                    record.commission_amount_company_currency = record.currency_id._convert(
                        record.commission_amount,
                        record.company_currency_id,
                        record.company_id,
                        date
                    )
            else:
                record.commission_amount_company_currency = record.commission_amount

    def action_calculate(self):
        """Calculate commission amount - Enhanced to handle all calculation methods and bases"""
        for record in self:
            if not record.sale_order_id:
                raise UserError(_("Sale Order is required for commission calculation."))

            # Base amount is automatically computed based on calculation_base
            # Force recomputation if needed
            record._compute_base_amount()

            # Calculate based on method
            if record.calculation_method == 'percentage':
                if not record.rate:
                    raise UserError(_("Commission rate is required for percentage calculation."))
                if not record.base_amount:
                    raise UserError(_("Base amount could not be determined. Please check calculation base settings."))
                record.commission_amount = record.base_amount * (record.rate / 100)
            elif record.calculation_method == 'fixed':
                # For fixed amount, commission_amount should already be set
                if not record.commission_amount:
                    raise UserError(_("Commission amount is required for fixed calculation method."))
            else:
                raise UserError(_("Invalid calculation method: %s") % record.calculation_method)

            record.state = 'calculated'
            record.calculation_date = fields.Datetime.now()

            # Log calculation with base information
            base_description = dict(record._fields['calculation_base'].selection).get(record.calculation_base)
            record.message_post(
                body=_("Commission calculated: %s %s<br/>"
                       "Method: %s<br/>"
                       "Base: %s (Amount: %s %s)<br/>"
                       "Rate: %s%%") % (
                    record.commission_amount,
                    record.currency_id.name,
                    record.calculation_method,
                    base_description,
                    record.base_amount,
                    record.currency_id.name,
                    record.rate if record.calculation_method == 'percentage' else 'N/A'
                )
            )

        return True

    def action_confirm(self):
        """Confirm commission calculation"""
        for record in self:
            if record.state not in ['draft', 'calculated']:
                raise UserError(_("Only draft or calculated commissions can be confirmed."))
            
            if not record.commission_amount:
                raise UserError(_("Commission amount must be set before confirmation."))
            
            record.state = 'confirmed'
            record.confirmation_date = fields.Datetime.now()
        
        return True

    def action_process(self):
        """Process commission (create purchase order if external)"""
        for record in self:
            # Allow processing from draft or calculated state - auto-confirm if needed
            if record.state not in ['confirmed', 'draft', 'calculated']:
                raise UserError(_("Only draft, calculated, or confirmed commissions can be processed."))

            # Validate required fields before processing
            if not record.commission_amount or record.commission_amount <= 0:
                raise UserError(_("Commission amount must be greater than zero before processing."))
            
            if not record.partner_id:
                raise UserError(_("Commission partner is required before processing."))

            # Auto-confirm if not already confirmed
            if record.state in ['draft', 'calculated']:
                record.action_confirm()

            # Create purchase order for ALL commission categories (for verification before billing)
            if not record.purchase_order_id:
                try:
                    _logger.info("Creating purchase order for commission line %s (Category: %s, Partner: %s, Amount: %s)", 
                                record.id, record.commission_category, record.partner_id.name, record.commission_amount)
                    
                    po = record._create_purchase_order()
                    
                    if not po:
                        raise UserError(_("Purchase order creation returned None - check commission product setup."))
                    
                    _logger.info("Successfully created purchase order %s for commission line %s", 
                                po.name, record.id)
                    
                except Exception as e:
                    _logger.error("Failed to create purchase order for commission line %s: %s", 
                                 record.id, str(e), exc_info=True)
                    raise UserError(_("Failed to create purchase order: %s\n\nPlease check:\n"
                                    "1. Commission partner is set as a vendor\n"
                                    "2. Commission amount is greater than zero\n"
                                    "3. System permissions allow purchase order creation") % str(e))

            record.state = 'processed'
            record.processing_date = fields.Datetime.now()

        return True

    def action_mark_paid(self):
        """Mark commission as paid"""
        for record in self:
            if record.state != 'processed':
                raise UserError(_("Only processed commissions can be marked as paid."))
            
            record.state = 'paid'
            record.payment_status = 'paid'
            record.payment_date = fields.Datetime.now()
        
        return True

    def action_cancel(self):
        """Cancel commission"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_("Paid commissions cannot be cancelled."))
            
            record.state = 'cancelled'
            record.payment_status = 'cancelled'
        
        return True

    def action_reset_to_draft(self):
        """Reset commission to draft"""
        for record in self:
            record.state = 'draft'
            record.payment_status = 'pending'
            record.calculation_date = False
            record.confirmation_date = False
            record.processing_date = False
            record.payment_date = False
        
        return True

    # ===== NEW ACTION METHODS FOR VIEW BUTTONS =====

    def action_recalculate(self):
        """Recalculate commission amount"""
        return self.action_calculate()

    def action_debug_calculation(self):
        """Debug commission calculation - Show current values"""
        self.ensure_one()
        base_description = dict(self._fields['calculation_base'].selection).get(self.calculation_base)
        message = _(
            "<strong>Commission Calculation Debug:</strong><br/>"
            "• Sale Order: %s<br/>"
            "• Sale Order Line: %s<br/>"
            "• Product: %s<br/>"
            "• Role: %s<br/>"
            "• Calculation Base: %s<br/>"
            "• Base Amount: %s %s<br/>"
            "• Order Total (Untaxed): %s %s<br/>"
            "• Order Total (With Tax): %s %s<br/>"
            "• Unit Price: %s<br/>"
            "• Calculation Method: %s<br/>"
            "• Rate: %s%%<br/>"
            "• Commission Amount: %s %s<br/>"
            "• State: %s<br/>"
            "• Commission Qty: %s<br/>"
            "• Invoiced Qty: %s<br/>"
            "• Completion: %s%%"
        ) % (
            self.sale_order_id.name if self.sale_order_id else 'Not Set',
            self.sale_order_line_id.name if self.sale_order_line_id else 'Not Set',
            self.product_id.name if self.product_id else 'Not Set',
            dict(self._fields['role'].selection).get(self.role) if self.role else 'Not Set',
            base_description,
            self.base_amount, self.currency_id.name,
            self.sale_order_id.amount_untaxed if self.sale_order_id else 0, self.currency_id.name,
            self.sale_order_id.amount_total if self.sale_order_id else 0, self.currency_id.name,
            self.sales_value,
            self.calculation_method,
            self.rate,
            self.commission_amount, self.currency_id.name,
            self.state,
            self.commission_qty,
            self.invoiced_qty,
            self.completion_percentage
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Commission Calculation Debug'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }

    def action_fix_calculation(self):
        """Fix calculation issues automatically"""
        for record in self:
            try:
                # Reset and recalculate
                if not record.sale_order_id:
                    raise UserError(_("Cannot fix: Sale Order is missing."))

                # Set base amount
                if record.sale_order_line_id:
                    record.base_amount = record.sale_order_line_id.price_subtotal
                elif record.sale_order_id:
                    record.base_amount = record.sale_order_id.amount_total

                # Recalculate commission
                if record.calculation_method == 'percentage' and record.rate:
                    record.commission_amount = record.base_amount * (record.rate / 100)

                # Update state if in draft
                if record.state == 'draft':
                    record.state = 'calculated'
                    record.calculation_date = fields.Datetime.now()

                record.message_post(body=_("Commission calculation fixed automatically."))

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Commission calculation has been fixed.'),
                        'type': 'success',
                    }
                }
            except Exception as e:
                raise UserError(_("Error fixing calculation: %s") % str(e))

    def action_record_partial_payment(self):
        """Open wizard to record partial payment"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Record Payment'),
            'res_model': 'commission.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_commission_line_id': self.id,
                'default_payment_amount': self.outstanding_amount,
            }
        }

    def action_view_purchase_order(self):
        """View related purchase order"""
        self.ensure_one()
        if not self.purchase_order_id:
            raise UserError(_("No purchase order linked to this commission."))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Order'),
            'res_model': 'purchase.order',
            'res_id': self.purchase_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_purchase_order(self):
        """Action to create purchase order from commission line (any category)"""
        self.ensure_one()
        
        if self.purchase_order_id:
            raise UserError(_("Purchase order already exists for this commission."))
        
        if not self.commission_amount:
            raise UserError(_("Commission amount must be set before creating purchase order."))
        
        try:
            po = self._create_purchase_order()
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Purchase Order Created'),
                'res_model': 'purchase.order',
                'res_id': po.id,
                'view_mode': 'form',
                'target': 'current',
            }
        except Exception as e:
            raise UserError(_("Failed to create purchase order: %s") % str(e))

    def action_debug_purchase_order_creation(self):
        """Debug action to check purchase order creation requirements"""
        self.ensure_one()
        
        debug_info = []
        
        # Check basic requirements
        debug_info.append(f"Commission Line ID: {self.id}")
        debug_info.append(f"Commission Category: {self.commission_category}")
        debug_info.append(f"Commission Amount: {self.commission_amount} {self.currency_id.name}")
        debug_info.append(f"Partner: {self.partner_id.name} (ID: {self.partner_id.id})")
        debug_info.append(f"Partner is Vendor: {bool(self.partner_id.supplier_rank)}")
        debug_info.append(f"Sale Order: {self.sale_order_id.name}")
        debug_info.append(f"State: {self.state}")
        debug_info.append(f"Existing PO: {self.purchase_order_id.name if self.purchase_order_id else 'None'}")
        
        # Check commission product
        try:
            product = self.sale_order_id._get_commission_product()
            debug_info.append(f"Commission Product: {product.name} (ID: {product.id})")
            debug_info.append(f"Product UOM: {product.uom_id.name}")
            debug_info.append(f"Product Purchase OK: {product.purchase_ok}")
        except Exception as e:
            debug_info.append(f"Commission Product Error: {str(e)}")
        
        # Check permissions
        try:
            can_create_po = self.env['purchase.order'].check_access_rights('create', False)
            debug_info.append(f"Can Create PO: {can_create_po}")
        except:
            debug_info.append("Can Create PO: Unknown")
        
        message = "\n".join(debug_info)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Purchase Order Creation Debug'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }

    def action_populate_from_sale_order(self):
        """Auto-populate commission line fields from sale order configuration"""
        self.ensure_one()
        
        if not self.sale_order_id:
            raise UserError(_("Sale order must be selected first."))
        
        # Auto-select sale order line if only one exists
        if len(self.sale_order_id.order_line) == 1 and not self.sale_order_line_id:
            self.sale_order_line_id = self.sale_order_id.order_line[0]
        
        # If partner and role are set, try to find matching configuration from sale order
        if self.partner_id and self.role:
            sale_order = self.sale_order_id
            partner_configs = {
                'broker': (sale_order.broker_partner_id, 'broker_rate', 'broker_amount', 'broker_calculation_base'),
                'referrer': (sale_order.referrer_partner_id, 'referrer_rate', 'referrer_amount', 'referrer_calculation_base'),
                'cashback': (sale_order.cashback_partner_id, 'cashback_rate', 'cashback_amount', 'cashback_calculation_base'),
                'other_external': (sale_order.other_external_partner_id, 'other_external_rate', 'other_external_amount', 'other_external_calculation_base'),
                'agent1': (sale_order.agent1_partner_id, 'agent1_rate', 'agent1_amount', 'agent1_calculation_base'),
                'agent2': (sale_order.agent2_partner_id, 'agent2_rate', 'agent2_amount', 'agent2_calculation_base'),
                'manager': (sale_order.manager_partner_id, 'manager_rate', 'manager_amount', 'manager_calculation_base'),
                'director': (sale_order.director_partner_id, 'director_rate', 'director_amount', 'director_calculation_base'),
            }
            
            if self.role in partner_configs:
                partner_field, rate_field, amount_field, base_field = partner_configs[self.role]
                
                # Check if partner matches
                if partner_field == self.partner_id:
                    # Auto-populate from sale order configuration
                    if hasattr(sale_order, rate_field) and getattr(sale_order, rate_field):
                        self.rate = getattr(sale_order, rate_field)
                        self.calculation_method = 'percentage'
                    
                    if hasattr(sale_order, amount_field) and getattr(sale_order, amount_field):
                        self.commission_amount = getattr(sale_order, amount_field)
                    
                    if hasattr(sale_order, base_field) and getattr(sale_order, base_field):
                        self.calculation_base = getattr(sale_order, base_field)
        
        # Force recomputation of all dependent fields
        self._compute_base_amount()
        self._compute_sales_value()
        self._compute_commission_qty()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission line populated from sale order configuration.'),
                'type': 'success',
            }
        }

    def action_view_invoices(self):
        """View related invoices"""
        self.ensure_one()
        invoices = self.env['account.move']

        if self.vendor_bill_id:
            invoices |= self.vendor_bill_id

        if self.purchase_order_id:
            invoice_lines = self.env['account.move.line'].search([
                ('purchase_line_id', 'in', self.purchase_order_id.order_line.ids)
            ])
            invoices |= invoice_lines.mapped('move_id').filtered(
                lambda m: m.move_type == 'in_invoice'
            )

        if not invoices:
            raise UserError(_("No invoices found for this commission."))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bills'),
            'res_model': 'account.move',
            'domain': [('id', 'in', invoices.ids)],
            'view_mode': 'tree,form',
            'context': {'default_move_type': 'in_invoice'}
        }

    def action_view_payments(self):
        """View related payments"""
        self.ensure_one()

        # Get payments from vendor bills
        invoices = self.env['account.move']
        if self.vendor_bill_id:
            invoices |= self.vendor_bill_id

        if self.purchase_order_id:
            invoice_lines = self.env['account.move.line'].search([
                ('purchase_line_id', 'in', self.purchase_order_id.order_line.ids)
            ])
            invoices |= invoice_lines.mapped('move_id').filtered(
                lambda m: m.move_type == 'in_invoice'
            )

        # Get payments from invoices
        payments = self.env['account.payment']
        for invoice in invoices:
            # Get reconciled payments
            payment_lines = invoice.line_ids.filtered(lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable'])
            reconciled_lines = payment_lines.mapped('matched_debit_ids.debit_move_id') | payment_lines.mapped('matched_credit_ids.credit_move_id')
            payment_moves = reconciled_lines.mapped('move_id').filtered(lambda m: m.payment_id)
            payments |= payment_moves.mapped('payment_id')

        if not payments:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Payments'),
                    'message': _('No payments found for this commission.'),
                    'type': 'info',
                }
            }

        return {
            'type': 'ir.actions.act_window',
            'name': _('Payments'),
            'res_model': 'account.payment',
            'domain': [('id', 'in', payments.ids)],
            'view_mode': 'tree,form',
        }

    def _create_purchase_order(self):
        """Create purchase order for commission (external, internal, or legacy) for verification and approval"""
        self.ensure_one()
        
        _logger.info(">>> ============ CREATING PURCHASE ORDER ============")
        _logger.info(">>> Commission Line ID: %s, Amount: %s, Partner: %s", 
                     self.id, self.commission_amount, self.partner_id.name)
        _logger.info(">>> Category: %s, Role: %s", self.commission_category, self.role)

        _logger.info(">>> Validating partner vendor status...")
        _logger.info(">>> Partner: %s (ID: %s)", self.partner_id.name, self.partner_id.id)
        _logger.info(">>> Supplier Rank: %s", self.partner_id.supplier_rank)


        # Validate partner is set as vendor
        if not self.partner_id.supplier_rank or self.partner_id.supplier_rank <= 0:
            # Auto-set as vendor if not already set
            _logger.info(">>> Auto-setting partner as vendor...")
            self.partner_id.write({'supplier_rank': 1})
            _logger.info(">>> Partner %s set as vendor (supplier_rank=1)", self.partner_id.name)

        # Get commission product
        try:
            _logger.info(">>> Getting commission product...")
            product = self.sale_order_id._get_commission_product()
            if not product:
                raise UserError(_("Could not create or find commission product"))
            _logger.info(">>> Commission product: %s (ID: %s)", product.name, product.id)
        except Exception as e:
            _logger.error(">>> Error getting commission product: %s", str(e), exc_info=True)
            raise UserError(_("Error getting commission product: %s") % str(e))

        # Get vendor reference from original sale order
        vendor_ref = self.sale_order_id.client_order_ref or self.sale_order_id.name
        _logger.info(">>> Vendor reference: %s", vendor_ref)

        # Create purchase order with comprehensive field mapping
        po_vals = {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'origin': f"Commission - {self.sale_order_id.name}",
            'partner_ref': vendor_ref,
            'date_order': fields.Datetime.now(),
            'state': 'draft',
        }
        
        # Add commission-specific fields if they exist in the model
        if hasattr(self.env['purchase.order'], 'commission_sale_order_id'):
            po_vals['commission_sale_order_id'] = self.sale_order_id.id
        
        if hasattr(self.env['purchase.order'], 'commission_line_id'):
            po_vals['commission_line_id'] = self.id
            
        if hasattr(self.env['purchase.order'], 'origin_so_id'):
            po_vals['origin_so_id'] = self.sale_order_id.id
            
        if hasattr(self.env['purchase.order'], 'notes'):
            po_vals['notes'] = f"Commission payment for {dict(self._fields['role'].selection).get(self.role)} role in sale order {self.sale_order_id.name}"

        _logger.info(">>> Creating purchase order with values: %s", po_vals)
        
        try:
            po = self.env['purchase.order'].create(po_vals)
            _logger.info(">>> Purchase order created successfully: %s (ID: %s)", po.name, po.id)
        except Exception as e:
            _logger.error(">>> Failed to create purchase order: %s", str(e), exc_info=True)
            raise

        # Create purchase order line with detailed description
        role_name = dict(self._fields['role'].selection).get(self.role, self.role)
        line_description = f"Commission Payment - {role_name} - SO: {self.sale_order_id.name}"
        
        _logger.info(">>> Creating purchase order line...")
        _logger.info(">>> Description: %s", line_description)
        
        # Get product UOM safely
        product_uom = product.uom_po_id or product.uom_id
        if not product_uom:
            # Fallback to default UOM
            _logger.warning(">>> No UOM found on product, using fallback...")
            product_uom = self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
            if not product_uom:
                raise UserError(_("No unit of measure found for commission product"))
        
        _logger.info(">>> Product UOM: %s (ID: %s)", product_uom.name, product_uom.id)

        po_line_vals = {
            'order_id': po.id,
            'product_id': product.id,
            'name': line_description,
            'product_qty': 1.0,
            'product_uom': product_uom.id,
            'price_unit': self.commission_amount,
            'date_planned': fields.Date.today(),
        }
        
        # Add taxes if they exist
        if product.supplier_taxes_id:
            po_line_vals['taxes_id'] = [(6, 0, product.supplier_taxes_id.ids)]

        _logger.info(">>> Creating PO line with values: %s", po_line_vals)
        
        try:
            po_line = self.env['purchase.order.line'].create(po_line_vals)
            _logger.info(">>> Purchase order line created successfully (ID: %s)", po_line.id)
        except Exception as e:
            _logger.error(">>> Failed to create purchase order line: %s", str(e), exc_info=True)
            # Clean up the PO if line creation fails
            try:
                po.unlink()
            except:
                pass
            raise
        
        # Link the commission line to the purchase order and line
        _logger.info(">>> Linking commission line to purchase order...")
        try:
            self.write({
                'purchase_line_id': po_line.id,
                'purchase_order_id': po.id,
            })
            _logger.info(">>> Commission line linked successfully to PO %s", po.name)
        except Exception as e:
            _logger.error(">>> Failed to link commission line to PO: %s", str(e), exc_info=True)
            # Clean up PO and line if linking fails
            try:
                po_line.unlink()
                po.unlink()
            except:
                pass
            raise

        # Add message to both sale order and purchase order
        _logger.info(">>> Adding messages to sale order and purchase order...")
        try:
            self.sale_order_id.message_post(
                body=f"Purchase Order {po.name} created for {role_name} commission payment to {self.partner_id.name} (Amount: {self.commission_amount} {self.currency_id.name})"
            )
            
            po.message_post(
                body=f"Commission Purchase Order created from Sale Order {self.sale_order_id.name} for {role_name} commission payment"
            )
            _logger.info(">>> Messages posted successfully")
        except Exception as e:
            _logger.warning(">>> Could not post messages: %s", str(e))

        _logger.info(">>> ============ PO CREATION COMPLETED SUCCESSFULLY ============")
        _logger.info(">>> PO Name: %s, ID: %s, Partner: %s, Amount: %s", 
                     po.name, po.id, self.partner_id.name, self.commission_amount)

        return po

    @api.model
    def create(self, vals):
        """Override create to auto-calculate if needed"""
        record = super().create(vals)
        
        # Auto-calculate if percentage method and base amount available
        if (record.calculation_method == 'percentage' and 
            record.rate and 
            record.base_amount and 
            not record.commission_amount):
            record.commission_amount = record.base_amount * (record.rate / 100)
        
        return record

    def write(self, vals):
        """Override write to recalculate if needed"""
        result = super().write(vals)

        # Recalculate if method, base, or values changed
        if any(field in vals for field in ['calculation_method', 'calculation_base', 'rate', 'base_amount']):
            for record in self:
                if (record.calculation_method == 'percentage' and
                    record.rate and
                    record.base_amount):
                    record.commission_amount = record.base_amount * (record.rate / 100)

        # Update payment status automatically based on paid amount
        if 'paid_amount' in vals or 'commission_amount' in vals:
            for record in self:
                record._update_payment_status()

        return result

    def _update_payment_status(self):
        """Update payment status based on paid amount"""
        for record in self:
            if record.state == 'cancelled':
                record.payment_status = 'cancelled'
            elif record.paid_amount <= 0:
                record.payment_status = 'pending'
            elif record.paid_amount >= record.commission_amount:
                record.payment_status = 'paid'
                if record.state == 'processed':
                    record.state = 'paid'
            elif record.paid_amount > 0 and record.paid_amount < record.commission_amount:
                record.payment_status = 'partial'

            # Check for overdue
            if record.expected_payment_date and record.payment_status not in ['paid', 'cancelled']:
                today = fields.Date.context_today(record)
                if today > record.expected_payment_date:
                    # Note: 'overdue' is not in the original selection, so we keep it as pending/partial
                    # But we have days_overdue field to track this
                    pass

    @api.constrains('commission_amount')
    def _check_commission_amount(self):
        """Ensure commission amount is not negative"""
        for record in self:
            if record.commission_amount < 0:
                raise ValidationError(_("Commission amount cannot be negative."))

    @api.constrains('rate')
    def _check_rate(self):
        """Ensure rate is not negative"""
        for record in self:
            if record.rate < 0:
                raise ValidationError(_("Commission rate cannot be negative."))

    @api.constrains('sale_order_line_id', 'sale_order_id')
    def _check_sale_order_line_consistency(self):
        """Ensure sale order line belongs to the selected sale order"""
        for record in self:
            if record.sale_order_line_id and record.sale_order_id:
                if record.sale_order_line_id.order_id != record.sale_order_id:
                    raise ValidationError(_("Sale order line must belong to the selected sale order."))
            elif record.sale_order_id and record.sale_order_id.order_line and not record.sale_order_line_id:
                raise ValidationError(_("A sale order line must be selected for commission calculation."))

    # SQL Constraints for data integrity
    _sql_constraints = [
        ('commission_amount_positive', 'CHECK(commission_amount >= 0)',
         'Commission amount must be positive or zero'),
        ('rate_valid', 'CHECK(rate >= 0)',
         'Commission rate must be positive or zero'),
        ('base_amount_positive', 'CHECK(base_amount >= 0)',
         'Base amount must be positive or zero'),
        ('paid_amount_valid', 'CHECK(paid_amount >= 0)',
         'Paid amount must be positive or zero'),
    ]