# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
import base64
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("xlsxwriter not installed. Excel reports will not be available.")
    xlsxwriter = None


class OrderStatusReport(models.TransientModel):
    """Wizard for generating various order status reports"""
    _name = 'order.status.report'
    _description = 'Order Status Report Generator'

    # Date Range Fields
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.today
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )
    
    # Filter Fields
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        help="Leave empty to include all customers"
    )
    status_ids = fields.Many2many(
        'order.status',
        string='Status Filter',
        help="Leave empty to include all statuses"
    )
    user_ids = fields.Many2many(
        'res.users',
        string='Responsible Users',
        help="Leave empty to include all users"
    )
    
    # Report Configuration
    report_type = fields.Selection([
        ('customer_invoice', 'Customer Invoice/Payment Receipt'),
        ('commission_payout', 'Commission Payout Report'),
        ('purchase_vendor', 'Purchase Orders/Vendor Bills'),
        ('payment_summary', 'Total Payment Out Summary'),
        ('comprehensive', 'Comprehensive Report'),
    ], string='Report Type', required=True, default='comprehensive')
    
    output_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('excel', 'Excel Export'),
    ], string='Output Format', default='pdf')
    
    include_details = fields.Boolean(
        string='Include Order Line Details',
        default=True
    )
    include_history = fields.Boolean(
        string='Include Status History',
        default=True
    )
    group_by_partner = fields.Boolean(
        string='Group by Customer',
        default=False
    )

    def _get_report_domain(self):
        """Build domain for report data filtering"""
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('custom_status_id', '!=', False),  # Only orders with custom status
        ]
        
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        
        if self.status_ids:
            domain.append(('custom_status_id', 'in', self.status_ids.ids))
            
        if self.user_ids:
            domain.extend([
                '|', '|',
                ('documentation_user_id', 'in', self.user_ids.ids),
                ('commission_user_id', 'in', self.user_ids.ids),
                ('final_review_user_id', 'in', self.user_ids.ids),
            ])
        
        return domain

    def _get_report_data(self):
        """Fetch and prepare report data"""
        domain = self._get_report_domain()
        orders = self.env['sale.order'].search(domain, order='date_order desc, name desc')
        
        if not orders:
            raise UserError(_("No orders found matching the selected criteria."))
        
        data = {
            'orders': orders,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_type': self.report_type,
            'include_details': self.include_details,
            'include_history': self.include_history,
            'group_by_partner': self.group_by_partner,
            'total_orders': len(orders),
            'total_amount': sum(orders.mapped('amount_total')),
            'total_commission': sum(orders.mapped('total_commission_amount')),
            'total_payment_out': sum(orders.mapped('total_payment_out')),
        }
        
        if self.group_by_partner:
            # Group orders by customer
            partner_groups = {}
            for order in orders:
                partner_id = order.partner_id.id
                if partner_id not in partner_groups:
                    partner_groups[partner_id] = {
                        'partner': order.partner_id,
                        'orders': self.env['sale.order'],
                        'total_amount': 0.0,
                        'total_commission': 0.0,
                        'total_payment_out': 0.0,
                    }
                partner_groups[partner_id]['orders'] |= order
                partner_groups[partner_id]['total_amount'] += order.amount_total
                partner_groups[partner_id]['total_commission'] += order.total_commission_amount
                partner_groups[partner_id]['total_payment_out'] += order.total_payment_out
            
            data['partner_groups'] = partner_groups
        
        return data

    def action_generate_pdf_report(self):
        """Generate PDF report based on selected type"""
        self.ensure_one()
        data = self._get_report_data()
        
        report_map = {
            'customer_invoice': 'order_status_override.report_customer_invoice',
            'commission_payout': 'order_status_override.report_commission_payout',
            'purchase_vendor': 'order_status_override.report_purchase_vendor',
            'payment_summary': 'order_status_override.report_payment_summary',
            'comprehensive': 'order_status_override.report_comprehensive',
        }
        
        report_name = report_map.get(self.report_type)
        if not report_name:
            raise UserError(_("Invalid report type selected."))
        
        try:
            report = self.env.ref(report_name)
            return report.report_action(data['orders'], data=data)
        except Exception as e:
            _logger.error(f"Error generating PDF report: {str(e)}")
            raise UserError(_("Error generating report: %s") % str(e))

    def action_generate_excel_report(self):
        """Generate Excel export based on selected type"""
        self.ensure_one()
        
        if not xlsxwriter:
            raise UserError(_("xlsxwriter library is required for Excel exports. Please install it."))
        
        data = self._get_report_data()
        
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        try:
            if self.report_type == 'customer_invoice':
                self._create_customer_invoice_excel(workbook, data)
            elif self.report_type == 'commission_payout':
                self._create_commission_payout_excel(workbook, data)
            elif self.report_type == 'purchase_vendor':
                self._create_purchase_vendor_excel(workbook, data)
            elif self.report_type == 'payment_summary':
                self._create_payment_summary_excel(workbook, data)
            elif self.report_type == 'comprehensive':
                self._create_comprehensive_excel(workbook, data)
            
            workbook.close()
            output.seek(0)
            
            # Create attachment
            filename = f"{self.report_type}_report_{fields.Date.today()}.xlsx"
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(output.read()),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
            
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'self',
            }
            
        except Exception as e:
            _logger.error(f"Error generating Excel report: {str(e)}")
            raise UserError(_("Error generating Excel report: %s") % str(e))
        finally:
            output.close()

    def _create_customer_invoice_excel(self, workbook, data):
        """Create Customer Invoice Excel Report"""
        worksheet = workbook.add_worksheet('Customer Invoice Report')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center',
            'bg_color': '#4CAF50', 'font_color': 'white'
        })
        subheader_format = workbook.add_format({
            'bold': True, 'bg_color': '#E8F5E8', 'border': 1
        })
        data_format = workbook.add_format({'border': 1})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        date_format = workbook.add_format({'border': 1, 'num_format': 'yyyy-mm-dd'})
        
        # Header
        worksheet.merge_range('A1:H1', 'Customer Invoice/Payment Receipt Report', header_format)
        worksheet.merge_range('A2:H2', f"Period: {data['date_from']} to {data['date_to']}", subheader_format)
        
        # Column headers
        headers = ['Order Ref', 'Customer', 'Order Date', 'Status', 'Total Amount', 'Commission', 'Payment Out', 'Net Profit']
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, subheader_format)
        
        # Data rows
        row = 4
        for order in data['orders']:
            net_profit = order.amount_total - order.total_payment_out
            worksheet.write(row, 0, order.name, data_format)
            worksheet.write(row, 1, order.partner_id.name, data_format)
            worksheet.write(row, 2, order.date_order, date_format)
            worksheet.write(row, 3, order.custom_status_id.name, data_format)
            worksheet.write(row, 4, order.amount_total, money_format)
            worksheet.write(row, 5, order.total_commission_amount, money_format)
            worksheet.write(row, 6, order.total_payment_out, money_format)
            worksheet.write(row, 7, net_profit, money_format)
            row += 1
        
        # Totals
        worksheet.write(row, 3, 'TOTAL:', subheader_format)
        worksheet.write(row, 4, data['total_amount'], money_format)
        worksheet.write(row, 5, data['total_commission'], money_format)
        worksheet.write(row, 6, data['total_payment_out'], money_format)
        worksheet.write(row, 7, data['total_amount'] - data['total_payment_out'], money_format)
        
        # Auto-adjust column widths
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:H', 12)

    def _create_commission_payout_excel(self, workbook, data):
        """Create Commission Payout Excel Report"""
        worksheet = workbook.add_worksheet('Commission Payout Report')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center',
            'bg_color': '#FF9800', 'font_color': 'white'
        })
        subheader_format = workbook.add_format({
            'bold': True, 'bg_color': '#FFF3E0', 'border': 1
        })
        data_format = workbook.add_format({'border': 1})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        
        # Header
        worksheet.merge_range('A1:G1', 'Commission Payout Report', header_format)
        worksheet.merge_range('A2:G2', f"Period: {data['date_from']} to {data['date_to']}", subheader_format)
        
        # Column headers
        headers = ['Order Ref', 'Customer', 'Commission Type', 'User/Partner', 'Rate/Amount', 'Commission', 'Status']
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, subheader_format)
        
        # Data rows
        row = 4
        for order in data['orders']:
            # Internal commissions
            for comm in order.internal_commission_ids:
                worksheet.write(row, 0, order.name, data_format)
                worksheet.write(row, 1, order.partner_id.name, data_format)
                worksheet.write(row, 2, 'Internal', data_format)
                worksheet.write(row, 3, comm.user_id.name, data_format)
                worksheet.write(row, 4, f"{comm.commission_rate}%" if comm.commission_rate else 'Fixed', data_format)
                worksheet.write(row, 5, comm.amount_fixed, money_format)
                worksheet.write(row, 6, comm.state or 'Draft', data_format)
                row += 1
            
            # External commissions
            for comm in order.external_commission_ids:
                worksheet.write(row, 0, order.name, data_format)
                worksheet.write(row, 1, order.partner_id.name, data_format)
                worksheet.write(row, 2, 'External', data_format)
                worksheet.write(row, 3, comm.partner_id.name, data_format)
                worksheet.write(row, 4, f"{comm.commission_rate}%" if comm.commission_rate else 'Fixed', data_format)
                worksheet.write(row, 5, comm.amount_fixed, money_format)
                worksheet.write(row, 6, comm.state or 'Draft', data_format)
                row += 1
        
        # Auto-adjust column widths
        worksheet.set_column('A:B', 15)
        worksheet.set_column('C:G', 12)

    def _create_comprehensive_excel(self, workbook, data):
        """Create Comprehensive Excel Report with multiple sheets"""
        # Summary sheet
        summary_ws = workbook.add_worksheet('Summary')
        self._create_summary_sheet(workbook, summary_ws, data)
        
        # Order details sheet
        details_ws = workbook.add_worksheet('Order Details')
        self._create_order_details_sheet(workbook, details_ws, data)
        
        # Commission details sheet
        commission_ws = workbook.add_worksheet('Commission Details')
        self._create_commission_details_sheet(workbook, commission_ws, data)
        
        if data['include_history']:
            # Status history sheet
            history_ws = workbook.add_worksheet('Status History')
            self._create_status_history_sheet(workbook, history_ws, data)

    def _create_summary_sheet(self, workbook, worksheet, data):
        """Create summary sheet for comprehensive report"""
        # Define formats
        title_format = workbook.add_format({
            'bold': True, 'font_size': 16, 'align': 'center',
            'bg_color': '#2196F3', 'font_color': 'white'
        })
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#E3F2FD', 'border': 1
        })
        data_format = workbook.add_format({'border': 1})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        
        # Title
        worksheet.merge_range('A1:F1', 'Order Status Report - Summary', title_format)
        worksheet.merge_range('A2:F2', f"Period: {data['date_from']} to {data['date_to']}", header_format)
        
        # Summary statistics
        row = 4
        summary_data = [
            ('Total Orders', data['total_orders']),
            ('Total Amount', data['total_amount']),
            ('Total Commission', data['total_commission']),
            ('Total Payment Out', data['total_payment_out']),
            ('Net Profit', data['total_amount'] - data['total_payment_out']),
        ]
        
        worksheet.write(row, 0, 'Metric', header_format)
        worksheet.write(row, 1, 'Value', header_format)
        row += 1
        
        for metric, value in summary_data:
            worksheet.write(row, 0, metric, data_format)
            if isinstance(value, (int, float)) and 'Amount' in metric or 'Commission' in metric or 'Payment' in metric or 'Profit' in metric:
                worksheet.write(row, 1, value, money_format)
            else:
                worksheet.write(row, 1, value, data_format)
            row += 1

    def _create_order_details_sheet(self, workbook, worksheet, data):
        """Create order details sheet"""
        # Implementation for order details
        pass  # Detailed implementation would go here

    def _create_commission_details_sheet(self, workbook, worksheet, data):
        """Create commission details sheet"""
        # Implementation for commission details
        pass  # Detailed implementation would go here

    def _create_status_history_sheet(self, workbook, worksheet, data):
        """Create status history sheet"""
        # Implementation for status history
        pass  # Detailed implementation would go here

    def action_generate_report(self):
        """Generate report based on output format"""
        self.ensure_one()
        
        if self.output_format == 'pdf':
            return self.action_generate_pdf_report()
        elif self.output_format == 'excel':
            return self.action_generate_excel_report()
        else:
            raise UserError(_("Invalid output format selected."))

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Update form behavior based on report type"""
        if self.report_type in ['customer_invoice', 'payment_summary']:
            self.include_details = True
        elif self.report_type == 'commission_payout':
            self.include_details = False
            self.include_history = False
