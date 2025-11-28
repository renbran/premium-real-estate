# -*- coding: utf-8 -*-

from odoo import models, api


class ScholarixReportInvoice(models.AbstractModel):
    _name = 'report.custom_reports_pdf.report_scholarix_invoice'
    _description = 'SCHOLARIX Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Generate report values for SCHOLARIX invoice report"""
        invoices = self.env['account.move'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': invoices,
            'data': data,
            'company_info': self._get_company_info(),
        }
    
    def _get_company_info(self):
        """Get standardized company information"""
        company = self.env.company
        return {
            'name': 'SCHOLARIX Global Consultants',
            'tagline': 'AI-Powered Business Transformation',
            'street': 'Al Quijada, Abu Saif Business Center 201',
            'street2': 'Metro Station - Hor Al Anz, Dubai',
            'city': 'Dubai',
            'country': 'United Arab Emirates',
            'phone': '+971 058 624 1100',
            'email': 'info@scholarixglobal.com',
            'website': 'www.scholarixglobal.com',
        }


class ScholarixReportSaleOrder(models.AbstractModel):
    _name = 'report.custom_reports_pdf.report_scholarix_quotation'
    _description = 'SCHOLARIX Quotation/Sales Order Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Generate report values for SCHOLARIX quotation report"""
        orders = self.env['sale.order'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': orders,
            'data': data,
            'company_info': self._get_company_info(),
        }
    
    def _get_company_info(self):
        """Get standardized company information"""
        company = self.env.company
        return {
            'name': 'SCHOLARIX Global Consultants',
            'tagline': 'AI-Powered Business Transformation',
            'street': 'Al Quijada, Abu Saif Business Center 201',
            'street2': 'Metro Station - Hor Al Anz, Dubai',
            'city': 'Dubai',
            'country': 'United Arab Emirates',
            'phone': '+971 058 624 1100',
            'email': 'info@scholarixglobal.com',
            'website': 'www.scholarixglobal.com',
        }