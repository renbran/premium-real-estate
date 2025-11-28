# -*- coding: utf-8 -*-
{
    'name': 'Website Menu Fix',
    'version': '17.0.1.0.0',
    'category': 'Website',
    'summary': 'Fix website layout menu rendering issues',
    'description': """
This module fixes the website layout menu rendering error that occurs when
templates try to access backend menu methods in website context.
    """,
    'author': 'Odoo Fix',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
        'views/website_layout_fix.xml',
    ],
    'python': [
        'models',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
