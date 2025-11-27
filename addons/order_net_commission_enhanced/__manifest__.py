# -*- coding: utf-8 -*-
{
    'name': 'Order Net Commission Enhanced - OSUS Properties',
    'version': '17.0.2.0.0',
    'category': 'Sales',
    'summary': 'Enhanced Sales Order Workflow with Commission Integration',
    'description': """
        Order Net Commission Enhanced Module - OSUS Properties
        =====================================================
        
        This module enhances the order_net_commission module by integrating with:
        - commission_ax: Advanced commission management
        - order_status_override: Enhanced workflow management
        
        Features:
        ---------
        * Enhanced workflow: draft → documentation → commission → allocation → final_review → approved → posted
        * Commission integration with external/internal commission structures
        * Advanced security with role-based permissions
        * CloudPepper compatibility with RPC error prevention
        * Enhanced reporting with commission breakdown
        * Real-time commission calculation and tracking
        * Workflow assignment and tracking
        * OSUS Properties branding and styling
        
        Integration Benefits:
        --------------------
        * Unified commission calculation across both external and internal teams
        * Enhanced workflow with commission-specific stages
        * Comprehensive reporting with commission analytics
        * Seamless integration between commission and order status management
        * Advanced security and access control
        
        CloudPepper Fixes:
        -----------------
        * RPC error prevention with proper field handling
        * Template compatibility enhancements
        * JavaScript error handling improvements
        * Enhanced validation and error recovery
        
        OSUS Properties Branding
        ------------------------
        * Burgundy color scheme (#800020)
        * Professional enterprise styling
        * Enhanced commission reporting templates
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
        'order_net_commission',  # Our base module
        'commission_ax',         # Commission management
        'order_status_override', # Order status workflow
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_enhanced_form.xml',
        'views/sale_order_enhanced_tree.xml',
        'views/commission_dashboard_view.xml',
        'reports/enhanced_order_commission_report.xml',
        'data/enhanced_mail_activity_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'order_net_commission_enhanced/static/src/scss/enhanced_commission_style.scss',
            'order_net_commission_enhanced/static/src/js/cloudpepper_rpc_protection.js',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 140,
}
