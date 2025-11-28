# -*- coding: utf-8 -*-
{
    'name': 'Report Font Enhancement',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Reports',
    'summary': 'Enhanced font visibility for reports with high contrast and adaptive transparency',
    'description': """
Report Font Enhancement
======================

This module enhances the font visibility and readability in all Odoo reports by:

Features:
---------
* High contrast font styling with adaptive colors
* Semi-transparent backgrounds that adjust based on content
* Better text readability on various background colors
* Enhanced table styling for reports
* Automatic contrast adjustment for light/dark backgrounds
* Professional font rendering with antialiasing
* Responsive design that works on all screen sizes

The module automatically applies these enhancements to:
* Invoice Reports
* Financial Reports
* Dynamic Account Reports
* Sale Reports
* Purchase Reports
* Custom Reports

Installation:
------------
1. Install the module
2. No configuration needed - enhancements are applied automatically
3. All existing and new reports will benefit from improved font visibility

Technical Features:
------------------
* CSS-based font enhancement
* JavaScript for dynamic contrast calculation
* Automatic background color detection
* Support for RTL languages
* Print-friendly styling
* Mobile responsive design
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base', 
        'web',
        'account',
        'sale',
        'purchase',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/report_enhancement_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'report_font_enhancement/static/src/css/report_font_enhancement.css',
            'report_font_enhancement/static/src/js/report_font_enhancement.js',
        ],
        'web.assets_frontend': [
            'report_font_enhancement/static/src/css/report_font_enhancement.css',
            'report_font_enhancement/static/src/js/report_font_enhancement.js',
        ],
        'web.report_assets_pdf': [
            'report_font_enhancement/static/src/css/report_font_enhancement_pdf.css',
        ],
        'web.report_assets_common': [
            'report_font_enhancement/static/src/css/report_font_enhancement_common.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
    'images': ['static/description/banner.png'],
}
