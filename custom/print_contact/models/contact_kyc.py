# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Personal Information
    x_date_of_birth = fields.Date(string='Date of Birth')
    x_place_of_birth = fields.Char(string='Place of Birth')
    x_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    x_aliases = fields.Char(string='Aliases')

    # Passport Information
    x_passport_number = fields.Char(string='Passport Number')
    x_passport_country_id = fields.Many2one('res.country', string='Passport Country of Issue')
    x_passport_issue_date = fields.Date(string='Passport Issue Date')
    x_passport_expiry_date = fields.Date(string='Passport Expiry Date')

    # UAE Residency
    x_residency_visa_no = fields.Char(string='Residency Visa Number')
    x_emirates_id = fields.Char(string='Emirates ID Number')
    x_residency_expiry_date = fields.Date(string='Residency Expiry Date')

    # Employment Details
    x_years_in_role = fields.Integer(string='Years in Present Role')
    x_employer_address = fields.Text(string='Employer Address')

    # Financial Information
    x_source_of_funds = fields.Many2many(
        'kyc.source.funds',
        'partner_source_funds_rel',
        'partner_id',
        'source_id',
        string='Source of Funds'
    )
    x_source_of_wealth = fields.Many2many(
        'kyc.source.wealth',
        'partner_source_wealth_rel',
        'partner_id',
        'source_id',
        string='Source of Wealth'
    )
    x_annual_income = fields.Monetary(string='Annual Income')
    x_purpose_of_purchase = fields.Selection([
        ('end_use', 'End Use'),
        ('savings', 'Savings'),
        ('investment', 'Investment'),
        ('other', 'Other')
    ], string='Purpose of Purchase')
    x_payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('mortgage', 'Mortgage'),
        ('crypto', 'Crypto'),
        ('other', 'Other')
    ], string='Payment Method')
    x_politically_exposed_person = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('other', 'Other')
    ], string='Politically Exposed Person')

class KycSourceFunds(models.Model):
    _name = 'kyc.source.funds'
    _description = 'KYC Source of Funds'

    name = fields.Char(string='Source', required=True)

class KycSourceWealth(models.Model):
    _name = 'kyc.source.wealth'
    _description = 'KYC Source of Wealth'

    name = fields.Char(string='Source', required=True)