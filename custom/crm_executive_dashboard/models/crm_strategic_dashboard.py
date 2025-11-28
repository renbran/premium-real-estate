# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar
import logging

_logger = logging.getLogger(__name__)


class CRMStrategicDashboard(models.Model):
    _name = 'crm.strategic.dashboard'
    _description = 'CRM Strategic Dashboard for Decision Makers'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Dashboard Name',
        required=True,
        default='CRM Strategic Dashboard',
        tracking=True
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )
    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.today().replace(day=1),
        tracking=True
    )
    date_to = fields.Date(
        string='Date To',
        default=fields.Date.today,
        tracking=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        tracking=True
    )
    team_ids = fields.Many2many(
        'crm.team',
        string='Sales Teams',
        help="Leave empty to include all teams"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.model
    def safe_env_ref(self, xml_id, raise_if_not_found=False):
        """Safely get environment reference with proper validation"""
        try:
            if not xml_id or xml_id == 'undefined' or '.' not in xml_id:
                if raise_if_not_found:
                    raise ValidationError(_("Invalid XML ID format: %s") % xml_id)
                return False
            return self.env.ref(xml_id, raise_if_not_found=raise_if_not_found)
        except Exception as e:
            _logger.warning(f"Failed to resolve XML ID '{xml_id}': {str(e)}")
            if raise_if_not_found:
                raise
            return False

    @api.model
    def get_strategic_dashboard_data(self, date_from=None, date_to=None, team_ids=None):
        """Get comprehensive strategic dashboard data for decision makers"""
        try:
            # Set default date range if not provided
            if not date_from:
                date_from = fields.Date.today().replace(day=1)
            if not date_to:
                date_to = fields.Date.today()
            
            # Convert string dates to date objects if needed
            if isinstance(date_from, str):
                try:
                    date_from = fields.Date.from_string(date_from)
                except (ValueError, TypeError) as e:
                    _logger.error(f"Invalid date_from format: {date_from}")
                    raise ValidationError(_("Invalid date format for date_from: %s") % date_from)
                    
            if isinstance(date_to, str):
                try:
                    date_to = fields.Date.from_string(date_to)
                except (ValueError, TypeError) as e:
                    _logger.error(f"Invalid date_to format: {date_to}")
                    raise ValidationError(_("Invalid date format for date_to: %s") % date_to)

            # Validate date range
            if date_from > date_to:
                raise ValidationError(_("Start date cannot be after end date"))

            domain = [
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ]
            
            if team_ids:
                if isinstance(team_ids, str):
                    team_ids = [int(x) for x in team_ids.split(',') if x.strip()]
                domain.append(('team_id', 'in', team_ids))

            # Strategic KPIs
            strategic_kpis = self._get_strategic_kpis(date_from, date_to, team_ids)
            
            # Financial Performance
            financial_data = self._get_financial_performance(date_from, date_to, team_ids)
            
            # Market Intelligence
            market_data = self._get_market_intelligence(date_from, date_to, team_ids)
            
            # Customer Insights
            customer_insights = self._get_customer_insights(date_from, date_to, team_ids)
            
            # Operational Efficiency
            operational_data = self._get_operational_efficiency(date_from, date_to, team_ids)
            
            # Risk Indicators
            risk_data = self._get_risk_indicators(date_from, date_to, team_ids)
            
            # Predictive Analytics
            predictive_data = self._get_predictive_analytics(date_from, date_to, team_ids)
            
            # Team Performance Overview
            team_overview = self._get_team_performance_overview(date_from, date_to, team_ids)

            return {
                'strategic_kpis': strategic_kpis,
                'financial_performance': financial_data,
                'market_intelligence': market_data,
                'customer_insights': customer_insights,
                'operational_efficiency': operational_data,
                'risk_indicators': risk_data,
                'predictive_analytics': predictive_data,
                'team_overview': team_overview,
                'currency_symbol': self.env.company.currency_id.symbol,
                'period': {
                    'from': date_from.strftime('%Y-%m-%d'),
                    'to': date_to.strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            _logger.error(f"Error in get_strategic_dashboard_data: {str(e)}")
            return {'error': str(e)}

    def _get_strategic_kpis(self, date_from, date_to, team_ids):
        """Get strategic KPIs for decision makers"""
        try:
            domain = [
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ]
            if team_ids:
                domain.append(('team_id', 'in', team_ids))

            # Previous period for comparison
            period_length = (date_to - date_from).days
            prev_date_to = date_from - timedelta(days=1)
            prev_date_from = prev_date_to - timedelta(days=period_length)
            
            prev_domain = [
                ('create_date', '>=', prev_date_from),
                ('create_date', '<=', prev_date_to)
            ]
            if team_ids:
                prev_domain.append(('team_id', 'in', team_ids))

            # Current period metrics
            total_pipeline_value = sum(self.env['crm.lead'].search(
                domain + [('type', '=', 'opportunity'), ('active', '=', True)]
            ).mapped('planned_revenue'))
            
            won_revenue = sum(self.env['crm.lead'].search(
                domain + [('stage_id.is_won', '=', True)]
            ).mapped('planned_revenue'))
            
            # Previous period metrics for comparison
            prev_won_revenue = sum(self.env['crm.lead'].search(
                prev_domain + [('stage_id.is_won', '=', True)]
            ).mapped('planned_revenue'))
            
            # Revenue growth
            revenue_growth = ((won_revenue - prev_won_revenue) / prev_won_revenue * 100) if prev_won_revenue > 0 else 0
            
            # Customer acquisition cost
            marketing_activities = self.env['mail.activity'].search_count([
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to),
                ('activity_type_id.name', 'ilike', 'marketing')
            ])
            
            new_customers = self.env['crm.lead'].search_count(
                domain + [('stage_id.is_won', '=', True), ('type', '=', 'lead')]
            )
            
            # Sales velocity (time from lead to close)
            won_leads = self.env['crm.lead'].search(
                domain + [('stage_id.is_won', '=', True)]
            )
            
            total_days = 0
            for lead in won_leads:
                if lead.date_closed and lead.create_date:
                    days = (lead.date_closed.date() - lead.create_date.date()).days
                    total_days += days
            
            avg_sales_cycle = total_days / len(won_leads) if won_leads else 0
            
            # Market share indicators
            total_market_leads = self.env['crm.lead'].search_count([
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ])
            
            our_leads = self.env['crm.lead'].search_count(domain)
            market_penetration = (our_leads / total_market_leads * 100) if total_market_leads > 0 else 0

            return {
                'total_pipeline_value': total_pipeline_value,
                'won_revenue': won_revenue,
                'revenue_growth': round(revenue_growth, 2),
                'avg_sales_cycle': round(avg_sales_cycle, 1),
                'market_penetration': round(market_penetration, 2),
                'new_customers': new_customers,
            }
        except Exception as e:
            _logger.error(f"Error in _get_strategic_kpis: {str(e)}")
            return {}

    def _get_financial_performance(self, date_from, date_to, team_ids):
        """Get financial performance metrics"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        won_opportunities = self.env['crm.lead'].search(
            domain + [('stage_id.is_won', '=', True)]
        )
        
        # Revenue by month
        monthly_revenue = {}
        current_date = date_from
        while current_date <= date_to:
            month_key = current_date.strftime('%Y-%m')
            month_revenue = sum(won_opportunities.filtered(
                lambda x: x.date_closed and x.date_closed.strftime('%Y-%m') == month_key
            ).mapped('planned_revenue'))
            monthly_revenue[month_key] = month_revenue
            current_date = current_date.replace(day=1) + relativedelta(months=1)
        
        # Profitability metrics
        total_revenue = sum(won_opportunities.mapped('planned_revenue'))
        total_opportunities = len(won_opportunities)
        
        # Revenue per opportunity
        revenue_per_opportunity = total_revenue / total_opportunities if total_opportunities > 0 else 0
        
        # Forecast accuracy (comparing expected vs actual)
        forecasted_revenue = sum(self.env['crm.lead'].search(
            domain + [('type', '=', 'opportunity')]
        ).mapped(lambda x: (x.planned_revenue or 0) * (x.probability or 0) / 100))

        forecast_accuracy = (total_revenue / forecasted_revenue * 100) if forecasted_revenue > 0 else 0

        return {
            'monthly_revenue': monthly_revenue,
            'total_revenue': total_revenue,
            'revenue_per_opportunity': round(revenue_per_opportunity, 2),
            'forecast_accuracy': round(forecast_accuracy, 2),
            'forecasted_revenue': forecasted_revenue
        }

    def _get_market_intelligence(self, date_from, date_to, team_ids):
        """Get market intelligence data"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        # Lead sources analysis
        lead_sources = self.env['crm.lead'].read_group(
            domain,
            ['source_id', 'planned_revenue'],
            ['source_id']
        )
        
        # Competitor analysis (from lost reasons)
        lost_reasons = self.env['crm.lead'].read_group(
            domain + [('active', '=', False), ('probability', '=', 0)],
            ['lost_reason_id'],
            ['lost_reason_id']
        )
        
        # Geographic distribution
        geographic_data = self.env['crm.lead'].read_group(
            domain,
            ['country_id', 'planned_revenue'],
            ['country_id']
        )
        
        # Industry analysis
        industry_data = self.env['crm.lead'].read_group(
            domain,
            ['partner_id.industry_id', 'planned_revenue'],
            ['partner_id.industry_id']
        )

        return {
            'lead_sources': lead_sources,
            'lost_reasons': lost_reasons,
            'geographic_distribution': geographic_data,
            'industry_analysis': industry_data
        }

    def _get_customer_insights(self, date_from, date_to, team_ids):
        """Get customer insights and behavior data"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        # Customer lifetime value indicators
        won_leads = self.env['crm.lead'].search(
            domain + [('stage_id.is_won', '=', True)]
        )
        
        # Repeat customers
        customer_partners = won_leads.mapped('partner_id')
        repeat_customers = 0
        for partner in customer_partners:
            partner_leads = self.env['crm.lead'].search_count([
                ('partner_id', '=', partner.id),
                ('stage_id.is_won', '=', True)
            ])
            if partner_leads > 1:
                repeat_customers += 1
        
        customer_retention_rate = (repeat_customers / len(customer_partners) * 100) if customer_partners else 0
        
        # Customer size segmentation
        large_deals = won_leads.filtered(lambda x: x.planned_revenue >= 50000)
        medium_deals = won_leads.filtered(lambda x: 10000 <= x.planned_revenue < 50000)
        small_deals = won_leads.filtered(lambda x: x.planned_revenue < 10000)
        
        # Customer engagement metrics
        avg_activities_per_lead = 0
        if won_leads:
            total_activities = sum(self.env['mail.activity'].search_count([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id)
            ]) for lead in won_leads)
            avg_activities_per_lead = total_activities / len(won_leads)

        return {
            'customer_retention_rate': round(customer_retention_rate, 2),
            'repeat_customers': repeat_customers,
            'total_customers': len(customer_partners),
            'deal_segmentation': {
                'large_deals': len(large_deals),
                'medium_deals': len(medium_deals),
                'small_deals': len(small_deals)
            },
            'avg_activities_per_lead': round(avg_activities_per_lead, 2)
        }

    def _get_operational_efficiency(self, date_from, date_to, team_ids):
        """Get operational efficiency metrics"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        all_leads = self.env['crm.lead'].search(domain)
        
        # Lead response time
        response_times = []
        for lead in all_leads:
            first_activity = self.env['mail.activity'].search([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id)
            ], order='create_date asc', limit=1)
            
            if first_activity:
                response_time = (first_activity.create_date - lead.create_date).total_seconds() / 3600
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Lead-to-opportunity conversion rate
        opportunities = all_leads.filtered(lambda x: x.type == 'opportunity')
        lead_to_opp_rate = (len(opportunities) / len(all_leads) * 100) if all_leads else 0
        
        # Sales team productivity
        if team_ids:
            teams = self.env['crm.team'].browse(team_ids)
        else:
            teams = self.env['crm.team'].search([])
        
        team_productivity = []
        for team in teams:
            team_domain = domain + [('team_id', '=', team.id)]
            team_revenue = sum(self.env['crm.lead'].search(
                team_domain + [('stage_id.is_won', '=', True)]
            ).mapped('planned_revenue'))
            
            team_members = len(team.member_ids)
            revenue_per_member = team_revenue / team_members if team_members > 0 else 0
            
            team_productivity.append({
                'team_name': team.name,
                'revenue_per_member': revenue_per_member,
                'total_revenue': team_revenue,
                'team_size': team_members
            })

        return {
            'avg_response_time': round(avg_response_time, 2),
            'lead_to_opportunity_rate': round(lead_to_opp_rate, 2),
            'team_productivity': team_productivity
        }

    def _get_risk_indicators(self, date_from, date_to, team_ids):
        """Get risk indicators for decision making"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        # Overdue opportunities
        overdue_opportunities = self.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('date_deadline', '<', fields.Date.today()),
            ('active', '=', True),
            ('probability', '>', 0),
            ('probability', '<', 100)
        ])
        
        overdue_value = sum(overdue_opportunities.mapped('planned_revenue'))
        
        # Stagnant opportunities (no activity in last 30 days)
        thirty_days_ago = fields.Date.today() - timedelta(days=30)
        stagnant_opportunities = self.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('probability', '>', 0),
            ('probability', '<', 100),
            ('date_last_stage_update', '<', thirty_days_ago)
        ])
        
        # High-value opportunities at risk
        at_risk_opportunities = self.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('planned_revenue', '>=', 50000),
            ('probability', '<=', 30),
            ('active', '=', True)
        ])
        
        # Pipeline concentration risk
        large_deal_percentage = 0
        total_pipeline = sum(self.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('active', '=', True)
        ]).mapped('planned_revenue'))
        
        if total_pipeline > 0:
            large_deals_value = sum(self.env['crm.lead'].search([
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('planned_revenue', '>=', 100000)
            ]).mapped('planned_revenue'))
            large_deal_percentage = (large_deals_value / total_pipeline * 100)

        return {
            'overdue_opportunities_count': len(overdue_opportunities),
            'overdue_value': overdue_value,
            'stagnant_opportunities_count': len(stagnant_opportunities),
            'at_risk_high_value_count': len(at_risk_opportunities),
            'pipeline_concentration_risk': round(large_deal_percentage, 2)
        }

    def _get_predictive_analytics(self, date_from, date_to, team_ids):
        """Get predictive analytics for forecasting"""
        # This is a simplified version - in practice, you'd use more sophisticated algorithms
        
        # Forecast next quarter revenue based on current pipeline
        current_pipeline = self.env['crm.lead'].search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('probability', '>', 0)
        ])
        
        # Weighted pipeline value
        weighted_pipeline = sum(lead.planned_revenue * (lead.probability / 100) for lead in current_pipeline)
        
        # Historical win rate
        historical_won = self.env['crm.lead'].search_count([
            ('stage_id.is_won', '=', True),
            ('create_date', '>=', date_from - relativedelta(months=6)),
            ('create_date', '<=', date_to)
        ])
        
        historical_total = self.env['crm.lead'].search_count([
            ('type', '=', 'opportunity'),
            ('create_date', '>=', date_from - relativedelta(months=6)),
            ('create_date', '<=', date_to)
        ])
        
        historical_win_rate = (historical_won / historical_total * 100) if historical_total > 0 else 0
        
        # Revenue trend prediction
        next_month_forecast = weighted_pipeline * 0.3  # Assuming 30% will close next month
        next_quarter_forecast = weighted_pipeline * 0.7  # Assuming 70% will close next quarter

        return {
            'weighted_pipeline': weighted_pipeline,
            'historical_win_rate': round(historical_win_rate, 2),
            'next_month_forecast': next_month_forecast,
            'next_quarter_forecast': next_quarter_forecast,
            'forecast_confidence': 'Medium' if historical_win_rate > 20 else 'Low'
        }

    def _get_team_performance_overview(self, date_from, date_to, team_ids):
        """Get comprehensive team performance overview"""
        if team_ids:
            teams = self.env['crm.team'].browse(team_ids)
        else:
            teams = self.env['crm.team'].search([])
        
        team_overview = []
        
        for team in teams:
            domain = [
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to),
                ('team_id', '=', team.id)
            ]
            
            team_revenue = sum(self.env['crm.lead'].search(
                domain + [('stage_id.is_won', '=', True)]
            ).mapped('planned_revenue'))
            
            team_opportunities = self.env['crm.lead'].search_count(
                domain + [('type', '=', 'opportunity')]
            )
            
            team_won = self.env['crm.lead'].search_count(
                domain + [('stage_id.is_won', '=', True)]
            )
            
            win_rate = (team_won / team_opportunities * 100) if team_opportunities > 0 else 0
            
            # Team targets (if available)
            target_revenue = team.invoiced_target if hasattr(team, 'invoiced_target') else 0
            target_achievement = (team_revenue / target_revenue * 100) if target_revenue > 0 else 0
            
            team_overview.append({
                'team_name': team.name,
                'revenue': team_revenue,
                'opportunities': team_opportunities,
                'won_count': team_won,
                'win_rate': round(win_rate, 2),
                'target_achievement': round(target_achievement, 2),
                'team_size': len(team.member_ids)
            })
        
        return team_overview
