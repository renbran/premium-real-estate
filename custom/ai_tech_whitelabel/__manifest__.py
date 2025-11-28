# -*- coding: utf-8 -*-
{
    'name': 'AI Tech White-Label System',
    'version': '17.0.1.0.0',
    'category': 'Themes/Backend',
    'summary': 'Complete AI-Tech White-Label Backend Theme with Configuration',
    'description': '''
AI-Tech White-Label System
===========================

Features:
---------
* Full backend white-labeling with AI/Tech aesthetic
* Configurable from Settings > General Settings
* Dynamic company branding (logos, colors, fonts)
* Modern glassmorphism and gradient effects
* Animated AI-inspired UI elements
* Custom login page with futuristic design
* Dynamic favicon and app icons
* Dark mode with cyan/purple accent colors
* Responsive and mobile-friendly
* Easy switching between brand configurations

Backend Configuration:
---------------------
* Company Name & Logo
* Primary/Secondary Colors
* Accent Colors (AI theme)
* Custom Fonts
* Login Background
* Favicon
* All configurable from Odoo backend

    ''',
    'author': 'OSUS Tech',
    'website': 'https://erposus.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/webclient_templates.xml',
        'views/login_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Core Theme Variables & Styles
            ('prepend', 'ai_tech_whitelabel/static/src/scss/variables.scss'),
            'ai_tech_whitelabel/static/src/scss/animations.scss',
            'ai_tech_whitelabel/static/src/scss/ai_theme.scss',
            'ai_tech_whitelabel/static/src/scss/components.scss',
            'ai_tech_whitelabel/static/src/scss/navbar.scss',
            'ai_tech_whitelabel/static/src/scss/sidebar.scss',
            'ai_tech_whitelabel/static/src/scss/forms.scss',
            'ai_tech_whitelabel/static/src/scss/glassmorphism.scss',
            
            # JavaScript Components
            'ai_tech_whitelabel/static/src/js/theme_config.js',
            'ai_tech_whitelabel/static/src/js/dynamic_colors.js',
            'ai_tech_whitelabel/static/src/js/particles.js',
        ],
        'web.assets_frontend': [
            'ai_tech_whitelabel/static/src/scss/login.scss',
            'ai_tech_whitelabel/static/src/scss/frontend.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
