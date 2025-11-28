# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    white_label_name = fields.Char(
        string='White Label Company Name',
        help="Custom company name to replace 'Odoo' branding",
        default=lambda self: self.name
    )
    
    replace_odoo_branding = fields.Boolean(
        string='Replace Odoo Branding',
        default=True,
        help="Enable to replace Odoo branding with custom company branding"
    )
    
    custom_logo_url = fields.Char(
        string='Custom Logo URL',
        help="URL for custom logo to replace Odoo logo"
    )
    
    custom_favicon_url = fields.Char(
        string='Custom Favicon URL',
        help="URL for custom favicon"
    )
    
    hide_odoo_documentation = fields.Boolean(
        string='Hide Odoo Documentation Links',
        default=True,
        help="Hide links to Odoo documentation"
    )
    
    hide_odoo_support = fields.Boolean(
        string='Hide Odoo Support Links',
        default=True,
        help="Hide links to Odoo support"
    )
    
    custom_footer_text = fields.Text(
        string='Custom Footer Text',
        help="Custom text to display in footer instead of Odoo copyright"
    )
    
    @api.model
    def get_white_label_settings(self):
        """Get white label settings for current company"""
        company = self.env.company
        return {
            'white_label_name': company.white_label_name or company.name,
            'replace_odoo_branding': company.replace_odoo_branding,
            'custom_logo_url': company.custom_logo_url,
            'custom_favicon_url': company.custom_favicon_url,
            'hide_odoo_documentation': company.hide_odoo_documentation,
            'hide_odoo_support': company.hide_odoo_support,
            'custom_footer_text': company.custom_footer_text,
        }
