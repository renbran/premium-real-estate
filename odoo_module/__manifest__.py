# -*- coding: utf-8 -*-
{
    'name': 'Bill Automation Webhook',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Automated vendor bill creation from webhook integration',
    'description': """
Bill Automation Webhook
========================

This module provides automated vendor bill creation through webhook integration
with external systems like Zapier, enabling seamless processing of bills
uploaded to Google Drive with AI-powered OCR extraction.

Key Features:
-------------
* Webhook endpoint for external bill processing systems
* Automatic vendor bill creation from structured data
* Vendor auto-creation if not exists
* Duplicate bill prevention
* File attachment support
* Comprehensive logging and monitoring
* Error handling and recovery
* Security features with API key authentication
* Dashboard for monitoring processing status

Technical Specifications:
-------------------------
* Compatible with Odoo 17, 18, 19
* RESTful API endpoint: /api/v1/bills/create
* JSON payload support
* File attachment via URL download
* Automatic vendor matching and creation
* Configurable duplicate detection
* Real-time processing logs
* Error notification system

Use Cases:
----------
* Zapier automation from Google Drive
* Third-party accounting system integration
* Bulk bill processing from external sources
* AI-powered OCR bill processing workflows
* Mobile app bill submission

Installation:
-------------
1. Copy this module to your Odoo addons directory
2. Restart Odoo service
3. Go to Apps and install "Bill Automation Webhook"
4. Configure webhook settings in Accounting → Configuration
5. Test with provided webhook URL

Authors: Bill Automation Project Team
License: LGPL-3
    """,
    'author': 'Bill Automation Project',
    'website': 'https://github.com/bill-automation',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'purchase',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/webhook_log_views.xml',
        'views/bill_automation_config_views.xml',
        'views/account_move_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 100,
    'images': [],
    'external_dependencies': {
        'python': ['requests']
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}