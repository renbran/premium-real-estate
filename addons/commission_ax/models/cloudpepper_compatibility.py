from odoo import models, fields, api

class ResPartner(models.Model):
    """Extend res.partner to add missing fields for CloudPepper compatibility"""
    _inherit = 'res.partner'
    
    # Add task_count field for CloudPepper compatibility
    task_count = fields.Integer(
        string='Task Count',
        compute='_compute_task_count',
        help="Number of tasks assigned to this partner"
    )
    
    @api.depends('user_ids.task_ids')
    def _compute_task_count(self):
        """Compute task count for partner"""
        for partner in self:
            task_count = 0
            if partner.user_ids:
                # Count tasks assigned to users linked to this partner
                task_count = self.env['project.task'].search_count([
                    ('user_ids', 'in', partner.user_ids.ids)
                ])
            partner.task_count = task_count
    
    def action_view_partner_tasks(self):
        """Action to view tasks related to this partner"""
        self.ensure_one()
        action = self.env.ref('project.action_view_task').read()[0]
        
        if self.user_ids:
            domain = [('user_ids', 'in', self.user_ids.ids)]
        else:
            domain = [('id', '=', False)]  # No tasks if no users
            
        action['domain'] = domain
        action['context'] = {
            'default_partner_id': self.id,
        }
        
        return action


class CrmLead(models.Model):
    """Extend crm.lead to add missing fields for CloudPepper compatibility"""
    _inherit = 'crm.lead'
    
    # Add x_lead_id field for CloudPepper compatibility
    x_lead_id = fields.Char(
        string='External Lead ID',
        help="External system lead identifier for integration purposes"
    )
