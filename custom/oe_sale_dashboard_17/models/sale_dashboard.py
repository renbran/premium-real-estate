# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class SaleDashboard(models.TransientModel):
    _name = 'sale.dashboard'
    _description = 'Sales Dashboard - Professional Analytics with Real Estate Integration'

    # Dashboard configuration fields - Enhanced with inherited fields
    start_date = fields.Date(string='Start Date', default=lambda self: fields.Date.today().replace(day=1))
    end_date = fields.Date(string='End Date', default=fields.Date.today)
    sale_type_ids = fields.Many2many('sale.order.type', string='Sale Types', help="Filter by sale types from le_sale_type module")
    
    # Enhanced filtering fields from inherited modules
    booking_date_filter = fields.Date(string='Booking Date Filter', help="Filter by booking date from invoice_report_for_realestate")
    project_filter_ids = fields.Many2many('product.template', string='Project Filter', help="Filter by real estate projects")
    buyer_filter_ids = fields.Many2many('res.partner', string='Buyer Filter', help="Filter by buyer from real estate module")

    @api.model
    def format_dashboard_value(self, value):
        """Format large numbers for dashboard display with K/M/B suffixes"""
        if not value or value == 0:
            return "0"
        
        abs_value = abs(value)
        
        if abs_value >= 1_000_000_000:
            formatted = round(value / 1_000_000_000, 2)
            return f"{formatted}B"
        elif abs_value >= 1_000_000:
            formatted = round(value / 1_000_000, 2)
            return f"{formatted}M"
        elif abs_value >= 1_000:
            formatted = round(value / 1_000)
            return f"{formatted:.0f}K"
        else:
            return f"{round(value):.0f}"

    @api.model
    def _get_date_field(self):
        """Get the appropriate date field to use for filtering"""
        sale_order = self.env['sale.order']
        # Check if booking_date field exists (from invoice_report_for_realestate module)
        if hasattr(sale_order, 'booking_date'):
            return 'booking_date'
        return 'date_order'

    @api.model
    def _check_optional_field(self, model_name, field_name):
        """Check if an optional field exists in a model"""
        try:
            model = self.env[model_name]
            return hasattr(model, field_name)
        except Exception:
            return False

    @api.model
    def get_sales_performance_data(self, start_date, end_date, sale_type_ids=None):
        """Get sales performance data with optional sale type filtering"""
        try:
            _logger.info(f"Getting performance data from {start_date} to {end_date}")
            
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if available and requested
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            # Get all sale orders in the date range
            orders = sale_order.search(base_domain)
            
            # Calculate basic metrics
            total_orders = len(orders)
            total_amount = sum(orders.mapped('amount_total'))
            total_quotations = len(orders.filtered(lambda o: o.state in ['draft', 'sent']))
            total_sales = len(orders.filtered(lambda o: o.state in ['sale', 'done']))
            total_invoiced = len(orders.filtered(lambda o: o.invoice_status in ['invoiced', 'upselling']))
            
            return {
                'total_orders': total_orders,
                'total_quotations': total_quotations,
                'total_sales': total_sales,
                'total_invoiced': total_invoiced,
                'total_amount': total_amount,
                'currency_symbol': self.env.company.currency_id.symbol or '$',
                'orders': orders.ids,
                'date_field_used': date_field,
            }
            
        except Exception as e:
            _logger.error(f"Error getting sales performance data: {e}")
            return {
                'total_orders': 0,
                'total_quotations': 0,
                'total_sales': 0,
                'total_invoiced': 0,
                'total_amount': 0,
                'currency_symbol': '$',
                'orders': [],
                'date_field_used': 'date_order',
                'error': str(e),
            }

    @api.model
    def get_filtered_data(self, booking_date=None, sale_order_type_id=None, project_ids=None, buyer_ids=None, start_date=None, end_date=None):
        """Enhanced filtering method - Step 2: Incorporate filtering based on booking_date and sale_order_type_id"""
        try:
            _logger.info(f"Enhanced filtering: booking_date={booking_date}, sale_type={sale_order_type_id}")
            
            sale_order = self.env['sale.order']
            domain = [('state', '!=', 'cancel')]
            
            # Date filtering with priority for booking_date
            if booking_date:
                if self._check_optional_field('sale.order', 'booking_date'):
                    domain.append(('booking_date', '=', booking_date))
                else:
                    # Fallback to date_order if booking_date not available
                    domain.append(('date_order', '=', booking_date))
            elif start_date and end_date:
                date_field = self._get_date_field()
                domain.extend([
                    (date_field, '>=', start_date),
                    (date_field, '<=', end_date)
                ])
            
            # Sale order type filtering (from le_sale_type module)
            if sale_order_type_id and self._check_optional_field('sale.order', 'sale_order_type_id'):
                domain.append(('sale_order_type_id', '=', sale_order_type_id))
            
            # Project filtering (from invoice_report_for_realestate module)
            if project_ids and self._check_optional_field('sale.order', 'project_id'):
                domain.append(('project_id', 'in', project_ids))
            
            # Buyer filtering (from invoice_report_for_realestate module)
            if buyer_ids and self._check_optional_field('sale.order', 'buyer_id'):
                domain.append(('buyer_id', 'in', buyer_ids))
            
            sales_data = sale_order.search(domain)
            
            return {
                'orders': sales_data,
                'count': len(sales_data),
                'total_amount': sum(sales_data.mapped('amount_total')),
                'filters_applied': {
                    'booking_date': booking_date,
                    'sale_order_type_id': sale_order_type_id,
                    'project_ids': project_ids,
                    'buyer_ids': buyer_ids,
                    'date_range': f"{start_date} to {end_date}" if start_date and end_date else None
                }
            }
            
        except Exception as e:
            _logger.error(f"Error in enhanced filtering: {e}")
            return {
                'orders': self.env['sale.order'].browse([]),
                'count': 0,
                'total_amount': 0,
                'error': str(e)
            }

    @api.model
    def compute_scorecard_metrics(self, orders=None, booking_date=None, sale_order_type_id=None):
        """Step 3: Enhanced scorecard with total sales value, total invoiced amount, and total paid amount"""
        try:
            _logger.info("Computing enhanced scorecard metrics")
            
            # Use provided orders or get filtered data
            if orders is None:
                filtered_data = self.get_filtered_data(
                    booking_date=booking_date,
                    sale_order_type_id=sale_order_type_id
                )
                orders = filtered_data['orders']
            
            # Basic sales metrics
            total_sales_value = sum(orders.mapped('amount_total'))
            total_orders_count = len(orders)
            
            # Invoice-related metrics
            total_invoiced_amount = 0
            total_paid_amount = 0
            payment_completion_rate = 0
            
            # Calculate invoiced and paid amounts from related invoices
            for order in orders:
                for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
                    total_invoiced_amount += invoice.amount_total
                    total_paid_amount += invoice.amount_total - invoice.amount_residual
            
            # Calculate payment completion rate
            if total_invoiced_amount > 0:
                payment_completion_rate = (total_paid_amount / total_invoiced_amount) * 100
            
            # Real estate specific metrics (if available)
            total_sale_value_realestate = 0
            total_developer_commission = 0
            
            if self._check_optional_field('sale.order', 'sale_value'):
                total_sale_value_realestate = sum(orders.mapped('sale_value'))
            
            if self._check_optional_field('sale.order', 'developer_commission'):
                total_developer_commission = sum(orders.mapped('developer_commission'))
            
            # Sale type breakdown (if available)
            sale_type_breakdown = {}
            if self._check_optional_field('sale.order', 'sale_order_type_id'):
                sale_types = orders.mapped('sale_order_type_id')
                for sale_type in sale_types:
                    type_orders = orders.filtered(lambda o: o.sale_order_type_id == sale_type)
                    sale_type_breakdown[sale_type.name] = {
                        'count': len(type_orders),
                        'amount': sum(type_orders.mapped('amount_total'))
                    }
            
            # Project breakdown (if available)
            project_breakdown = {}
            if self._check_optional_field('sale.order', 'project_id'):
                projects = orders.mapped('project_id')
                for project in projects:
                    project_orders = orders.filtered(lambda o: o.project_id == project)
                    project_breakdown[project.name] = {
                        'count': len(project_orders),
                        'amount': sum(project_orders.mapped('amount_total'))
                    }
            
            return {
                'total_sales_value': total_sales_value,
                'total_orders_count': total_orders_count,
                'total_invoiced_amount': total_invoiced_amount,
                'total_paid_amount': total_paid_amount,
                'payment_completion_rate': payment_completion_rate,
                'total_sale_value_realestate': total_sale_value_realestate,
                'total_developer_commission': total_developer_commission,
                'sale_type_breakdown': sale_type_breakdown,
                'project_breakdown': project_breakdown,
                'currency_symbol': self.env.company.currency_id.symbol or '$',
            }
            
        except Exception as e:
            _logger.error(f"Error computing scorecard metrics: {e}")
            return {
                'total_sales_value': 0,
                'total_orders_count': 0,
                'total_invoiced_amount': 0,
                'total_paid_amount': 0,
                'payment_completion_rate': 0,
                'total_sale_value_realestate': 0,
                'total_developer_commission': 0,
                'sale_type_breakdown': {},
                'project_breakdown': {},
                'currency_symbol': '$',
                'error': str(e)
            }

    @api.model
    def generate_enhanced_charts(self, orders=None, chart_types=None):
        """Step 4: Enhanced chart generation with trends and comparison using booking_date and sale_order_type_id"""
        try:
            _logger.info("Generating enhanced charts for visualization")
            
            if chart_types is None:
                chart_types = ['trends', 'comparison', 'project_performance', 'commission_analysis']
            
            charts_data = {}
            
            # Generate Trends Chart using booking_date
            if 'trends' in chart_types:
                charts_data['trends_chart'] = self._generate_trends_chart(orders)
            
            # Generate Comparison Chart using sale_order_type_id
            if 'comparison' in chart_types:
                charts_data['comparison_chart'] = self._generate_comparison_chart(orders)
            
            # Generate Real Estate specific charts
            if 'project_performance' in chart_types:
                charts_data['project_performance'] = self._generate_real_estate_charts(orders)
            
            if 'commission_analysis' in chart_types:
                charts_data['commission_analysis'] = self._generate_commission_chart(orders)
            
            return charts_data
            
        except Exception as e:
            _logger.error(f"Error generating enhanced charts: {e}")
            return {'error': str(e)}

    @api.model
    def _generate_trends_chart(self, orders=None):
        """Generate trends chart using booking_date for date-related visuals"""
        try:
            if orders is None:
                orders = self.env['sale.order'].search([('state', '!=', 'cancel')])
            
            # Group by booking_date or date_order
            date_field = 'booking_date' if self._check_optional_field('sale.order', 'booking_date') else 'date_order'
            
            trends_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            for order in orders:
                order_date = getattr(order, date_field, None)
                if order_date:
                    date_key = order_date.strftime('%Y-%m-%d')
                    trends_data[date_key]['count'] += 1
                    trends_data[date_key]['amount'] += order.amount_total
            
            # Sort by date and format for Chart.js
            sorted_dates = sorted(trends_data.keys())
            
            return {
                'type': 'line',
                'data': {
                    'labels': sorted_dates,
                    'datasets': [
                        {
                            'label': 'Sales Count',
                            'data': [trends_data[date]['count'] for date in sorted_dates],
                            'borderColor': '#4d1a1a',  # OSUS burgundy
                            'backgroundColor': 'rgba(77, 26, 26, 0.1)',
                            'tension': 0.4,
                            'yAxisID': 'y'
                        },
                        {
                            'label': 'Sales Amount',
                            'data': [trends_data[date]['amount'] for date in sorted_dates],
                            'borderColor': '#DAA520',  # OSUS gold
                            'backgroundColor': 'rgba(218, 165, 32, 0.1)',
                            'tension': 0.4,
                            'yAxisID': 'y1'
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'interaction': {'mode': 'index', 'intersect': False},
                    'scales': {
                        'y': {'type': 'linear', 'display': True, 'position': 'left'},
                        'y1': {'type': 'linear', 'display': True, 'position': 'right', 'grid': {'drawOnChartArea': False}}
                    }
                }
            }
            
        except Exception as e:
            _logger.error(f"Error generating trends chart: {e}")
            return {'error': str(e)}

    @api.model
    def _generate_comparison_chart(self, orders=None):
        """Generate comparison chart using sale_order_type_id for categorization"""
        try:
            if orders is None:
                orders = self.env['sale.order'].search([('state', '!=', 'cancel')])
            
            # Group by sale order type
            if not self._check_optional_field('sale.order', 'sale_order_type_id'):
                return {'error': 'Sale order type field not available'}
            
            type_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            for order in orders:
                if order.sale_order_type_id:
                    type_name = order.sale_order_type_id.name
                    type_data[type_name]['count'] += 1
                    type_data[type_name]['amount'] += order.amount_total
                else:
                    type_data['Unspecified']['count'] += 1
                    type_data['Unspecified']['amount'] += order.amount_total
            
            labels = list(type_data.keys())
            amounts = [type_data[label]['amount'] for label in labels]
            counts = [type_data[label]['count'] for label in labels]
            
            # Generate colors (burgundy variations)
            colors = [
                '#4d1a1a', '#722a2a', '#9d3a3a', '#c84a4a', '#DAA520',
                '#B8860B', '#CD853F', '#D2691E', '#A0522D', '#8B4513'
            ][:len(labels)]
            
            return {
                'type': 'doughnut',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Sales by Type',
                        'data': amounts,
                        'backgroundColor': colors,
                        'borderColor': colors,
                        'borderWidth': 2
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'bottom'},
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.label + ": " + context.formattedValue + " (" + context.dataset.counts[context.dataIndex] + " orders)"; }'
                            }
                        }
                    }
                },
                'counts': counts  # Additional data for tooltips
            }
            
        except Exception as e:
            _logger.error(f"Error generating comparison chart: {e}")
            return {'error': str(e)}

    @api.model
    def _generate_real_estate_charts(self, orders=None):
        """Generate real estate project performance charts"""
        try:
            if orders is None:
                orders = self.env['sale.order'].search([('state', '!=', 'cancel')])
            
            if not self._check_optional_field('sale.order', 'project_id'):
                return {'error': 'Project field not available'}
            
            project_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'sale_value': 0})
            
            for order in orders:
                if order.project_id:
                    project_name = order.project_id.name
                    project_data[project_name]['count'] += 1
                    project_data[project_name]['amount'] += order.amount_total
                    
                    # Real estate specific sale value
                    if self._check_optional_field('sale.order', 'sale_value'):
                        project_data[project_name]['sale_value'] += order.sale_value or 0
            
            labels = list(project_data.keys())
            amounts = [project_data[label]['amount'] for label in labels]
            
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Project Sales Performance',
                        'data': amounts,
                        'backgroundColor': '#4d1a1a',
                        'borderColor': '#DAA520',
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {'legend': {'display': False}},
                    'scales': {
                        'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Sales Amount'}}
                    }
                }
            }
            
        except Exception as e:
            _logger.error(f"Error generating real estate charts: {e}")
            return {'error': str(e)}

    @api.model
    def _generate_commission_chart(self, orders=None):
        """Generate commission analysis chart"""
        try:
            if orders is None:
                orders = self.env['sale.order'].search([('state', '!=', 'cancel')])
            
            if not self._check_optional_field('sale.order', 'developer_commission'):
                return {'error': 'Developer commission field not available'}
            
            commission_ranges = {
                '0-5%': 0, '5-10%': 0, '10-15%': 0, '15-20%': 0, '20%+': 0
            }
            
            for order in orders:
                commission = order.developer_commission or 0
                if commission <= 5:
                    commission_ranges['0-5%'] += 1
                elif commission <= 10:
                    commission_ranges['5-10%'] += 1
                elif commission <= 15:
                    commission_ranges['10-15%'] += 1
                elif commission <= 20:
                    commission_ranges['15-20%'] += 1
                else:
                    commission_ranges['20%+'] += 1
            
            return {
                'type': 'pie',
                'data': {
                    'labels': list(commission_ranges.keys()),
                    'datasets': [{
                        'label': 'Commission Distribution',
                        'data': list(commission_ranges.values()),
                        'backgroundColor': ['#4d1a1a', '#722a2a', '#9d3a3a', '#DAA520', '#B8860B']
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {'legend': {'position': 'bottom'}}
                }
            }
            
        except Exception as e:
            _logger.error(f"Error generating commission chart: {e}")
            return {'error': str(e)}

    @api.model
    def get_monthly_trend_data(self, start_date, end_date, sale_type_ids=None):
        """Get monthly sales trend data"""
        try:
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by month
            monthly_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            for order in orders:
                order_date = getattr(order, date_field)
                if order_date:
                    month_key = order_date.strftime('%Y-%m')
                    monthly_data[month_key]['count'] += 1
                    monthly_data[month_key]['amount'] += order.amount_total
            
            # Format for Chart.js
            sorted_months = sorted(monthly_data.keys())
            
            return {
                'labels': [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months],
                'datasets': [
                    {
                        'label': 'Order Count',
                        'data': [monthly_data[month]['count'] for month in sorted_months],
                        'borderColor': '#4d1a1a',  # OSUS burgundy
                        'backgroundColor': 'rgba(77, 26, 26, 0.1)',
                        'yAxisID': 'y'
                    },
                    {
                        'label': 'Total Amount',
                        'data': [monthly_data[month]['amount'] for month in sorted_months],
                        'borderColor': '#b8a366',  # OSUS gold
                        'backgroundColor': 'rgba(184, 163, 102, 0.1)',
                        'yAxisID': 'y1'
                    }
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting monthly trend data: {e}")
            return {
                'labels': [],
                'datasets': [],
                'error': str(e)
            }

    @api.model
    def get_sales_pipeline_data(self, start_date, end_date, sale_type_ids=None):
        """Get sales pipeline data by state"""
        try:
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel')
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by state
            pipeline_data = defaultdict(lambda: {'count': 0, 'amount': 0})
            
            state_mapping = {
                'draft': 'Draft',
                'sent': 'Quotation Sent',
                'sale': 'Sales Order',
                'done': 'Locked',
                'cancel': 'Cancelled'
            }
            
            for order in orders:
                state_label = state_mapping.get(order.state, order.state.title())
                pipeline_data[state_label]['count'] += 1
                pipeline_data[state_label]['amount'] += order.amount_total
            
            # Colors for different states (OSUS brand palette)
            colors = [
                '#4d1a1a',  # burgundy
                '#7d1e2d',  # dark burgundy  
                '#b8a366',  # gold
                '#d4c299',  # light gold
                '#cc4d66',  # burgundy light
            ]
            
            labels = list(pipeline_data.keys())
            data = [pipeline_data[label]['count'] for label in labels]
            
            return {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors[:len(labels)],
                    'borderColor': '#ffffff',
                    'borderWidth': 2
                }]
            }
            
        except Exception as e:
            _logger.error(f"Error getting pipeline data: {e}")
            return {
                'labels': [],
                'datasets': [],
                'error': str(e)
            }

    @api.model
    def get_agent_rankings(self, start_date, end_date, sale_type_ids=None, limit=10):
        """Get agent rankings if commission_ax module is available"""
        try:
            if not self._check_optional_field('sale.order', 'agent1_partner_id'):
                return {'error': 'Agent tracking not available (commission_ax module not installed)'}
            
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                ('agent1_partner_id', '!=', False)
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by agent
            agent_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'name': ''})
            
            for order in orders:
                agent = order.agent1_partner_id
                if agent:
                    agent_data[agent.id]['count'] += 1
                    agent_data[agent.id]['amount'] += order.amount_total
                    agent_data[agent.id]['name'] = agent.name
            
            # Sort by amount and limit
            sorted_agents = sorted(agent_data.items(), key=lambda x: x[1]['amount'], reverse=True)[:limit]
            
            return {
                'rankings': [
                    {
                        'rank': i + 1,
                        'agent_id': agent_id,
                        'name': data['name'],
                        'deal_count': data['count'],
                        'total_amount': data['amount'],
                        'formatted_amount': self.format_dashboard_value(data['amount'])
                    }
                    for i, (agent_id, data) in enumerate(sorted_agents)
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting agent rankings: {e}")
            return {'error': str(e)}

    @api.model
    def get_broker_rankings(self, start_date, end_date, sale_type_ids=None, limit=10):
        """Get broker rankings if commission_ax module is available"""
        try:
            if not self._check_optional_field('sale.order', 'broker_partner_id'):
                return {'error': 'Broker tracking not available (commission_ax module not installed)'}
            
            sale_order = self.env['sale.order']
            date_field = self._get_date_field()
            
            # Base domain
            base_domain = [
                (date_field, '>=', start_date),
                (date_field, '<=', end_date),
                ('state', '!=', 'cancel'),
                ('broker_partner_id', '!=', False)
            ]
            
            # Add sale type filter if available
            if sale_type_ids and self._check_optional_field('sale.order', 'sale_order_type_id'):
                base_domain.append(('sale_order_type_id', 'in', sale_type_ids))
            
            orders = sale_order.search(base_domain)
            
            # Group by broker
            broker_data = defaultdict(lambda: {'count': 0, 'amount': 0, 'name': ''})
            
            for order in orders:
                broker = order.broker_partner_id
                if broker:
                    broker_data[broker.id]['count'] += 1
                    broker_data[broker.id]['amount'] += order.amount_total
                    broker_data[broker.id]['name'] = broker.name
            
            # Sort by amount and limit
            sorted_brokers = sorted(broker_data.items(), key=lambda x: x[1]['amount'], reverse=True)[:limit]
            
            return {
                'rankings': [
                    {
                        'rank': i + 1,
                        'broker_id': broker_id,
                        'name': data['name'],
                        'deal_count': data['count'],
                        'total_amount': data['amount'],
                        'formatted_amount': self.format_dashboard_value(data['amount'])
                    }
                    for i, (broker_id, data) in enumerate(sorted_brokers)
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting broker rankings: {e}")
            return {'error': str(e)}

    @api.model
    def get_sale_types(self):
        """Get available sale types if le_sale_type module is available"""
        try:
            if not self._check_optional_field('le.sale.type', 'name'):
                return {'error': 'Sale types not available (le_sale_type module not installed)'}
            
            sale_types = self.env['le.sale.type'].search([])
            
            return {
                'sale_types': [
                    {
                        'id': st.id,
                        'name': st.name,
                        'code': getattr(st, 'code', '') if hasattr(st, 'code') else ''
                    }
                    for st in sale_types
                ]
            }
            
        except Exception as e:
            _logger.error(f"Error getting sale types: {e}")
            return {'error': str(e)}

    @api.model
    def get_dashboard_data(self, start_date=None, end_date=None, sale_type_ids=None):
        """Main method to get all dashboard data"""
        try:
            # Set default dates if not provided
            if not start_date:
                start_date = fields.Date.today().replace(day=1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = fields.Date.today().strftime('%Y-%m-%d')
            
            # Convert string dates to date objects if needed
            if isinstance(start_date, str):
                start_date = fields.Date.from_string(start_date)
            if isinstance(end_date, str):
                end_date = fields.Date.from_string(end_date)
            
            # Get all dashboard data
            performance_data = self.get_sales_performance_data(start_date, end_date, sale_type_ids)
            monthly_trend = self.get_monthly_trend_data(start_date, end_date, sale_type_ids)
            pipeline_data = self.get_sales_pipeline_data(start_date, end_date, sale_type_ids)
            agent_rankings = self.get_agent_rankings(start_date, end_date, sale_type_ids)
            broker_rankings = self.get_broker_rankings(start_date, end_date, sale_type_ids)
            sale_types = self.get_sale_types()
            
            return {
                'performance': performance_data,
                'monthly_trend': monthly_trend,
                'pipeline': pipeline_data,
                'agent_rankings': agent_rankings,
                'broker_rankings': broker_rankings,
                'sale_types': sale_types,
                'date_range': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'date_field_used': self._get_date_field()
                }
            }
            
        except Exception as e:
            _logger.error(f"Error getting dashboard data: {e}")
            return {
                'error': str(e),
                'performance': {'total_orders': 0, 'total_amount': 0},
                'monthly_trend': {'labels': [], 'datasets': []},
                'pipeline': {'labels': [], 'datasets': []},
                'agent_rankings': {'rankings': []},
                'broker_rankings': {'rankings': []},
                'sale_types': {'sale_types': []}
            }
