# -*- coding: utf-8 -*-
{
    'name': 'Enhanced REST API for Server-Wide Modules',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Enhanced REST API functionality for all server-wide modules including CRM, Sales, Payments, and more',
    'description': """
        Enhanced REST API Module for Server-Wide Integration
        
        This module extends the base REST API functionality to provide comprehensive 
        API endpoints for all major Odoo modules including:
        
        Features:
        - CRM Dashboard API endpoints
        - Sales Kit API integration  
        - Payment Account Enhanced API
        - Rental Management API
        - Enhanced authentication and security
        - Bulk operations support
        - Advanced filtering and pagination
        - Real-time data synchronization
        - API versioning support
        
        This module is designed to work as a server-wide module and provides
        RESTful API access to all major business functions.
    """,
    'author': 'OSUS Technology Solutions',
    'website': 'https://www.osus.com',
    'depends': [
        'base', 
        'web',
        'rest_api_odoo',  # Base REST API module
        'crm',
        'sale',
        'account',
        'contacts',
        'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security_groups.xml',
        'views/api_config_views.xml',
        'views/api_logs_views.xml',
        'data/api_endpoints_data.xml',
    ],
    'external_dependencies': {
        'python': ['jwt', 'requests', 'qrcode', 'Pillow'],
    },
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'server_wide': True,  # This indicates it's a server-wide module
}
