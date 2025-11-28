{
    'name': 'OSUS Properties Website',
    'version': '17.0.1.0',
    'category': 'Website',
    'summary': 'Premium luxury real estate landing page for OSUS Properties',
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
        'templates/osus_homepage.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_osus_properties/static/src/css/osus_landing.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
