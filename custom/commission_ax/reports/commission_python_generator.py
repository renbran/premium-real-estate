# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import base64
import io
import logging
from datetime import datetime, date
import json

# Optional dependencies with graceful fallbacks
try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

_logger = logging.getLogger(__name__)


class CommissionReportGenerator(models.Model):
    """Unified Python-based Commission Report Generator"""
    _name = 'commission.report.generator'
    _description = 'Commission Report Generator'

    def generate_partner_statement_report(self, wizard_data, format_type='pdf'):
        """
        Generate commission partner statement report
        
        Args:
            wizard_data: Data from commission partner statement wizard
            format_type: 'pdf', 'excel', or 'json'
        
        Returns:
            dict: Report data with content, filename, and format info
        """
        try:
            # Get commission data
            commission_data = self._get_commission_statement_data(wizard_data)
            
            if format_type == 'pdf':
                return self._generate_partner_statement_pdf(commission_data, wizard_data)
            elif format_type == 'excel':
                return self._generate_partner_statement_excel(commission_data, wizard_data)
            elif format_type == 'json':
                return self._generate_partner_statement_json(commission_data, wizard_data)
            else:
                raise UserError(_("Unsupported format type: %s") % format_type)
                
        except Exception as e:
            _logger.error("Error generating partner statement report: %s", str(e))
            raise UserError(_("Failed to generate report: %s") % str(e))

    def generate_profit_analysis_report(self, wizard_data, format_type='pdf'):
        """
        Generate commission profit analysis report
        
        Args:
            wizard_data: Data from commission wizard
            format_type: 'pdf', 'excel', or 'json'
        
        Returns:
            dict: Report data with content, filename, and format info
        """
        try:
            # Get commission data with profit analysis
            commission_data = self._get_profit_analysis_data(wizard_data)
            
            if format_type == 'pdf':
                return self._generate_profit_analysis_pdf(commission_data, wizard_data)
            elif format_type == 'excel':
                return self._generate_profit_analysis_excel(commission_data, wizard_data)
            elif format_type == 'json':
                return self._generate_profit_analysis_json(commission_data, wizard_data)
            else:
                raise UserError(_("Unsupported format type: %s") % format_type)
                
        except Exception as e:
            _logger.error("Error generating profit analysis report: %s", str(e))
            raise UserError(_("Failed to generate report: %s") % str(e))

    def _get_commission_statement_data(self, wizard_data):
        """Get commission data for partner statement"""
        domain = [
            ('date_commission', '>=', wizard_data.get('date_from')),
            ('date_commission', '<=', wizard_data.get('date_to')),
        ]
        
        # Add partner filter if specified
        partner_ids = wizard_data.get('partner_ids', [])
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))
            
        # Add state filter if specified
        commission_state = wizard_data.get('commission_state', 'all')
        if commission_state != 'all':
            domain.append(('state', '=', commission_state))
        
        # Get commission lines
        commission_lines = self.env['commission.line'].search(domain, order='partner_id, date_commission')
        
        # Process data
        report_data = []
        totals = {
            'total_sales': 0.0,
            'total_commissions': 0.0,
            'external_commissions': 0.0,
            'internal_commissions': 0.0,
            'commission_count': 0,
        }
        
        for line in commission_lines:
            sale_order = line.sale_order_id
            
            # Calculate unit price (weighted average of order lines)
            unit_price = 0.0
            product_description = ''
            if sale_order and sale_order.order_line:
                total_value = sum(ol.price_unit * ol.product_uom_qty for ol in sale_order.order_line)
                total_qty = sum(ol.product_uom_qty for ol in sale_order.order_line)
                unit_price = total_value / total_qty if total_qty > 0 else 0.0
                
                # Get product description from first order line
                if sale_order.order_line:
                    first_line = sale_order.order_line[0]
                    product_description = first_line.product_id.name if first_line.product_id else ''
            
            # Extract project and unit from client_order_ref or use product name
            # Format: "PROJECT_NAME UNIT_NUMBER" or just use client_order_ref as project
            project_name = sale_order.client_order_ref if sale_order else 'N/A'
            unit_name = product_description
            
            # Try to split client_order_ref into project and unit if it contains space
            if project_name and ' ' in project_name:
                parts = project_name.rsplit(' ', 1)  # Split from right, max 1 split
                if len(parts) == 2:
                    project_name = parts[0]
                    unit_name = parts[1]
            
            # Build line data
            line_data = {
                'partner_name': line.partner_id.name or 'Unknown Partner',
                'booking_date': line.date_commission.strftime('%Y-%m-%d') if line.date_commission else '',
                'client_order_ref': sale_order.client_order_ref or 'No Reference' if sale_order else 'No Reference',
                'sale_order_name': sale_order.name if sale_order else 'No Sale Order',
                'unit_price': unit_price,
                'commission_rate': line.rate or 0.0,
                'commission_amount': line.commission_amount or 0.0,
                'commission_status': dict(line._fields['state'].selection).get(line.state, line.state),
                'currency': sale_order.currency_id.name if sale_order and sale_order.currency_id else 'AED',
                'commission_category': getattr(line, 'commission_category', 'sales_commission'),
                'is_cost_to_company': getattr(line, 'is_cost_to_company', True),
                'profit_impact_percentage': getattr(line, 'profit_impact_percentage', 0.0),
                'commission_type_name': line.commission_type_id.name if line.commission_type_id else 'Standard Commission',
                'project_name': project_name,
                'unit_name': unit_name,
                'product_description': product_description,
            }
            
            report_data.append(line_data)
            
            # Update totals
            totals['total_sales'] += unit_price
            totals['total_commissions'] += line.commission_amount or 0.0
            totals['commission_count'] += 1
            
            # Categorize commissions
            category = getattr(line, 'commission_category', '')
            if 'external' in category:
                totals['external_commissions'] += line.commission_amount or 0.0
            else:
                totals['internal_commissions'] += line.commission_amount or 0.0
        
        return {
            'report_data': report_data,
            'totals': totals,
            'filters': wizard_data,
        }

    def _get_profit_analysis_data(self, wizard_data):
        """Get commission data for profit analysis"""
        base_data = self._get_commission_statement_data(wizard_data)
        
        # Add profit analysis calculations
        categories = {}
        for line in base_data['report_data']:
            category = line['commission_category']
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_amount': 0.0,
                    'rates': [],
                    'sales_value': 0.0,
                }
            
            categories[category]['count'] += 1
            categories[category]['total_amount'] += line['commission_amount']
            categories[category]['rates'].append(line['commission_rate'])
            categories[category]['sales_value'] += line['unit_price']
        
        # Calculate averages and percentages
        for category, data in categories.items():
            if data['rates']:
                data['avg_rate'] = sum(data['rates']) / len(data['rates'])
            else:
                data['avg_rate'] = 0.0
            
            if base_data['totals']['total_sales'] > 0:
                data['percent_of_sales'] = (data['total_amount'] / base_data['totals']['total_sales']) * 100
            else:
                data['percent_of_sales'] = 0.0
        
        base_data['categories'] = categories
        return base_data

    def _generate_partner_statement_pdf(self, commission_data, wizard_data):
        """Generate PDF partner statement report"""
        if not REPORTLAB_AVAILABLE:
            raise UserError(_("ReportLab library is required for PDF generation. Please install: pip install reportlab"))
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()

        summary_label_style = ParagraphStyle(
            'ProfitSummaryLabel',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
        )
        summary_value_style = ParagraphStyle(
            'ProfitSummaryValue',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        )
        category_label_style = ParagraphStyle(
            'ProfitCategoryLabel',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
        )
        category_center_style = ParagraphStyle(
            'ProfitCategoryCenter',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
        )
        category_value_style = ParagraphStyle(
            'ProfitCategoryValue',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        )
        
        # Title with burgundy branding
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#800020'),  # Rich burgundy color
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        )
        
        # Company header with branding
        company_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#800020'),  # Rich burgundy color
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        story.append(Paragraph("COMMISSION STATEMENT", title_style))
        story.append(Paragraph("Professional Commission Management Report", company_style))
        story.append(Paragraph(f"Report Period: {wizard_data.get('date_from', '')} to {wizard_data.get('date_to', '')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary section with burgundy and white theme
        totals = commission_data['totals']
        # Get primary currency from first record
        primary_currency = commission_data['report_data'][0]['currency'] if commission_data['report_data'] else 'AED'
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Records', str(totals['commission_count'])],
            ['Total Sales', f"{primary_currency} {totals['total_sales']:,.2f}"],
            ['Total Commissions', f"{primary_currency} {totals['total_commissions']:,.2f}"],
            ['External Commissions', f"{primary_currency} {totals['external_commissions']:,.2f}"],
            ['Internal Commissions', f"{primary_currency} {totals['internal_commissions']:,.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            # Header styling with rich burgundy
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#800020')),  # Rich burgundy header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            # Data rows with white background and burgundy accents
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#4A4A4A')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#800020')),  # Burgundy grid lines
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Bold first column
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Detail table - Smart format with SO Reference first, no partner names
        if commission_data['report_data']:
            headers = ['SO Reference', 'Date', 'Project', 'Unit', 'Percent', 'Sales Value', 'Total Amount', 'Status']
            table_data = [headers]
            
            for line in commission_data['report_data']:
                # Get currency for this line
                currency = line.get('currency', 'AED')
                
                # Extract project and unit from client_order_ref or product description
                project_name = line.get('project_name', '') or line.get('client_order_ref', 'N/A')
                unit_name = line.get('unit_name', '') or line.get('product_description', '')
                
                table_data.append([
                    line['sale_order_name'],  # SO Reference (e.g., "SO 6814")
                    str(line['booking_date']) if line['booking_date'] else 'N/A',  # Date
                    project_name,  # Project
                    unit_name,  # Unit
                    f"{line['commission_rate']:.2f}%",  # Percent
                    f"{currency} {line['unit_price']:,.2f}",  # Sales Value (currency-aware)
                    f"{currency} {line['commission_amount']:,.2f}",  # Total Amount (currency-aware)
                    line['commission_status']  # Status
                ])
            
            # Create table with appropriate column widths for the smart format
            col_widths = [1.0*inch, 0.85*inch, 1.4*inch, 1.2*inch, 0.7*inch, 1.1*inch, 1.1*inch, 0.9*inch]
            detail_table = Table(table_data, repeatRows=1, colWidths=col_widths)
            detail_table.setStyle(TableStyle([
                # Header styling with rich burgundy theme
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#800020')),  # Rich burgundy header  
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                # Data rows with clean white background
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#4A4A4A')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#800020')),  # Burgundy grid lines
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                # Alternate row coloring for better readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FDF5F5')]),  # Very light burgundy tint
                # Align columns appropriately
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # SO Reference - left
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Date - center
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Project - left
                ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Unit - left
                ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Percent - center
                ('ALIGN', (5, 1), (5, -1), 'RIGHT'),   # Sales Value - right
                ('ALIGN', (6, 1), (6, -1), 'RIGHT'),   # Total Amount - right
                ('ALIGN', (7, 1), (7, -1), 'CENTER'),  # Status - center
            ]))
            
            story.append(detail_table)
        else:
            story.append(Paragraph("No commission data found for the selected criteria.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        filename = f"Commission_Statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return {
            'content': base64.b64encode(buffer.read()),
            'filename': filename,
            'format': 'pdf',
            'mimetype': 'application/pdf'
        }

    def _generate_partner_statement_excel(self, commission_data, wizard_data):
        """Generate Excel partner statement report"""
        if not XLSXWRITER_AVAILABLE:
            raise UserError(_("XlsxWriter library is required for Excel generation. Please install: pip install xlsxwriter"))
        
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        
        # Create formats with burgundy branding
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#800020',  # Rich burgundy color
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        currency_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        percent_format = workbook.add_format({'num_format': '0.00%', 'border': 1})
        normal_format = workbook.add_format({'border': 1})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        
        # Alternate row format with light burgundy tint
        alt_row_format = workbook.add_format({
            'bg_color': '#FDF5F5',  # Very light burgundy tint
            'border': 1
        })
        
        # Main worksheet
        worksheet = workbook.add_worksheet('Commission Statement')
        
        # Headers - Smart format without partner names
        headers = [
            'SO Reference', 'Date', 'Project', 'Unit', 
            'Percent', 'Sales Value', 'Total Amount', 'Status'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data rows with alternating colors and proper formatting
        row = 1
        for line in commission_data['report_data']:
            # Use alternating row format for better readability
            row_format = alt_row_format if row % 2 == 0 else normal_format
            currency_row_format = workbook.add_format({
                'num_format': '#,##0.00', 
                'border': 1,
                'bg_color': '#FDF5F5' if row % 2 == 0 else '#FFFFFF'
            })
            percent_row_format = workbook.add_format({
                'num_format': '0.00%',
                'border': 1,
                'bg_color': '#FDF5F5' if row % 2 == 0 else '#FFFFFF',
                'align': 'center'
            })
            
            # Extract project and unit from client_order_ref or product description
            project_name = line.get('project_name', '') or line.get('client_order_ref', 'N/A')
            unit_name = line.get('unit_name', '') or line.get('product_description', '')
            
            worksheet.write(row, 0, line['sale_order_name'], row_format)  # SO Reference
            worksheet.write(row, 1, str(line['booking_date']) if line['booking_date'] else 'N/A', row_format)  # Date
            worksheet.write(row, 2, project_name, row_format)  # Project
            worksheet.write(row, 3, unit_name, row_format)  # Unit
            worksheet.write(row, 4, line['commission_rate'] / 100, percent_row_format)  # Percent (as decimal for Excel %)
            worksheet.write(row, 5, line['unit_price'], currency_row_format)  # Sales Value
            worksheet.write(row, 6, line['commission_amount'], currency_row_format)  # Total Amount
            worksheet.write(row, 7, line['commission_status'], row_format)  # Status
            row += 1
            
        # Auto-adjust column widths for better readability
        worksheet.set_column('A:A', 12)  # SO Reference
        worksheet.set_column('B:B', 12)  # Date
        worksheet.set_column('C:C', 20)  # Project
        worksheet.set_column('D:D', 18)  # Unit
        worksheet.set_column('E:E', 10)  # Percent
        worksheet.set_column('F:F', 14)  # Sales Value
        worksheet.set_column('G:G', 14)  # Total Amount
        worksheet.set_column('H:H', 12)  # Status
        
        # Summary worksheet
        summary_ws = workbook.add_worksheet('Summary')
        totals = commission_data['totals']
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Records', totals['commission_count']],
            ['Total Sales', totals['total_sales']],
            ['Total Commissions', totals['total_commissions']],
            ['External Commissions', totals['external_commissions']],
            ['Internal Commissions', totals['internal_commissions']],
            ['Commission Rate', (totals['total_commissions'] / totals['total_sales'] * 100) if totals['total_sales'] > 0 else 0],
        ]
        
        for row, (label, value) in enumerate(summary_data):
            if row == 0:
                summary_ws.write(row, 0, label, header_format)
                summary_ws.write(row, 1, value, header_format)
            else:
                summary_ws.write(row, 0, label, normal_format)
                if isinstance(value, (int, float)) and 'Commission' in label:
                    summary_ws.write(row, 1, value, currency_format)
                elif 'Rate' in label:
                    summary_ws.write(row, 1, value / 100, percent_format)
                else:
                    summary_ws.write(row, 1, value, normal_format)
        
        workbook.close()
        buffer.seek(0)
        
        filename = f"Commission_Statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return {
            'content': base64.b64encode(buffer.read()),
            'filename': filename,
            'format': 'excel',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

    def _generate_profit_analysis_pdf(self, commission_data, wizard_data):
        """Generate PDF profit analysis report"""
        if not REPORTLAB_AVAILABLE:
            raise UserError(_("ReportLab library is required for PDF generation. Please install: pip install reportlab"))
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Define custom styles for profit analysis report
        summary_label_style = ParagraphStyle(
            'ProfitSummaryLabel',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
        )
        summary_value_style = ParagraphStyle(
            'ProfitSummaryValue',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        )
        category_label_style = ParagraphStyle(
            'ProfitCategoryLabel',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
        )
        category_center_style = ParagraphStyle(
            'ProfitCategoryCenter',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
        )
        category_value_style = ParagraphStyle(
            'ProfitCategoryValue',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        )
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        story.append(Paragraph("Commission Profit Analysis Report", title_style))
        story.append(Paragraph(f"Period: {wizard_data.get('date_from', '')} to {wizard_data.get('date_to', '')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        totals = commission_data['totals']
        net_profit = totals['total_sales'] - totals['total_commissions']
        profit_margin = (net_profit / totals['total_sales'] * 100) if totals['total_sales'] > 0 else 0
        
        # Get primary currency from commission data
        primary_currency = commission_data['report_data'][0]['currency'] if commission_data['report_data'] else 'AED'
        
        exec_summary = [['Metric', 'Value']]
        metrics = [
            ('Total Sales Revenue', f"{primary_currency} {totals['total_sales']:,.2f}"),
            ('Total Commission Cost', f"{primary_currency} {totals['total_commissions']:,.2f}"),
            ('External Commission Cost', f"{primary_currency} {totals['external_commissions']:,.2f}"),
            ('Internal Commission Investment', f"{primary_currency} {totals['internal_commissions']:,.2f}"),
            ('Net Profit After Commissions', f"{primary_currency} {net_profit:,.2f}"),
            ('Profit Margin', f"{profit_margin:.2f}%"),
        ]

        for label, value in metrics:
            exec_summary.append([
                Paragraph(label, summary_label_style),
                Paragraph(value, summary_value_style),
            ])

        exec_table = Table(exec_summary, colWidths=[3.1*inch, 2.1*inch])
        exec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(exec_table)
        story.append(Spacer(1, 20))
        
        # Category Analysis
        if 'categories' in commission_data:
            story.append(Paragraph("Commission Category Analysis", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            category_headers = ['Category', 'Count', 'Total Amount', 'Avg Rate', '% of Sales']
            category_data = [category_headers]
            
            for category, data in commission_data['categories'].items():
                category_data.append([
                    Paragraph(category.replace('_', ' ').title(), category_label_style),
                    Paragraph(str(data['count']), category_center_style),
                    Paragraph(f"{primary_currency} {data['total_amount']:,.2f}", category_value_style),
                    Paragraph(f"{data['avg_rate']:.2f}%", category_value_style),
                    Paragraph(f"{data['percent_of_sales']:.2f}%", category_value_style)
                ])

            category_table = Table(
                category_data,
                repeatRows=1,
                colWidths=[2.4*inch, 0.8*inch, 1.2*inch, 1.0*inch, 1.0*inch],
            )
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('WORDWRAP', (0, 0), (-1, -1), 'LTR'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(category_table)
            story.append(Spacer(1, 10))
        
        doc.build(story)
        buffer.seek(0)
        
        filename = f"Commission_Profit_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return {
            'content': base64.b64encode(buffer.read()),
            'filename': filename,
            'format': 'pdf',
            'mimetype': 'application/pdf'
        }

    def _generate_partner_statement_json(self, commission_data, wizard_data):
        """Generate JSON partner statement report"""
        report_json = {
            'report_type': 'commission_partner_statement',
            'generated_at': datetime.now().isoformat(),
            'filters': wizard_data,
            'data': commission_data,
            'summary': {
                'record_count': len(commission_data['report_data']),
                'totals': commission_data['totals']
            }
        }
        
        filename = f"Commission_Partner_Statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return {
            'content': base64.b64encode(json.dumps(report_json, indent=2, default=str).encode()),
            'filename': filename,
            'format': 'json',
            'mimetype': 'application/json'
        }

    def _generate_profit_analysis_json(self, commission_data, wizard_data):
        """Generate JSON profit analysis report"""
        report_json = {
            'report_type': 'commission_profit_analysis',
            'generated_at': datetime.now().isoformat(),
            'filters': wizard_data,
            'data': commission_data,
            'summary': {
                'record_count': len(commission_data['report_data']),
                'totals': commission_data['totals'],
                'categories': commission_data.get('categories', {})
            }
        }
        
        filename = f"Commission_Profit_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return {
            'content': base64.b64encode(json.dumps(report_json, indent=2, default=str).encode()),
            'filename': filename,
            'format': 'json',
            'mimetype': 'application/json'
        }

    def _generate_profit_analysis_excel(self, commission_data, wizard_data):
        """Generate Excel profit analysis report"""
        if not XLSXWRITER_AVAILABLE:
            raise UserError(_("XlsxWriter library is required for Excel generation. Please install: pip install xlsxwriter"))
        
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        
        # Create formats
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#3498db',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        currency_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        percent_format = workbook.add_format({'num_format': '0.00%', 'border': 1})
        normal_format = workbook.add_format({'border': 1})
        
        # Executive Summary worksheet
        exec_ws = workbook.add_worksheet('Executive Summary')
        totals = commission_data['totals']
        net_profit = totals['total_sales'] - totals['total_commissions']
        profit_margin = (net_profit / totals['total_sales']) if totals['total_sales'] > 0 else 0
        
        exec_data = [
            ['Metric', 'Value'],
            ['Total Sales Revenue', totals['total_sales']],
            ['Total Commission Cost', totals['total_commissions']],
            ['External Commission Cost', totals['external_commissions']],
            ['Internal Commission Investment', totals['internal_commissions']],
            ['Net Profit After Commissions', net_profit],
            ['Profit Margin', profit_margin],
            ['Commission Rate', (totals['total_commissions'] / totals['total_sales']) if totals['total_sales'] > 0 else 0],
        ]
        
        for row, (label, value) in enumerate(exec_data):
            if row == 0:
                exec_ws.write(row, 0, label, header_format)
                exec_ws.write(row, 1, value, header_format)
            else:
                exec_ws.write(row, 0, label, normal_format)
                if 'Margin' in label or 'Rate' in label:
                    exec_ws.write(row, 1, value, percent_format)
                else:
                    exec_ws.write(row, 1, value, currency_format)
        
        # Category Analysis worksheet
        if 'categories' in commission_data:
            cat_ws = workbook.add_worksheet('Category Analysis')
            
            cat_headers = ['Category', 'Count', 'Total Amount', 'Average Rate', '% of Total Sales']
            for col, header in enumerate(cat_headers):
                cat_ws.write(0, col, header, header_format)
            
            row = 1
            for category, data in commission_data['categories'].items():
                cat_ws.write(row, 0, category.replace('_', ' ').title(), normal_format)
                cat_ws.write(row, 1, data['count'], normal_format)
                cat_ws.write(row, 2, data['total_amount'], currency_format)
                cat_ws.write(row, 3, data['avg_rate'] / 100, percent_format)
                cat_ws.write(row, 4, data['percent_of_sales'] / 100, percent_format)
                row += 1
        
        # Detailed Data worksheet
        detail_ws = workbook.add_worksheet('Detailed Data')
        
        headers = [
            'Commission Partner', 'Booking Date', 'Client Order Ref', 'Sale Order',
            'Unit Price', 'Commission Rate (%)', 'Commission Amount', 'Status',
            'Category', 'Profit Impact (%)', 'Currency'
        ]
        
        for col, header in enumerate(headers):
            detail_ws.write(0, col, header, header_format)
        
        row = 1
        for line in commission_data['report_data']:
            detail_ws.write(row, 0, line['partner_name'], normal_format)
            detail_ws.write(row, 1, line['booking_date'], normal_format)
            detail_ws.write(row, 2, line['client_order_ref'], normal_format)
            detail_ws.write(row, 3, line['sale_order_name'], normal_format)
            detail_ws.write(row, 4, line['unit_price'], currency_format)
            detail_ws.write(row, 5, line['commission_rate'], normal_format)
            detail_ws.write(row, 6, line['commission_amount'], currency_format)
            detail_ws.write(row, 7, line['commission_status'], normal_format)
            detail_ws.write(row, 8, line['commission_category'].replace('_', ' ').title(), normal_format)
            detail_ws.write(row, 9, line['profit_impact_percentage'] / 100, percent_format)
            detail_ws.write(row, 10, line['currency'], normal_format)
            row += 1
        
        workbook.close()
        buffer.seek(0)
        
        filename = f"Commission_Profit_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return {
            'content': base64.b64encode(buffer.read()),
            'filename': filename,
            'format': 'excel',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }