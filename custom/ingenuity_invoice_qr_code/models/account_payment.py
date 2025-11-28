# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
import qrcode
import base64
from io import BytesIO
import secrets
import hashlib
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


def generate_qr_code_payment(value):
    """Generate QR code for payment data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4
    )
    qr.add_data(value)
    qr.make(fit=True)
    img = qr.make_image()
    stream = BytesIO()
    img.save(stream, format="PNG")
    qr_img = base64.b64encode(stream.getvalue())
    return qr_img


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    qr_code = fields.Binary("Payment QR Code", compute='_generate_payment_qr_code')
    qr_in_report = fields.Boolean('Display QR Code in Report?', default=True)
    
    # Validation fields
    validation_token = fields.Char(
        string='Validation Token',
        help="Unique token for payment validation via QR code",
        readonly=True,
        copy=False
    )
    validation_token_expiry = fields.Datetime(
        string='Token Expiry',
        help="Expiry date for validation token (optional)",
        readonly=True
    )
    validation_access_count = fields.Integer(
        string='Validation Access Count',
        default=0,
        readonly=True,
        help="Number of times this payment was validated"
    )
    last_validation_access = fields.Datetime(
        string='Last Validation Access',
        readonly=True,
        help="Last time this payment was validated"
    )
    validation_url = fields.Char(
        string='Validation URL',
        compute='_compute_validation_url',
        help="Complete URL for payment validation"
    )

    @api.depends('validation_token')
    def _compute_validation_url(self):
        """Compute the complete validation URL"""
        for payment in self:
            if payment.validation_token:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                payment.validation_url = f"{base_url}/payment/validate/{payment.validation_token}"
            else:
                payment.validation_url = False

    def _generate_validation_token(self):
        """Generate a unique validation token for the payment"""
        if not self.validation_token:
            # Create a unique token using payment details + random secret
            payment_data = f"{self.id}-{self.name}-{self.amount}-{self.date}"
            random_secret = secrets.token_urlsafe(32)
            combined = f"{payment_data}-{random_secret}"
            
            # Generate SHA256 hash and take first 32 characters for URL-friendly token
            token = hashlib.sha256(combined.encode()).hexdigest()[:32]
            
            # Set expiry to 1 year from now (adjustable)
            expiry = datetime.now() + timedelta(days=365)
            
            self.write({
                'validation_token': token,
                'validation_token_expiry': expiry
            })
            
            _logger.info("Generated validation token for payment %s", self.name)
            return token
        return self.validation_token

    @api.depends('name', 'partner_id', 'amount', 'date', 'payment_type', 'qr_in_report', 'validation_token')
    def _generate_payment_qr_code(self):
        """Generate QR code for payment validation URL"""
        for payment in self:
            if not payment.qr_in_report:
                payment.qr_code = False
                continue
                
            try:
                # Generate validation token if not exists
                if not payment.validation_token:
                    payment._generate_validation_token()
                
                # Get validation URL
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                validation_url = f"{base_url}/payment/validate/{payment.validation_token}"
                
                # Generate the QR code with validation URL
                qr_img = generate_qr_code_payment(validation_url)
                payment.qr_code = qr_img
                
                _logger.info("QR code with validation URL generated for payment %s", payment.name)
                
            except Exception as e:
                _logger.error("Error generating QR code for payment %s: %s", payment.name, str(e))
                payment.qr_code = False

    @api.model
    def create(self, vals):
        """Override create to generate validation token for new payments"""
        payment = super().create(vals)
        if payment.state == 'posted' and payment.qr_in_report:
            payment._generate_validation_token()
        return payment

    def action_post(self):
        """Override post to generate validation token when payment is confirmed"""
        result = super().action_post()
        for payment in self:
            if payment.qr_in_report and not payment.validation_token:
                payment._generate_validation_token()
        return result

    def regenerate_validation_token(self):
        """Manually regenerate validation token"""
        self.ensure_one()
        self.validation_token = False
        self._generate_validation_token()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Token Regenerated',
                'message': f'New validation token generated for payment {self.name}',
                'type': 'success',
            }
        }

    def action_open_validation_page(self):
        """Open validation page in browser"""
        self.ensure_one()
        if not self.validation_token:
            self._generate_validation_token()
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.validation_url,
            'target': 'new',
        }
