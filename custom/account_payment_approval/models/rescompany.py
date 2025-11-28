# models/res_company.py
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Essential settings only
    use_osus_branding = fields.Boolean(default=True)
    auto_post_approved_payments = fields.Boolean(default=False)
    max_approval_amount = fields.Monetary(default=10000.0)
    enable_qr_codes = fields.Boolean(default=True)
    enable_four_stage_approval = fields.Boolean(default=True)
    authorization_threshold = fields.Monetary(default=5000.0)
    
    voucher_footer_message = fields.Text(default='Thank you for your business')
    voucher_terms = fields.Text(default='Computer-generated document')
