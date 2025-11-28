# -*- coding: utf-8 -*-
#############################################################################
#
#    Payment Report Wizard
#    Allows users to select and generate multiple report types
#
#############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import base64


class PaymentReportWizard(models.TransientModel):
    """Wizard for generating multiple payment reports"""
    _name = 'payment.report.wizard'
    _description = 'Payment Report Generation Wizard'
    
    payment_id = fields.Many2one('account.payment', string='Payment', required=True)
    report_types = fields.Selection([
        ('enhanced', 'Enhanced Voucher'),
        ('detailed', 'Detailed OSUS Voucher'),
        ('verification', 'QR Verification Report'),
        ('audit_trail', 'Audit Trail Report'),
    ], string='Report Type', required=True, default='enhanced')
    
    include_qr_code = fields.Boolean(string='Include QR Code', default=True)
    include_signatures = fields.Boolean(string='Include Digital Signatures', default=True)
    include_audit_trail = fields.Boolean(string='Include Audit Information', default=True)
    
    format_type = fields.Selection([
        ('pdf', 'PDF'),
        ('html', 'HTML (Web View)'),
    ], string='Format', default='pdf', required=True)
    
    send_email = fields.Boolean(string='Send via Email', default=False)
    email_recipient = fields.Char(string='Email Recipient')
    
    @api.onchange('payment_id')
    def _onchange_payment_id(self):
        """Set default email recipient"""
        if self.payment_id and self.payment_id.partner_id.email:
            self.email_recipient = self.payment_id.partner_id.email
    
    def action_generate_report(self):
        """Generate the selected report"""
        self.ensure_one()
        
        if not self.payment_id:
            raise UserError(_("Please select a payment."))
        
        # Map report types to report actions
        report_mapping = {
            'enhanced': 'account_payment_approval.action_report_payment_voucher_enhanced',
            'detailed': 'account_payment_approval.action_report_payment_voucher',
            'verification': 'account_payment_approval.action_report_voucher_verification_web',
            'audit_trail': 'account_payment_approval.action_report_voucher_audit_trail',
        }
        
        report_ref = report_mapping.get(self.report_types)
        if not report_ref:
            raise UserError(_("Invalid report type selected."))
        
        # Get report action
        try:
            report = self.env.ref(report_ref)
        except ValueError:
            raise UserError(_("Report template not found. Please check module installation."))
        
        # Prepare context with wizard options
        context = self.env.context.copy()
        context.update({
            'include_qr_code': self.include_qr_code,
            'include_signatures': self.include_signatures,
            'include_audit_trail': self.include_audit_trail,
        })
        
        # Generate report
        if self.format_type == 'pdf':
            report_type = 'qweb-pdf'
        else:
            report_type = 'qweb-html'
        
        # Send email if requested
        if self.send_email and self.email_recipient:
            self._send_report_email(report)
        
        # Return report action
        return {
            'type': 'ir.actions.report',
            'report_name': report.report_name,
            'report_type': report_type,
            'data': {'ids': [self.payment_id.id]},
            'context': context,
            'target': 'new' if self.format_type == 'html' else 'self',
        }
    
    def _send_report_email(self, report):
        """Send report via email"""
        try:
            # Generate PDF for email attachment
            pdf_content, content_type = report._render_qweb_pdf([self.payment_id.id])
            
            # Create attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'{self.payment_id.name}_{self.report_types}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'account.payment',
                'res_id': self.payment_id.id,
                'mimetype': 'application/pdf',
            })
            
            # Send email
            mail_values = {
                'subject': f'Payment Report - {self.payment_id.name}',
                'body_html': self._get_email_body(),
                'email_to': self.email_recipient,
                'attachment_ids': [(4, attachment.id)],
            }
            
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
            
            return True
        except Exception as e:
            raise UserError(_("Failed to send email: %s") % str(e))
    
    def _get_email_body(self):
        """Get email body for report"""
        return f"""
        <div style="font-family: Arial, sans-serif;">
            <h3>Payment Report - {self.payment_id.name}</h3>
            
            <p>Dear {self.payment_id.partner_id.name},</p>
            
            <p>Please find attached the payment report for:</p>
            
            <ul>
                <li><strong>Payment Reference:</strong> {self.payment_id.name}</li>
                <li><strong>Amount:</strong> {self.payment_id.currency_id.symbol}{self.payment_id.amount:,.2f}</li>
                <li><strong>Date:</strong> {self.payment_id.date.strftime('%B %d, %Y') if self.payment_id.date else 'N/A'}</li>
                <li><strong>Status:</strong> {self.payment_id.state.title()}</li>
            </ul>
            
            <p>Thank you for your business.</p>
            
            <p>Best regards,<br/>
            OSUS Properties<br/>
            Business Bay, Dubai<br/>
            +971-4-366-4500</p>
        </div>
        """
    
    def action_preview_report(self):
        """Preview the report before generating"""
        self.ensure_one()
        
        # Generate HTML preview
        context = self.env.context.copy()
        context.update({
            'include_qr_code': self.include_qr_code,
            'include_signatures': self.include_signatures,
            'include_audit_trail': self.include_audit_trail,
        })
        
        report_mapping = {
            'enhanced': 'account_payment_approval.action_report_payment_voucher_enhanced',
            'detailed': 'account_payment_approval.action_report_payment_voucher',
            'verification': 'account_payment_approval.action_report_voucher_verification_web',
            'audit_trail': 'account_payment_approval.action_report_voucher_audit_trail',
        }
        
        report_ref = report_mapping.get(self.report_types)
        try:
            report = self.env.ref(report_ref)
        except ValueError:
            raise UserError(_("Report template not found."))
        
        return {
            'type': 'ir.actions.report',
            'report_name': report.report_name,
            'report_type': 'qweb-html',
            'data': {'ids': [self.payment_id.id]},
            'context': context,
            'target': 'new',
        }


