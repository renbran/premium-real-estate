# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DigestDigest(models.Model):
    _inherit = 'digest.digest'

    @api.model
    def _get_white_label_name(self):
        """Get white label company name for digest emails"""
        company = self.env.company
        return company.white_label_name or company.name

    def _render_template(self, template_xml_id, **values):
        """Override to inject white label branding in digest templates"""
        values.update({
            'white_label_name': self._get_white_label_name(),
            'replace_odoo_branding': self.env.company.replace_odoo_branding,
        })
        return super()._render_template(template_xml_id, **values)
