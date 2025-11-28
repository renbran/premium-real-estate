# -*- coding: utf-8 -*-
{
    'name': 'White Label Branding',
    'version': '17.0.1.0.0',
    'category': 'Base',
    'summary': 'Remove Odoo branding and replace with custom company branding',
    'description': """
        White Label Branding Module
        ===========================
        
        This module allows you to:
        * Replace Odoo branding with your company branding
        * Hide Odoo documentation and support links
        * Customize login page and footer
        * Replace Odoo logo with custom logo
        * Customize email templates to remove Odoo references
        
        Perfect for companies who want to completely white-label their Odoo instance.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'web',
        'mail',
        'digest',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/assets.xml',
        'data/white_label_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'white_label_branding/static/src/css/white_label.css',
            'white_label_branding/static/src/js/white_label.js',
        ],
        'web.assets_frontend': [
            'white_label_branding/static/src/css/frontend.css',
            'white_label_branding/static/src/js/frontend.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
