from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # --- Deal Information Fields ---
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
    )
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
    )
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
    )
    developer_commission = fields.Float(
        string='Developer Commission %',
        tracking=True,
        digits=(16, 2),
    )

    # --- Relational Fields ---
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
    )
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
    )
