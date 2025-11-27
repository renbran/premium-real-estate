from odoo import models, fields, api, _

class PaymentRejectionWizard(models.TransientModel):
    _name = 'payment.rejection.wizard'
    _description = 'Payment Rejection Wizard'
    
    payment_id = fields.Many2one('account.payment', string='Payment', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)
    rejected_by = fields.Many2one('res.users', string='Rejected By', default=lambda self: self.env.user)
    rejection_date = fields.Datetime(string='Rejection Date', default=fields.Datetime.now)
    # Add more fields and logic as needed
