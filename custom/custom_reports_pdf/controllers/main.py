# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class ScholarixReportController(http.Controller):
    
    @http.route(['/report/pdf/custom_reports_pdf.report_scholarix_invoice/<docids>'], 
                type='http', auth="user", website=True)
    def report_scholarix_invoice_pdf(self, docids, **data):
        """Generate SCHOLARIX Invoice PDF Report"""
        try:
            docids = [int(i) for i in docids.split(',')]
            report = request.env.ref('custom_reports_pdf.action_report_scholarix_invoice')
            pdf = report._render_qweb_pdf(docids)[0]
            
            # Set proper headers for PDF download
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
                ('Content-Disposition', 'attachment; filename="SCHOLARIX_Invoice.pdf"')
            ]
            
            return request.make_response(pdf, headers=pdfhttpheaders)
            
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
    
    @http.route(['/report/pdf/custom_reports_pdf.report_scholarix_quotation/<docids>'], 
                type='http', auth="user", website=True)
    def report_scholarix_quotation_pdf(self, docids, **kwargs):
        """Generate SCHOLARIX Quotation/Sales Order PDF Report"""
        try:
            docids = [int(i) for i in docids.split(',')]
            report = request.env.ref('custom_reports_pdf.action_report_scholarix_quotation')
            pdf = report._render_qweb_pdf(docids)[0]
            
            # Set proper headers for PDF download
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
                ('Content-Disposition', 'attachment; filename="SCHOLARIX_Quotation.pdf"')
            ]
            
            return request.make_response(pdf, headers=pdfhttpheaders)
            
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
    
    @http.route(['/report/html/custom_reports_pdf.report_scholarix_invoice/<docids>'], 
                type='http', auth="user", website=True)
    def report_scholarix_invoice_html(self, docids, **kwargs):
        """Generate SCHOLARIX Invoice HTML Preview"""
        try:
            docids = [int(i) for i in docids.split(',')]
            report = request.env.ref('custom_reports_pdf.action_report_scholarix_invoice')
            html = report._render_qweb_html(docids)[0]
            
            return request.make_response(
                html,
                headers=[('Content-Type', 'text/html')]
            )
            
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
    
    @http.route(['/report/html/custom_reports_pdf.report_scholarix_quotation/<docids>'], 
                type='http', auth="user", website=True)
    def report_scholarix_quotation_html(self, docids, **kwargs):
        """Generate SCHOLARIX Quotation HTML Preview"""
        try:
            docids = [int(i) for i in docids.split(',')]
            report = request.env.ref('custom_reports_pdf.action_report_scholarix_quotation')
            html = report._render_qweb_html(docids)[0]
            
            return request.make_response(
                html,
                headers=[('Content-Type', 'text/html')]
            )
            
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )