# -*- coding: utf-8 -*-
{
    'name': 'SCHOLARIX Custom PDF Reports',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Reports',
    'summary': 'Custom PDF Reports for Invoice and Sales Orders with SCHOLARIX Branding',
    'description': """
        SCHOLARIX Custom PDF Reports
        ============================
        
        This module provides professionally designed PDF reports for:
        * Customer Invoices with SCHOLARIX branding
        * Sales Orders with enhanced layout
        * Print-optimized templates
        * Professional footer with company information
        
        Features:
        ---------
        * Custom QWeb templates with SCHOLARIX design
        * Professional PDF layouts with company branding
        * Enhanced invoice and sales order reports
        * Print-optimized styling
        * Responsive design elements
        * Custom CSS styling for professional appearance
        
        Author: SCHOLARIX Global Consultants
        Website: https://scholarixglobal.com
        Email: info@scholarixglobal.com
    """,
    'author': 'SCHOLARIX Global Consultants',
    'website': 'https://scholarixglobal.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'sale',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/report_actions.xml',
        'reports/report_invoice_templates.xml',
        'reports/report_sale_templates.xml',
        'reports/report_styles.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            'custom_reports_pdf/static/src/css/report_styles.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'sequence': 10,
}