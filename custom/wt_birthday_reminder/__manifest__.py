# -*- coding: utf-8 -*-
{
    "name": "OSUS Properties Birthday Greetings",
    "version": "17.0.1.0.0",
    "category": "HR",
    "summary": "Automated Birthday Wishes for OSUS Properties Employees",
    "description": """
    Professional birthday greeting system for OSUS Properties that sends:
    - Personalized birthday wishes to employees on their special day
    - Birthday reminders to all team members to celebrate together
    - Elegant, branded email templates matching OSUS Properties corporate identity
    - Automated daily scheduling through cron jobs
    
    Features:
    - Burgundy and gold branded email templates
    - Professional typography and layout
    - Responsive design for all devices
    - Integration with Telegram for team celebrations
    - Complete company contact information
    """,
    "author": "OSUS Properties",
    "website": "https://osusproperties.com",
    "support": "info@osusproperties.com",
    "depends": ['contacts', 'hr', 'mail'],
    "data": [
        "data/ir_cron.xml",
        "data/mail_template_osus.xml"
    ],
    "images": ["static/description/banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
    "price": 0,
    "currency": "USD",
}