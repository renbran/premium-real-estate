# -*- coding: utf-8 -*-
{
    'name': 'Frontend Enhancement - Order References & File Upload',
    'version': '17.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Enhanced frontend views with order references and file upload functionality',
    'description': """
        Frontend Enhancement Module for Odoo 17
        =======================================
        
        This module enhances the frontend user experience by providing:
        
        Key Features:
        * Display Client Order Reference in sales orders
        * Display Customer Reference in invoices  
        * File upload functionality for user records
        * Automatic file attachment to record log notes
        * Professional UI/UX improvements
        * Portal integration for customers
        * Advanced search and filtering capabilities
        
        Compatible with Odoo 17 architecture and follows OSUS Properties branding standards.
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osusproperties.com',
    'depends': [
        'base',
        'sale',
        'account', 
        'mail',
        'portal',
        'web',
        'website'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/sale_order_views.xml',
        'views/account_move_views.xml', 
        'views/res_users_views.xml',
        'views/reference_dashboard.xml',
        
        # Data
        'data/file_upload_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'frontend_enhancement/static/src/css/frontend_enhancement.css',
            'frontend_enhancement/static/src/js/file_upload_widget.js',
        ],
        'web.assets_frontend': [
            'frontend_enhancement/static/src/css/frontend_public.css',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    'sequence': 100,
}
