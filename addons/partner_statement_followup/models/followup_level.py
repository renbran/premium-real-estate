# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FollowupLevel(models.Model):
    _name = 'followup.level'
    _description = 'Follow-up Level'
    _order = 'sequence, id'

    name = fields.Char(string='Level Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    days = fields.Integer(string='Days after due date', required=True, default=1,
                         help="Number of days after due date to trigger this follow-up level")
    delay_days = fields.Integer(string='Delay Days', required=True, default=1,
                               help="Number of days after due date (alias for days)")
    description = fields.Text(string='Follow-up Description')
    email_template_id = fields.Many2one('mail.template', string='Email Template')
    send_email = fields.Boolean(string='Send Email', default=True)
    send_letter = fields.Boolean(string='Print Letter', default=False)
    manual_action = fields.Boolean(string='Manual Action Required', default=False)
    manual_action_note = fields.Text(string='Manual Action Note')
    active = fields.Boolean(string='Active', default=True)
    
    # Email template fields from demo data
    email_subject = fields.Char(string='Email Subject')
    email_body = fields.Html(string='Email Body')
    
    @api.constrains('days', 'delay_days')
    def _check_days(self):
        for record in self:
            if record.days < 0 or record.delay_days < 0:
                raise ValueError("Days must be positive")
                
    @api.model
    def create(self, vals):
        # Sync days and delay_days fields
        if 'delay_days' in vals and 'days' not in vals:
            vals['days'] = vals['delay_days']
        elif 'days' in vals and 'delay_days' not in vals:
            vals['delay_days'] = vals['days']
        return super().create(vals)
        
    def write(self, vals):
        # Sync days and delay_days fields
        if 'delay_days' in vals and 'days' not in vals:
            vals['days'] = vals['delay_days']
        elif 'days' in vals and 'delay_days' not in vals:
            vals['delay_days'] = vals['days']
        return super().write(vals)