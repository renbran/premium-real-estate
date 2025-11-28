# -*- coding: utf-8 -*-
#############################################################################
#
#    Scholarix Global Consultants
#
#    Copyright (C) 2025-TODAY Scholarix Global Consultants
#    Author: Scholarix AI Development Team
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#############################################################################
{
    'name': 'Scholarix AI Theme',
    'version': '18.0.1.0.0',
    'category': 'Theme/Corporate',
    'summary': 'Futuristic AI Tech Theme for Scholarix Global Consultants',
    'description': """
        A cutting-edge, futuristic web theme designed specifically for 
        Scholarix Global Consultants. This theme embodies the aesthetic 
        of an AI wizard tech company with:
        
        • Futuristic design elements with neon accents
        • Dark theme with electric blue color scheme
        • Circuit board pattern overlays
        • Holographic effects and animations
        • AI-themed iconography and elements
        • Professional yet innovative appearance
        • Fully responsive design
        • Optimized for consulting and tech services
        
        Perfect for showcasing AI expertise and advanced technology consulting services.
    """,
    'author': 'Scholarix Global Consultants',
    'company': 'Scholarix Global Consultants',
    'maintainer': 'Scholarix AI Development Team',
    'website': "https://scholarixglobal.com",
    'depends': ['base', 'website', 'website_sale', 'website_blog'],
    'data': [
        'views/layout_templates.xml',
        'views/index/index_banner.xml',
        'views/index/index_about.xml',
        'views/index/index_services.xml',
        'views/index/index_portfolio.xml',
        'views/index/index_testimonials.xml',
        'views/index/index_blog.xml',
        'views/index/index_contact.xml',
        'views/about/about.xml',
        'views/services/services.xml',
        'views/portfolio/portfolio.xml',
        'views/blog/blog.xml',
        'views/contact/contact.xml',
        'views/website_templates.xml',
        'views/snippets/snippets.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            # External libraries for enhanced functionality
            'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js',
            'https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css',
            
            # Custom SCSS files
            'scholarix_theme/static/src/scss/primary_variables.scss',
            'scholarix_theme/static/src/scss/bootstrap_overrides.scss',
            'scholarix_theme/static/src/scss/scholarix_loading.scss',
            'scholarix_theme/static/src/scss/scholarix_cursor.scss',
            'scholarix_theme/static/src/scss/scholarix_main.scss',
            'scholarix_theme/static/src/scss/scholarix_animations.scss',
            'scholarix_theme/static/src/scss/scholarix_components.scss',
            'scholarix_theme/static/src/scss/scholarix_responsive.scss',
            
            # Custom JavaScript - Load in correct order
            'scholarix_theme/static/src/js/scholarix_loader.js',
            'scholarix_theme/static/src/js/scholarix_cursor.js',
            'scholarix_theme/static/src/js/scholarix_3d_hero.js',
            'scholarix_theme/static/src/js/scholarix_animations.js',
            'scholarix_theme/static/src/js/scholarix_particles.js',
            'scholarix_theme/static/src/js/scholarix_main.js',
            
            # Custom CSS (compiled from SCSS)
            'scholarix_theme/static/src/css/scholarix_theme.css',
        ],
        'web.assets_backend': [
            'scholarix_theme/static/src/scss/backend_overrides.scss',
        ]
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/theme_screenshot.png',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 0,
    'currency': 'USD',
}
