# -*- coding: utf-8 -*-
{
    "name": "OSUS Properties HR Greetings",
    "version": "17.0.1.0.0",
    "category": "HR",
    "summary": "Comprehensive Birthday & Work Anniversary Greetings for OSUS Properties",
    "description": """
    Professional greeting system for OSUS Properties that includes:
    
    Birthday Celebrations:
    - Personalized birthday wishes to employees on their special day
    - Birthday announcements to all team members with Telegram integration
    - Elegant, branded email templates matching OSUS Properties corporate identity
    
    Work Anniversary Celebrations:
    - Automated work anniversary wishes based on joining_date field
    - Professional anniversary email templates
    - Team notifications for milestone celebrations
    
    Features:
    - Burgundy and gold branded email templates
    - Professional typography with Montserrat and Playfair Display fonts
    - Responsive design for all devices
    - Integration with Telegram for team celebrations
    - Automated daily scheduling through cron jobs
    - Complete company contact information
    - Overrides default birthday and anniversary modules
    """,
    "author": "OSUS Properties",
    "website": "https://osusproperties.com",
    "support": "info@osusproperties.com",
    "depends": ['contacts', 'hr', 'hr_contract', 'mail', 'hr_uae'],
    "data": [
        "security/greetings_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/mail_template_birthday.xml",
        "data/mail_template_anniversary.xml",
        "views/hr_employee_views.xml"
    ],
    "images": ["static/description/banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
    "price": 0,
    "currency": "USD",
}