from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BrokerCommissionInvoice(models.Model):
    _name = 'broker.commission.invoice'
    _description = 'Broker Commission Invoice'
    _order = 'create_date desc, id desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    property_sale_id = fields.Many2one('property.sale', string="Property Sale", required=True, ondelete='cascade', index=True, tracking=True)
    seller_id = fields.Many2one('res.partner', string="Seller/Broker", required=True, domain=[('is_company', '=', True)], tracking=True)
    commission_percentage = fields.Float(string="Commission Percentage", digits=(5, 2), tracking=True)
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(related='property_sale_id.currency_id', string="Currency", readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    invoice_ids = fields.One2many('account.move', 'broker_commission_id', string="Invoices", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string="State", default='draft', tracking=True)
    display_name = fields.Char(string="Reference", compute='_compute_display_name', store=True)
    total_invoiced = fields.Monetary(string="Invoiced Amount", compute="_compute_payment_info", store=True, currency_field='currency_id')
    total_paid = fields.Monetary(string="Paid Amount", compute="_compute_payment_info", store=True, currency_field='currency_id')
    payment_progress = fields.Float(string="Payment Progress (%)", compute="_compute_payment_info", store=True)
    payment_state = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid')
    ], string="Payment Status", compute="_compute_payment_info", store=True)

    @api.depends('property_sale_id', 'seller_id', 'create_date')
    def _compute_display_name(self):
        for record in self:
            if record.property_sale_id and record.seller_id:
                record.display_name = f"COM/{record.property_sale_id.name}/{record.seller_id.name}"
            else:
                record.display_name = f"New Commission {record.id or ''}"

    @api.depends('invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _compute_payment_info(self):
        for record in self:
            total = sum(record.invoice_ids.mapped('amount_total'))
            paid = sum(invoice.amount_total - invoice.amount_residual for invoice in record.invoice_ids)
            record.total_invoiced = total
            record.total_paid = paid
            record.payment_progress = round((paid / total) * 100, 2) if total else 0.0
            if not record.invoice_ids:
                record.payment_state = 'not_invoiced'
            elif all(inv.payment_state == 'paid' for inv in record.invoice_ids):
                record.payment_state = 'paid'
            elif any(inv.payment_state in ['partial', 'in_payment'] for inv in record.invoice_ids):
                record.payment_state = 'partial'
            else:
                record.payment_state = 'not_invoiced'

    def action_confirm(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'

    def action_cancel(self):
        for record in self:
            if record.state in ['draft', 'confirmed'] and not record.invoice_ids:
                record.state = 'cancelled'
            else:
                raise UserError(_("Cannot cancel a commission that has been invoiced."))

    def action_draft(self):
        for record in self:
            if record.state == 'cancelled':
                record.state = 'draft'

    def action_generate_customer_invoice(self):
        self.ensure_one()
        if not self.seller_id:
            raise UserError(_("Please specify a seller/broker before generating an invoice."))
        if not self.property_sale_id.property_id.revenue_account_id:
            raise UserError(_("No revenue account defined on the property."))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.seller_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [(0, 0, {
                'name': f"Broker Commission for {self.property_sale_id.name}",
                'quantity': 1,
                'price_unit': self.commission_amount,
                'account_id': self.property_sale_id.property_id.revenue_account_id.id,
            })],
            'broker_commission_id': self.id,
            'property_order_id': self.property_sale_id.id,
        }

        invoice = self.env['account.move'].create(invoice_vals)
        self.write({
            'invoice_ids': [(4, invoice.id)],
            'state': 'invoiced'
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'target': 'current',
        }
    
    @api.constrains('commission_percentage')
    def _check_commission_percentage(self):
        for record in self:
            if not (0 <= record.commission_percentage <= 100):
                raise UserError(_("Commission percentage must be between 0 and 100."))
    
    @api.constrains('commission_amount')
    def _check_commission_amount(self):
        for record in self:
            if record.commission_amount < 0:
                raise UserError(_("Commission amount cannot be negative."))
    
    _sql_constraints = [
        ('positive_commission', 'CHECK(commission_amount >= 0)', 'Commission amount must be positive!'),
        ('valid_commission_percentage', 'CHECK(commission_percentage >= 0 AND commission_percentage <= 100)', 'Commission percentage must be between 0 and 100!')
    ]