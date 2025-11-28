# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StatementConfigAlias(models.Model):
    """Alias model for statement.config references"""
    _name = 'statement.config'
    _description = 'Statement Configuration (Alias)'
    _order = 'name, id'

    name = fields.Char(string='Configuration Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    
    # Ageing bucket fields (referenced in XML data)
    ageing_bucket_1 = fields.Integer(string='Ageing Bucket 1 (Days)', default=30)
    ageing_bucket_2 = fields.Integer(string='Ageing Bucket 2 (Days)', default=60)
    ageing_bucket_3 = fields.Integer(string='Ageing Bucket 3 (Days)', default=90)
    ageing_bucket_4 = fields.Integer(string='Ageing Bucket 4 (Days)', default=120)
    
    # Basic statement settings (referenced in XML data)
    include_zero_balance = fields.Boolean(string='Include Zero Balance', default=False)
    show_credit_balance = fields.Boolean(string='Show Credit Balance', default=True)
    currency_format = fields.Selection([
        ('symbol_before', 'Symbol Before'),
        ('symbol_after', 'Symbol After'),
        ('code_before', 'Code Before'),
        ('code_after', 'Code After')
    ], string='Currency Format', default='symbol_before')
    date_format = fields.Selection([
        ('dd/mm/yyyy', 'DD/MM/YYYY'),
        ('mm/dd/yyyy', 'MM/DD/YYYY'),
        ('yyyy-mm-dd', 'YYYY-MM-DD'),
        ('dd-mm-yyyy', 'DD-MM-YYYY')
    ], string='Date Format', default='dd/mm/yyyy')
    statement_footer = fields.Text(string='Statement Footer', 
                                  default='Thank you for your business. Please contact us if you have any questions about this statement.')
    
    # Follow-up settings (referenced in XML data)
    auto_followup = fields.Boolean(string='Auto Follow-up', default=True)
    followup_interval = fields.Integer(string='Follow-up Interval (Days)', default=7)
    
    # Additional fields referenced in demo data
    frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Frequency', default='monthly')
    auto_send = fields.Boolean(string='Auto Send', default=False)
    email_template_id = fields.Many2one('mail.template', string='Email Template')
    include_ageing = fields.Boolean(string='Include Ageing Analysis', default=True)
    filter_by = fields.Selection([
        ('all', 'All Partners'),
        ('customers', 'Customers Only'),
        ('suppliers', 'Suppliers Only')
    ], string='Filter By', default='customers')
    exclude_zero_balance = fields.Boolean(string='Exclude Zero Balance', default=True)
    
    # Legacy fields for compatibility
    aging_bucket_ids = fields.One2many('statement.ageing.period', 'config_id', 
                                     string='Aging Buckets')
    
    # Additional fields that might be referenced
    statement_format = fields.Selection([
        ('standard', 'Standard'),
        ('detailed', 'Detailed'),
        ('summary', 'Summary')
    ], string='Statement Format', default='standard')
    
    show_aging = fields.Boolean(string='Show Aging Analysis', default=True)
    show_payments = fields.Boolean(string='Show Payments', default=True)

class FollowupHistoryAlias(models.Model):
    """Alias model for followup.history references"""
    _name = 'followup.history'
    _description = 'Follow-up History (Alias)'
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date = fields.Date(string='Follow-up Date', required=True)
    level_id = fields.Many2one('followup.level', string='Follow-up Level')
    user_id = fields.Many2one('res.users', string='Responsible User')
    description = fields.Text(string='Notes')
    email_sent = fields.Boolean(string='Email Sent', default=False)
    letter_printed = fields.Boolean(string='Letter Printed', default=False)
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)

class BatchFollowupConfig(models.Model):
    """Model for batch.followup.config references"""
    _name = 'batch.followup.config'
    _description = 'Batch Follow-up Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    schedule_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], string='Schedule Type', default='weekly')
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)

class ReportConfig(models.Model):
    """Model for report.config references"""
    _name = 'report.config'
    _description = 'Report Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    report_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Report Type', default='monthly')
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
