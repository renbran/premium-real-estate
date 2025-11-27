{
    'name': 'Account Payment Final - Professional Payment Management',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Complete payment workflow with QR verification, 4-stage approval, and professional vouchers',
    'description': """
        Professional Payment Management System for Odoo 17
        ==================================================
        
        **Key Features:**
        • 4-stage approval workflow (Draft → Review → Approval → Authorization → Posted)
        • QR code generation and public verification portal
        • Professional payment and receipt voucher templates
        • Invoice/Bill approval integration
        • Comprehensive audit trail and approval history
        • Role-based security and permissions
        • Company-level configuration and branding
        • Bulk operations and advanced reporting
        
        **Business Benefits:**
        • Enhanced security through QR verification
        • Streamlined approval processes
        • Professional document generation
        • Complete audit compliance
        • Flexible workflow configuration
        
        This module provides enterprise-grade payment management with complete
        workflow control, security, and professional reporting capabilities.
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osusproperties.com',
    'depends': [
        'base',
        'account',
        'mail',
        'website',
        'portal'
    ],
    'external_dependencies': {
        'python': ['qrcode', 'Pillow']
    },
    'data': [
        # Security (Load first)
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/payment_sequence.xml',
        'data/mail_template_data.xml',
        
        # Views
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/payment_approval_history_views.xml',
        'views/payment_qr_verification_views.xml',
        'views/payment_workflow_stage_views.xml',
        'views/res_config_settings_views.xml',
        'views/website_verification_templates.xml',
        'views/menuitems.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/invoice_bill_approval_report.xml',
        
        # Wizards
        'wizard/payment_register_views.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'account_payment_final/static/src/css/payment_workflow.css',
        ],
        'web.assets_frontend': [
            'account_payment_final/static/src/css/verification_portal.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 15,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
