# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class HRAirTicket(models.Model):
    _name = 'hr.air.ticket'
    _description = 'Employee Air Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.today)
    ticket_date = fields.Date(string='Ticket Date', required=True)
    home_country = fields.Many2one(related='employee_id.country_id', string='Home Country', store=True)
    joining_date = fields.Date(related='employee_id.joining_date', string='Joining Date', store=True)
    service_years = fields.Float(string='Years of Service', compute='_compute_service_years', store=True)
    is_eligible = fields.Boolean(string='Is Eligible', compute='_compute_eligibility', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    ticket_class = fields.Selection([
        ('economy', 'Economy'),
        ('business', 'Business'),
    ], string='Ticket Class', default='economy', required=True)
    ticket_amount = fields.Float(string='Ticket Amount')
    destination_city = fields.Char(string='Destination City', required=True)
    notes = fields.Text(string='Notes')
    
    @api.depends('joining_date', 'ticket_date')
    def _compute_service_years(self):
        for record in self:
            if record.joining_date and record.ticket_date:
                delta = relativedelta(record.ticket_date, record.joining_date)
                record.service_years = delta.years + (delta.months / 12.0)
            else:
                record.service_years = 0.0

    @api.depends('joining_date', 'ticket_date', 'employee_id.air_ticket_frequency')
    def _compute_eligibility(self):
        for record in self:
            # Check if employee has completed 1 year (or 2 years for two_yearly)
            if not record.joining_date or not record.ticket_date:
                record.is_eligible = False
                continue
            delta = relativedelta(record.ticket_date, record.joining_date)
            years = delta.years + (delta.months / 12.0)
            if record.employee_id.air_ticket_frequency == 'yearly':
                record.is_eligible = years >= 1.0
            else:  # two_yearly
                record.is_eligible = years >= 2.0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.air.ticket') or _('New')
        return super(HRAirTicket, self).create(vals)

    def action_submit(self):
        self.ensure_one()
        if not self.is_eligible:
            raise UserError(_('Employee is not eligible for air ticket at this time.'))
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
        })
        # Update employee's last ticket date
        self.employee_id.write({
            'last_ticket_date': self.ticket_date,
            'next_ticket_date': self.ticket_date + relativedelta(years=1 if self.employee_id.air_ticket_frequency == 'yearly' else 2)
        })

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
