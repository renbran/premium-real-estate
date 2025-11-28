# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_scholarix_report_values(self):
        """Get custom report values for SCHOLARIX PDF reports"""
        self.ensure_one()
        
        # Calculate additional metrics for the report
        total_discount = sum(line.discount for line in self.order_line)
        avg_discount = total_discount / len(self.order_line) if self.order_line else 0
        
        # Get order status information
        status_label = dict(self._fields['state'].selection).get(self.state, self.state)
        
        # Format dates properly
        order_date_formatted = self.date_order.strftime('%B %d, %Y') if self.date_order else ''
        validity_date_formatted = self.validity_date.strftime('%B %d, %Y') if self.validity_date else ''
        
        return {
            'doc': self,
            'total_discount': total_discount,
            'avg_discount': avg_discount,
            'status_label': status_label,
            'order_date_formatted': order_date_formatted,
            'validity_date_formatted': validity_date_formatted,
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
    
    def action_print_scholarix_quotation(self):
        """Print SCHOLARIX custom quotation/sales order report"""
        return self.env.ref('custom_reports_pdf.action_report_scholarix_quotation').report_action(self)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def get_line_discount_amount(self):
        """Calculate the discount amount for this line"""
        if self.discount > 0:
            return (self.price_unit * self.product_uom_qty * self.discount) / 100
        return 0.0