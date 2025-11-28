# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words
import qrcode
import io
import base64
import logging

_logger = logging.getLogger(__name__)


class PaymentReportExtension(models.Model):
    _inherit = 'account.payment'
    
    # Override name field to ensure it's always visible and properly labeled
    name = fields.Char(
        string='Reference Number',
        required=True,
        readonly=False,
        copy=False,
        default='/',
        help="Payment/Receipt reference number that will appear on the voucher"
    )
    
    # QR Code fields for customer receipts
    display_qr_code = fields.Boolean(
        string='Display QR Code',
        default=lambda self: self.payment_type == 'inbound',
        help="Show QR code on payment voucher for customer receipts"
    )
    
    qr_code_urls = fields.Text(
        string='QR Code URLs',
        compute='_compute_qr_code',
        help="Generated QR code data URLs for payment voucher"
    )
    
    @api.model
    def create(self, vals):
        """Override create to ensure name field is always populated for NEW payments only"""
        # Only generate new reference if it's a new payment and no name is provided
        if not vals.get('name') or vals.get('name') == '/':
            if vals.get('payment_type') == 'inbound':
                # Use default customer payment sequence
                vals['name'] = self.env['ir.sequence'].next_by_code('account.payment.customer.invoice') or \
                              self.env['ir.sequence'].next_by_code('account.payment.customer') or '/'
            else:
                # Use default supplier payment sequence
                vals['name'] = self.env['ir.sequence'].next_by_code('account.payment.supplier.invoice') or \
                              self.env['ir.sequence'].next_by_code('account.payment.supplier') or '/'
        return super().create(vals)
    
    @api.depends('name', 'partner_id', 'amount', 'date', 'display_qr_code', 'payment_type')
    def _compute_qr_code(self):
        """Generate QR code for customer receipts"""
        for record in self:
            if not record.display_qr_code or record.payment_type != 'inbound':
                record.qr_code_urls = False
                continue
                
            try:
                # Create QR code content with payment information
                qr_content = f"Payment Receipt\n"
                qr_content += f"Reference: {record.name or 'N/A'}\n"
                qr_content += f"Amount: {record.amount} {record.currency_id.name}\n"
                qr_content += f"Date: {record.date}\n"
                qr_content += f"From: {record.partner_id.name or 'N/A'}\n"
                
                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_content)
                qr.make(fit=True)
                
                # Create image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_data = base64.b64encode(buffer.getvalue()).decode()
                
                # Create data URL
                data_url = f"data:image/png;base64,{img_data}"
                record.qr_code_urls = data_url
                
            except Exception as e:
                _logger.warning("Failed to generate QR code for payment %s: %s", record.id, str(e))
                record.qr_code_urls = False
    
    def _get_amount_in_words(self):
        """Convert the amount to words"""
        self.ensure_one()
        try:
            amount_in_words = num2words(abs(self.amount), lang=self.partner_id.lang or 'en')
            currency_name = self.currency_id.name or 'AED'
            return amount_in_words.title() + ' ' + currency_name
        except NotImplementedError:
            return "Amount in words not available"
        
    def get_report_type_name(self):
        """Return the type of payment voucher"""
        self.ensure_one()
        if self.payment_type == 'inbound':
            return "Receipt Voucher"
        else:
            return "Payment Voucher"

    def get_related_documents(self):
        """Get related invoices or bills based on payment type and reconciliation"""
        self.ensure_one()
        related_docs = self.env['account.move']
        
        if self.reconciled_invoice_ids:
            # If we have reconciled invoices, return them
            related_docs = self.reconciled_invoice_ids
        else:
            # Try to find related documents through move lines
            move_lines = self.move_id.line_ids.filtered(lambda l: l.account_id.reconcile)
            reconciled_lines = move_lines.mapped('full_reconcile_id.reconciled_line_ids')
            
            # Get the related moves from reconciled lines
            related_moves = reconciled_lines.mapped('move_id').filtered(
                lambda m: m.id != self.move_id.id and m.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']
            )
            related_docs = related_moves
            
        return related_docs

    def get_document_type_label(self):
        """Get the appropriate label for related documents based on payment type"""
        self.ensure_one()
        related_docs = self.get_related_documents()
        
        if not related_docs:
            if self.payment_type == 'inbound':
                return "Related invoice"
            else:
                return "Related bill"
        
        # Check if we have bills (vendor invoices)
        has_bills = any(doc.move_type == 'in_invoice' for doc in related_docs)
        # Check if we have customer invoices
        has_invoices = any(doc.move_type == 'out_invoice' for doc in related_docs)
        # Check if we have credit notes
        has_credits = any(doc.move_type in ['out_refund', 'in_refund'] for doc in related_docs)
        
        # Determine the most appropriate label
        if has_bills and not has_invoices:
            return "Related bill"
        elif has_invoices and not has_bills:
            return "Related invoice"
        elif has_credits:
            return "Related credit note"
        elif has_bills and has_invoices:
            return "Related documents"
        else:
            # Fallback based on payment type
            if self.payment_type == 'inbound':
                return "Related invoice"
            else:
                return "Related bill"

    def get_related_document_references(self):
        """Get the reference numbers of related documents"""
        self.ensure_one()
        related_docs = self.get_related_documents()
        
        if related_docs:
            return ', '.join(related_docs.mapped('name'))
        else:
            return '-'

    def get_related_document_info(self):
        """Get comprehensive information about related documents"""
        self.ensure_one()
        related_docs = self.get_related_documents()
        
        if not related_docs:
            return {
                'label': self.get_document_type_label(),
                'references': '-',
                'count': 0,
                'documents': self.env['account.move']
            }
        
        return {
            'label': self.get_document_type_label(),
            'references': self.get_related_document_references(),
            'count': len(related_docs),
            'documents': related_docs
        }

    def get_payment_summary(self):
        """Get payment summary with reconciliation details"""
        self.ensure_one()
        related_docs = self.get_related_documents()
        
        total_invoice_amount = sum(related_docs.mapped('amount_total'))
        payment_amount = self.amount
        
        return {
            'total_invoice_amount': total_invoice_amount,
            'payment_amount': payment_amount,
            'remaining_balance': total_invoice_amount - payment_amount if total_invoice_amount else 0,
            'is_full_payment': abs(total_invoice_amount - payment_amount) < 0.01 if total_invoice_amount else True,
            'currency': self.currency_id
        }

    def get_voucher_description(self):
        """Get a descriptive text for the voucher based on related documents"""
        self.ensure_one()
        doc_info = self.get_related_document_info()
        
        if doc_info['count'] == 0:
            if self.payment_type == 'inbound':
                return f"Receipt of {self.amount} {self.currency_id.name}"
            else:
                return f"Payment of {self.amount} {self.currency_id.name}"
        
        elif doc_info['count'] == 1:
            doc = doc_info['documents'][0]
            doc_type = "invoice" if doc.move_type == 'out_invoice' else "bill" if doc.move_type == 'in_invoice' else "credit note"
            
            if self.payment_type == 'inbound':
                return f"Receipt for {doc_type} {doc.name}"
            else:
                return f"Payment for {doc_type} {doc.name}"
        
        else:
            if self.payment_type == 'inbound':
                return f"Receipt for {doc_info['count']} documents"
            else:
                return f"Payment for {doc_info['count']} documents"

    def action_print_voucher(self):
        """
        Print the payment voucher using the custom OSUS template.
        This method is called from the 'Print Voucher' button.
        """
        self.ensure_one()
        try:
            return self.env.ref('invoice_report_for_realestate.action_report_payment_voucher').report_action(self)
        except ValueError as e:
            # If custom report is not found, use a fallback or show error
            from odoo.exceptions import UserError
            raise UserError(f"Payment voucher report not found: {str(e)}")
