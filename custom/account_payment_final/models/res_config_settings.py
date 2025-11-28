# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # ============================================================================
    # COMPANY-RELATED FIELDS (DELEGATED)
    # ============================================================================
    
    # OSUS Branding Settings
    use_osus_branding = fields.Boolean(
        related='company_id.use_osus_branding',
        readonly=False,
        string='Use OSUS Branding',
        help="Apply OSUS brand guidelines to payment vouchers"
    )
    
    voucher_footer_message = fields.Text(
        related='company_id.voucher_footer_message',
        readonly=False,
        string='Voucher Footer Message',
        help="Custom footer message for payment vouchers"
    )
    
    voucher_terms = fields.Text(
        related='company_id.voucher_terms',
        readonly=False,
        string='Voucher Terms',
        help="Terms and conditions text for payment vouchers"
    )
    
    # Workflow Settings
    auto_post_approved_payments = fields.Boolean(
        related='company_id.auto_post_approved_payments',
        readonly=False,
        string='Auto-Post Approved Payments',
        help="Automatically post payments when approved"
    )
    
    enable_four_stage_approval = fields.Boolean(
        related='company_id.enable_four_stage_approval',
        readonly=False,
        string='Enable 4-Stage Approval',
        help="Enable the full 4-stage approval workflow for vendor payments"
    )
    
    skip_authorization_for_small_amounts = fields.Boolean(
        related='company_id.skip_authorization_for_small_amounts',
        readonly=False,
        string='Skip Authorization for Small Amounts',
        help="Skip authorization stage for payments below a certain amount"
    )
    
    authorization_threshold = fields.Monetary(
        related='company_id.authorization_threshold',
        readonly=False,
        string='Authorization Threshold',
        help="Amount below which authorization stage is skipped"
    )
    
    # Approval Settings
    max_approval_amount = fields.Monetary(
        related='company_id.max_approval_amount',
        readonly=False,
        string='Maximum Approval Amount',
        help="Maximum amount that regular users can approve"
    )
    
    require_remarks_for_large_payments = fields.Boolean(
        related='company_id.require_remarks_for_large_payments',
        readonly=False,
        string='Require Remarks for Large Payments',
        help="Require remarks for payments above the maximum approval amount"
    )
    
    # Notification Settings
    send_approval_notifications = fields.Boolean(
        related='company_id.send_approval_notifications',
        readonly=False,
        string='Send Approval Notifications',
        help="Send email notifications for approval requests"
    )
    
    # QR Code Settings
    enable_qr_codes = fields.Boolean(
        related='company_id.enable_qr_codes',
        readonly=False,
        string='Enable QR Codes',
        help="Generate QR codes for payment vouchers"
    )
    
    qr_code_verification_url = fields.Char(
        related='company_id.qr_code_verification_url',
        readonly=False,
        string='QR Verification URL',
        help="Custom URL for QR code verification portal"
    )
    
    # Security Settings
    restrict_payment_modification = fields.Boolean(
        related='company_id.restrict_payment_modification',
        readonly=False,
        string='Restrict Payment Modification',
        help="Prevent modification of payments after submission"
    )
    
    allow_manager_override = fields.Boolean(
        related='company_id.allow_manager_override',
        readonly=False,
        string='Allow Manager Override',
        help="Allow account managers to override workflow restrictions"
    )
    
    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================
    
    payment_voucher_statistics = fields.Text(
        string='Payment Voucher Statistics',
        compute='_compute_payment_voucher_statistics',
        help="Current payment voucher statistics"
    )
    
    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('company_id')
    def _compute_payment_voucher_statistics(self):
        """Compute payment voucher statistics for the dashboard"""
        for record in self:
            if record.company_id:
                # Get statistics from account.payment model
                payment_obj = self.env['account.payment']
                domain = [
                    ('company_id', '=', record.company_id.id),
                    ('payment_type', 'in', ['outbound', 'inbound'])
                ]
                
                stats = {}
                states = ['draft', 'under_review', 'for_approval', 'for_authorization', 'approved', 'posted', 'cancelled']
                
                for state in states:
                    count = payment_obj.search_count(domain + [('approval_state', '=', state)])
                    stats[state] = count
                
                total_payments = sum(stats.values())
                
                # Format statistics as readable text
                stats_text = f"""
Current Payment Voucher Status:
• Total Payments: {total_payments}
• Draft: {stats['draft']}
• Under Review: {stats['under_review']}
• For Approval: {stats['for_approval']}
• For Authorization: {stats['for_authorization']}
• Approved: {stats['approved']}
• Posted: {stats['posted']}
• Cancelled: {stats['cancelled']}
                """.strip()
                
                record.payment_voucher_statistics = stats_text
            else:
                record.payment_voucher_statistics = "No company selected"
    
    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_view_payment_dashboard(self):
        """Open payment voucher dashboard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Voucher Dashboard',
            'res_model': 'account.payment',
            'view_mode': 'kanban,tree,form',
            'domain': [
                ('company_id', '=', self.company_id.id),
                ('payment_type', 'in', ['outbound', 'inbound'])
            ],
            'context': {
                'group_by': 'approval_state',
                'search_default_filter_this_month': 1,
            }
        }
    
    def action_configure_user_groups(self):
        """Open user groups configuration"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Voucher User Groups',
            'res_model': 'res.groups',
            'view_mode': 'tree,form',
            'domain': [('category_id.name', '=', 'Accounting')],
            'context': {
                'search_default_payment_voucher': 1,
            }
        }
    
    def action_setup_email_templates(self):
        """Open email templates setup"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Voucher Email Templates',
            'res_model': 'mail.template',
            'view_mode': 'tree,form',
            'domain': [('model', '=', 'account.payment')],
            'context': {
                'default_model': 'account.payment',
                'default_model_id': self.env.ref('account.model_account_payment').id,
            }
        }
    
    def action_test_qr_generation(self):
        """Test QR code generation"""
        # Create a sample payment for testing
        test_payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.env.ref('base.res_partner_1').id,
            'amount': 1000.0,
            'currency_id': self.env.company.currency_id.id,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
            'date': fields.Date.today(),
            'remarks': 'QR Code Test Payment',
        })
        
        # Generate QR code
        test_payment._compute_payment_qr_code()
        
        if test_payment.qr_code:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('QR Code Test'),
                    'message': _('QR code generated successfully! Check the payment voucher: %s') % test_payment.voucher_number,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('QR Code Test'),
                    'message': _('QR code generation failed. Please check your configuration.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
    
    def action_regenerate_all_qr_codes(self):
        """Regenerate all QR codes for existing payments"""
        payments = self.env['account.payment'].search([
            ('company_id', '=', self.company_id.id),
            ('approval_state', '!=', 'draft'),
            ('qr_in_report', '=', True)
        ])
        
        for payment in payments:
            payment._compute_payment_qr_code()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('QR Codes Regenerated'),
                'message': _('Successfully regenerated QR codes for %d payment vouchers.') % len(payments),
                'type': 'success',
                'sticky': False,
            }
        }
    
    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================
    
    @api.constrains('max_approval_amount', 'authorization_threshold')
    def _check_amount_thresholds(self):
        """Validate amount thresholds"""
        for record in self:
            if record.max_approval_amount <= 0:
                raise ValidationError(_("Maximum approval amount must be greater than zero."))
            
            if record.authorization_threshold < 0:
                raise ValidationError(_("Authorization threshold cannot be negative."))
            
            if record.skip_authorization_for_small_amounts and record.authorization_threshold >= record.max_approval_amount:
                raise ValidationError(_("Authorization threshold should be less than maximum approval amount."))
    
    @api.onchange('enable_qr_codes')
    def _onchange_enable_qr_codes(self):
        """Handle QR code enablement"""
        if not self.enable_qr_codes:
            self.qr_code_verification_url = False
    
    @api.onchange('enable_four_stage_approval')
    def _onchange_enable_four_stage_approval(self):
        """Handle 4-stage approval enablement"""
        if not self.enable_four_stage_approval:
            self.skip_authorization_for_small_amounts = False
            self.authorization_threshold = 0.0