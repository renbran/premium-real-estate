from odoo import models, fields, api
import hashlib
import datetime

class PaymentQRVerification(models.Model):
    _name = 'payment.qr.verification'
    _description = 'Payment QR Verification Log'
    _order = 'verification_date desc'

    payment_id = fields.Many2one('account.payment', required=True, ondelete='cascade', index=True)
    verification_code = fields.Char(required=True, index=True)
    verification_date = fields.Datetime(default=fields.Datetime.now, required=True)
    verifier_ip = fields.Char('IP Address')
    verification_method = fields.Selection([
        ('qr_scan', 'QR Code Scan'),
        ('web_access', 'Direct Web Access')
    ], default='qr_scan')
    verification_status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed')
    ], default='success')

    @api.model
    def log_verification(self, payment_id, ip_address=None):
        """Log QR verification attempt"""
        verification_code = hashlib.md5(f"{payment_id}-{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:12].upper()
        
        return self.create({
            'payment_id': payment_id,
            'verification_code': verification_code,
            'verifier_ip': ip_address,
            'verification_status': 'success'
        })
