# -*- coding: utf-8 -*-
#############################################################################
#
#    Ingenuity Info
#
#    Copyright (C) 2023-TODAY Ingenuity Info(<https://ingenuityinfo.in>)
#    Author: Ingenuity Info(<https://ingenuityinfo.in>)
#
#
#############################################################################
{
    'name': "QR Code on Invoice and Payment with Validation",
    'author': "Ingenuity Info",
    'category': 'Other',
    'summary': """ Generate QR Codes for Invoices and Payments with secure validation system for payment authenticity verification. """,
    'website': "https://ingenuityinfo.in",
    'company': 'Ingenuity Info',
    'maintainer': 'Ingenuity Info',
    'version': '17.0.1.0',
    'price': 0.0,
    'currency': 'EUR',
    'description': """ 
        Enhanced QR Code Generator for Invoices and Payments with Payment Validation System:
        
        Features:
        - Generate QR codes for invoices and payments
        - Secure payment validation system with cryptographic tokens
        - QR codes redirect to validation webpages for payment authenticity verification
        - Token-based security with expiry dates and access tracking
        - Professional validation pages with payment details
        - Regenerate validation tokens as needed
        - Track validation access and usage statistics
        - Compatible with existing invoice and payment workflows
        
        The QR codes will be visible on Invoice and Payment forms and can be printed on reports.
        Payment QR codes link to secure validation pages that verify payment authenticity.
    """,
    'depends': [
        'web',
        'account'
    ],
    'data': [
        'report/account_invoice_report_template.xml',
        'report/account_payment_report_template.xml',
        'views/qr_code_invoice_view.xml',
        'views/qr_code_payment_view.xml',
        'templates/payment_validation_templates.xml',
    ],
    'qweb': [
        ],
    "assets": {
        "web.assets_backend": [
        ],
        "web.assets_tests": [
        ],
    },
    "images": ['static/description/Banner.gif'],
    "license": "AGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False,
}