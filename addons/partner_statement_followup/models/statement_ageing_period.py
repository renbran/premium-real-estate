# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StatementAgeingPeriod(models.Model):
    _name = 'statement.ageing.period'
    _description = 'Statement Ageing Period'
    _order = 'sequence, id'

    name = fields.Char(string='Period Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    date_from = fields.Integer(string='From (days)', default=0,
                              help="Number of days from due date (negative for overdue)")
    date_to = fields.Integer(string='To (days)', default=0,
                            help="Number of days to due date (negative for overdue)")
    # XML data uses days_from and days_to, so add these as aliases
    days_from = fields.Integer(string='Days From', default=0,
                              help="Number of days from due date (alias for date_from)")
    days_to = fields.Integer(string='Days To', default=0,
                            help="Number of days to due date (alias for date_to)")
    color = fields.Char(string='Color', help="Color code for this ageing period")
    active = fields.Boolean(string='Active', default=True)
    config_id = fields.Many2one('statement.config', string='Configuration', 
                               ondelete='cascade')

    @api.constrains('date_from', 'date_to', 'days_from', 'days_to')
    def _check_date_range(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValueError("From date must be less than or equal to To date")
            if record.days_from > record.days_to:
                raise ValueError("Days from must be less than or equal to Days to")
                
    @api.model
    def create(self, vals):
        # Sync days_from/days_to with date_from/date_to
        if 'days_from' in vals and 'date_from' not in vals:
            vals['date_from'] = vals['days_from']
        elif 'date_from' in vals and 'days_from' not in vals:
            vals['days_from'] = vals['date_from']
            
        if 'days_to' in vals and 'date_to' not in vals:
            vals['date_to'] = vals['days_to']
        elif 'date_to' in vals and 'days_to' not in vals:
            vals['days_to'] = vals['date_to']
            
        return super().create(vals)
        
    def write(self, vals):
        # Sync days_from/days_to with date_from/date_to
        if 'days_from' in vals and 'date_from' not in vals:
            vals['date_from'] = vals['days_from']
        elif 'date_from' in vals and 'days_from' not in vals:
            vals['days_from'] = vals['date_from']
            
        if 'days_to' in vals and 'date_to' not in vals:
            vals['date_to'] = vals['days_to']
        elif 'date_to' in vals and 'days_to' not in vals:
            vals['days_to'] = vals['date_to']
            
        return super().write(vals)

class AgeingPeriod(models.Model):
    """Alias model for ageing.period references"""
    _name = 'ageing.period'
    _description = 'Ageing Period (Alias)'
    _order = 'sequence, id'

    name = fields.Char(string='Period Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    date_from = fields.Integer(string='From (days)', default=0)
    date_to = fields.Integer(string='To (days)', default=0)
    days_from = fields.Integer(string='Days From', default=0)
    days_to = fields.Integer(string='Days To', default=0)
    is_current = fields.Boolean(string='Is Current Period', default=False)
    active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def create(self, vals):
        # Sync days_from/days_to with date_from/date_to
        if 'days_from' in vals and 'date_from' not in vals:
            vals['date_from'] = vals['days_from']
        elif 'date_from' in vals and 'days_from' not in vals:
            vals['days_from'] = vals['date_from']
            
        if 'days_to' in vals and 'date_to' not in vals:
            vals['date_to'] = vals['days_to']
        elif 'date_to' in vals and 'days_to' not in vals:
            vals['days_to'] = vals['date_to']
            
        return super().create(vals)
        
    def write(self, vals):
        # Sync days_from/days_to with date_from/date_to
        if 'days_from' in vals and 'date_from' not in vals:
            vals['date_from'] = vals['days_from']
        elif 'date_from' in vals and 'days_from' not in vals:
            vals['days_from'] = vals['date_from']
            
        if 'days_to' in vals and 'date_to' not in vals:
            vals['date_to'] = vals['days_to']
        elif 'date_to' in vals and 'days_to' not in vals:
            vals['days_to'] = vals['date_to']
            
        return super().write(vals)