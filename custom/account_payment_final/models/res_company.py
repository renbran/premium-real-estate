# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # ============================================================================
    # OSUS BRANDING AND PAYMENT SETTINGS
    # ============================================================================
    
    use_osus_branding = fields.Boolean(
        string='Use OSUS Branding',
        default=True,
        help="Apply OSUS brand guidelines to payment vouchers"
    )
    
    auto_post_approved_payments = fields.Boolean(
        string='Auto-Post Approved Payments',
        default=False,
        help="Automatically post payments when approved"
    )
    
    max_approval_amount = fields.Monetary(
        string='Maximum Approval Amount',
        currency_field='currency_id',
        default=10000.0,
        help="Maximum amount that regular users can approve"
    )
    
    send_approval_notifications = fields.Boolean(
        string='Send Approval Notifications',
        default=True,
        help="Send email notifications for approval requests"
    )
    
    require_remarks_for_large_payments = fields.Boolean(
        string='Require Remarks for Large Payments',
        default=True,
        help="Require remarks for payments above the maximum approval amount"
    )
    
    voucher_footer_message = fields.Text(
        string='Voucher Footer Message',
        default='Thank you for your business with OSUS Properties',
        help="Custom footer message for payment vouchers"
    )
    
    voucher_terms = fields.Text(
        string='Voucher Terms',
        default='This is a computer-generated document. No physical signature required for system verification.',
        help="Terms and conditions text for payment vouchers"
    )
    
    # ============================================================================
    # WORKFLOW SETTINGS
    # ============================================================================
    
    enable_four_stage_approval = fields.Boolean(
        string='Enable 4-Stage Approval',
        default=True,
        help="Enable the full 4-stage approval workflow for vendor payments"
    )
    
    skip_authorization_for_small_amounts = fields.Boolean(
        string='Skip Authorization for Small Amounts',
        default=False,
        help="Skip authorization stage for payments below a certain amount"
    )
    
    authorization_threshold = fields.Monetary(
        string='Authorization Threshold',
        currency_field='currency_id',
        default=5000.0,
        help="Amount below which authorization stage is skipped"
    )
    
    # ============================================================================
    # QR CODE SETTINGS
    # ============================================================================
    
    enable_qr_codes = fields.Boolean(
        string='Enable QR Codes',
        default=True,
        help="Generate QR codes for payment vouchers"
    )
    
    qr_code_verification_url = fields.Char(
        string='QR Verification URL',
        help="Custom URL for QR code verification portal"
    )
    
    # ============================================================================
    # SECURITY SETTINGS
    # ============================================================================
    
    restrict_payment_modification = fields.Boolean(
        string='Restrict Payment Modification',
        default=True,
        help="Prevent modification of payments after submission"
    )
    
    allow_manager_override = fields.Boolean(
        string='Allow Manager Override',
        default=True,
        help="Allow account managers to override workflow restrictions"
    )
    
    # ============================================================================
    # METHODS
    # ============================================================================
    
    @api.model
    def get_payment_voucher_settings(self):
        """Get payment voucher settings for the current company"""
        company = self.env.company
        return {
            'use_osus_branding': company.use_osus_branding,
            'auto_post_approved_payments': company.auto_post_approved_payments,
            'max_approval_amount': company.max_approval_amount,
            'send_approval_notifications': company.send_approval_notifications,
            'require_remarks_for_large_payments': company.require_remarks_for_large_payments,
            'voucher_footer_message': company.voucher_footer_message,
            'voucher_terms': company.voucher_terms,
            'enable_four_stage_approval': company.enable_four_stage_approval,
            'skip_authorization_for_small_amounts': company.skip_authorization_for_small_amounts,
            'authorization_threshold': company.authorization_threshold,
            'enable_qr_codes': company.enable_qr_codes,
            'qr_code_verification_url': company.qr_code_verification_url,
            'restrict_payment_modification': company.restrict_payment_modification,
            'allow_manager_override': company.allow_manager_override,
        }
    
    def action_configure_payment_vouchers(self):
        """Open payment voucher configuration wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Voucher Configuration',
            'res_model': 'res.config.settings',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_company_id': self.id,
            }
        }