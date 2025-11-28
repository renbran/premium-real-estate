{
    'name': 'OSUS Premium Branding',
    'version': '17.0.1.0.0',
    'category': 'Theme/Branding',
    'summary': 'Premium luxury branding for OSUS Properties - Global Odoo transformation',
    'description': '''
        OSUS Premium Branding Module
        ============================
        
        This module transforms your entire Odoo interface to align with OSUS Properties' 
        luxury brand identity, featuring:
        
        * Burgundy & Gold color palette implementation
        * Montserrat typography integration
        * Curved design elements inspired by OSUS logo
        * Premium button and form styling
        * Sophisticated gradients and visual effects
        * Luxury-grade spacing and layout refinements
        * Enhanced visual hierarchy for premium feel
        * Smooth transitions and micro-animations
        
        Designed to provide a consistent, luxury experience across all Odoo applications
        while maintaining full functionality and performance.
    ''',
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        # Backend Assets (Main Odoo Interface)
        'web.assets_backend': [
            'osus_premium/static/src/scss/osus_variables.scss',
            'osus_premium/static/src/scss/osus_base.scss',
            'osus_premium/static/src/scss/osus_layout.scss',
            'osus_premium/static/src/scss/osus_navigation.scss',
            'osus_premium/static/src/scss/osus_components.scss',
            'osus_premium/static/src/scss/osus_forms.scss',
            'osus_premium/static/src/scss/osus_buttons.scss',
            'osus_premium/static/src/scss/osus_animations.scss',
        ],
        
        # Frontend Assets (Website/Portal)
        'web.assets_frontend': [
            'osus_premium/static/src/scss/osus_variables.scss',
            'osus_premium/static/src/scss/osus_frontend.scss',
            'osus_premium/static/src/scss/osus_components.scss',
            'osus_premium/static/src/scss/osus_buttons.scss',
            'osus_premium/static/src/scss/osus_forms.scss',
            'osus_premium/static/src/scss/osus_animations.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}