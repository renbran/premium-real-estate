""" controller for xlsx report """
# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Haseen (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape


class XLSXReportController(http.Controller):
    """ controller for xlsx report """

    @http.route('/xlsx_report', type='http', auth='user', methods=['POST'],
                csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name):
        """ Get xlsx report data with enhanced error handling """
        try:
            # Validate inputs to prevent 'undefined' errors
            if not report_name or report_name == 'undefined':
                report_name = f'Statement_Report_{http.request.env.user.id}'
            
            if not model:
                raise ValueError("Model parameter is required")
                
            if not options:
                raise ValueError("Options parameter is required")

            report_obj = request.env[model].sudo()
            options = json.loads(options)
            
            # Add validation for options
            if not isinstance(options, dict):
                raise ValueError("Invalid options format")
            
            if output_format == 'xlsx':
                # Create response with proper headers
                response = request.make_response(
                    None, headers=[
                        ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                        ('Content-Disposition', content_disposition(f'{report_name}.xlsx')),
                        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                        ('Pragma', 'no-cache'),
                        ('Expires', '0')
                    ])
                
                # Generate the report
                report_obj.get_xlsx_report(options, response)
                response.set_cookie('fileToken', 'dummy token')
                return response
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
        except json.JSONDecodeError as e:
            return request.make_response(
                f"Invalid JSON in options: {str(e)}", 
                status=400, 
                headers=[('Content-Type', 'text/plain')]
            )
        except ValueError as e:
            return request.make_response(
                f"Validation error: {str(e)}", 
                status=400, 
                headers=[('Content-Type', 'text/plain')]
            )
        except Exception as e:
            serialize = http.serialize_exception(e)
            return request.make_response(
                f"Error generating report: {str(e)}", 
                status=500, 
                headers=[('Content-Type', 'text/plain')]
            )
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': serialize
            }
            return request.make_response(html_escape(json.dumps(error)))
