# -*- coding: utf-8 -*-
{
    'name': 'Webhook CRM Lead Handler',
    'version': '17.0.1.0.0',
    'category': 'CRM',
    'summary': 'Handle external webhooks for CRM lead creation',
    'description': """
        This module provides a comprehensive webhook handler for creating CRM leads
        from external sources with advanced field mapping capabilities.
        
        Features:
        - Webhook endpoints for CRM lead creation
        - Flexible field mapping configuration
        - Data transformation and validation
        - Support for multiple webhook sources
        - Error handling and logging
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'crm', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/webhook_mapping_views.xml',
        'data/webhook_mapping_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
