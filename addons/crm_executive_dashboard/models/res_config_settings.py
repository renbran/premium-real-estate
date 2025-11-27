# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_dashboard_auto_refresh = fields.Boolean(
        string='Auto Refresh Dashboard',
        config_parameter='crm_executive_dashboard.auto_refresh',
        default=True,
        help="Enable automatic dashboard refresh every 5 minutes"
    )
    crm_dashboard_refresh_interval = fields.Integer(
        string='Refresh Interval (minutes)',
        config_parameter='crm_executive_dashboard.refresh_interval',
        default=5,
        help="Dashboard refresh interval in minutes"
    )
    crm_dashboard_default_period = fields.Selection([
        ('7', 'Last 7 days'),
        ('30', 'Last 30 days'),
        ('90', 'Last 90 days'),
        ('365', 'Last year'),
        ('custom', 'Custom period'),
    ], string='Default Time Period',
        config_parameter='crm_executive_dashboard.default_period',
        default='30',
        help="Default time period for dashboard data"
    )
    crm_dashboard_show_forecasts = fields.Boolean(
        string='Show Revenue Forecasts',
        config_parameter='crm_executive_dashboard.show_forecasts',
        default=True,
        help="Display revenue forecasting charts"
    )
    crm_dashboard_currency_format = fields.Selection([
        ('symbol', 'Symbol (€)'),
        ('code', 'Code (EUR)'),
        ('both', 'Both (€ EUR)'),
    ], string='Currency Display Format',
        config_parameter='crm_executive_dashboard.currency_format',
        default='symbol',
        help="How to display currency in dashboard"
    )
