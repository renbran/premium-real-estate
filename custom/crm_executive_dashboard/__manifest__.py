# -*- coding: utf-8 -*-
{
    'name': 'CRM Executive Dashboard',
    'version': '17.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Advanced CRM analytics and executive dashboard for Odoo 17',
    'description': """
        CRM Executive Dashboard - Odoo 17
        =================================
        
        A comprehensive CRM dashboard providing advanced analytics and executive-level insights:
        
        Key Features:
        - Executive KPI Dashboard with real-time metrics
        - Advanced sales pipeline analytics
        - Customer acquisition and retention metrics
        - Sales performance trends and forecasting
        - Team productivity and conversion analytics
        - Agent performance tracking with partner_id integration
        - Lead quality analysis and response time metrics
        - Interactive charts with modern Chart.js
        - Mobile-responsive design
        - Real-time data updates
        - Export capabilities for reports
        
        Agent Performance Features:
        - Top agents with leads in progress
        - Most converted leads analysis
        - Junked leads tracking with reasons
        - Fast/slow response time identification
        - Lead update frequency monitoring
        
        Technical Features:
        - Built with Odoo 17 OWL framework
        - Modern JavaScript ES6+ components
        - Responsive CSS with Bootstrap integration
        - Optimized for performance
        - Comprehensive security model
        - RESTful API endpoints
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'crm',
        'sales_team',
        'mail',
        'web',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/crm_executive_dashboard_views.xml',
        'views/crm_strategic_dashboard_views.xml',
        'views/menus.xml',
        'data/crm_dashboard_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'crm_executive_dashboard/static/src/scss/**/*.scss',
            'crm_executive_dashboard/static/src/js/**/*.js',
            'crm_executive_dashboard/static/src/xml/**/*.xml',
        ],
        'web.qunit_suite_tests': [
            'crm_executive_dashboard/static/tests/**/*.js',
        ],
    },
    'demo': [
        'data/demo_data.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'USD',
}
