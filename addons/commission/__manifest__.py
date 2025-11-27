{
    "name": "Commission AX",
    "version": "17.0.1.0.0",
    "summary": "Automated commission management for Odoo 17",
    "description": "Automates commission purchase orders, vendor bills, and reconciliation for sales.",
    "author": "Your Company",
    "website": "https://yourcompany.com",
    "category": "Sales",
    "depends": ["base", "sale", "purchase", "account", "mail"],
    "data": [
        "views/commission_ax_views.xml",
        "data/commission_ax_cron.xml",
        "report/commission_payout_report_template.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False
}
