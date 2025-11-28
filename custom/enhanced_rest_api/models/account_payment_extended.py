# -*- coding: utf-8 -*-
"""
Account Payment Model Extension
Adds voucher-specific fields and methods for the Enhanced REST API
"""

from odoo import models, fields, api
try:
    import qrcode
    from io import BytesIO
    import base64
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Additional fields for voucher functionality
    voucher_type = fields.Selection([
        ('receipt', 'Receipt Voucher'),
        ('payment', 'Payment Voucher')
    ], string='Voucher Type', compute='_compute_voucher_type', store=True)
    
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code')
    qr_code_data = fields.Char(string='QR Code Data', compute='_compute_qr_code_data')

    @api.depends('payment_type')
    def _compute_voucher_type(self):
        """Compute voucher type based on payment type"""
        for payment in self:
            if payment.payment_type == 'inbound':
                payment.voucher_type = 'receipt'
            else:
                payment.voucher_type = 'payment'

    @api.depends('name', 'reference', 'amount', 'partner_id')
    def _compute_qr_code_data(self):
        """Compute QR code data string"""
        for payment in self:
            qr_data = f"Payment: {payment.name or payment.reference}\n"
            qr_data += f"Amount: {payment.currency_id.symbol}{payment.amount}\n"
            qr_data += f"Partner: {payment.partner_id.name}\n"
            qr_data += f"Date: {payment.date}\n"
            qr_data += f"Reference: {payment.reference}"
            payment.qr_code_data = qr_data

    @api.depends('qr_code_data')
    def _compute_qr_code(self):
        """Generate QR code image"""
        for payment in self:
            if payment.qr_code_data and QRCODE_AVAILABLE:
                try:
                    # Generate QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(payment.qr_code_data)
                    qr.make(fit=True)
                    
                    # Create QR code image
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Convert to base64
                    buffer = BytesIO()
                    qr_img.save(buffer, format='PNG')
                    qr_code_base64 = base64.b64encode(buffer.getvalue())
                    payment.qr_code = qr_code_base64
                except Exception:
                    payment.qr_code = False
            else:
                payment.qr_code = False

    def get_voucher_data(self):
        """Get voucher data for API responses"""
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'reference': self.reference,
            'voucher_type': self.voucher_type,
            'amount': self.amount,
            'currency': self.currency_id.name,
            'currency_symbol': self.currency_id.symbol,
            'partner': {
                'id': self.partner_id.id,
                'name': self.partner_id.name,
                'phone': self.partner_id.phone,
                'mobile': self.partner_id.mobile,
                'email': self.partner_id.email,
            },
            'company': {
                'id': self.company_id.id,
                'name': self.company_id.name,
                'vat': self.company_id.vat,
                'phone': self.company_id.phone,
                'address': {
                    'street': self.company_id.street,
                    'street2': self.company_id.street2,
                    'city': self.company_id.city,
                    'country': self.company_id.country_id.name if self.company_id.country_id else None,
                }
            },
            'payment_method': self.payment_method_id.name if self.payment_method_id else self.journal_id.name,
            'journal': self.journal_id.name,
            'state': self.state,
            'date': self.date.isoformat() if self.date else None,
            'create_date': self.create_date.isoformat() if self.create_date else None,
            'create_user': self.create_uid.name if self.create_uid else None,
            'qr_code_data': self.qr_code_data,
            'voucher_urls': {
                'pdf': f'/api/v1/payments/voucher/{self.id}',
                'html': f'/api/v1/payments/voucher/html/{self.id}',
            }
        }