class PaymentBulkReportWizard(models.TransientModel):
    """Wizard for generating bulk reports"""
    _name = 'payment.bulk.report.wizard'
    _description = 'Bulk Payment Report Generation Wizard'
    
    payment_ids = fields.Many2many('account.payment', string='Payments', required=True)
    report_type = fields.Selection([
        ('enhanced', 'Enhanced Vouchers'),
        ('detailed', 'Detailed OSUS Vouchers'),
        ('verification', 'QR Verification Reports'),
        ('audit_trail', 'Audit Trail Reports'),
    ], string='Report Type', required=True, default='enhanced')
    
    format_type = fields.Selection([
        ('pdf', 'Combined PDF'),
        ('separate_pdf', 'Separate PDF Files'),
        ('html', 'HTML (Web View)'),
    ], string='Format', default='pdf', required=True)
    
    include_cover_page = fields.Boolean(string='Include Cover Page', default=True)
    group_by_partner = fields.Boolean(string='Group by Partner', default=False)
    group_by_date = fields.Boolean(string='Group by Date', default=False)
    
    # Computed fields for display
    total_payments_count = fields.Integer(string='Total Payments', compute='_compute_summary_fields')
    total_amount = fields.Float(string='Total Amount', compute='_compute_summary_fields')
    date_from = fields.Date(string='From Date', compute='_compute_summary_fields')
    date_to = fields.Date(string='To Date', compute='_compute_summary_fields')
    
    @api.depends('payment_ids')
    def _compute_summary_fields(self):
        """Compute summary fields for display"""
        for wizard in self:
            if wizard.payment_ids:
                wizard.total_payments_count = len(wizard.payment_ids)
                wizard.total_amount = sum(wizard.payment_ids.mapped('amount'))
                dates = wizard.payment_ids.mapped('date')
                wizard.date_from = min(dates) if dates else False
                wizard.date_to = max(dates) if dates else False
            else:
                wizard.total_payments_count = 0
                wizard.total_amount = 0.0
                wizard.date_from = False
                wizard.date_to = False
    
    def action_generate_bulk_reports(self):
        """Generate bulk reports"""
        self.ensure_one()
        
        if not self.payment_ids:
            raise UserError(_("Please select at least one payment."))
        
        # Sort payments if grouping is requested
        payments = self.payment_ids
        if self.group_by_partner:
            payments = payments.sorted(lambda p: p.partner_id.name)
        elif self.group_by_date:
            payments = payments.sorted(lambda p: p.date or fields.Date.today())
        
        # Map report types
        report_mapping = {
            'enhanced': 'account_payment_approval.action_report_payment_voucher_enhanced',
            'detailed': 'account_payment_approval.action_report_payment_voucher',
            'verification': 'account_payment_approval.action_report_voucher_verification_web',
            'audit_trail': 'account_payment_approval.action_report_voucher_audit_trail',
        }
        
        report_ref = report_mapping.get(self.report_type)
        try:
            report = self.env.ref(report_ref)
        except ValueError:
            raise UserError(_("Report template not found."))
        
        # Prepare context
        context = self.env.context.copy()
        context.update({
            'include_cover_page': self.include_cover_page,
            'group_by_partner': self.group_by_partner,
            'group_by_date': self.group_by_date,
        })
        
        # Return report action
        return {
            'type': 'ir.actions.report',
            'report_name': report.report_name,
            'report_type': 'qweb-pdf' if 'pdf' in self.format_type else 'qweb-html',
            'data': {'ids': payments.ids},
            'context': context,
            'target': 'new' if self.format_type == 'html' else 'self',
        }