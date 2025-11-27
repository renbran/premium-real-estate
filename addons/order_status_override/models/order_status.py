# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OrderStatus(models.Model):
    _name = 'order.status'
    _description = 'Custom Order Status'
    _order = 'sequence, id'
    
    name = fields.Char(string='Status Name', required=True)
    code = fields.Char(string='Status Code', required=True, help="Unique code for this status")
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    is_initial = fields.Boolean(string='Is Initial Status', default=False)
    is_final = fields.Boolean(string='Is Final Status', default=False)
    next_status_ids = fields.Many2many('order.status', 
                                    'order_status_next_rel', 
                                    'status_id', 
                                    'next_status_id', 
                                    string='Next Statuses')
    responsible_type = fields.Selection([
        ('none', 'No Assignment'),
        ('documentation', 'Documentation User'),
        ('commission', 'Commission User'),
        ('final_review', 'Final Review User'),
    ], string='Responsible Type', default='none')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')
    
    _sql_constraints = [
        ('unique_initial_status', 'UNIQUE(is_initial) WHERE is_initial = True', 
         'There can only be one initial status!'),
        ('unique_code', 'UNIQUE(code)', 'Status code must be unique!'),
    ]
    
    @api.constrains('is_initial', 'is_final')
    def _check_initial_final(self):
        for status in self:
            if status.is_initial and status.is_final:
                raise UserError(_("A status cannot be both initial and final."))

class OrderStatusHistory(models.Model):
    _name = 'order.status.history'
    _description = 'Order Status History'
    _order = 'create_date desc'
    
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    status_id = fields.Many2one('order.status', string='Status', required=True)
    previous_status_id = fields.Many2one('order.status', string='Previous Status')
    user_id = fields.Many2one('res.users', string='Changed By', 
                            default=lambda self: self.env.user.id, readonly=True)
    notes = fields.Text(string='Notes')
    create_date = fields.Datetime(string='Date Changed', readonly=True)