from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class CommissionAX(models.Model):
    """Enhanced Commission Management Model for Odoo 17"""
    _name = 'commission.ax'
    _description = 'Commission AX Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(
        string='Commission Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('commission.ax') or 'New'
    )
    
    # Core Relationships
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Customer Invoice',
        domain=[('move_type', '=', 'out_invoice')],
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )
    
    payment_ids = fields.Many2many(
        'account.payment',
        string='Payments',
        readonly=True,
        help="Payments received for the invoice"
    )
    
    # Commission Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Commission Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, required=True)
    
    commission_type = fields.Selection([
        ('manual', 'Manual Processing'),
        ('automatic', 'Automatic Processing')
    ], string='Commission Type', default='manual', tracking=True)
    
    # Financial Information
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='sale_order_id.currency_id',
        store=True
    )
    
    sale_amount = fields.Monetary(
        string='Sale Amount',
        related='sale_order_id.amount_total',
        store=True,
        currency_field='currency_id'
    )
    
    total_commission_amount = fields.Monetary(
        string='Total Commission',
        compute='_compute_commission_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    paid_amount = fields.Monetary(
        string='Paid Amount',
        compute='_compute_payment_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    outstanding_amount = fields.Monetary(
        string='Outstanding Amount',
        compute='_compute_payment_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    # Commission Vendor Bills
    vendor_bill_ids = fields.One2many(
        'account.move',
        'commission_id',
        string='Commission Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )
    
    vendor_bill_count = fields.Integer(
        string='Vendor Bills Count',
        compute='_compute_vendor_bill_count'
    )
    
    # Timestamps
    calculation_date = fields.Datetime(
        string='Calculation Date',
        readonly=True,
        tracking=True
    )
    
    confirmation_date = fields.Datetime(
        string='Confirmation Date',
        readonly=True,
        tracking=True
    )
    
    payment_date = fields.Datetime(
        string='Commission Payment Date',
        readonly=True,
        tracking=True
    )
    
    # Processing Information
    processed_by = fields.Many2one(
        'res.users',
        string='Processed By',
        readonly=True
    )
    
    auto_process_eligible = fields.Boolean(
        string='Auto Process Eligible',
        compute='_compute_auto_process_eligible',
        store=True,
        help="Indicates if this commission is eligible for automatic processing"
    )
    
    # Constraints and Validation Fields
    invoice_posted = fields.Boolean(
        string='Invoice Posted',
        compute='_compute_invoice_posted',
        store=True
    )

    @api.depends('invoice_id.state')
    def _compute_invoice_posted(self):
        for record in self:
            record.invoice_posted = record.invoice_id and record.invoice_id.state == 'posted'
    
    sale_confirmed = fields.Boolean(
        string='Sale Confirmed',
        compute='_compute_sale_confirmed',
        store=True
    )
    
    # Notes and Description
    notes = fields.Text(string='Notes')
    
    @api.depends('sale_order_id.state')
    def _compute_sale_confirmed(self):
        """Compute if sale order is confirmed"""
        for record in self:
            record.sale_confirmed = record.sale_order_id.state == 'sale'
    
    @api.depends('invoice_id.state')
    def _compute_invoice_posted(self):
        """Compute if invoice is posted"""
        for record in self:
            record.invoice_posted = record.invoice_id.state == 'posted'
    
    @api.depends('sale_confirmed', 'invoice_posted', 'state')
    def _compute_auto_process_eligible(self):
        """Compute if commission is eligible for automatic processing"""
        for record in self:
            record.auto_process_eligible = (
                record.sale_confirmed and 
                record.invoice_posted and 
                record.state == 'draft'
            )
    
    @api.depends('sale_order_id')
    def _compute_commission_amounts(self):
        """Compute total commission amounts from sale order"""
        for record in self:
            if record.sale_order_id:
                record.total_commission_amount = (
                    record.sale_order_id.total_external_commission_amount +
                    record.sale_order_id.total_internal_commission_amount
                )
            else:
                record.total_commission_amount = 0.0
    
    @api.depends('payment_ids', 'payment_ids.amount')
    def _compute_payment_amounts(self):
        """Compute payment amounts and outstanding balance"""
        for record in self:
            total_paid = sum(payment.amount for payment in record.payment_ids)
            record.paid_amount = total_paid
            record.outstanding_amount = record.sale_amount - total_paid
    
    @api.depends('vendor_bill_ids')
    def _compute_vendor_bill_count(self):
        """Compute vendor bill count"""
        for record in self:
            record.vendor_bill_count = len(record.vendor_bill_ids)
    
    @api.constrains('sale_order_id', 'invoice_id')
    def _check_order_invoice_requirements(self):
        """Validate that commission can only be created if requirements are met"""
        for record in self:
            if record.state in ['confirmed', 'paid']:
                if not record.sale_order_id or record.sale_order_id.state != 'sale':
                    raise ValidationError(
                        "Commission can only be confirmed if the Sales Order is confirmed (state = 'sale')."
                    )
                
                if not record.invoice_id or record.invoice_id.state != 'posted':
                    raise ValidationError(
                        "Commission can only be confirmed if the Invoice is posted (state = 'posted')."
                    )
    
    @api.onchange('sale_order_id')
    def _onchange_sale_order(self):
        """Update related fields when sale order changes"""
        if self.sale_order_id:
            # Find related invoice
            invoices = self.env['account.move'].search([
                ('invoice_origin', '=', self.sale_order_id.name),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted')
            ], limit=1)
            
            if invoices:
                self.invoice_id = invoices[0]
            
            # Reset state to draft if sale order is not confirmed
            if self.sale_order_id.state != 'sale':
                self.state = 'draft'
    
    @api.onchange('invoice_id')
    def _onchange_invoice(self):
        """Update payment information when invoice changes"""
        if self.invoice_id:
            # Get payments for this invoice
            payments = self.env['account.payment'].search([
                ('invoice_ids', 'in', [self.invoice_id.id])
            ])
            self.payment_ids = [(6, 0, payments.ids)]
    
    def action_calculate_commission(self):
        """Calculate commission amounts"""
        for record in self:
            if not record.sale_order_id:
                raise UserError("Sales Order is required to calculate commission.")
            
            # Trigger commission calculation on sale order
            record.sale_order_id._compute_commissions()
            
            record.write({
                'state': 'calculated',
                'calculation_date': fields.Datetime.now(),
                'processed_by': self.env.user.id
            })
            
            # Log activity
            record.message_post(
                body=f"Commission calculated. Total amount: {record.total_commission_amount}",
                message_type='notification'
            )
    
    def action_confirm_commission(self):
        """Confirm commission after validation"""
        for record in self:
            # Validate requirements
            if record.sale_order_id.state != 'sale':
                raise UserError("Sales Order must be confirmed to confirm commission.")
            
            if not record.invoice_id or record.invoice_id.state != 'posted':
                raise UserError("Invoice must be posted to confirm commission.")
            
            record.write({
                'state': 'confirmed',
                'confirmation_date': fields.Datetime.now(),
                'processed_by': self.env.user.id
            })
            
            # Create purchase orders for commissions if auto-creation is enabled
            record._create_commission_purchase_orders()
            
            # Log activity
            record.message_post(
                body="Commission confirmed and ready for payment processing.",
                message_type='notification'
            )
    
    def action_manual_process(self):
        """Manual commission processing"""
        for record in self:
            if record.state == 'draft':
                record.action_calculate_commission()
            
            if record.state == 'calculated':
                record.action_confirm_commission()
    
    def action_cancel_commission(self):
        """Cancel commission"""
        for record in self:
            # Cancel related vendor bills if any
            for vendor_bill in record.vendor_bill_ids:
                if vendor_bill.state == 'draft':
                    vendor_bill.action_cancel()
            
            # Cancel related purchase orders
            purchase_orders = self.env['purchase.order'].search([
                ('origin_so_id', '=', record.sale_order_id.id)
            ])
            for po in purchase_orders:
                if po.state in ['draft', 'sent']:
                    po.button_cancel()
            
            record.write({
                'state': 'cancelled',
                'processed_by': self.env.user.id
            })
            
            record.message_post(
                body="Commission cancelled and related documents updated.",
                message_type='notification'
            )
    
    def action_create_vendor_bill(self):
        """Create vendor bill for commission payment"""
        for record in self:
            if record.outstanding_amount <= 0:
                raise UserError("Invoice must have outstanding payment to create commission vendor bill.")
            
            if record.state != 'confirmed':
                raise UserError("Commission must be confirmed before creating vendor bills.")
            
            # Get commission partners and amounts
            commission_data = record._get_commission_data()
            
            for partner_data in commission_data:
                vendor_bill = self._create_vendor_bill_for_partner(partner_data)
                record.message_post(
                    body=f"Vendor bill {vendor_bill.name} created for {partner_data['partner'].name}",
                    message_type='notification'
                )
    
    def _get_commission_data(self):
        """Get commission data for vendor bill creation"""
        commission_data = []
        sale_order = self.sale_order_id
        
        # External commissions
        external_partners = [
            ('broker_partner_id', 'broker_amount'),
            ('referrer_partner_id', 'referrer_amount'),
            ('cashback_partner_id', 'cashback_amount'),
            ('other_external_partner_id', 'other_external_amount')
        ]
        
        for partner_field, amount_field in external_partners:
            partner = getattr(sale_order, partner_field, False)
            amount = getattr(sale_order, amount_field, 0.0)
            if partner and amount > 0:
                commission_data.append({
                    'partner': partner,
                    'amount': amount,
                    'type': 'external'
                })
        
        # Internal commissions
        internal_partners = [
            ('agent1_partner_id', 'agent1_amount'),
            ('agent2_partner_id', 'agent2_amount'),
            ('manager_partner_id', 'manager_amount'),
            ('director_partner_id', 'director_amount')
        ]
        
        for partner_field, amount_field in internal_partners:
            partner = getattr(sale_order, partner_field, False)
            amount = getattr(sale_order, amount_field, 0.0)
            if partner and amount > 0:
                commission_data.append({
                    'partner': partner,
                    'amount': amount,
                    'type': 'internal'
                })
        
        return commission_data
    
    def _create_vendor_bill_for_partner(self, partner_data):
        """Create vendor bill for specific partner"""
        vendor_bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': partner_data['partner'].id,
            'commission_id': self.id,
            'invoice_date': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'ref': f"Commission for {self.sale_order_id.name}",
            'invoice_line_ids': [(0, 0, {
                'name': f"Commission for Sale Order {self.sale_order_id.name}",
                'quantity': 1,
                'price_unit': partner_data['amount'],
                'account_id': self._get_commission_expense_account().id,
            })],
        })
        
        return vendor_bill
    
    def _get_commission_expense_account(self):
        """Get commission expense account"""
        # Try to find commission expense account
        account = self.env['account.account'].search([
            ('code', 'like', '6%'),
            ('name', 'ilike', 'commission'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not account:
            # Fallback to general expense account
            account = self.env['account.account'].search([
                ('code', 'like', '6%'),
                ('account_type', '=', 'expense'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
        
        if not account:
            raise UserError("Please configure a commission expense account.")
        
        return account
    
    def _create_commission_purchase_orders(self):
        """Create purchase orders for commission payments"""
        for record in self:
            commission_data = record._get_commission_data()
            
            for partner_data in commission_data:
                # Check if PO already exists for this partner
                existing_po = self.env['purchase.order'].search([
                    ('partner_id', '=', partner_data['partner'].id),
                    ('origin_so_id', '=', record.sale_order_id.id),
                    ('state', '!=', 'cancel')
                ], limit=1)
                
                if not existing_po:
                    record._create_purchase_order_for_partner(partner_data)
    
    def _create_purchase_order_for_partner(self, partner_data):
        """Create purchase order for specific partner commission"""
        purchase_order = self.env['purchase.order'].create({
            'partner_id': partner_data['partner'].id,
            'origin_so_id': self.sale_order_id.id,
            'currency_id': self.currency_id.id,
            'order_line': [(0, 0, {
                'name': f"Commission for {self.sale_order_id.name}",
                'product_qty': 1,
                'price_unit': partner_data['amount'],
                'date_planned': fields.Datetime.now() + timedelta(days=7),
            })],
        })
        
        self.message_post(
            body=f"Purchase order {purchase_order.name} created for {partner_data['partner'].name}",
            message_type='notification'
        )
        
        return purchase_order
    
    @api.model
    def _cron_process_commissions(self):
        """Automated commission processing via cron job"""
        _logger.info("Starting automated commission processing...")
        
        # Find eligible commissions for automatic processing
        eligible_commissions = self.search([
            ('state', '=', 'draft'),
            ('commission_type', '=', 'automatic'),
            ('auto_process_eligible', '=', True)
        ])
        
        processed_count = 0
        for commission in eligible_commissions:
            try:
                commission.action_manual_process()
                processed_count += 1
                _logger.info(f"Automatically processed commission {commission.name}")
            except Exception as e:
                _logger.error(f"Failed to process commission {commission.name}: {str(e)}")
                commission.message_post(
                    body=f"Automatic processing failed: {str(e)}",
                    message_type='notification'
                )
        
        _logger.info(f"Automated commission processing completed. Processed {processed_count} commissions.")
        return processed_count
    
    def action_view_vendor_bills(self):
        """Action to view vendor bills"""
        action = self.env.ref('account.action_vendor_bill_template').read()[0]
        if len(self.vendor_bill_ids) > 1:
            action['domain'] = [('id', 'in', self.vendor_bill_ids.ids)]
        elif len(self.vendor_bill_ids) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.vendor_bill_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_view_sale_order(self):
        """Action to view related sale order"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }
    
    def action_view_invoice(self):
        """Action to view related invoice"""
        if self.invoice_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.invoice_id.id,
                'target': 'current',
            }
        
    @api.model
    def create(self, vals):
        """Override create to set sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('commission.ax') or 'New'
        return super(CommissionAX, self).create(vals)


class AccountMove(models.Model):
    """Extend Account Move for commission integration"""
    _inherit = 'account.move'
    
    commission_id = fields.Many2one(
        'commission.ax',
        string='Related Commission',
        help="Commission record related to this vendor bill"
    )


class AccountPayment(models.Model):
    """Extend Account Payment for automatic commission processing"""
    _inherit = 'account.payment'
    
    def action_post(self):
        """Override post to trigger commission vendor bill creation"""
        res = super(AccountPayment, self).action_post()
        
        for payment in self:
            # Find related commissions
            commissions = self.env['commission.ax'].search([
                ('invoice_id', 'in', payment.invoice_ids.ids),
                ('state', '=', 'confirmed')
            ])
            
            for commission in commissions:
                # Update payment information
                commission._onchange_invoice()
                
                # Auto-create vendor bills if enabled
                if commission.commission_type == 'automatic':
                    try:
                        commission.action_create_vendor_bill()
                        commission.write({
                            'state': 'paid',
                            'payment_date': fields.Datetime.now()
                        })
                    except Exception as e:
                        _logger.error(f"Failed to auto-create vendor bill for commission {commission.name}: {str(e)}")
        
        return res
