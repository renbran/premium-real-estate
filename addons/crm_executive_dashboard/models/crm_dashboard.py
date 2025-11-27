# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar
import logging

_logger = logging.getLogger(__name__)


class CRMExecutiveDashboard(models.Model):
    _name = 'crm.executive.dashboard'
    _description = 'CRM Executive Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Dashboard Name',
        required=True,
        default='CRM Executive Dashboard',
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
    def get_dashboard_data(self, date_from=None, date_to=None, team_ids=None):
        """Get comprehensive dashboard data for CRM analytics"""
        try:
            # Set default date range if not provided
            if not date_from:
                date_from = fields.Date.today().replace(day=1)
            if not date_to:
                date_to = fields.Date.today()
            
            # Convert string dates to date objects if needed
            if isinstance(date_from, str):
                date_from = fields.Date.from_string(date_from)
            if isinstance(date_to, str):
                date_to = fields.Date.from_string(date_to)

            domain = [
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to)
            ]
            
            if team_ids:
                domain.append(('team_id', 'in', team_ids))

            # Get basic CRM metrics
            leads_domain = domain.copy()
            opportunities_domain = domain + [('type', '=', 'opportunity')]
            
            # KPI calculations
            total_leads = self.env['crm.lead'].search_count(leads_domain)
            total_opportunities = self.env['crm.lead'].search_count(opportunities_domain)
            won_opportunities = self.env['crm.lead'].search_count(
                opportunities_domain + [('stage_id.is_won', '=', True)]
            )
            lost_opportunities = self.env['crm.lead'].search_count(
                opportunities_domain + [('active', '=', False), ('probability', '=', 0)]
            )
            
            # Revenue calculations
            won_revenue = sum(self.env['crm.lead'].search(
                opportunities_domain + [('stage_id.is_won', '=', True)]
            ).mapped('planned_revenue'))
            
            # Expected revenue calculation
            expected_revenue = 0
            for opp in self.env['crm.lead'].search(opportunities_domain):
                expected_revenue += (opp.planned_revenue or 0.0) * (opp.probability or 0) / 100.0

            # Conversion rates
            conversion_rate = (won_opportunities / total_leads * 100) if total_leads > 0 else 0
            opportunity_conversion_rate = (won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0

            # Average deal size
            avg_deal_size = (won_revenue / won_opportunities) if won_opportunities > 0 else 0

            # Get pipeline data
            pipeline_data = self._get_pipeline_data(date_from, date_to, team_ids)
            
            # Get trend data
            trend_data = self._get_trend_data(date_from, date_to, team_ids)
            
            # Get team performance data
            team_performance = self._get_team_performance_data(date_from, date_to, team_ids)
            
            # Get customer acquisition data
            customer_data = self._get_customer_acquisition_data(date_from, date_to, team_ids)
            
            # Get agent performance metrics
            agent_metrics = self._get_agent_performance_metrics(date_from, date_to, team_ids)
            
            # Get lead quality metrics
            lead_quality_metrics = self._get_lead_quality_metrics(date_from, date_to, team_ids)
            
            # Get response time metrics
            response_metrics = self._get_response_time_metrics(date_from, date_to, team_ids)

            return {
                'kpis': {
                    'total_leads': total_leads,
                    'total_opportunities': total_opportunities,
                    'won_opportunities': won_opportunities,
                    'lost_opportunities': lost_opportunities,
                    'won_revenue': won_revenue,
                    'expected_revenue': expected_revenue,
                    'conversion_rate': round(conversion_rate, 2),
                    'opportunity_conversion_rate': round(opportunity_conversion_rate, 2),
                    'avg_deal_size': round(avg_deal_size, 2),
                },
                'pipeline': pipeline_data,
                'trends': trend_data,
                'team_performance': team_performance,
                'customer_acquisition': customer_data,
                'agent_metrics': agent_metrics,
                'lead_quality': lead_quality_metrics,
                'response_metrics': response_metrics,
                'currency_symbol': self.env.company.currency_id.symbol,
            }
            
        except Exception as e:
            _logger.error(f"Error in get_dashboard_data: {str(e)}")
            return {
                'error': str(e),
                'kpis': {},
                'pipeline': {},
                'trends': {},
                'team_performance': {},
                'customer_acquisition': {},
            }

    def _get_pipeline_data(self, date_from, date_to, team_ids):
        """Get sales pipeline data by stage"""
        domain = [('type', '=', 'opportunity')]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        stages = self.env['crm.stage'].search([])
        pipeline_data = {
            'labels': [],
            'data': [],
            'colors': [],
            'total_value': 0
        }

        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        
        for i, stage in enumerate(stages):
            stage_domain = domain + [('stage_id', '=', stage.id)]
            opportunities = self.env['crm.lead'].search(stage_domain)
            
            stage_value = sum(opportunities.mapped('planned_revenue'))
            stage_count = len(opportunities)
            
            if stage_count > 0:
                pipeline_data['labels'].append(f"{stage.name} ({stage_count})")
                pipeline_data['data'].append(stage_value)
                pipeline_data['colors'].append(colors[i % len(colors)])
                pipeline_data['total_value'] += stage_value

        return pipeline_data

    def _get_trend_data(self, date_from, date_to, team_ids):
        """Get trend data for the last 12 months"""
        trends = {
            'labels': [],
            'leads': [],
            'opportunities': [],
            'won_revenue': [],
            'expected_revenue': []
        }

        # Calculate 12 months of data
        current_date = date_to
        for i in range(12):
            month_start = current_date.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            domain = [
                ('create_date', '>=', month_start),
                ('create_date', '<=', month_end)
            ]
            if team_ids:
                domain.append(('team_id', 'in', team_ids))

            # Month label
            month_label = month_start.strftime('%b %Y')
            trends['labels'].insert(0, month_label)
            
            # Leads count
            leads_count = self.env['crm.lead'].search_count(domain)
            trends['leads'].insert(0, leads_count)
            
            # Opportunities count
            opp_count = self.env['crm.lead'].search_count(domain + [('type', '=', 'opportunity')])
            trends['opportunities'].insert(0, opp_count)
            
            # Won revenue
            won_revenue = sum(self.env['crm.lead'].search(
                domain + [('type', '=', 'opportunity'), ('stage_id.is_won', '=', True)]
            ).mapped('planned_revenue'))
            trends['won_revenue'].insert(0, won_revenue)
            
            # Expected revenue
            expected_revenue = 0
            for opp in self.env['crm.lead'].search(domain + [('type', '=', 'opportunity')]):
                expected_revenue += (opp.planned_revenue or 0.0) * (opp.probability or 0) / 100.0
            trends['expected_revenue'].insert(0, expected_revenue)
            
            current_date = month_start - timedelta(days=1)

        return trends

    def _get_team_performance_data(self, date_from, date_to, team_ids):
        """Get team performance data"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to),
            ('type', '=', 'opportunity')
        ]
        
        if team_ids:
            teams = self.env['crm.team'].browse(team_ids)
        else:
            teams = self.env['crm.team'].search([])

        team_data = {
            'labels': [],
            'opportunities': [],
            'won_revenue': [],
            'conversion_rates': []
        }

        for team in teams:
            team_domain = domain + [('team_id', '=', team.id)]
            
            total_opportunities = self.env['crm.lead'].search_count(team_domain)
            won_opportunities = self.env['crm.lead'].search_count(
                team_domain + [('stage_id.is_won', '=', True)]
            )
            won_revenue = sum(self.env['crm.lead'].search(
                team_domain + [('stage_id.is_won', '=', True)]
            ).mapped('planned_revenue'))
            
            conversion_rate = (won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0
            
            team_data['labels'].append(team.name)
            team_data['opportunities'].append(total_opportunities)
            team_data['won_revenue'].append(won_revenue)
            team_data['conversion_rates'].append(round(conversion_rate, 2))

        return team_data

    def _get_customer_acquisition_data(self, date_from, date_to, team_ids):
        """Get customer acquisition and source data"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        # Lead sources
        sources = self.env['crm.lead'].read_group(
            domain,
            ['source_id', 'planned_revenue'],
            ['source_id']
        )
        
        source_data = {
            'labels': [],
            'counts': [],
            'revenue': []
        }
        
        for source in sources:
            source_name = source['source_id'][1] if source['source_id'] else 'Undefined'
            source_data['labels'].append(source_name)
            source_data['counts'].append(source['source_id_count'])
            
            # Calculate revenue for this source
            source_revenue = sum(self.env['crm.lead'].search(
                domain + [('source_id', '=', source['source_id'][0] if source['source_id'] else False)]
            ).mapped('planned_revenue'))
            source_data['revenue'].append(source_revenue)

        return {
            'sources': source_data,
            'new_customers': self._get_new_customers_count(date_from, date_to, team_ids),
        }

    def _get_new_customers_count(self, date_from, date_to, team_ids):
        """Get count of new customers acquired"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to),
            ('type', '=', 'opportunity'),
            ('stage_id.is_won', '=', True)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))
        
        won_opportunities = self.env['crm.lead'].search(domain)
        new_customers = len(set(won_opportunities.mapped('partner_id.id')))
        
        return new_customers

    @api.model
    def get_overdue_opportunities(self, team_ids=None):
        """Get overdue opportunities for action items"""
        domain = [
            ('type', '=', 'opportunity'),
            ('date_deadline', '<', fields.Date.today()),
            ('stage_id.is_won', '=', False),
            ('active', '=', True)
        ]
        if team_ids:
            domain.append(('team_id', 'in', team_ids))

        opportunities = self.env['crm.lead'].search(domain, limit=10)
        
        return [{
            'id': opp.id,
            'name': opp.name,
            'partner_name': opp.partner_id.name if opp.partner_id else 'Unknown',
            'planned_revenue': opp.planned_revenue,
            'probability': opp.probability,
            'date_deadline': opp.date_deadline,
            'user_id': opp.user_id.name if opp.user_id else 'Unassigned',
            'team_id': opp.team_id.name if opp.team_id else 'No Team',
        } for opp in opportunities]

    def _get_agent_performance_metrics(self, date_from, date_to, team_ids=None):
        """Get agent performance metrics including leads in progress, conversions, etc."""
        try:
            domain = [
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to),
            ]
            
            if team_ids:
                domain.append(('team_id', 'in', team_ids))

            # Top agents with leads in progress
            progress_domain = domain + [('stage_id.is_won', '=', False), ('active', '=', True), ('probability', '>', 0)]
            leads_in_progress = self.env['crm.lead'].read_group(
                progress_domain,
                ['user_id', 'planned_revenue'],
                ['user_id']
            )
            
            top_agents_progress = []
            for agent_data in leads_in_progress:
                if agent_data['user_id']:
                    user = self.env['res.users'].browse(agent_data['user_id'][0])
                    partner = user.partner_id
                    top_agents_progress.append({
                        'agent_id': user.id,
                        'agent_name': user.name,
                        'partner_id': partner.id if partner else None,
                        'leads_count': agent_data['user_id_count'],
                        'total_revenue': agent_data['planned_revenue'] or 0,
                        'avg_revenue': (agent_data['planned_revenue'] or 0) / agent_data['user_id_count'] if agent_data['user_id_count'] > 0 else 0
                    })
            
            # Sort by leads count and revenue
            top_agents_progress.sort(key=lambda x: (x['leads_count'], x['total_revenue']), reverse=True)
            
            # Most converted leads (won opportunities)
            won_domain = domain + [('stage_id.is_won', '=', True)]
            most_converted = self.env['crm.lead'].read_group(
                won_domain,
                ['user_id', 'planned_revenue'],
                ['user_id']
            )
            
            converted_agents = []
            for agent_data in most_converted:
                if agent_data['user_id']:
                    user = self.env['res.users'].browse(agent_data['user_id'][0])
                    converted_agents.append({
                        'agent_id': user.id,
                        'agent_name': user.name,
                        'won_count': agent_data['user_id_count'],
                        'won_revenue': agent_data['planned_revenue'] or 0,
                        'avg_deal_size': (agent_data['planned_revenue'] or 0) / agent_data['user_id_count'] if agent_data['user_id_count'] > 0 else 0
                    })
            
            converted_agents.sort(key=lambda x: x['won_count'], reverse=True)
            
            return {
                'top_agents_with_progress': top_agents_progress[:10],
                'most_converted_agents': converted_agents[:10],
            }
            
        except Exception as e:
            _logger.error(f"Error in _get_agent_performance_metrics: {str(e)}")
            return {'top_agents_with_progress': [], 'most_converted_agents': []}

    def _get_lead_quality_metrics(self, date_from, date_to, team_ids=None):
        """Get lead quality metrics including most junked leads by agent"""
        try:
            domain = [
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to),
            ]
            
            if team_ids:
                domain.append(('team_id', 'in', team_ids))

            # Most junked leads (lost opportunities with probability 0)
            junked_domain = domain + [('probability', '=', 0), ('active', '=', False)]
            junked_leads = self.env['crm.lead'].read_group(
                junked_domain,
                ['user_id', 'lost_reason'],
                ['user_id']
            )
            
            junked_agents = []
            for agent_data in junked_leads:
                if agent_data['user_id']:
                    user = self.env['res.users'].browse(agent_data['user_id'][0])
                    # Get detailed reasons for this agent
                    agent_junked_leads = self.env['crm.lead'].search([
                        ('user_id', '=', user.id),
                        ('probability', '=', 0),
                        ('active', '=', False),
                        ('create_date', '>=', date_from),
                        ('create_date', '<=', date_to)
                    ])
                    
                    reasons = {}
                    for lead in agent_junked_leads:
                        reason = lead.lost_reason.name if lead.lost_reason else 'No Reason'
                        reasons[reason] = reasons.get(reason, 0) + 1
                    
                    junked_agents.append({
                        'agent_id': user.id,
                        'agent_name': user.name,
                        'junked_count': agent_data['user_id_count'],
                        'top_reason': max(reasons.items(), key=lambda x: x[1])[0] if reasons else 'No Reason',
                        'reasons_breakdown': reasons
                    })
            
            junked_agents.sort(key=lambda x: x['junked_count'], reverse=True)
            
            # Lead conversion quality by source
            lead_sources = self.env['crm.lead'].read_group(
                domain,
                ['source_id', 'stage_id'],
                ['source_id']
            )
            
            source_quality = []
            for source_data in lead_sources:
                if source_data['source_id']:
                    source = self.env['utm.source'].browse(source_data['source_id'][0])
                    
                    # Calculate conversion rate for this source
                    source_leads = self.env['crm.lead'].search([
                        ('source_id', '=', source.id),
                        ('create_date', '>=', date_from),
                        ('create_date', '<=', date_to)
                    ])
                    
                    won_leads = source_leads.filtered(lambda l: l.stage_id.is_won)
                    conversion_rate = (len(won_leads) / len(source_leads) * 100) if source_leads else 0
                    
                    source_quality.append({
                        'source_name': source.name,
                        'total_leads': len(source_leads),
                        'won_leads': len(won_leads),
                        'conversion_rate': round(conversion_rate, 2)
                    })
            
            source_quality.sort(key=lambda x: x['conversion_rate'], reverse=True)
            
            return {
                'most_junked_agents': junked_agents[:10],
                'source_quality': source_quality[:10],
            }
            
        except Exception as e:
            _logger.error(f"Error in _get_lead_quality_metrics: {str(e)}")
            return {'most_junked_agents': [], 'source_quality': []}

    def _get_response_time_metrics(self, date_from, date_to, team_ids=None):
        """Get response time metrics for agents"""
        try:
            domain = [
                ('create_date', '>=', date_from),
                ('create_date', '<=', date_to),
            ]
            
            if team_ids:
                domain.append(('team_id', 'in', team_ids))

            leads = self.env['crm.lead'].search(domain)
            
            agent_response_metrics = {}
            agent_update_metrics = {}
            
            for lead in leads:
                if not lead.user_id:
                    continue
                    
                agent_id = lead.user_id.id
                agent_name = lead.user_id.name
                
                if agent_id not in agent_response_metrics:
                    agent_response_metrics[agent_id] = {
                        'agent_name': agent_name,
                        'response_times': [],
                        'update_intervals': []
                    }
                
                # Calculate first response time (first message/activity after lead creation)
                first_message = self.env['mail.message'].search([
                    ('res_id', '=', lead.id),
                    ('model', '=', 'crm.lead'),
                    ('author_id', '=', lead.user_id.partner_id.id),
                    ('create_date', '>', lead.create_date)
                ], limit=1, order='create_date asc')
                
                if first_message:
                    response_time = (first_message.create_date - lead.create_date).total_seconds() / 3600  # hours
                    agent_response_metrics[agent_id]['response_times'].append(response_time)
                
                # Calculate update frequency (time between activities/messages)
                activities = self.env['mail.message'].search([
                    ('res_id', '=', lead.id),
                    ('model', '=', 'crm.lead'),
                    ('author_id', '=', lead.user_id.partner_id.id)
                ], order='create_date asc')
                
                for i in range(1, len(activities)):
                    update_interval = (activities[i].create_date - activities[i-1].create_date).total_seconds() / 3600  # hours
                    agent_response_metrics[agent_id]['update_intervals'].append(update_interval)
            
            # Process metrics
            fast_responders = []
            slow_responders = []
            fast_updaters = []
            slow_updaters = []
            
            for agent_id, metrics in agent_response_metrics.items():
                response_times = metrics['response_times']
                update_intervals = metrics['update_intervals']
                
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    fast_responders.append({
                        'agent_id': agent_id,
                        'agent_name': metrics['agent_name'],
                        'avg_response_time': round(avg_response_time, 2),
                        'response_count': len(response_times)
                    })
                    slow_responders.append({
                        'agent_id': agent_id,
                        'agent_name': metrics['agent_name'],
                        'avg_response_time': round(avg_response_time, 2),
                        'response_count': len(response_times)
                    })
                
                if update_intervals:
                    avg_update_interval = sum(update_intervals) / len(update_intervals)
                    fast_updaters.append({
                        'agent_id': agent_id,
                        'agent_name': metrics['agent_name'],
                        'avg_update_interval': round(avg_update_interval, 2),
                        'update_count': len(update_intervals)
                    })
                    slow_updaters.append({
                        'agent_id': agent_id,
                        'agent_name': metrics['agent_name'],
                        'avg_update_interval': round(avg_update_interval, 2),
                        'update_count': len(update_intervals)
                    })
            
            # Sort lists
            fast_responders.sort(key=lambda x: x['avg_response_time'])
            slow_responders.sort(key=lambda x: x['avg_response_time'], reverse=True)
            fast_updaters.sort(key=lambda x: x['avg_update_interval'])
            slow_updaters.sort(key=lambda x: x['avg_update_interval'], reverse=True)
            
            return {
                'fast_responders': fast_responders[:10],
                'slow_responders': slow_responders[:10],
                'fast_updaters': fast_updaters[:10],
                'slow_updaters': slow_updaters[:10],
            }
            
        except Exception as e:
            _logger.error(f"Error in _get_response_time_metrics: {str(e)}")
            return {
                'fast_responders': [],
                'slow_responders': [],
                'fast_updaters': [],
                'slow_updaters': []
            }

    @api.model
    def get_top_performers(self, date_from=None, date_to=None, limit=5):
        """Get top performing sales people"""
        if not date_from:
            date_from = fields.Date.today().replace(day=1)
        if not date_to:
            date_to = fields.Date.today()

        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to),
            ('type', '=', 'opportunity'),
            ('stage_id.is_won', '=', True)
        ]

        # Group by user
        won_opportunities = self.env['crm.lead'].read_group(
            domain,
            ['user_id', 'planned_revenue'],
            ['user_id']
        )

        performers = []
        for user_data in won_opportunities:
            if user_data['user_id']:
                user = self.env['res.users'].browse(user_data['user_id'][0])
                performers.append({
                    'name': user.name,
                    'revenue': user_data['planned_revenue'],
                    'count': user_data['user_id_count'],
                    'avatar': f"/web/image/res.users/{user.id}/avatar_128"
                })

        # Sort by revenue and return top performers
        performers.sort(key=lambda x: x['revenue'], reverse=True)
        return performers[:limit]

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError(_("Start date must be before end date"))

    @api.model
    def create_default_dashboard(self):
        """Create a default dashboard configuration"""
        vals = {
            'name': 'Executive CRM Dashboard',
            'date_from': fields.Date.today().replace(day=1),
            'date_to': fields.Date.today(),
            'user_id': self.env.user.id,
        }
        return self.create(vals)
