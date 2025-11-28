# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Mates, Walnut Software Solutions
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Odoo 17 Accounting Community',
    'version': '17.0.1.0.3',
    'category': 'Accounting',
    'summary': 'Accounting Reports, Asset Management and Budget, Recurring Payments, '
               'Lock Dates, Fiscal Year, Accounting Dashboard, Financial Reports, '
               'Customer Follow up Management, Bank Statement Import',
    'description': 'Odoo 17 Financial Reports, Asset Management and '
                   'Budget, Financial Reports, Recurring Payments, '
                   'Bank Statement Import, Customer Follow Up Management,'
                   'Account Lock Date, Accounting Dashboard',
    'live_test_url': 'https://www.youtube.com/c/OdooMates',
    'sequence': '1',
    'website': 'https://www.walnutit.com',
    'author': 'Odoo Mates, Walnut Software Solutions, Odoo SA',
    'maintainer': 'Odoo Mates, Walnut Software Solutions',
    'license': 'LGPL-3',
    'support': 'odoomates@gmail.com',
    'depends': [
        'account',  # Base accounting module
        'accounting_pdf_reports',
    ],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/settings.xml',
        'views/account_group.xml',
        'views/account_tag.xml',
        'views/res_partner.xml',
        'views/account_bank_statement.xml',
        'views/payment_method.xml',
        'views/reconciliation.xml',
        'views/account_journal.xml',
    ],
    'application': True,
    'images': ['static/description/banner.gif'],
}

