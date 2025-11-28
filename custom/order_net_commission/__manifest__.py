# -*- coding: utf-8 -*-
{
    'name': 'Order Net Commission - OSUS Properties',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Enhanced Sales Order Workflow with Net Commission Calculation',
    'description': """
        Order Net Commission Module - OSUS Properties
        ============================================
        
        This module extends the standard Odoo sales workflow with:
        
        * Custom workflow stages: draft → documentation → commission → sale
        * Role-based access control with specialized groups
        * Net commission calculation and tracking
        * Custom approval workflow with restricted button visibility
        * Override of legacy Send by Email and Confirm buttons
        
        Features:
        ---------
        * Documentation Officer: Can move draft → documentation
        * Commission Analyst: Can move documentation → commission 
        * Sales Approver: Can move commission → sale (final approval)
        * Automatic net commission calculation
        * Enhanced security with group-based permissions
        * Complete statusbar override for controlled workflow
        
        OSUS Properties Branding
        ------------------------
        * Burgundy color scheme (#800020)
        * Professional enterprise styling
        * Consistent with OSUS brand guidelines
    """,
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sales_team',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_form.xml',
        'views/sale_order_tree.xml',
        'data/mail_activity_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'order_net_commission/static/src/scss/order_commission_style.scss',
            'order_net_commission/static/src/js/cloudpepper_rpc_protection.js',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 150,
}
