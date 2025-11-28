# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta

class UAELeaveAllocation(models.Model):
    _name = 'uae.leave.allocation'
    _description = 'UAE Leave Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    leave_type_id = fields.Many2one('uae.leave.type', string='Leave Type', required=True)
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    number_of_days = fields.Float(string='Number of Days', compute='_compute_number_of_days', store=True)
    payment_amount = fields.Float(string='Payment Amount', compute='_compute_payment_amount', store=True)
    notes = fields.Text(string='Notes')
    
    @api.depends('date_from', 'date_to')
    def _compute_number_of_days(self):
        for record in self:
            if record.date_from and record.date_to:
                record.number_of_days = (record.date_to - record.date_from).days + 1
            else:
                record.number_of_days = 0
                
    @api.depends('leave_type_id', 'number_of_days')
    def _compute_payment_amount(self):
        for record in self:
            if record.leave_type_id.payment_type == 'full':
                record.payment_amount = record.number_of_days * record.employee_id.contract_id.wage / 30
            elif record.leave_type_id.payment_type == 'split':
                full_days = min(record.number_of_days, record.leave_type_id.full_pay_days)
                remaining_days = record.number_of_days - full_days
                half_days = min(remaining_days, record.leave_type_id.half_pay_days)
                
                daily_wage = record.employee_id.contract_id.wage / 30
                record.payment_amount = (full_days * daily_wage) + (half_days * daily_wage * 0.5)
            else:
                record.payment_amount = 0
                
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('uae.leave.allocation') or _('New')
        return super(UAELeaveAllocation, self).create(vals)
    
    def action_confirm(self):
        self.write({'state': 'confirm'})
        
    def action_validate(self):
        self.ensure_one()
        # Check maximum days allowed
        if self.number_of_days > self.leave_type_id.max_days:
            raise UserError(_('Maximum allowed days for this leave type is %s') % self.leave_type_id.max_days)
        
        # Check for UAE nationals only leaves
        if self.leave_type_id.for_uae_national_only and not self.employee_id.is_uae_national:
            raise UserError(_('This leave type is only available for UAE nationals'))
            
        self.write({'state': 'validate'})
        
    def action_refuse(self):
        self.write({'state': 'refuse'})
        
    def action_cancel(self):
        self.write({'state': 'cancel'})
