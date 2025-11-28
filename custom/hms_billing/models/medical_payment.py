# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError


class MedicalPayment(models.Model):
    _name = 'medical.payment'
    _description = 'Medical Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payment_date desc'

    name = fields.Char('Payment Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    billing_id = fields.Many2one('medical.billing', 'Billing', required=True)
    patient_id = fields.Many2one('medical.patient', related='billing_id.patient_id', string='Patient', store=True)
    partner_id = fields.Many2one('res.partner', related='billing_id.partner_id', string='Partner', store=True)
    
    payment_date = fields.Date('Payment Date', required=True, default=fields.Date.today)
    amount = fields.Monetary('Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='billing_id.currency_id', store=True)
    
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ], 'Payment Method', required=True)
    
    reference = fields.Char('Reference/Check Number')
    notes = fields.Text('Notes')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], 'Status', default='draft', tracking=True)
    
    journal_id = fields.Many2one('account.journal', 'Journal')
    move_id = fields.Many2one('account.move', 'Journal Entry')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.payment') or _('New')
        return super(MedicalPayment, self).create(vals)

    def action_post(self):
        """Post the payment"""
        self.write({'state': 'posted'})
        # Optionally create accounting entries
        self._create_account_move()
        return True

    def action_cancel(self):
        """Cancel the payment"""
        self.write({'state': 'cancelled'})
        if self.move_id:
            self.move_id.button_cancel()
        return True

    def _create_account_move(self):
        """Create accounting entry for the payment"""
        if not self.journal_id:
            return
        
        move_lines = []
        # Debit line (Cash/Bank account)
        move_lines.append((0, 0, {
            'name': f'Payment for {self.billing_id.name}',
            'debit': self.amount,
            'credit': 0,
            'account_id': self.journal_id.default_account_id.id,
            'partner_id': self.partner_id.id,
        }))
        
        # Credit line (Accounts Receivable)
        receivable_account = self.partner_id.property_account_receivable_id
        move_lines.append((0, 0, {
            'name': f'Payment for {self.billing_id.name}',
            'debit': 0,
            'credit': self.amount,
            'account_id': receivable_account.id,
            'partner_id': self.partner_id.id,
        }))
        
        move_vals = {
            'journal_id': self.journal_id.id,
            'date': self.payment_date,
            'ref': self.name,
            'line_ids': move_lines,
        }
        
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        self.move_id = move.id


class MedicalPaymentMethod(models.Model):
    _name = 'medical.payment.method'
    _description = 'Medical Payment Method'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal')
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)