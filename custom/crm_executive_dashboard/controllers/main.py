# -*- coding: utf-8 -*-

import json
from odoo import http, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CRMExecutiveDashboardController(http.Controller):

    @http.route('/crm/dashboard/data', type='json', auth='user', methods=['POST'])
    def get_dashboard_data(self, date_from=None, date_to=None, team_ids=None, **kwargs):
        """Get dashboard data via AJAX"""
        try:
            # Validate user permissions
            if not request.env.user.has_group('sales_team.group_sale_salesman'):
                raise AccessError(_("You don't have permission to access CRM dashboard"))

            # Get dashboard data
            dashboard_model = request.env['crm.executive.dashboard']
            data = dashboard_model.get_dashboard_data(date_from, date_to, team_ids)
            
            return {
                'success': True,
                'data': data
            }
            
        except Exception as e:
            _logger.error(f"Error in get_dashboard_data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/crm/dashboard/overdue', type='json', auth='user', methods=['POST'])
    def get_overdue_opportunities(self, team_ids=None, **kwargs):
        """Get overdue opportunities"""
        try:
            dashboard_model = request.env['crm.executive.dashboard']
            data = dashboard_model.get_overdue_opportunities(team_ids)
            
            return {
                'success': True,
                'data': data
            }
            
        except Exception as e:
            _logger.error(f"Error in get_overdue_opportunities: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/crm/dashboard/performers', type='json', auth='user', methods=['POST'])
    def get_top_performers(self, date_from=None, date_to=None, limit=5, **kwargs):
        """Get top performing sales people"""
        try:
            dashboard_model = request.env['crm.executive.dashboard']
            data = dashboard_model.get_top_performers(date_from, date_to, limit)
            
            return {
                'success': True,
                'data': data
            }
            
        except Exception as e:
            _logger.error(f"Error in get_top_performers: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/crm/dashboard/export', type='http', auth='user', methods=['GET'])
    def export_dashboard_data(self, date_from=None, date_to=None, team_ids=None, format='xlsx', **kwargs):
        """Export dashboard data to Excel/CSV"""
        try:
            # Validate user permissions
            if not request.env.user.has_group('sales_team.group_sale_manager'):
                raise AccessError(_("You don't have permission to export CRM dashboard data"))

            dashboard_model = request.env['crm.executive.dashboard']
            data = dashboard_model.get_dashboard_data(date_from, date_to, team_ids)
            
            if format == 'xlsx':
                return self._export_to_excel(data, date_from, date_to)
            else:
                return self._export_to_csv(data, date_from, date_to)
                
        except Exception as e:
            _logger.error(f"Error in export_dashboard_data: {str(e)}")
            return request.make_response(
                f"Error exporting data: {str(e)}", 
                status=500
            )

    def _export_to_excel(self, data, date_from, date_to):
        """Export data to Excel format"""
        try:
            import io
            import xlsxwriter
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            
            # Create worksheets
            kpi_sheet = workbook.add_worksheet('KPIs')
            trends_sheet = workbook.add_worksheet('Trends')
            teams_sheet = workbook.add_worksheet('Team Performance')
            
            # Format styles
            header_format = workbook.add_format({
                'bold': True, 
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            number_format = workbook.add_format({'num_format': '#,##0.00'})
            
            # Write KPI data
            kpi_sheet.write('A1', 'KPI', header_format)
            kpi_sheet.write('B1', 'Value', header_format)
            
            row = 1
            for key, value in data.get('kpis', {}).items():
                kpi_sheet.write(row, 0, key.replace('_', ' ').title())
                kpi_sheet.write(row, 1, value, number_format if isinstance(value, (int, float)) else None)
                row += 1
            
            # Write trend data
            trends = data.get('trends', {})
            if trends.get('labels'):
                trends_sheet.write('A1', 'Month', header_format)
                trends_sheet.write('B1', 'Leads', header_format)
                trends_sheet.write('C1', 'Opportunities', header_format)
                trends_sheet.write('D1', 'Won Revenue', header_format)
                trends_sheet.write('E1', 'Expected Revenue', header_format)
                
                for i, label in enumerate(trends['labels']):
                    trends_sheet.write(i + 1, 0, label)
                    trends_sheet.write(i + 1, 1, trends['leads'][i])
                    trends_sheet.write(i + 1, 2, trends['opportunities'][i])
                    trends_sheet.write(i + 1, 3, trends['won_revenue'][i], number_format)
                    trends_sheet.write(i + 1, 4, trends['expected_revenue'][i], number_format)
            
            # Write team performance data
            team_perf = data.get('team_performance', {})
            if team_perf.get('labels'):
                teams_sheet.write('A1', 'Team', header_format)
                teams_sheet.write('B1', 'Opportunities', header_format)
                teams_sheet.write('C1', 'Won Revenue', header_format)
                teams_sheet.write('D1', 'Conversion Rate %', header_format)
                
                for i, label in enumerate(team_perf['labels']):
                    teams_sheet.write(i + 1, 0, label)
                    teams_sheet.write(i + 1, 1, team_perf['opportunities'][i])
                    teams_sheet.write(i + 1, 2, team_perf['won_revenue'][i], number_format)
                    teams_sheet.write(i + 1, 3, team_perf['conversion_rates'][i])
            
            workbook.close()
            output.seek(0)
            
            response = request.make_response(
                output.read(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename=crm_dashboard_{date_from}_{date_to}.xlsx')
                ]
            )
            output.close()
            return response
            
        except ImportError:
            # Fallback to CSV if xlsxwriter is not available
            return self._export_to_csv(data, date_from, date_to)
        except Exception as e:
            _logger.error(f"Error creating Excel export: {str(e)}")
            raise

    def _export_to_csv(self, data, date_from, date_to):
        """Export data to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write KPI data
        writer.writerow(['CRM Dashboard Export', f'Period: {date_from} to {date_to}'])
        writer.writerow([])
        writer.writerow(['KPI', 'Value'])
        
        for key, value in data.get('kpis', {}).items():
            writer.writerow([key.replace('_', ' ').title(), value])
        
        csv_data = output.getvalue()
        output.close()
        
        response = request.make_response(
            csv_data,
            headers=[
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', f'attachment; filename=crm_dashboard_{date_from}_{date_to}.csv')
            ]
        )
        return response
