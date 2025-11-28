{
    'name': 'Enhanced Commission Management System',
    'version': '17.0.2.0.0',
    'summary': 'Advanced commission calculation with dual-group structure and comprehensive automation',
    'description': '''
        Enhanced Commission Management System for Odoo 17
        
        Features:
        - Dual Commission Groups: External (Broker, Referrer, Cashback, Others) and Internal (Agent 1, Agent 2, Manager, Director)
        - Multiple Calculation Methods: Price Unit, Untaxed Total, Fixed Amount
        - Auto-calculation with rate/amount conversion
        - Smart buttons and reference management
        - Commission workflow with status tracking (Draft → Calculated → Confirmed → Paid)
        - Automated purchase order generation for commission payments
        - Comprehensive Commission Management with validation constraints
        - Automated cron processing for eligible commissions
        - Vendor bill creation automation
        - Enhanced reporting and analysis views
        - Proper field grouping and sorting
        - Email notifications and activity tracking
        
        This module provides a comprehensive solution for managing complex commission structures
        with both external and internal stakeholders, complete automation, and advanced workflows.
    ''',
    'category': 'Sales/Commission',
    'author': 'Enhanced Commission Team',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'purchase', 'account', 'mail', 'crm', 'project'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/commission_data.xml',
        'data/commission_demo_data.xml',
        'data/commission_email_templates.xml',
        'views/commission_ax_views.xml',
        'views/sale_order.xml',
        'views/purchase_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'commission_ax/static/src/js/cloudpepper_compatibility_patch.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
}
