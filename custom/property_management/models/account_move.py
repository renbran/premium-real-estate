from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    property_order_id = fields.Many2one('property.sale', string="Property Sale Order", ondelete='set null', index=True)
    property_rental_id = fields.Many2one('property.rental', string="Rental Order", ondelete='set null', index=True)
    broker_commission_id = fields.Many2one('broker.commission.invoice', string="Broker Commission", ondelete='set null', index=True)