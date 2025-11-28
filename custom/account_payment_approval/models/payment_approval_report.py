from odoo import models, fields, api, _

class PaymentApprovalReport(models.Model):
    _name = 'payment.approval.report'
    _description = 'Payment Approval Report'
    
    name = fields.Char(string='Report Name', required=True)
    payment_ids = fields.Many2many('account.payment', string='Payments')
    report_date = fields.Date(string='Report Date', default=fields.Date.today)
    company_id = fields.Many2one('res.company', string='Company')
    # Add more fields as needed for reporting
