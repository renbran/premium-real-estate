# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # UAE Specific Fields
    joining_date = fields.Date(string='Joining Date', required=True, 
                             help='Date when the employee joined the company')
    visa_expiry_date = fields.Date(string='Visa Expiry Date')
    passport_expiry_date = fields.Date(string='Passport Expiry Date')
    emirates_id = fields.Char(string='Emirates ID')
    emirates_id_expiry_date = fields.Date(string='Emirates ID Expiry Date')
    is_uae_national = fields.Boolean(string='Is UAE National')
    country_id = fields.Many2one('res.country', string='Home Country', 
                                help='Employee\'s home country for air ticket purposes')

    # Annual Benefits
    annual_air_ticket = fields.Boolean(string='Eligible for Annual Air Ticket')
    air_ticket_amount = fields.Float(string='Air Ticket Amount')
    air_ticket_frequency = fields.Selection([
        ('yearly', 'Yearly'),
        ('two_yearly', 'Every Two Years')
    ], string='Air Ticket Frequency', default='yearly')
    last_ticket_date = fields.Date(string='Last Air Ticket Date')
    next_ticket_date = fields.Date(string='Next Air Ticket Date', compute='_compute_next_ticket_date', store=True)

    # Leave Benefits
    annual_leave_days = fields.Float(string='Annual Leave Days', default=30)
    annual_leave_salary_type = fields.Selection([
        ('basic', 'Basic Salary'),
        ('gross', 'Gross Salary')
    ], string='Annual Leave Salary Calculation', default='basic')
    
    # Agent Commission
    is_agent = fields.Boolean(string='Is Agent')
    agent_type = fields.Selection([
        ('primary', 'Primary Agent'),
        ('secondary', 'Secondary Agent'),
        ('exclusive_rm', 'Exclusive Agent (RM)'),
        ('exclusive_sm', 'Exclusive Agent (SM)'),
    ], string='Agent Type')
    # Commission percentages for each agent type
    primary_agent_commission = fields.Float(string='Primary Agent Commission %', digits=(5, 2), default=55.0)
    secondary_agent_commission = fields.Float(string='Secondary Agent Commission %', digits=(5, 2), default=45.0)
    exclusive_rm_commission = fields.Float(string='Exclusive RM Commission %', digits=(5, 2), default=5.0)
    exclusive_sm_commission = fields.Float(string='Exclusive SM Commission %', digits=(5, 2), default=2.0)

    # Commission rates for business and personal leads
    primary_agent_business_commission = fields.Float(string='Primary Agent Business Lead %', digits=(5, 2), default=40.0)
    primary_agent_personal_commission = fields.Float(string='Primary Agent Personal Lead %', digits=(5, 2), default=60.0)
    secondary_agent_business_commission = fields.Float(string='Secondary Agent Business Lead %', digits=(5, 2), default=40.0)
    secondary_agent_personal_commission = fields.Float(string='Secondary Agent Personal Lead %', digits=(5, 2), default=60.0)

    @api.depends('last_ticket_date', 'air_ticket_frequency')
    def _compute_next_ticket_date(self):
        for employee in self:
            if employee.last_ticket_date:
                if employee.air_ticket_frequency == 'yearly':
                    employee.next_ticket_date = employee.last_ticket_date + relativedelta(years=1)
                else:
                    employee.next_ticket_date = employee.last_ticket_date + relativedelta(years=2)
            else:
                employee.next_ticket_date = False

    def calculate_leave_salary(self, days):
        """Calculate leave salary based on UAE labor law"""
        self.ensure_one()
        if self.annual_leave_salary_type == 'basic':
            daily_rate = self.contract_id.wage / 30
        else:
            # Include allowances for gross calculation
            daily_rate = (self.contract_id.wage + self.contract_id.allowances) / 30
        return daily_rate * days
