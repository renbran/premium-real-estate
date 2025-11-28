# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Agent fields for new logic
    primary_agent_id = fields.Many2one('hr.employee', string='Primary Agent', domain=[('is_agent', '=', True), ('agent_type', '=', 'primary')])
    secondary_agent_id = fields.Many2one('hr.employee', string='Secondary Agent', domain=[('is_agent', '=', True), ('agent_type', '=', 'secondary')])
    exclusive_rm_id = fields.Many2one('hr.employee', string='Exclusive Agent (RM)', domain=[('is_agent', '=', True), ('agent_type', '=', 'exclusive_rm')])
    exclusive_sm_id = fields.Many2one('hr.employee', string='Exclusive Agent (SM)', domain=[('is_agent', '=', True), ('agent_type', '=', 'exclusive_sm')])
    # Commission fields
    primary_agent_commission = fields.Float(string='Primary Agent Commission %', digits=(5, 2), default=0.0)
    secondary_agent_commission = fields.Float(string='Secondary Agent Commission %', digits=(5, 2), default=0.0)
    exclusive_rm_commission = fields.Float(string='Exclusive RM Commission %', digits=(5, 2), default=0.0)
    exclusive_sm_commission = fields.Float(string='Exclusive SM Commission %', digits=(5, 2), default=0.0)

    @api.onchange('primary_agent_id', 'secondary_agent_id', 'exclusive_rm_id', 'exclusive_sm_id', 'source_id', 'origin', 'sale_type')
    def _onchange_agent_commission(self):
        for order in self:
            # Reset commissions
            order.primary_agent_commission = 0.0
            order.secondary_agent_commission = 0.0
            order.exclusive_rm_commission = 0.0
            order.exclusive_sm_commission = 0.0

            # Determine if it's a personal lead
            is_personal_lead = False
            if order.source_id:
                is_personal_lead = 'personal' in order.source_id.name.lower() or 'referral' in order.source_id.name.lower()
            elif order.origin:
                is_personal_lead = 'personal' in order.origin.lower() or 'referral' in order.origin.lower()

            # Assign commissions for primary and secondary agents
            if order.primary_agent_id:
                if is_personal_lead:
                    order.primary_agent_commission = order.primary_agent_id.primary_agent_personal_commission
                else:
                    order.primary_agent_commission = order.primary_agent_id.primary_agent_business_commission
            if order.secondary_agent_id:
                if is_personal_lead:
                    order.secondary_agent_commission = order.secondary_agent_id.secondary_agent_personal_commission
                else:
                    order.secondary_agent_commission = order.secondary_agent_id.secondary_agent_business_commission
            if order.exclusive_rm_id:
                order.exclusive_rm_commission = order.exclusive_rm_id.exclusive_rm_commission
            if order.exclusive_sm_id:
                order.exclusive_sm_commission = order.exclusive_sm_id.exclusive_sm_commission

    def action_confirm(self):
        for order in self:
            # Check for primary agent using either field (new logic or commission_ax)
            primary_agent = order.primary_agent_id or order.agent1_partner_id
            if not primary_agent:
                raise models.ValidationError(_('Primary Agent must be set before confirming the order.'))
            if order.secondary_agent_id and order.secondary_agent_id == order.primary_agent_id:
                raise models.ValidationError(_('Primary Agent and Secondary Agent must be different.'))
            if order.exclusive_rm_id and order.exclusive_rm_id == order.primary_agent_id:
                raise models.ValidationError(_('Primary Agent and Exclusive RM must be different.'))
            if order.exclusive_sm_id and order.exclusive_sm_id == order.primary_agent_id:
                raise models.ValidationError(_('Primary Agent and Exclusive SM must be different.'))
        return super(SaleOrder, self).action_confirm()
