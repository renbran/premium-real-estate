# -*- coding: utf-8 -*-
{
    'name': 'OSUS Payment Approval System',
    'version': '17.0.1.1.0',
    'category': 'Accounting/Payments',
    'summary': 'OSUS Properties - Professional Payment Voucher System with Multi-Stage Approval Workflow',
    'description': """
        OSUS Properties Payment Approval System
        ======================================
        
        Professional payment voucher management system designed specifically for 
        OSUS Properties with comprehensive approval workflows and security features.
        
        Key Features:
        -------------
        * 4-Stage Approval Workflow: Reviewer -> Approver -> Authorizer -> Final Approval
        * QR Code Verification: Secure payment authentication system
        * OSUS Branding: Professional styling with OSUS Properties brand colors
        * Role-Based Security: Granular access control for different user roles
        * Digital Signatures: Electronic signature capture for each approval stage
        * Professional Reports: OSUS-branded voucher reports with QR verification
        * Automated Sequences: Smart voucher numbering system
        * Email Notifications: Workflow status updates for stakeholders
        * Mobile Responsive: Optimized for desktop, tablet, and mobile devices
        * Audit Trail: Complete payment history and approval tracking
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'web',
        'mail',
        'portal',
        'website',
    ],
    'data': [
        # Security (Load First)
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data and Sequences
        'data/payment_sequences.xml',
        'data/email_templates.xml',
        
        # Main Views
        'views/account_payment_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_template.xml',
        
        # Website/Portal Views
        'views/payment_verification_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Core JavaScript functionality
            'account_payment_final/static/src/js/payment_workflow.js',
            'account_payment_final/static/src/js/components/payment_approval_widget.js',
            'account_payment_final/static/src/js/fields/qr_code_field.js',
            
            # Core Styles
            'account_payment_final/static/src/scss/osus_branding.scss',
            'account_payment_final/static/src/scss/payment_interface.scss',
            
            # XML templates
            'account_payment_final/static/src/xml/payment_templates.xml',
        ],
        'web.assets_frontend': [
            # Frontend verification portal
            'account_payment_final/static/src/scss/frontend_portal.scss',
            'account_payment_final/static/src/js/frontend/qr_verification.js',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow'],
    },
    'demo': [
        'demo/demo_payments.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
