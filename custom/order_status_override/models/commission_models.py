from odoo import models, fields, api

class CommissionExternal(models.Model):
    """External Commission model for commission_ax integration compatibility"""
    _name = 'commission.external'
    _description = 'External Commission'
    
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    amount_fixed = fields.Float(string='Commission Amount', default=0.0)
    percentage = fields.Float(string='Commission Percentage', default=0.0)
    partner_id = fields.Many2one('res.partner', string='Commission Partner')
    date = fields.Date(string='Commission Date', default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('paid', 'Paid')
    ], string='State', default='draft')

class CommissionInternal(models.Model):
    """Internal Commission model for commission_ax integration compatibility"""
    _name = 'commission.internal'
    _description = 'Internal Commission'
    
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    amount_fixed = fields.Float(string='Commission Amount', default=0.0)
    percentage = fields.Float(string='Commission Percentage', default=0.0)
    user_id = fields.Many2one('res.users', string='Salesperson')
    date = fields.Date(string='Commission Date', default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('paid', 'Paid')
    ], string='State', default='draft')
