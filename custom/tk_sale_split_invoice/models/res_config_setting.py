from odoo import fields, models


class ResConfigSetting(models.TransientModel):
    """
        Inherits from 'res.config.settings' to customize behavior or add additional fields.
    """
    _inherit = 'res.config.settings'

    split_invoice_count = fields.Integer(string='Split Invoice Count',
                            config_parameter='tk_sale_split_invoice.split_invoice_count')
