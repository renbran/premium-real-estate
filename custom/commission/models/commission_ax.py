from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError

class CommissionAX(models.Model):
    _name = 'commission.ax'
    _description = 'Commission AX'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, tracking=True)
    order_id = fields.Many2one('sale.order', string='Sales Order', required=True, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    amount = fields.Monetary(string='Commission Amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)

    @api.constrains('order_id', 'invoice_id')
    def _check_order_invoice(self):
        for record in self:
            if record.order_id.state != 'sale' or record.invoice_id.state != 'posted':
                raise ValidationError(_(
                    "Commissions can only be created or calculated if the Sales Order is confirmed and the Invoice is posted."
                ))

    @api.onchange('order_id')
    def _onchange_order(self):
        if self.order_id and self.order_id.state != 'sale':
            self.state = 'draft'

    def action_confirm(self):
        for record in self:
            if record.order_id.state == 'sale' and record.invoice_id.state == 'posted':
                record.state = 'confirmed'
            else:
                raise UserError(_("Sales Order must be confirmed and Invoice must be posted to confirm the Commission."))

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'

    def action_manual_process(self):
        for record in self:
            record.action_confirm()

    def action_create_vendor_bill(self):
        for record in self:
            if record.invoice_id.state == 'paid':
                vendor_bill = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': record.order_id.partner_id.id,
                    'currency_id': record.currency_id.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': record.order_id.name,
                        'quantity': 1,
                        'price_unit': record.amount,
                    })],
                })
                vendor_bill.action_post()
            else:
                raise UserError(_("Invoice not paid, can't create vendor bill."))

class CommissionAxCron(models.Model):
    _inherit = 'commission.ax'

    def _cron_process_commissions(self):
        commissions = self.search([('state', '=', 'draft')])
        for commission in commissions:
            commission.action_confirm()

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def post(self):
        res = super(AccountPayment, self).post()
        for payment in self:
            commissions = self.env['commission.ax'].search([
                ('invoice_id', 'in', payment.invoice_ids.ids),
                ('state', '=', 'confirmed')
            ])
            for commission in commissions:
                vendor_bill = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': commission.order_id.partner_id.id,
                    'currency_id': commission.currency_id.id,
                    'invoice_line_ids': [
                        (0, 0, {
                            'name': commission.order_id.name,
                            'quantity': 1,
                            'price_unit': commission.amount
                        })
                    ]
                })
                vendor_bill.action_post()
        return res
