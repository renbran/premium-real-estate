# -*- coding: utf-8 -*-
{
    'name': 'OSUS Premium Branding Enhanced',
    'version': '17.0.2.0.0',
    'category': 'Theme/Branding',
    'summary': 'Enhanced premium luxury branding system for OSUS Properties - Complete Odoo 17 transformation',
    'description': '''
        OSUS Premium Enhanced Branding Module
        ====================================
        A comprehensive luxury branding transformation system for OSUS Properties that provides:
        🎨 Advanced Visual Design
        ⚡ Performance & Accessibility
        🔧 Enhanced User Experience
        📊 Developer Features
        🎯 Odoo 17 Integration
        Built following Odoo 17 best practices with modern web standards for enterprise-grade luxury user experience.
    ''',
    'author': 'OSUS Properties Development Team',
    'website': 'https://osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/osus_brand_data.xml',
        'views/osus_brand_assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'osus_premium_enhanced/static/src/scss/foundation/_variables.scss',
            'osus_premium_enhanced/static/src/scss/foundation/_mixins.scss',
            'osus_premium_enhanced/static/src/scss/foundation/_base.scss',
            'osus_premium_enhanced/static/src/scss/components/_buttons.scss',
            'osus_premium_enhanced/static/src/scss/components/_forms.scss',
            'osus_premium_enhanced/static/src/scss/components/_navigation.scss',
            'osus_premium_enhanced/static/src/scss/components/_cards.scss',
            'osus_premium_enhanced/static/src/scss/components/_modals.scss',
            'osus_premium_enhanced/static/src/scss/components/_notifications.scss',
            'osus_premium_enhanced/static/src/scss/components/_tables.scss',
            'osus_premium_enhanced/static/src/scss/layout/_header.scss',
            'osus_premium_enhanced/static/src/scss/layout/_sidebar.scss',
            'osus_premium_enhanced/static/src/scss/layout/_content.scss',
            'osus_premium_enhanced/static/src/scss/layout/_footer.scss',
            'osus_premium_enhanced/static/src/scss/utilities/_animations.scss',
            'osus_premium_enhanced/static/src/scss/utilities/_utilities.scss',
            'osus_premium_enhanced/static/src/scss/utilities/_responsive.scss',
            'osus_premium_enhanced/static/src/scss/osus_backend_theme.scss',
            'osus_premium_enhanced/static/src/js/osus_enhanced_system.js',
        ],
        'web.assets_frontend': [
            'osus_premium_enhanced/static/src/scss/foundation/_variables.scss',
            'osus_premium_enhanced/static/src/scss/foundation/_base.scss',
            'osus_premium_enhanced/static/src/scss/frontend/_website.scss',
            'osus_premium_enhanced/static/src/scss/frontend/_portal.scss',
            'osus_premium_enhanced/static/src/scss/components/_buttons.scss',
            'osus_premium_enhanced/static/src/scss/components/_forms.scss',
            'osus_premium_enhanced/static/src/scss/utilities/_animations.scss',
            'osus_premium_enhanced/static/src/js/osus_frontend_enhanced.js',
        ],
        'web.assets_common': [
            'osus_premium_enhanced/static/src/scss/foundation/_variables.scss',
            'osus_premium_enhanced/static/src/fonts/montserrat/montserrat.css',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
