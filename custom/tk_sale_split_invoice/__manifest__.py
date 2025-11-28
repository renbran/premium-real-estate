# -*- coding: utf-8 -*-
{
    'name': 'Sales Order Split Invoice',
    'description': """
        Sales Order Split Invoice
    """,
    'summary': 'Sales Order Split Invoice',
    'version': '1.0',
    'category': 'Sales',
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'depends': [
        'sale_management', 'stock',
    ],
    'data': [
        #  views
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/res_config_setting_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
