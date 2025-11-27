# -*- coding: utf-8 -*-
from odoo import models

class PartnerXlsxReport(models.AbstractModel):
    _name = 'report.statement_report.res_partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, partners):
        """ Generate XLSX report for partners """
        for partner in partners:
            # Use the existing get_xlsx_report logic
            response = type('MockResponse', (), {'stream': workbook})()
            partner.get_xlsx_report(data, response)
