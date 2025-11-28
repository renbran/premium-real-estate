# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def _render_template(self, template_src, model, res_ids, post_process=False):
        """Override to replace Odoo branding in email templates"""
        result = super()._render_template(template_src, model, res_ids, post_process)
        
        if self.env.company.replace_odoo_branding:
            white_label_name = self.env.company.white_label_name or self.env.company.name
            
            # Replace Odoo mentions in the rendered content
            if isinstance(result, dict):
                for res_id, content in result.items():
                    if isinstance(content, str):
                        # Replace "Odoo" with white label name
                        content = re.sub(r'\bOdoo\b', white_label_name, content, flags=re.IGNORECASE)
                        # Replace odoo.com references
                        content = re.sub(r'\bodoo\.com\b', f'{white_label_name.lower().replace(" ", "")}.com', content, flags=re.IGNORECASE)
                        result[res_id] = content
            elif isinstance(result, str):
                # Replace "Odoo" with white label name
                result = re.sub(r'\bOdoo\b', white_label_name, result, flags=re.IGNORECASE)
                # Replace odoo.com references
                result = re.sub(r'\bodoo\.com\b', f'{white_label_name.lower().replace(" ", "")}.com', result, flags=re.IGNORECASE)
        
        return result

    @api.model
    def _get_default_from_address(self):
        """Override to use white label name in from address"""
        if self.env.company.replace_odoo_branding:
            white_label_name = self.env.company.white_label_name or self.env.company.name
            return f'"{white_label_name}" <noreply@{self.env.company.email or "example.com"}>'
        return super()._get_default_from_address()
