# -*- coding: utf-8 -*-
{
    'name': 'Contact KYC',
    'version': '17.0.1.0.0',
    'summary': 'Know-Your-Customer fields and printable KYC form for contacts',
    'description': """
        Contact KYC Module
        ==================
        
        This module adds Know-Your-Customer (KYC) functionality to contacts including:
        
        * Personal information fields (DOB, gender, aliases)
        * Passport information tracking
        * UAE residency details
        * Employment information
        * Financial information (source of funds/wealth, income)
        * Politically Exposed Person (PEP) status
        * Printable KYC form report
        * KYC data management interface
        
        Features:
        ---------
        * KYC tab in partner form view
        * Configurable source of funds and wealth options
        * Professional KYC form report
        * Security groups for KYC management
        * Menu structure for KYC configuration
    """,
    'category': 'Contacts',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/kyc_data.xml',
        'views/contact_kyc_views.xml',
        'reports/contact_kyc_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}