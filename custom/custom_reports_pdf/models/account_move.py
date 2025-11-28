# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_scholarix_report_values(self):
        """Get custom report values for SCHOLARIX PDF reports"""
        self.ensure_one()
        
        # Calculate additional metrics for the report
        total_discount = sum(line.discount for line in self.invoice_line_ids)
        avg_discount = total_discount / len(self.invoice_line_ids) if self.invoice_line_ids else 0
        
        # Get payment information
        payment_status = 'Paid' if self.payment_state == 'paid' else 'Pending'
        
        # Format dates properly
        invoice_date_formatted = self.invoice_date.strftime('%B %d, %Y') if self.invoice_date else ''
        due_date_formatted = self.invoice_date_due.strftime('%B %d, %Y') if self.invoice_date_due else ''
        
        return {
            'doc': self,
            'total_discount': total_discount,
            'avg_discount': avg_discount,
            'payment_status': payment_status,
            'invoice_date_formatted': invoice_date_formatted,
            'due_date_formatted': due_date_formatted,
            'company_info': self._get_company_details(),
        }
    
    def _get_company_details(self):
        """Get company details for report footer"""
        company = self.company_id
        return {
            'name': company.name or 'SCHOLARIX Global Consultants',
            'street': company.street or 'Al Quijada, Abu Saif Business Center 201',
            'street2': company.street2 or 'Metro Station - Hor Al Anz, Dubai',
            'city': company.city or 'Dubai',
            'country': company.country_id.name or 'United Arab Emirates',
            'phone': company.phone or '+971 058 624 1100',
            'email': company.email or 'info@scholarixglobal.com',
            'website': company.website or 'www.scholarixglobal.com',
            'vat': company.vat or '[VAT NUMBER]',
            'company_registry': company.company_registry or '[LICENSE NO.]',
        }
    
    def action_print_scholarix_invoice(self):
        """Print SCHOLARIX custom invoice report"""
        return self.env.ref('custom_reports_pdf.action_report_scholarix_invoice').report_action(self)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    def get_line_discount_amount(self):
        """Calculate the discount amount for this line"""
        if self.discount > 0:
            return (self.price_unit * self.quantity * self.discount) / 100
        return 0.0