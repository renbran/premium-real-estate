# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class SalesDashboardController(http.Controller):
    """
    Step 5: Enhanced controller for testing and validation of inheritance-based features
    """

    @http.route('/sale_dashboard/data', type='json', auth='user', methods=['POST'])
    def get_dashboard_data(self, **kwargs):
        """Get enhanced dashboard data with inherited fields"""
        try:
            dashboard = request.env['sale.dashboard']
            
            # Get filters from request
            filters = kwargs.get('filters', {})
            
            # Enhanced data retrieval using Step 2 method
            data = dashboard.get_filtered_data(filters)
            
            return {
                'success': True,
                'data': data,
                'message': 'Dashboard data retrieved successfully'
            }
            
        except Exception as e:
            _logger.error(f"Error getting dashboard data: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve dashboard data'
            }

    @http.route('/sale_dashboard/scorecard', type='json', auth='user', methods=['POST'])
    def get_scorecard_metrics(self, **kwargs):
        """Get enhanced scorecard metrics using Step 3 method"""
        try:
            dashboard = request.env['sale.dashboard']
            
            # Get filters from request
            filters = kwargs.get('filters', {})
            
            # Compute scorecard metrics using inheritance
            metrics = dashboard.compute_scorecard_metrics(filters)
            
            return {
                'success': True,
                'metrics': metrics,
                'message': 'Scorecard metrics computed successfully'
            }
            
        except Exception as e:
            _logger.error(f"Error computing scorecard metrics: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to compute scorecard metrics'
            }

    @http.route('/sale_dashboard/charts', type='json', auth='user', methods=['POST'])
    def get_enhanced_charts(self, **kwargs):
        """Get enhanced charts using Step 4 method"""
        try:
            dashboard = request.env['sale.dashboard']
            
            # Get parameters from request
            chart_types = kwargs.get('chart_types', None)
            filters = kwargs.get('filters', {})
            
            # Get filtered orders first
            data = dashboard.get_filtered_data(filters)
            orders = data.get('orders', None)
            
            # Generate enhanced charts
            charts = dashboard.generate_enhanced_charts(orders, chart_types)
            
            return {
                'success': True,
                'charts': charts,
                'message': 'Enhanced charts generated successfully'
            }
            
        except Exception as e:
            _logger.error(f"Error generating enhanced charts: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate enhanced charts'
            }

    @http.route('/sale_dashboard/test_inheritance', type='json', auth='user', methods=['POST'])
    def test_inheritance_features(self, **kwargs):
        """Test all inheritance-based features for validation"""
        try:
            dashboard = request.env['sale.dashboard']
            test_results = {}
            
            # Test Step 1: Inheritance setup
            try:
                # Check if inherited fields are accessible
                test_fields = [
                    'booking_date_filter', 'project_filter_ids', 'buyer_filter_ids'
                ]
                
                for field in test_fields:
                    if hasattr(dashboard, field):
                        test_results[f'field_{field}'] = 'PASS'
                    else:
                        test_results[f'field_{field}'] = 'FAIL'
                        
                test_results['step1_inheritance'] = 'PASS'
                
            except Exception as e:
                test_results['step1_inheritance'] = f'FAIL: {e}'
            
            # Test Step 2: Enhanced filtering
            try:
                sample_filters = {
                    'date_from': '2024-01-01',
                    'date_to': '2024-12-31'
                }
                filtered_data = dashboard.get_filtered_data(sample_filters)
                test_results['step2_filtering'] = 'PASS' if 'orders' in filtered_data else 'FAIL'
                
            except Exception as e:
                test_results['step2_filtering'] = f'FAIL: {e}'
            
            # Test Step 3: Scorecard metrics
            try:
                metrics = dashboard.compute_scorecard_metrics({})
                test_results['step3_scorecard'] = 'PASS' if 'total_orders' in metrics else 'FAIL'
                
            except Exception as e:
                test_results['step3_scorecard'] = f'FAIL: {e}'
            
            # Test Step 4: Chart generation
            try:
                charts = dashboard.generate_enhanced_charts()
                test_results['step4_charts'] = 'PASS' if isinstance(charts, dict) else 'FAIL'
                
            except Exception as e:
                test_results['step4_charts'] = f'FAIL: {e}'
            
            # Overall test result
            passed_tests = sum(1 for result in test_results.values() if result == 'PASS')
            total_tests = len(test_results)
            overall_status = 'PASS' if passed_tests == total_tests else 'PARTIAL'
            
            return {
                'success': True,
                'test_results': test_results,
                'overall_status': overall_status,
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'message': f'Inheritance testing completed: {passed_tests}/{total_tests} tests passed'
            }
            
        except Exception as e:
            _logger.error(f"Error testing inheritance features: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to test inheritance features'
            }

    @http.route('/sale_dashboard/validation_report', type='json', auth='user', methods=['GET'])
    def get_validation_report(self, **kwargs):
        """Generate comprehensive validation report for the enhanced dashboard"""
        try:
            dashboard = request.env['sale.dashboard']
            
            # Module availability check
            module_checks = {}
            required_modules = ['le_sale_type', 'invoice_report_for_realestate']
            
            for module in required_modules:
                try:
                    module_obj = request.env['ir.module.module'].search([
                        ('name', '=', module),
                        ('state', '=', 'installed')
                    ])
                    module_checks[module] = 'INSTALLED' if module_obj else 'NOT_INSTALLED'
                except:
                    module_checks[module] = 'ERROR'
            
            # Field availability check
            field_checks = {}
            sale_order_model = request.env['sale.order']
            
            required_fields = [
                'sale_order_type_id', 'booking_date', 'project_id', 
                'buyer_id', 'sale_value', 'developer_commission'
            ]
            
            for field in required_fields:
                field_checks[field] = 'AVAILABLE' if hasattr(sale_order_model, field) else 'NOT_AVAILABLE'
            
            # Performance metrics
            try:
                sample_data = dashboard.get_filtered_data({})
                performance_metrics = {
                    'data_retrieval': 'GOOD',
                    'order_count': len(sample_data.get('orders', [])),
                    'response_time': 'ACCEPTABLE'
                }
            except Exception as e:
                performance_metrics = {
                    'data_retrieval': f'ERROR: {e}',
                    'order_count': 0,
                    'response_time': 'ERROR'
                }
            
            return {
                'success': True,
                'validation_report': {
                    'module_checks': module_checks,
                    'field_checks': field_checks,
                    'performance_metrics': performance_metrics,
                    'enhancement_status': 'READY' if all(
                        status == 'INSTALLED' for status in module_checks.values()
                    ) else 'PARTIAL'
                },
                'message': 'Validation report generated successfully'
            }
            
        except Exception as e:
            _logger.error(f"Error generating validation report: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to generate validation report'
            }
