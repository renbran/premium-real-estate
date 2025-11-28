# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrAgentCommission(models.Model):
    _name = 'hr.agent.commission'
    _description = 'Agent Commission Settings'
    _rec_name = 'property_type'

    agent_id = fields.Many2one('hr.employee', string='Agent', required=True,
                              domain=[('is_agent', '=', True)])
    property_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    ], string='Property Type', required=True)
    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string='Commission Type', default='percentage')
    commission_percentage = fields.Float(string='Commission %', digits=(5, 2))
    fixed_amount = fields.Float(string='Fixed Amount')
    
    # Add agent_type for clarity and filtering
    agent_type = fields.Selection([
        ('primary', 'Primary Agent'),
        ('secondary', 'Secondary Agent'),
        ('exclusive_rm', 'Exclusive Agent (RM)'),
        ('exclusive_sm', 'Exclusive Agent (SM)'),
    ], string='Agent Type', related='agent_id.agent_type', store=True, readonly=True)

    _sql_constraints = [
        ('unique_agent_property_type', 'unique(agent_id, property_type)',
         'Commission settings already exist for this agent and property type!')
    ]

    @api.onchange('agent_id')
    def _onchange_agent_id(self):
        if self.agent_id and self.commission_type == 'percentage':
            # Set commission based on agent type
            if self.agent_id.agent_type == 'primary':
                self.commission_percentage = self.agent_id.primary_agent_commission
            elif self.agent_id.agent_type == 'secondary':
                self.commission_percentage = self.agent_id.secondary_agent_commission
            elif self.agent_id.agent_type == 'exclusive_rm':
                self.commission_percentage = self.agent_id.exclusive_rm_commission
            elif self.agent_id.agent_type == 'exclusive_sm':
                self.commission_percentage = self.agent_id.exclusive_sm_commission
