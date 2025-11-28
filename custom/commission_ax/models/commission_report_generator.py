# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import io
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class CommissionReportGenerator(models.TransientModel):
    """Commission Report Generator - Generates various commission reports in different formats"""
    _name = 'commission.report.generator'
    _description = 'Commission Report Generator'

    def generate_partner_statement_report(self, wizard_data, output_format='pdf'):
        """
        Generate commission partner statement report

        Args:
            wizard_data: Dictionary with report parameters
            output_format: 'pdf', 'excel', or 'json'

        Returns:
            Dictionary with file data: {'filename': str, 'content': base64, 'mimetype': str}
        """
        try:
            # Get commission data based on filters
            commission_data = self._get_commission_data_for_statement(wizard_data)

            if output_format == 'pdf':
                return self._generate_pdf_statement(commission_data, wizard_data)
            elif output_format == 'excel':
                return self._generate_excel_statement(commission_data, wizard_data)
            elif output_format == 'json':
                return self._generate_json_statement(commission_data, wizard_data)
            else:
                raise ValidationError(_("Invalid output format: %s") % output_format)

        except Exception as e:
            _logger.error("Error generating partner statement: %s", str(e))
            raise UserError(_("Error generating report: %s") % str(e))

    def generate_profit_analysis_report(self, wizard_data, output_format='pdf'):
        """
        Generate commission profit analysis report

        Args:
            wizard_data: Dictionary with report parameters
            output_format: 'pdf', 'excel', or 'json'

        Returns:
            Dictionary with file data
        """
        try:
            # Get commission data with profit metrics
            commission_data = self._get_commission_data_for_profit_analysis(wizard_data)

            if output_format == 'pdf':
                return self._generate_pdf_profit_analysis(commission_data, wizard_data)
            elif output_format == 'excel':
                return self._generate_excel_profit_analysis(commission_data, wizard_data)
            elif output_format == 'json':
                return self._generate_json_profit_analysis(commission_data, wizard_data)
            else:
                raise ValidationError(_("Invalid output format: %s") % output_format)

        except Exception as e:
            _logger.error("Error generating profit analysis: %s", str(e))
            raise UserError(_("Error generating report: %s") % str(e))

    def _get_commission_data_for_statement(self, wizard_data):
        """Get commission line data for partner statement"""
        domain = [
            ('sale_order_id.date_order', '>=', wizard_data.get('date_from')),
            ('sale_order_id.date_order', '<=', wizard_data.get('date_to')),
        ]

        if wizard_data.get('partner_ids'):
            domain.append(('partner_id', 'in', wizard_data['partner_ids']))

        if wizard_data.get('commission_state') and wizard_data['commission_state'] != 'all':
            domain.append(('state', '=', wizard_data['commission_state']))

        commission_lines = self.env['commission.line'].search(domain, order='partner_id, sale_order_id')

        # Transform to report data
        report_data = []
        for line in commission_lines:
            report_data.append({
                'partner_name': line.partner_id.name,
                'sale_order_name': line.sale_order_id.name,
                'date_order': line.sale_order_id.date_order,
                'product_name': line.product_id.name if line.product_id else '',
                'base_amount': line.base_amount,
                'rate': line.rate,
                'commission_amount': line.commission_amount,
                'state': line.state,
                'currency': line.currency_id.name,
            })

        return report_data

    def _get_commission_data_for_profit_analysis(self, wizard_data):
        """Get commission data for profit analysis"""
        data = self._get_commission_data_for_statement(wizard_data)

        # Add profit calculations
        for item in data:
            # Calculate profit metrics
            commission_line = self.env['commission.line'].search([
                ('partner_id.name', '=', item['partner_name']),
                ('sale_order_id.name', '=', item['sale_order_name'])
            ], limit=1)

            if commission_line:
                item['sales_value'] = commission_line.sales_value
                item['commission_qty'] = commission_line.commission_qty
                item['total_sales'] = commission_line.base_amount
                item['total_commission'] = commission_line.commission_amount
                item['company_share'] = item['total_sales'] - item['total_commission']
                item['commission_percentage'] = (item['total_commission'] / item['total_sales'] * 100) if item['total_sales'] else 0

        return data

    def _generate_pdf_statement(self, data, wizard_data):
        """Generate PDF statement (placeholder - requires reportlab or wkhtmltopdf)"""
        # For now, return JSON as fallback
        _logger.warning("PDF generation not yet implemented, returning JSON")
        return self._generate_json_statement(data, wizard_data)

    def _generate_excel_statement(self, data, wizard_data):
        """Generate Excel statement"""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("xlsxwriter library is required for Excel export"))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Commission Statement')

        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'color': 'white',
            'align': 'center',
            'border': 1
        })

        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        data_format = workbook.add_format({'border': 1})

        # Headers
        headers = ['Partner', 'Sale Order', 'Date', 'Product', 'Base Amount', 'Rate %', 'Commission', 'Status', 'Currency']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Data
        row = 1
        for item in data:
            worksheet.write(row, 0, item.get('partner_name', ''), data_format)
            worksheet.write(row, 1, item.get('sale_order_name', ''), data_format)
            worksheet.write(row, 2, str(item.get('date_order', '')), data_format)
            worksheet.write(row, 3, item.get('product_name', ''), data_format)
            worksheet.write(row, 4, item.get('base_amount', 0), money_format)
            worksheet.write(row, 5, item.get('rate', 0), data_format)
            worksheet.write(row, 6, item.get('commission_amount', 0), money_format)
            worksheet.write(row, 7, item.get('state', ''), data_format)
            worksheet.write(row, 8, item.get('currency', ''), data_format)
            row += 1

        workbook.close()
        output.seek(0)

        filename = f"commission_statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return {
            'filename': filename,
            'content': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

    def _generate_json_statement(self, data, wizard_data):
        """Generate JSON statement"""
        json_data = {
            'report_type': 'commission_partner_statement',
            'generated_at': datetime.now().isoformat(),
            'parameters': wizard_data,
            'data': data,
            'summary': {
                'total_records': len(data),
                'total_commission': sum(item.get('commission_amount', 0) for item in data),
                'total_base': sum(item.get('base_amount', 0) for item in data),
            }
        }

        filename = f"commission_statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return {
            'filename': filename,
            'content': base64.b64encode(json.dumps(json_data, indent=2, default=str).encode()),
            'mimetype': 'application/json'
        }

    def _generate_pdf_profit_analysis(self, data, wizard_data):
        """Generate PDF profit analysis (placeholder)"""
        _logger.warning("PDF generation not yet implemented, returning JSON")
        return self._generate_json_profit_analysis(data, wizard_data)

    def _generate_excel_profit_analysis(self, data, wizard_data):
        """Generate Excel profit analysis"""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("xlsxwriter library is required for Excel export"))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Profit Analysis')

        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'color': 'white',
            'align': 'center',
            'border': 1
        })

        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        percent_format = workbook.add_format({'num_format': '0.00%', 'border': 1})
        data_format = workbook.add_format({'border': 1})

        # Headers
        headers = ['Partner', 'Sale Order', 'Total Sales', 'Total Commission', 'Company Share', 'Commission %']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Data
        row = 1
        for item in data:
            worksheet.write(row, 0, item.get('partner_name', ''), data_format)
            worksheet.write(row, 1, item.get('sale_order_name', ''), data_format)
            worksheet.write(row, 2, item.get('total_sales', 0), money_format)
            worksheet.write(row, 3, item.get('total_commission', 0), money_format)
            worksheet.write(row, 4, item.get('company_share', 0), money_format)
            worksheet.write(row, 5, item.get('commission_percentage', 0) / 100, percent_format)
            row += 1

        workbook.close()
        output.seek(0)

        filename = f"profit_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return {
            'filename': filename,
            'content': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

    def _generate_json_profit_analysis(self, data, wizard_data):
        """Generate JSON profit analysis"""
        json_data = {
            'report_type': 'commission_profit_analysis',
            'generated_at': datetime.now().isoformat(),
            'parameters': wizard_data,
            'data': data,
            'summary': {
                'total_records': len(data),
                'total_sales': sum(item.get('total_sales', 0) for item in data),
                'total_commission': sum(item.get('total_commission', 0) for item in data),
                'total_company_share': sum(item.get('company_share', 0) for item in data),
                'avg_commission_percentage': sum(item.get('commission_percentage', 0) for item in data) / len(data) if data else 0,
            }
        }

        filename = f"profit_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return {
            'filename': filename,
            'content': base64.b64encode(json.dumps(json_data, indent=2, default=str).encode()),
            'mimetype': 'application/json'
        }
