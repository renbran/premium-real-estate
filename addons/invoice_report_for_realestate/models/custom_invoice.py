from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import qrcode
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        """
        Print the PDF copy of the invoice using the custom report action.
        With fallback to standard invoice report if custom report is not available.
        """
        try:
            return self.env.ref('invoice_report_for_realestate.action_report_osus_invoice').report_action(self)
        except ValueError as e:
            _logger.warning("Custom invoice report not found: %s. Using standard report as fallback.", str(e))
            return self.env.ref('account.account_invoices').report_action(self)

    def action_print_custom_bill(self):
        """
        Print the PDF copy of the bill using the custom report action.
        With fallback to standard bill report if custom report is not available.
        """
        try:
            return self.env.ref('invoice_report_for_realestate.action_report_osus_bill').report_action(self)
        except ValueError as e:
            _logger.warning("Custom bill report not found: %s. Using standard report as fallback.", str(e))
            return self.env.ref('account.account_invoices').report_action(self)

    # Note: Customer receipts are handled by account.payment module (payment vouchers), 
    # not account.move. See account_payment.py for customer receipt functionality.

    @api.model
    def action_bulk_print_invoices(self):
        """
        Print multiple invoices in bulk as a single PDF file.
        Called from list view action.
        """
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_("Please select at least one invoice to print."))
        
        invoices = self.browse(active_ids)
        
        # Filter only customer invoices
        customer_invoices = invoices.filtered(lambda inv: inv.move_type == 'out_invoice')
        if not customer_invoices:
            raise UserError(_("Please select at least one customer invoice."))
        
        try:
            return self.env.ref('invoice_report_for_realestate.action_report_osus_invoice_bulk').report_action(customer_invoices)
        except ValueError as e:
            _logger.warning("Custom bulk invoice report not found: %s. Using standard report as fallback.", str(e))
            return self.env.ref('account.account_invoices').report_action(customer_invoices)

    @api.model
    def action_bulk_print_bills(self):
        """
        Print multiple bills in bulk as a single PDF file.
        Called from list view action.
        """
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_("Please select at least one bill to print."))
        
        bills = self.browse(active_ids)
        
        # Filter only vendor bills
        vendor_bills = bills.filtered(lambda bill: bill.move_type == 'in_invoice')
        if not vendor_bills:
            raise UserError(_("Please select at least one vendor bill."))
        
        try:
            return self.env.ref('invoice_report_for_realestate.action_report_osus_bill_bulk').report_action(vendor_bills)
        except ValueError as e:
            _logger.warning("Custom bulk bill report not found: %s. Using standard report as fallback.", str(e))
            return self.env.ref('account.account_invoices').report_action(vendor_bills)

    @api.model
    def action_bulk_print_mixed(self):
        """
        Print multiple documents (invoices, bills, credit notes) in bulk as a single PDF file.
        Called from list view action.
        """
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_("Please select at least one document to print."))
        
        documents = self.browse(active_ids)
        
        # Filter only posted documents
        posted_documents = documents.filtered(lambda doc: doc.state == 'posted')
        if not posted_documents:
            raise UserError(_("Please select at least one posted document."))
        
        try:
            return self.env.ref('invoice_report_for_realestate.action_report_osus_mixed_bulk').report_action(posted_documents)
        except ValueError as e:
            _logger.warning("Custom bulk mixed report not found: %s. Using standard report as fallback.", str(e))
            return self.env.ref('account.account_invoices').report_action(posted_documents)

    # Deal Information Fields
    booking_date = fields.Date(string='Booking Date', help="Date when the property booking was confirmed")

    # QR Code fields
    qr_in_report = fields.Boolean(
        string='Show QR Code in Report',
        default=True,
        help="Enable to display QR code on generated documents"
    )
    qr_image = fields.Binary(
        string='QR Code Image',
        compute='_compute_qr_code',
        store=True,
        help="Automatically generated QR code for this document"
    )
    
    amount_total_words = fields.Char(
        string='Total Amount in Words',
        compute='_compute_amount_total_words',
        help="The total amount expressed in words"
    )

    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
        help="Internal reference ID for the real estate deal"
    )
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
        help="Total value of the property sale"
    )
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits=(16, 2),
        help="Commission percentage for this deal"
    )

    # Relational Fields
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        help="The buyer of the property"
    )
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
        help="The real estate project this deal belongs to"
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        help="The specific property unit in this deal"
    )
    property_type_id = fields.Many2one(
        'product.category',
        string='Property Type',
        tracking=True,
        help="The type/category of the property (e.g., Villa, Apartment, Commercial)"
    )

    # Computed fields for enhanced tree view
    is_property_deal = fields.Boolean(
        string='Is Property Deal',
        compute='_compute_deal_status',
        store=True,
        help="Indicates if this invoice is related to a property deal"
    )
    commission_amount = fields.Monetary(
        string='Commission Amount',
        compute='_compute_commission_amount',
        store=True,
        currency_field='currency_id',
        help="Calculated commission amount based on sale value and percentage"
    )

    @api.depends('name', 'partner_id', 'amount_total', 'invoice_date', 'qr_in_report', 'buyer_id', 'project_id', 'unit_id')
    def _compute_qr_code(self):
        for record in self:
            if not record.qr_in_report:
                record.qr_image = False
                continue
                
            try:
                if record.name and record.partner_id:
                    portal_url = record._get_portal_url()
                    record.qr_image = self._generate_qr_code(portal_url)
                else:
                    record.qr_image = False
            except Exception as e:
                _logger.error("Error generating QR code for %s: %s", record.name, str(e))
                record.qr_image = False

    def _get_portal_url(self):
        """Generate portal URL for secure access to the document"""
        try:
            # Get the base URL of the Odoo instance
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not base_url:
                base_url = 'http://localhost:8069'  # Fallback URL
            
            # Generate the portal URL with access token for the invoice
            # This uses Odoo's built-in method which automatically includes the access token
            relative_url = self.get_portal_url()
            
            # Combine the base URL with the relative URL
            full_url = base_url + relative_url
            
            _logger.info("Generated portal URL for %s: %s", self.name, full_url)
            return full_url
        except Exception as e:
            _logger.error("Error generating portal URL for %s: %s", self.name, str(e))
            # Fallback to manual URL construction if portal URL fails
            return self._get_manual_portal_url()

    def _get_manual_portal_url(self):
        """Generate manual portal URL as fallback"""
        try:
            # Get the base URL of the Odoo instance
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not base_url:
                base_url = 'http://localhost:8069'  # Fallback URL
            
            # Get or create access token
            access_token = self._portal_ensure_token()
            
            # Construct the portal URL manually
            portal_url = f"{base_url}/my/invoices/{self.id}?access_token={access_token}"
            
            _logger.info("Generated manual portal URL for %s: %s", self.name, portal_url)
            return portal_url
        except Exception as e:
            _logger.error("Error generating manual portal URL for %s: %s", self.name, str(e))
            # Final fallback to informational content
            return self._get_qr_content_fallback()

    def _get_qr_content_fallback(self):
        """Generate QR code content with real estate deal information as fallback"""
        content_lines = [
            f"Invoice: {self.name}",
            f"Company: {self.company_id.name}",
            f"Partner: {self.partner_id.name}",
            f"Amount: {self.amount_total} {self.currency_id.name}",
            f"Date: {self.invoice_date or ''}",
        ]
        
        # Add real estate specific information if available
        if self.buyer_id:
            content_lines.append(f"Buyer: {self.buyer_id.name}")
        if self.project_id:
            content_lines.append(f"Project: {self.project_id.name}")
        if self.unit_id:
            content_lines.append(f"Unit: {self.unit_id.name}")
        if self.deal_id:
            content_lines.append(f"Deal ID: {self.deal_id}")
        if self.sale_value:
            content_lines.append(f"Sale Value: {self.sale_value} {self.currency_id.name}")
        
        return '\n'.join(content_lines)

    def _generate_qr_code(self, content=None, silent_errors=False):
        """Generate QR code image from content"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue())
        except Exception as e:
            _logger.error("Error generating QR code image: %s", str(e))
            return False

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for record in self:
            try:
                record.amount_total_words = record._amount_to_words(record.amount_total)
            except Exception as e:
                _logger.error("Error converting amount to words: %s", str(e))
                record.amount_total_words = _("Amount in words unavailable")

    def _amount_to_words(self, amount):
        try:
            from num2words import num2words
            words = num2words(amount, lang='en').title()
            return f"{words} {self.currency_id.name or 'AED'} Only"
        except ImportError:
            _logger.warning("num2words library not found, using simple amount display")
            return f"{amount:.2f} {self.currency_id.name or 'AED'}"

    @api.constrains('developer_commission')
    def _check_developer_commission(self):
        for record in self:
            if record.developer_commission < 0 or record.developer_commission > 100:
                raise ValidationError(_("Commission percentage must be between 0 and 100"))

    @api.model
    def _ensure_base_url_configured(self):
        """Ensure the base URL is correctly configured for QR code generation"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not base_url or base_url == 'http://localhost:8069':
            _logger.warning("Base URL not properly configured. QR codes may not work correctly.")
            return False
        return True

    def get_qr_code_url(self):
        """Public method to get the QR code URL for testing purposes"""
        return self._get_portal_url()

    def regenerate_qr_code(self):
        """Manually regenerate QR code for this invoice"""
        self._compute_qr_code()
        return True

    @api.model
    def create(self, vals):
        if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('invoice_origin'):
            self._populate_from_sale_order(vals)
        return super().create(vals)

    def _populate_from_sale_order(self, vals):
        sale_order = self.env['sale.order'].search([
            ('name', '=', vals.get('invoice_origin'))
        ], limit=1)
        
        if sale_order:
            _logger.info(f"Populating invoice fields from sale order {sale_order.name}")
            
            field_map = {
                'booking_date': 'booking_date',  # Added missing booking_date mapping
                'developer_commission': 'developer_commission',
                'buyer_id': 'buyer_id',
                'deal_id': 'deal_id',
                'project_id': 'project_id',
                'sale_value': 'sale_value',
                'unit_id': 'unit_id',
            }
            
            for invoice_field, sale_field in field_map.items():
                if sale_field in sale_order._fields and invoice_field not in vals:
                    field_value = sale_order[sale_field]
                    if field_value:  # Only set if value exists
                        if hasattr(field_value, 'id'):
                            vals[invoice_field] = field_value.id
                        else:
                            vals[invoice_field] = field_value
                        _logger.info(f"Mapped {sale_field} -> {invoice_field}: {vals[invoice_field]}")
                    else:
                        _logger.debug(f"Field {sale_field} is empty in sale order")
                else:
                    if sale_field not in sale_order._fields:
                        _logger.debug(f"Field {sale_field} not found in sale order model")
                    if invoice_field in vals:
                        _logger.debug(f"Field {invoice_field} already set in vals")

    @api.depends('buyer_id', 'project_id', 'unit_id', 'deal_id', 'booking_date')
    def _compute_deal_status(self):
        """Compute if this is a property deal based on available deal information"""
        for record in self:
            record.is_property_deal = bool(
                record.buyer_id or record.project_id or 
                record.unit_id or record.deal_id or record.booking_date
            )

    @api.depends('sale_value', 'developer_commission')
    def _compute_commission_amount(self):
        """Compute commission amount from sale value and percentage"""
        for record in self:
            if record.sale_value and record.developer_commission:
                record.commission_amount = (record.sale_value * record.developer_commission) / 100
            else:
                record.commission_amount = 0.0
