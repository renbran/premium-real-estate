# -*- coding: utf-8 -*-

import json
from odoo import http, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CRMStrategicDashboardController(http.Controller):

    @http.route('/crm/strategic/dashboard/data', type='json', auth='user', methods=['POST'])
    def get_strategic_dashboard_data(self, date_from=None, date_to=None, team_ids=None, **kwargs):
        """Get strategic dashboard data via AJAX"""
        try:
            # Validate user permissions
            if not request.env.user.has_group('sales_team.group_sale_manager'):
                raise AccessError(_("You don't have permission to access Strategic CRM dashboard"))

            # Get strategic dashboard data
            dashboard_model = request.env['crm.strategic.dashboard']
            data = dashboard_model.get_strategic_dashboard_data(date_from, date_to, team_ids)
            
            return {
                'success': True,
                'data': data
            }
            
        except Exception as e:
            _logger.error(f"Error in get_strategic_dashboard_data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/crm/strategic/dashboard/export', type='http', auth='user', methods=['GET'])
    def export_strategic_dashboard_data(self, date_from=None, date_to=None, team_ids=None, format='xlsx', **kwargs):
        """Export strategic dashboard data to Excel/CSV"""
        try:
            # Validate user permissions
            if not request.env.user.has_group('sales_team.group_sale_manager'):
                raise AccessError(_("You don't have permission to export Strategic CRM dashboard data"))

            # Validate parameters
            if not date_from or not date_to:
                return request.make_response(
                    "Missing required parameters: date_from and date_to",
                    status=400
                )

            # Parse team_ids if provided as string
            if team_ids and isinstance(team_ids, str):
                try:
                    team_ids = [int(x) for x in team_ids.split(',') if x.strip()]
                except ValueError:
                    team_ids = None

            dashboard_model = request.env['crm.strategic.dashboard']
            data = dashboard_model.get_strategic_dashboard_data(date_from, date_to, team_ids)
            
            # Check if data was retrieved successfully
            if 'error' in data:
                return request.make_response(
                    f"Error retrieving dashboard data: {data['error']}",
                    status=500
                )
            
            if format == 'xlsx':
                return self._export_strategic_to_excel(data, date_from, date_to)
            else:
                return self._export_strategic_to_csv(data, date_from, date_to)
                
        except Exception as e:
            _logger.error(f"Error in export_strategic_dashboard_data: {str(e)}")
            return request.make_response(
                f"Error exporting data: {str(e)}", 
                status=500
            )

    def _export_strategic_to_excel(self, data, date_from, date_to):
        """Export strategic data to Excel format"""
        try:
            # Check if xlsxwriter is available
            try:
                import xlsxwriter
            except ImportError:
                _logger.warning("xlsxwriter not available, falling back to CSV export")
                return self._export_strategic_to_csv(data, date_from, date_to)
            
            import io
            from datetime import datetime
            
            # Validate data structure
            if not isinstance(data, dict) or not data:
                raise ValidationError(_("Invalid dashboard data provided"))
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            
            # Create worksheets
            summary_sheet = workbook.add_worksheet('Strategic Summary')
            kpi_sheet = workbook.add_worksheet('KPIs')
            financial_sheet = workbook.add_worksheet('Financial Performance')
            team_sheet = workbook.add_worksheet('Team Performance')
            risk_sheet = workbook.add_worksheet('Risk Analysis')
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'bg_color': '#366092',
                'font_color': 'white',
                'align': 'center'
            })
            
            subheader_format = workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#D9E1F2',
                'align': 'center'
            })
            
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})
            percent_format = workbook.add_format({'num_format': '0.00%'})
            number_format = workbook.add_format({'num_format': '#,##0'})
            
            # Summary Sheet
            summary_sheet.merge_range('A1:F1', 'Strategic CRM Dashboard Report', header_format)
            summary_sheet.write('A2', f'Period: {date_from} to {date_to}')
            summary_sheet.write('A3', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            
            # KPI Sheet
            kpi_sheet.merge_range('A1:D1', 'Strategic KPIs', header_format)
            kpi_headers = ['Metric', 'Value', 'Type', 'Comments']
            for col, header in enumerate(kpi_headers):
                kpi_sheet.write(1, col, header, subheader_format)
            
            # KPI data
            strategic_kpis = data.get('strategic_kpis', {})
            kpi_data = [
                ['Total Pipeline Value', strategic_kpis.get('total_pipeline_value', 0), 'Currency', 'Total value of active opportunities'],
                ['Revenue Growth', strategic_kpis.get('revenue_growth', 0), 'Percentage', 'Period-over-period growth'],
                ['Average Sales Cycle', strategic_kpis.get('avg_sales_cycle', 0), 'Days', 'Average days from lead to close'],
                ['Market Penetration', strategic_kpis.get('market_penetration', 0), 'Percentage', 'Share of total market leads'],
                ['New Customers', strategic_kpis.get('new_customers', 0), 'Number', 'New customers acquired in period'],
            ]
            
            for row, (metric, value, type_, comment) in enumerate(kpi_data, 2):
                kpi_sheet.write(row, 0, metric)
                if type_ == 'Currency':
                    kpi_sheet.write(row, 1, value, currency_format)
                elif type_ == 'Percentage':
                    kpi_sheet.write(row, 1, value/100, percent_format)
                elif type_ == 'Number':
                    kpi_sheet.write(row, 1, value, number_format)
                else:
                    kpi_sheet.write(row, 1, value)
                kpi_sheet.write(row, 2, type_)
                kpi_sheet.write(row, 3, comment)
            
            # Team Performance Sheet
            team_sheet.merge_range('A1:G1', 'Team Performance Analysis', header_format)
            team_headers = ['Team Name', 'Revenue', 'Opportunities', 'Won Count', 'Win Rate', 'Target Achievement', 'Team Size']
            for col, header in enumerate(team_headers):
                team_sheet.write(1, col, header, subheader_format)
            
            team_overview = data.get('team_overview', [])
            for row, team in enumerate(team_overview, 2):
                team_sheet.write(row, 0, team.get('team_name', ''))
                team_sheet.write(row, 1, team.get('revenue', 0), currency_format)
                team_sheet.write(row, 2, team.get('opportunities', 0), number_format)
                team_sheet.write(row, 3, team.get('won_count', 0), number_format)
                team_sheet.write(row, 4, team.get('win_rate', 0)/100, percent_format)
                team_sheet.write(row, 5, team.get('target_achievement', 0)/100, percent_format)
                team_sheet.write(row, 6, team.get('team_size', 0), number_format)
            
            # Risk Analysis Sheet
            risk_sheet.merge_range('A1:C1', 'Risk Analysis', header_format)
            risk_headers = ['Risk Factor', 'Count/Value', 'Severity']
            for col, header in enumerate(risk_headers):
                risk_sheet.write(1, col, header, subheader_format)
            
            risk_indicators = data.get('risk_indicators', {})
            risk_data = [
                ['Overdue Opportunities', risk_indicators.get('overdue_opportunities_count', 0), 'High'],
                ['Stagnant Opportunities', risk_indicators.get('stagnant_opportunities_count', 0), 'Medium'],
                ['High-Value at Risk', risk_indicators.get('at_risk_high_value_count', 0), 'High'],
                ['Pipeline Concentration', f"{risk_indicators.get('pipeline_concentration_risk', 0)}%", 
                 'High' if risk_indicators.get('pipeline_concentration_risk', 0) > 50 else 'Medium'],
            ]
            
            for row, (factor, value, severity) in enumerate(risk_data, 2):
                risk_sheet.write(row, 0, factor)
                risk_sheet.write(row, 1, value)
                risk_sheet.write(row, 2, severity)
                
                # Color code severity
                if severity == 'High':
                    risk_format = workbook.add_format({'bg_color': '#FFE6E6'})
                    risk_sheet.write(row, 2, severity, risk_format)
            
            # Adjust column widths
            for sheet in [summary_sheet, kpi_sheet, financial_sheet, team_sheet, risk_sheet]:
                sheet.set_column('A:A', 25)
                sheet.set_column('B:G', 15)
            
            workbook.close()
            output.seek(0)
            
            # Create response
            filename = f'strategic_dashboard_{date_from}_{date_to}.xlsx'
            response = request.make_response(
                output.read(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="{filename}"')
                ]
            )
            return response
            
        except ImportError:
            return request.make_response(
                "xlsxwriter library is required for Excel export",
                status=500
            )
        except Exception as e:
            _logger.error(f"Error in Excel export: {str(e)}")
            return request.make_response(
                f"Error generating Excel file: {str(e)}",
                status=500
            )

    def _export_strategic_to_csv(self, data, date_from, date_to):
        """Export strategic data to CSV format"""
        try:
            import csv
            import io
            from datetime import datetime
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Strategic CRM Dashboard Report'])
            writer.writerow([f'Period: {date_from} to {date_to}'])
            writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Strategic KPIs
            writer.writerow(['STRATEGIC KPIs'])
            writer.writerow(['Metric', 'Value', 'Type'])
            
            strategic_kpis = data.get('strategic_kpis', {})
            kpi_rows = [
                ['Total Pipeline Value', strategic_kpis.get('total_pipeline_value', 0), 'Currency'],
                ['Revenue Growth (%)', strategic_kpis.get('revenue_growth', 0), 'Percentage'],
                ['Average Sales Cycle (days)', strategic_kpis.get('avg_sales_cycle', 0), 'Days'],
                ['Market Penetration (%)', strategic_kpis.get('market_penetration', 0), 'Percentage'],
                ['New Customers', strategic_kpis.get('new_customers', 0), 'Number'],
            ]
            
            for row in kpi_rows:
                writer.writerow(row)
            
            writer.writerow([])
            
            # Team Performance
            writer.writerow(['TEAM PERFORMANCE'])
            writer.writerow(['Team Name', 'Revenue', 'Opportunities', 'Win Rate (%)', 'Target Achievement (%)', 'Team Size'])
            
            team_overview = data.get('team_overview', [])
            for team in team_overview:
                writer.writerow([
                    team.get('team_name', ''),
                    team.get('revenue', 0),
                    team.get('opportunities', 0),
                    team.get('win_rate', 0),
                    team.get('target_achievement', 0),
                    team.get('team_size', 0)
                ])
            
            writer.writerow([])
            
            # Risk Analysis
            writer.writerow(['RISK ANALYSIS'])
            writer.writerow(['Risk Factor', 'Count/Value', 'Severity'])
            
            risk_indicators = data.get('risk_indicators', {})
            risk_rows = [
                ['Overdue Opportunities', risk_indicators.get('overdue_opportunities_count', 0), 'High'],
                ['Stagnant Opportunities', risk_indicators.get('stagnant_opportunities_count', 0), 'Medium'],
                ['High-Value at Risk', risk_indicators.get('at_risk_high_value_count', 0), 'High'],
                ['Pipeline Concentration (%)', risk_indicators.get('pipeline_concentration_risk', 0), 'Variable'],
            ]
            
            for row in risk_rows:
                writer.writerow(row)
            
            # Create response
            filename = f'strategic_dashboard_{date_from}_{date_to}.csv'
            output_bytes = output.getvalue().encode('utf-8')
            
            response = request.make_response(
                output_bytes,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', f'attachment; filename="{filename}"')
                ]
            )
            return response
            
        except Exception as e:
            _logger.error(f"Error in CSV export: {str(e)}")
            return request.make_response(
                f"Error generating CSV file: {str(e)}",
                status=500
            )
