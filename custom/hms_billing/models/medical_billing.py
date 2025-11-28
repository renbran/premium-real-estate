# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError


class MedicalBilling(models.Model):
    _name = 'medical.billing'
    _description = 'Medical Billing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'billing_date desc'

    name = fields.Char('Billing Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', related='patient_id.patient_id', string='Partner', store=True)
    doctor_id = fields.Many2one('medical.physician', 'Doctor', tracking=True)
    appointment_id = fields.Many2one('medical.appointment', 'Appointment')
    billing_date = fields.Date('Billing Date', required=True, default=fields.Date.today)
    due_date = fields.Date('Due Date', required=True)
    
    # Billing Items
    billing_line_ids = fields.One2many('medical.billing.line', 'billing_id', 'Billing Lines')
    
    # Financial Information
    subtotal_amount = fields.Monetary('Subtotal', compute='_compute_amounts', store=True, currency_field='currency_id')
    tax_amount = fields.Monetary('Tax Amount', compute='_compute_amounts', store=True, currency_field='currency_id')
    discount_amount = fields.Monetary('Discount', currency_field='currency_id')
    total_amount = fields.Monetary('Total Amount', compute='_compute_amounts', store=True, currency_field='currency_id')
    paid_amount = fields.Monetary('Paid Amount', compute='_compute_paid_amount', store=True, currency_field='currency_id')
    remaining_amount = fields.Monetary('Remaining Amount', compute='_compute_paid_amount', store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)
    
    # Insurance Information
    insurance_id = fields.Many2one('medical.insurance', 'Insurance')
    insurance_coverage_percent = fields.Float('Insurance Coverage %')
    insurance_amount = fields.Monetary('Insurance Amount', compute='_compute_insurance_amount', store=True, currency_field='currency_id')
    patient_responsibility = fields.Monetary('Patient Responsibility', compute='_compute_insurance_amount', store=True, currency_field='currency_id')
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('cancel', 'Cancelled'),
    ], 'Status', default='draft', tracking=True)
    
    # Payment Information
    payment_ids = fields.One2many('medical.payment', 'billing_id', 'Payments')
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ], 'Payment Method')
    
    # Additional Information
    notes = fields.Text('Notes')
    internal_notes = fields.Text('Internal Notes')
    
    # Invoice Integration
    invoice_id = fields.Many2one('account.move', 'Invoice')
    invoice_status = fields.Selection(related='invoice_id.state', string='Invoice Status')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.billing') or _('New')
        return super(MedicalBilling, self).create(vals)

    @api.depends('billing_line_ids.total_amount', 'discount_amount')
    def _compute_amounts(self):
        for billing in self:
            subtotal = sum(line.total_amount for line in billing.billing_line_ids)
            billing.subtotal_amount = subtotal
            billing.tax_amount = sum(line.tax_amount for line in billing.billing_line_ids)
            billing.total_amount = subtotal + billing.tax_amount - billing.discount_amount

    @api.depends('payment_ids.amount')
    def _compute_paid_amount(self):
        for billing in self:
            paid = sum(payment.amount for payment in billing.payment_ids if payment.state == 'posted')
            billing.paid_amount = paid
            billing.remaining_amount = billing.total_amount - paid
            
            if billing.remaining_amount <= 0:
                billing.state = 'paid'
            elif billing.paid_amount > 0:
                billing.state = 'partial'

    @api.depends('total_amount', 'insurance_coverage_percent')
    def _compute_insurance_amount(self):
        for billing in self:
            if billing.insurance_id and billing.insurance_coverage_percent:
                billing.insurance_amount = billing.total_amount * (billing.insurance_coverage_percent / 100)
                billing.patient_responsibility = billing.total_amount - billing.insurance_amount
            else:
                billing.insurance_amount = 0
                billing.patient_responsibility = billing.total_amount

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        return True

    def action_send(self):
        self.write({'state': 'sent'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def action_create_invoice(self):
        """Create invoice from billing"""
        if self.invoice_id:
            raise UserError(_('Invoice already exists for this billing.'))
        
        invoice_lines = []
        for line in self.billing_line_ids:
            invoice_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.description,
                'quantity': line.quantity,
                'price_unit': line.unit_price,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
            }))
        
        invoice_vals = {
            'partner_id': self.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': self.billing_date,
            'invoice_date_due': self.due_date,
            'invoice_line_ids': invoice_lines,
            'ref': self.name,
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }


class MedicalBillingLine(models.Model):
    _name = 'medical.billing.line'
    _description = 'Medical Billing Line'

    billing_id = fields.Many2one('medical.billing', 'Billing', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Service/Product', required=True)
    description = fields.Text('Description')
    quantity = fields.Float('Quantity', default=1.0)
    unit_price = fields.Monetary('Unit Price', currency_field='currency_id')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    tax_amount = fields.Monetary('Tax Amount', compute='_compute_tax_amount', store=True, currency_field='currency_id')
    total_amount = fields.Monetary('Total', compute='_compute_total', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='billing_id.currency_id', store=True)

    @api.depends('quantity', 'unit_price', 'tax_ids')
    def _compute_tax_amount(self):
        for line in self:
            if line.tax_ids:
                tax_result = line.tax_ids.compute_all(
                    line.unit_price, 
                    line.currency_id, 
                    line.quantity, 
                    product=line.product_id, 
                    partner=line.billing_id.partner_id
                )
                line.tax_amount = sum(t.get('amount', 0.0) for t in tax_result['taxes'])
            else:
                line.tax_amount = 0.0

    @api.depends('quantity', 'unit_price', 'tax_amount')
    def _compute_total(self):
        for line in self:
            line.total_amount = (line.quantity * line.unit_price) + line.tax_amount

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.unit_price = self.product_id.list_price
            self.tax_ids = self.product_id.taxes_id