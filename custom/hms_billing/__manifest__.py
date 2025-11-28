# -*- coding: utf-8 -*-
{
    'name': 'HMS Billing Management',
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Billing',
    'summary': 'Advanced billing and payment management for Hospital Management System',
    'description': '''
        HMS Billing Management Extension
        ================================
        
        Enhanced billing features for Basic Hospital Management System:
        
        * Advanced invoice generation with customizable templates
        * Insurance claim processing and management
        * Payment tracking and reconciliation
        * Billing reports and analytics
        * Multi-payment method support
        * Automatic billing workflows
        * Patient payment history
        * Insurance coverage verification
        * Billing reminders and notifications
        * Revenue management and analytics
        
        This module extends the basic HMS functionality with comprehensive
        billing and financial management capabilities.
    ''',
    'author': 'HMS Development Team',
    'website': 'https://www.example.com',
    'depends': ['basic_hms', 'account', 'sale', 'purchase'],
    'data': [
        'security/billing_security.xml',
        'security/ir.model.access.csv',
        'views/hms_billing_menu.xml',
        'views/medical_billing_views.xml',
        'views/medical_payment_views.xml',
        'views/medical_insurance_claim_views.xml',
        'views/res_partner_billing_views.xml',
        'wizard/billing_report_wizard_views.xml',
        'wizard/insurance_claim_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}