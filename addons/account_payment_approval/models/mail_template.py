# -*- coding: utf-8 -*-
#############################################################################
#
#    Email Template Enhancements for Payment Approval
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import fields, models, api, _


class MailTemplate(models.Model):
    """Enhanced email template with payment approval specific features"""
    _inherit = 'mail.template'
    
    # ========================================
    # Payment Approval Fields
    # ========================================
    
    is_payment_approval_template = fields.Boolean(
        string='Payment Approval Template',
        default=False,
        help="Indicates this template is for payment approval workflows"
    )
    
    approval_stage = fields.Selection([
        ('submitted', 'Submitted for Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('authorized', 'Authorized'),
        ('posted', 'Posted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('escalated', 'Escalated'),
    ], string='Approval Stage',
       help="Which approval stage this template is for")
    
    include_payment_details = fields.Boolean(
        string='Include Payment Details',
        default=True,
        help="Include payment amount, partner, and reference details"
    )
    
    include_approval_history = fields.Boolean(
        string='Include Approval History',
        default=False,
        help="Include approval workflow history in email"
    )
    
    include_qr_code = fields.Boolean(
        string='Include QR Code',
        default=True,
        help="Include QR code for payment verification"
    )
    
    include_digital_signature = fields.Boolean(
        string='Include Digital Signature',
        default=False,
        help="Include digital signature information"
    )
    
    urgency_sensitive = fields.Boolean(
        string='Urgency Sensitive',
        default=True,
        help="Adjust template content based on payment urgency"
    )
    
    # ========================================
    # Enhanced Template Features
    # ========================================
    
    @api.model
    def _get_payment_approval_context(self, payment_id):
        """Get enhanced context for payment approval templates"""
        if not payment_id:
            return {}
        
        payment = self.env['account.payment'].browse(payment_id)
        if not payment.exists():
            return {}
        
        # Base payment information
        context = {
            'payment': payment,
            'partner': payment.partner_id,
            'company': payment.company_id,
            'currency': payment.currency_id,
            'amount': payment.amount,
            'payment_date': payment.date,
            'communication': payment.ref or payment.name,
            'payment_method': payment.payment_method_line_id.name,
            'journal': payment.journal_id.name,
        }
        
        # Approval workflow information
        if hasattr(payment, 'voucher_state'):
            context.update({
                'voucher_state': payment.voucher_state,
                'voucher_state_name': dict(payment._fields['voucher_state'].selection)[payment.voucher_state],
                'submission_date': payment.submission_date,
                'approval_date': payment.approval_date,
                'authorization_date': payment.authorization_date,
                'approved_by': payment.approved_by_id,
                'authorized_by': payment.authorized_by_id,
                'urgency': payment.urgency,
                'urgency_name': dict(payment._fields['urgency'].selection)[payment.urgency],
                'approval_notes': payment.approval_notes,
                'rejection_reason': payment.rejection_reason,
            })
        
        # QR Code and verification
        if payment.qr_code_token:
            verification_url = f"{payment.company_id.website or 'https://osus.ae'}/payment/verify/{payment.qr_code_token}"
            context.update({
                'qr_code_token': payment.qr_code_token,
                'verification_url': verification_url,
                'qr_code_data': payment._generate_qr_code_data(),
            })
        
        # Approval history
        if hasattr(payment, 'approval_history_ids'):
            context['approval_history'] = payment.approval_history_ids.sorted('create_date')
        
        # Time limits and deadlines
        config = payment._get_approval_config()
        if config:
            context.update({
                'review_deadline': payment._calculate_stage_deadline('under_review'),
                'approval_deadline': payment._calculate_stage_deadline('approved'),
                'authorization_deadline': payment._calculate_stage_deadline('authorized'),
            })
        
        # Formatted amounts
        context.update({
            'amount_formatted': payment.currency_id.format(payment.amount),
            'amount_words': payment.currency_id.amount_to_text(payment.amount),
        })
        
        return context
    
    @api.model
    def _render_template_enhanced(self, template_src, model, res_ids, context=None):
        """Enhanced template rendering with payment approval context"""
        if not context:
            context = {}
        
        # If this is a payment approval template, enhance context
        if self.is_payment_approval_template and model == 'account.payment':
            for res_id in res_ids:
                payment_context = self._get_payment_approval_context(res_id)
                context.update(payment_context)
        
        return super()._render_template_enhanced(template_src, model, res_ids, context)
    
    def generate_email(self, res_ids, fields=None):
        """Override to include payment approval enhancements"""
        result = super().generate_email(res_ids, fields)
        
        if not self.is_payment_approval_template:
            return result
        
        # Enhance each email with payment-specific content
        if isinstance(res_ids, int):
            res_ids = [res_ids]
        
        for res_id in res_ids:
            if res_id in result:
                email_values = result[res_id]
                payment = self.env['account.payment'].browse(res_id)
                
                if payment.exists():
                    self._enhance_payment_email(email_values, payment)
        
        return result
    
    def _enhance_payment_email(self, email_values, payment):
        """Enhance email with payment-specific features"""
        
        # Add urgency to subject if urgent
        if payment.urgency in ['urgent', 'high'] and 'subject' in email_values:
            urgency_prefix = {
                'urgent': '[URGENT]',
                'high': '[HIGH PRIORITY]'
            }.get(payment.urgency, '')
            
            if urgency_prefix and urgency_prefix not in email_values['subject']:
                email_values['subject'] = f"{urgency_prefix} {email_values['subject']}"
        
        # Add QR code attachment if enabled
        if self.include_qr_code and payment.qr_code_token:
            qr_attachment = payment._generate_qr_code_attachment()
            if qr_attachment:
                if 'attachments' not in email_values:
                    email_values['attachments'] = []
                email_values['attachments'].append(qr_attachment)
        
        # Add payment voucher PDF if posted
        if payment.voucher_state == 'posted' and hasattr(payment, '_generate_payment_voucher'):
            voucher_attachment = payment._generate_payment_voucher_attachment()
            if voucher_attachment:
                if 'attachments' not in email_values:
                    email_values['attachments'] = []
                email_values['attachments'].append(voucher_attachment)
        
        # Set email priority based on urgency
        if payment.urgency == 'urgent':
            email_values['priority'] = '1'  # High priority
        elif payment.urgency == 'high':
            email_values['priority'] = '2'  # Normal priority
        else:
            email_values['priority'] = '3'  # Low priority
    
    # ========================================
    # Template Helpers
    # ========================================
    
    def action_preview_payment_email(self):
        """Preview email with sample payment data"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Preview Payment Email'),
            'res_model': 'payment.email.preview.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                'default_model': 'account.payment',
            },
        }
    
    @api.model
    def create_payment_approval_templates(self):
        """Create default payment approval email templates"""
        templates_data = [
            {
                'name': 'Payment Submitted for Review',
                'model_id': self.env.ref('account.model_account_payment').id,
                'approval_stage': 'submitted',
                'subject': 'Payment Submitted: ${object.name or object.ref} - ${object.currency_id.format(object.amount)}',
                'body_html': self._get_submitted_template_body(),
            },
            {
                'name': 'Payment Under Review',
                'model_id': self.env.ref('account.model_account_payment').id,
                'approval_stage': 'under_review',
                'subject': 'Payment Under Review: ${object.name or object.ref} - ${object.currency_id.format(object.amount)}',
                'body_html': self._get_under_review_template_body(),
            },
            {
                'name': 'Payment Approved',
                'model_id': self.env.ref('account.model_account_payment').id,
                'approval_stage': 'approved',
                'subject': 'Payment Approved: ${object.name or object.ref} - ${object.currency_id.format(object.amount)}',
                'body_html': self._get_approved_template_body(),
            },
            {
                'name': 'Payment Authorized',
                'model_id': self.env.ref('account.model_account_payment').id,
                'approval_stage': 'authorized',
                'subject': 'Payment Authorized: ${object.name or object.ref} - ${object.currency_id.format(object.amount)}',
                'body_html': self._get_authorized_template_body(),
            },
            {
                'name': 'Payment Posted',
                'model_id': self.env.ref('account.model_account_payment').id,
                'approval_stage': 'posted',
                'subject': 'Payment Completed: ${object.name or object.ref} - ${object.currency_id.format(object.amount)}',
                'body_html': self._get_posted_template_body(),
            },
            {
                'name': 'Payment Rejected',
                'model_id': self.env.ref('account.model_account_payment').id,
                'approval_stage': 'rejected',
                'subject': 'Payment Rejected: ${object.name or object.ref} - ${object.currency_id.format(object.amount)}',
                'body_html': self._get_rejected_template_body(),
            },
        ]
        
        created_templates = []
        for template_data in templates_data:
            template_data.update({
                'is_payment_approval_template': True,
                'include_payment_details': True,
                'include_qr_code': True,
                'urgency_sensitive': True,
            })
            
            # Check if template already exists
            existing = self.search([
                ('name', '=', template_data['name']),
                ('approval_stage', '=', template_data['approval_stage']),
            ], limit=1)
            
            if not existing:
                template = self.create(template_data)
                created_templates.append(template)
        
        return created_templates
    
    # ========================================
    # Template Bodies
    # ========================================
    
    def _get_submitted_template_body(self):
        """Template body for submitted stage"""
        return """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #1f4788 0%, #2563eb 100%); padding: 20px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">Payment Submitted for Review</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">OSUS Properties</p>
    </div>
    
    <div style="padding: 30px; background: #f8f9fa;">
        <p>Dear Review Team,</p>
        
        <p>A new payment has been submitted for review and requires your attention.</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #1f4788;">
            <h3 style="margin-top: 0; color: #1f4788;">Payment Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Amount:</td>
                    <td style="padding: 8px 0;">${object.currency_id.format(object.amount)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Partner:</td>
                    <td style="padding: 8px 0;">${object.partner_id.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Reference:</td>
                    <td style="padding: 8px 0;">${object.ref or object.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Payment Date:</td>
                    <td style="padding: 8px 0;">${object.date}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Urgency:</td>
                    <td style="padding: 8px 0; color: ${'#dc3545' if object.urgency == 'urgent' else '#ffc107' if object.urgency == 'high' else '#6c757d'};">
                        ${dict(object._fields['urgency'].selection)[object.urgency].upper()}
                    </td>
                </tr>
            </table>
        </div>
        
        % if object.approval_notes:
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h4 style="margin-top: 0; color: #1976d2;">Notes:</h4>
            <p style="margin-bottom: 0;">${object.approval_notes}</p>
        </div>
        % endif
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${ctx.get('verification_url', '#')}" 
               style="background: #1f4788; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                Review Payment
            </a>
        </div>
        
        <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
            This payment requires review within ${ctx.get('review_deadline', '24 hours')}. 
            Please log into the system to complete the review process.
        </p>
    </div>
    
    <div style="background: #1f4788; color: white; padding: 15px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">© 2025 OSUS Properties. All rights reserved.</p>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">This is an automated message from the Payment Approval System.</p>
    </div>
</div>
        """.strip()
    
    def _get_under_review_template_body(self):
        """Template body for under review stage"""
        return """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #ffc107 0%, #ff8f00 100%); padding: 20px; color: #212529; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">Payment Under Review</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.8;">OSUS Properties</p>
    </div>
    
    <div style="padding: 30px; background: #f8f9fa;">
        <p>Dear Approval Team,</p>
        
        <p>The payment has completed initial review and is now ready for approval.</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
            <h3 style="margin-top: 0; color: #e65100;">Payment Summary</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Amount:</td>
                    <td style="padding: 8px 0;">${object.currency_id.format(object.amount)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Partner:</td>
                    <td style="padding: 8px 0;">${object.partner_id.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Reviewed By:</td>
                    <td style="padding: 8px 0;">${object.reviewed_by_id.name if object.reviewed_by_id else 'System'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Review Date:</td>
                    <td style="padding: 8px 0;">${object.review_date or 'Just completed'}</td>
                </tr>
            </table>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${ctx.get('verification_url', '#')}" 
               style="background: #e65100; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                Approve Payment
            </a>
        </div>
        
        <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
            This payment requires approval within ${ctx.get('approval_deadline', '48 hours')}.
        </p>
    </div>
    
    <div style="background: #e65100; color: white; padding: 15px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">© 2025 OSUS Properties. All rights reserved.</p>
    </div>
</div>
        """.strip()
    
    def _get_approved_template_body(self):
        """Template body for approved stage"""
        return """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 20px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">✓ Payment Approved</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">OSUS Properties</p>
    </div>
    
    <div style="padding: 30px; background: #f8f9fa;">
        <p>Dear Authorization Team,</p>
        
        <p>The payment has been approved and is ready for final authorization.</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
            <h3 style="margin-top: 0; color: #28a745;">Approved Payment</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Amount:</td>
                    <td style="padding: 8px 0;">${object.currency_id.format(object.amount)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Approved By:</td>
                    <td style="padding: 8px 0;">${object.approved_by_id.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Approval Date:</td>
                    <td style="padding: 8px 0;">${object.approval_date}</td>
                </tr>
            </table>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${ctx.get('verification_url', '#')}" 
               style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                Authorize Payment
            </a>
        </div>
    </div>
    
    <div style="background: #28a745; color: white; padding: 15px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">© 2025 OSUS Properties. All rights reserved.</p>
    </div>
</div>
        """.strip()
    
    def _get_authorized_template_body(self):
        """Template body for authorized stage"""
        return """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); padding: 20px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">✓ Payment Authorized</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">OSUS Properties</p>
    </div>
    
    <div style="padding: 30px; background: #f8f9fa;">
        <p>Dear Finance Team,</p>
        
        <p>The payment has been fully authorized and is ready for posting.</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #17a2b8;">
            <h3 style="margin-top: 0; color: #17a2b8;">Authorized Payment</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Amount:</td>
                    <td style="padding: 8px 0;">${object.currency_id.format(object.amount)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Authorized By:</td>
                    <td style="padding: 8px 0;">${object.authorized_by_id.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Authorization Date:</td>
                    <td style="padding: 8px 0;">${object.authorization_date}</td>
                </tr>
            </table>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${ctx.get('verification_url', '#')}" 
               style="background: #17a2b8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                Post Payment
            </a>
        </div>
    </div>
    
    <div style="background: #17a2b8; color: white; padding: 15px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">© 2025 OSUS Properties. All rights reserved.</p>
    </div>
</div>
        """.strip()
    
    def _get_posted_template_body(self):
        """Template body for posted stage"""
        return """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); padding: 20px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">✅ Payment Completed</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">OSUS Properties</p>
    </div>
    
    <div style="padding: 30px; background: #f8f9fa;">
        <p>Dear Team,</p>
        
        <p>The payment has been successfully completed and posted to the accounting system.</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #6f42c1;">
            <h3 style="margin-top: 0; color: #6f42c1;">Completed Payment</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Amount:</td>
                    <td style="padding: 8px 0;">${object.currency_id.format(object.amount)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Posted By:</td>
                    <td style="padding: 8px 0;">${object.posted_by_id.name if object.posted_by_id else object.write_uid.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Posting Date:</td>
                    <td style="padding: 8px 0;">${object.posting_date or object.write_date}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Move Reference:</td>
                    <td style="padding: 8px 0;">${object.move_id.name if object.move_id else 'Pending'}</td>
                </tr>
            </table>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${ctx.get('verification_url', '#')}" 
               style="background: #6f42c1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                View Payment Receipt
            </a>
        </div>
        
        <p style="color: #28a745; font-weight: bold; text-align: center; margin: 20px 0;">
            ✅ Payment workflow completed successfully
        </p>
    </div>
    
    <div style="background: #6f42c1; color: white; padding: 15px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">© 2025 OSUS Properties. All rights reserved.</p>
    </div>
</div>
        """.strip()
    
    def _get_rejected_template_body(self):
        """Template body for rejected stage"""
        return """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 20px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 24px;">❌ Payment Rejected</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">OSUS Properties</p>
    </div>
    
    <div style="padding: 30px; background: #f8f9fa;">
        <p>Dear Payment Creator,</p>
        
        <p>Unfortunately, your payment has been rejected during the approval process.</p>
        
        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
            <h3 style="margin-top: 0; color: #dc3545;">Rejected Payment</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; width: 30%;">Amount:</td>
                    <td style="padding: 8px 0;">${object.currency_id.format(object.amount)}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Rejected By:</td>
                    <td style="padding: 8px 0;">${object.rejected_by_id.name if object.rejected_by_id else 'System'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold;">Rejection Date:</td>
                    <td style="padding: 8px 0;">${object.rejection_date or object.write_date}</td>
                </tr>
            </table>
        </div>
        
        % if object.rejection_reason:
        <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #f5c6cb;">
            <h4 style="margin-top: 0; color: #721c24;">Rejection Reason:</h4>
            <p style="margin-bottom: 0; color: #721c24;">${object.rejection_reason}</p>
        </div>
        % endif
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${ctx.get('verification_url', '#')}" 
               style="background: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                Review and Resubmit
            </a>
        </div>
        
        <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
            Please review the rejection reason and make necessary corrections before resubmitting.
        </p>
    </div>
    
    <div style="background: #dc3545; color: white; padding: 15px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">© 2025 OSUS Properties. All rights reserved.</p>
    </div>
</div>
        """.strip()
