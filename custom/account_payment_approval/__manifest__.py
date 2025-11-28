# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Approval',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Advanced Payment Approval Workflow with Digital Signatures and QR Verification',
    'description': """
        Advanced Payment Approval Workflow System
        ==========================================
        
        This module provides a comprehensive payment approval workflow system with:
        
        * Multi-tier approval process (6 security groups)
        * Digital signature integration
        * QR code verification system
        * Bulk approval operations
        * Payment voucher generation
        * Comprehensive audit trail
        * Email notifications
        * Advanced reporting
        
        Features:
        ---------
        * Voucher State Management: Draft → Submitted → Under Review → Approved → Authorized → Posted
        * Role-based Security: Creator, Reviewer, Approver, Authorizer, Finance Manager, Administrator
        * Digital Signatures: Required signatures for critical approval steps
        * QR Verification: Secure QR codes for payment verification
        * Bulk Operations: Approve multiple payments at once
        * Enhanced Reporting: Payment voucher reports and summaries
        * Account Move Integration: Enhanced journal entry views with payment tracking
        * Reconciliation Navigator: Advanced reconciliation tracking and navigation
        
        Security Groups:
        ----------------
        * Payment Approval - Creator: Can create and submit payments
        * Payment Approval - Reviewer: Can review submitted payments
        * Payment Approval - Approver: Can approve reviewed payments
        * Payment Approval - Authorizer: Can authorize approved payments
        * Payment Approval - Finance Manager: Can post authorized payments
        * Payment Approval - Administrator: Full access to all operations
        
        Technical Features:
        -------------------
        * Modern Odoo 17 syntax (no deprecated attrs/states)
        * Stored computed fields for fast searching
        * Robust field compatibility checking
        * Safe XPath expressions using reliable field targets
        * Comprehensive error handling and validation
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osus.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
        'web',
        'portal',
        'payment',
        'account_payment',
    ],
    'external_dependencies': {
        'python': [
            'qrcode',
            'PIL',
            'reportlab',
            'xlsxwriter',
        ],
    },
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/payment_voucher_security.xml',
        
        # Data
        'data/voucher_sequence.xml',
        'data/email_templates.xml',
        'data/system_parameters.xml',
        'data/cron_jobs.xml',
        'data/server_actions.xml',
        'data/qr_verification_data.xml',
        
        # Views
        'views/menus.xml',
        'views/menu_items.xml',
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/wizard_views.xml',
        'views/payment_report_wizard.xml',
        'views/qr_verification_templates.xml',
        'views/res_config_settings_views.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_summary_report.xml',
        'reports/receipt_voucher_report.xml',
        'reports/qr_verification_report.xml',
        'reports/report_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_payment_approval/static/src/scss/payment_approval.scss',
            'account_payment_approval/static/src/js/digital_signature_widget.js',
            'account_payment_approval/static/src/js/payment_approval_dashboard.js',
            'account_payment_approval/static/src/js/qr_verification.js',
            'account_payment_approval/static/src/js/qr_widget_enhanced.js',
            'account_payment_approval/static/src/xml/account_move_templates.xml',
            'account_payment_approval/static/src/xml/dashboard_templates.xml',
            'account_payment_approval/static/src/xml/digital_signature_templates.xml',
            'account_payment_approval/static/src/xml/payment_approval_templates.xml',
            'account_payment_approval/static/src/xml/qr_verification_templates.xml',
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'pre_init_hook': None,
    'post_init_hook': None,
    'uninstall_hook': None,
}
