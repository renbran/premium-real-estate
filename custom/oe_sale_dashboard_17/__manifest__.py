# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard - Odoo 17',
    'version': '17.0.2.0.0',
    'category': 'Sales',
    'summary': 'Enhanced Sales Dashboard - Professional Charts, Analytics & OSUS Brand Theme',
    'description': """
Enhanced Sales Dashboard for Odoo 17 - Professional Edition
===========================================================

IMPORTANT: This module provides a completely independent sales dashboard.

This module provides a comprehensive enhanced sales dashboard with:

* ZERO INHERITANCE of sale.order model - completely separate
* NO MODIFICATIONS to quotation/order forms or views
* Independent TransientModel 'sale.dashboard' for data only
* Visual analytics with OSUS burgundy/gold brand theme
* Interactive Chart.js visualizations with professional color palette
* Mobile-responsive design optimized for business presentation
* Real-time data updates through optimized data queries

ENHANCED FEATURES:
-----------------
* Agent Rankings by deal count, price_unit and amount_total
* Broker Rankings by deal count, price_unit and amount_total
* Flexible Date Integration (booking_date with fallback to date_order)
* Sale Type Filtering with multi-select support
* Enhanced performance tables with detailed analytics
* Comprehensive metrics and KPIs
* Professional OSUS branding integration

Complete Independence:
---------------------
* sale.order forms remain 100% unchanged
* No view inheritance affecting quotations
* No data modifications to sales workflow
* Pure read-only dashboard functionality
* Zero impact on sales module operations

Professional Architecture:
--------------------------
* TransientModel 'sale.dashboard' - completely separate from sale.order
* Client-side dashboard rendering with modern JavaScript
* Optimized read-only queries to existing sale.order data
* No model extensions or inheritance
* No view modifications to sales module
* Intelligent field detection with graceful fallbacks

Professional Features:
---------------------
* Interactive charts with OSUS brand colors (#4d1a1a burgundy)
* Agent and broker ranking visualizations
* Sales pipeline visualization in burgundy/gold theme
* Performance KPIs with professional styling
* Monthly/quarterly reports with brand consistency
* Export capabilities with professional formatting
* Multi-currency support with enhanced formatting
* Sale type filtering for targeted analysis
* Responsive design for mobile and desktop

Optional Module Integration:
---------------------------
* le_sale_type (for sale_order_type_id filtering) - optional
* commission_ax (for agent1_partner_id and broker_partner_id) - optional
* invoice_report_for_realestate (for booking_date field) - optional

This module is SAFE to install and will NOT affect your sales quotation workflow.
All enhancements are contained within the dashboard interface only.
Works with or without optional modules - graceful degradation included.
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osusproperties.com',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'web',
        'le_sale_type',
        'invoice_report_for_realestate',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_dashboard_views.xml',
        'views/sales_dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            ('include', 'web._assets_helpers'),
            # Emergency fixes (load first)
            ('prepend', 'oe_sale_dashboard_17/static/src/js/cloudpepper_dashboard_fix.js'),
            
            # Local Chart.js (no CDN dependency)
            'oe_sale_dashboard_17/static/src/js/chart.min.js',
            
            # CSS Files
            'oe_sale_dashboard_17/static/src/css/dashboard.css',
            'oe_sale_dashboard_17/static/src/css/enhanced_dashboard.css',
            
            # XML Templates
            'oe_sale_dashboard_17/static/src/xml/sales_dashboard_main.xml',
            'oe_sale_dashboard_17/static/src/xml/enhanced_sales_dashboard.xml',
            
            # JavaScript Files
            'oe_sale_dashboard_17/static/src/js/sales_dashboard.js',
            'oe_sale_dashboard_17/static/src/js/enhanced_sales_dashboard.js',
        ],
    },
    'demo': [],
    'images': ['static/description/banner.svg'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
