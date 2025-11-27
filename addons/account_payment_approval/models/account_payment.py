class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # QR Code fields
    qr_code = fields.Binary(compute='_compute_qr_code', store=True)
    qr_in_report = fields.Boolean('Show QR in Report', default=True)

    @api.depends('name', 'amount', 'partner_id', 'approval_state', 'qr_in_report', 'id')
    def _compute_qr_code(self):
        """Generate QR code with verification URL"""
        for record in self:
            if record.qr_in_report and record.id:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
                verification_url = f"{base_url}/payment/verify/{record.id}"
                record.qr_code = record._generate_qr_image(verification_url)
            else:
                record.qr_code = False

    def _generate_qr_image(self, data):
        """Generate QR code image"""
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            
            buffer = BytesIO()
            qr.make_image(fill_color="black", back_color="white").save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue())
        except Exception as e:
            _logger.error(f"QR generation failed: {e}")
            return False

    def get_verification_url(self):
        """Get public verification URL"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        return f"{base_url}/payment/verify/{self.id}" if self.id else False

    def get_amount_in_words(self):
        """Convert amount to words for voucher"""
        try:
            if hasattr(self.currency_id, 'amount_to_text'):
                return self.currency_id.amount_to_text(self.amount)
            return self._simple_amount_to_words()
        except:
            return f"{self.currency_id.name} {self.amount:,.2f} Only"

    def _simple_amount_to_words(self):
        """Basic amount to words conversion"""
        # Simplified implementation for common use cases
        integer_part = int(self.amount)
        decimal_part = int((self.amount - integer_part) * 100)
        
        if integer_part == 0:
            result = "Zero"
        elif integer_part < 1000:
            result = f"{integer_part}"
        elif integer_part < 1000000:
            thousands = integer_part // 1000
            remainder = integer_part % 1000
            result = f"{thousands} Thousand"
            if remainder > 0:
                result += f" {remainder}"
        else:
            result = f"{integer_part:,}"
        
        result += f" {self.currency_id.name}"
        if decimal_part > 0:
            result += f" and {decimal_part:02d}/100"
        return result + " Only"