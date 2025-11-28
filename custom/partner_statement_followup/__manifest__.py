# -*- coding: utf-8 -*-
{
    'name': 'Partner Statement & Follow-up Manager',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Advanced Partner Statement with Follow-up Management',
    'description': """
        Partner Statement & Follow-up Manager
        ====================================
        
        Replace and extend account_followup with comprehensive features:
        
        Key Features:
        -------------
        * One-screen partner statement with ageing analysis
        * Printable and e-mailable PDF statements
        * Advanced follow-up tracking and automation
        * On-the-fly reconciliation from statement wizard
        * Multi-level follow-up system with customizable templates
        * Portal integration for customer self-service
        * Comprehensive audit trail and history
        
        Technical Features:
        ------------------
        * Multi-company support with proper security rules
        * Automated follow-up scheduling with cron jobs
        * Customizable ageing buckets and follow-up levels
        * Advanced reconciliation suggestions
        * Professional PDF reports with company branding
        * Portal download functionality
        * Comprehensive test coverage
        
        Perfect for businesses requiring professional receivables
        management with automated follow-up capabilities.
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
        'portal',
        'web',
    ],
    'data': [
        # Security
        'security/statement_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/statement_config_data.xml',
        'data/followup_levels.xml',
        'data/mail_templates.xml',
        'data/cron_jobs.xml',
        
        # Views
        'views/partner_views.xml',
        'views/wizard_views.xml',
        'views/statement_menus.xml',
        'views/alias_model_views.xml',
        'views/statement_config_views.xml',
        
        # Wizards
        'wizards/statement_wizard_views.xml',
        'wizards/batch_followup_wizard_views.xml',
        
        # Reports
        'reports/statement_report.xml',
        'reports/statement_template.xml',
    ],
    'demo': [
        'demo/statement_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'external_dependencies': {
        'python': [],
    },
}
