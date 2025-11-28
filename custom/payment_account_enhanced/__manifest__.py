{
    'name': 'Account Payment Final - Professional Payment Management',
    'version': '17.0.1.2.0',
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
        # Security (Load first) - Use the main security file
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence.xml',
        'data/mail_template_data.xml',
        'data/cron_data.xml',
        
        # Reports - Single well-structured one-page voucher
        'reports/payment_voucher_dual_design.xml',  # Dual design with smart detection (Receipt: Green, Payment: Blue)
        
        # Views (Load actions before menus that reference them)
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/payment_approval_history_views.xml',
        'views/payment_qr_verification_views.xml',
        'views/payment_workflow_stage_views.xml',
        'views/website_verification_templates.xml',
        'views/payment_dashboard_views.xml',
        'views/executive_views.xml',  # Executive-focused views and filters
        
        # Menus (Load after views to ensure actions exist)
        'views/menus.xml',
        
        # Wizards
        'wizards/register_payment.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'payment_account_enhanced/static/src/css/payment_enhanced.css',
        ],
        'web.assets_frontend': [
            'payment_account_enhanced/static/src/css/payment_enhanced.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 15,
    'post_init_hook': 'post_init_hook',
}
