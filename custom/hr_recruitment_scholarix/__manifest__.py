# -*- coding: utf-8 -*-
{
    'name': 'SCHOLARIX HR Recruitment Enhancement',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Recruitment',
    'summary': 'Enhanced HR Recruitment with custom email templates and contract proposal automation for SCHOLARIX',
    'description': """
        SCHOLARIX HR Recruitment Enhancement
        ===================================
        
        This module enhances the standard Odoo HR Recruitment module with:
        
        * Automatic email sending when applicant reaches "Contract Proposal" stage
        * Customizable responsive email templates with SCHOLARIX branding
        * Professional training period offer emails with dynamic content
        * Custom button integration in applicant form view
        * Advanced email wizard for template customization
        * Mobile-responsive email design with SCHOLARIX colors and branding
        
        Features:
        ---------
        * Professional email templates with circuit-style SCHOLARIX logo
        * Responsive design optimized for all devices
        * Dynamic data population from applicant records
        * Customizable content through email wizard
        * Integration with contract proposal recruitment stage
        * SCHOLARIX brand colors and professional styling
        * Training period offer template with terms and conditions
        
        Perfect for companies looking to automate their recruitment communication
        with professional, branded email templates.
    """,
    'author': 'SCHOLARIX Global Consultants',
    'website': 'https://scholarix.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr_recruitment',
        'mail',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/test_simple.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_backend': [
            'hr_recruitment_scholarix/static/src/js/applicant_form.js',
        ],
    },
}