# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    white_label_name = fields.Char(
        related='company_id.white_label_name',
        readonly=False,
        string='White Label Company Name'
    )
    
    replace_odoo_branding = fields.Boolean(
        related='company_id.replace_odoo_branding',
        readonly=False,
        string='Replace Odoo Branding'
    )
    
    custom_logo_url = fields.Char(
        related='company_id.custom_logo_url',
        readonly=False,
        string='Custom Logo URL'
    )
    
    custom_favicon_url = fields.Char(
        related='company_id.custom_favicon_url',
        readonly=False,
        string='Custom Favicon URL'
    )
    
    hide_odoo_documentation = fields.Boolean(
        related='company_id.hide_odoo_documentation',
        readonly=False,
        string='Hide Odoo Documentation Links'
    )
    
    hide_odoo_support = fields.Boolean(
        related='company_id.hide_odoo_support',
        readonly=False,
        string='Hide Odoo Support Links'
    )
    
    custom_footer_text = fields.Text(
        related='company_id.custom_footer_text',
        readonly=False,
        string='Custom Footer Text'
    )
