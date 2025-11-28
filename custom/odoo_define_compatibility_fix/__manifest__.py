{
    'name': 'Odoo Define Compatibility Fix',
    'version': '17.0.1.0.0',
    'category': 'Technical',
    'summary': 'Emergency fix for "odoo.define is not a function" JS errors.',
    'description': """
This module provides a compatibility layer for legacy JavaScript code by ensuring
'odoo.define' is available globally. It loads a shim before other assets to prevent
errors in modules that do not adhere to the modern Odoo JS module system.
    """,
    'author': 'Sixth',
    'website': 'https://www.odoo.com',
    'depends': ['web'],
    'assets': {
            'web.assets_backend': [
                ('prepend', 'odoo_define_compatibility_fix/static/src/js/cloudpepper_compatibility_patch.js'),
                ('prepend', 'odoo_define_compatibility_fix/static/src/js/emergency_odoo_define_global_fix.js'),
                'odoo_define_compatibility_fix/static/src/js/main_component.js',
            ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
}
