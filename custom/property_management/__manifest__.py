{
    'name': 'Property Sale Management',
    'version': '18.0.1.0.0',
    'summary': 'Manage property sales and property details',
    'description': '''
        This module allows you to manage property details and their sales.
        - Maintain property records with details like price, address, and status.
        - Link properties to sales and auto-fill relevant details.
        - Generate broker commission invoices based on property sales.
    ''',
    'author': 'Renbran',
    'website': 'https://yourcompany.com',
    'category': 'Real Estate',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'reports/property_sale_management.xml',
        'reports/property_sale_report_template.xml',
        'reports/sales_offer_report_template.xml',
        'reports/property_sales_offer_template.xml',
        'reports/property_contract_template.xml',
        'reports/statement_of_account_template.xml',
        'views/property_sale_views.xml',
        'views/property_property_views.xml',
        'views/account_move_views.xml',
        'views/broker_commission.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}