# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class UAELeaveType(models.Model):
    _name = 'uae.leave.type'
    _description = 'UAE Leave Types'
    _order = 'sequence'

    name = fields.Char(string='Leave Type', required=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    max_days = fields.Integer(string='Maximum Days Allowed', required=True)
    is_paid = fields.Boolean(string='Is Paid Leave', default=True)
    payment_type = fields.Selection([
        ('full', 'Full Pay'),
        ('split', 'Split Payment'),
        ('unpaid', 'Unpaid')
    ], string='Payment Type', default='full', required=True)
    
    # For split payment types
    full_pay_days = fields.Integer(string='Full Pay Days')
    half_pay_days = fields.Integer(string='Half Pay Days')
    unpaid_days = fields.Integer(string='Unpaid Days')
    
    requires_documentation = fields.Boolean(string='Requires Documentation')
    is_annual = fields.Boolean(string='Is Annual Leave Type')
    is_religious = fields.Boolean(string='Is Religious Leave')
    is_study = fields.Boolean(string='Is Study Leave')
    for_uae_national_only = fields.Boolean(string='For UAE Nationals Only')
    validity_in_months = fields.Integer(
        string='Valid Within Months', 
        help='Number of months within which the leave must be taken (e.g., 6 months for parental leave)'
    )
    
    hr_leave_type_id = fields.Many2one('hr.leave.type', string='HR Leave Type', help='Link to Odoo Time Off Type')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Leave type code must be unique!')
    ]
