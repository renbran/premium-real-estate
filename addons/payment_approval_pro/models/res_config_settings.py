# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # ============================================================================
    # PAYMENT VERIFICATION SETTINGS
    # ============================================================================
    
    enable_payment_verification = fields.Boolean(
        string="Enable Payment Verification",
        related='company_id.enable_payment_verification',
        readonly=False,
        help="Globally enable payment verification via QR codes"
    )
    
    default_journal_for_payments = fields.Many2one(
        'account.journal',
        string="Default Journal for Payments",
        related='company_id.default_journal_for_payments',
        readonly=False,
        domain="[('type', 'in', ('bank', 'cash'))]",
        help="Default journal for new payments"
    )
    
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
    
    # ============================================================================
    # COMPUTED FIELDS FOR DASHBOARD
    # ============================================================================
    
    payment_voucher_statistics = fields.Text(
        string='Payment Voucher Statistics',
        compute='_compute_payment_voucher_statistics',
        help="Current payment voucher statistics"
    )
    
    @api.depends('company_id')
    def _compute_payment_voucher_statistics(self):
        """Compute payment voucher statistics for the dashboard"""
        for record in self:
            if record.company_id:
                payment_obj = self.env['account.payment']
                domain = [
                    ('company_id', '=', record.company_id.id),
                    ('payment_type', 'in', ['outbound', 'inbound'])
                ]
                
                stats = {}
                
                # Count by approval states if available
                if hasattr(payment_obj, 'approval_state'):
                    states = ['draft', 'under_review', 'for_approval', 'for_authorization', 'approved', 'posted', 'cancelled']
                    for state in states:
                        count = payment_obj.search_count(domain + [('approval_state', '=', state)])
                        stats[state] = count
                else:
                    # Fallback to verification status
                    states = ['pending', 'verified', 'rejected']
                    for state in states:
                        count = payment_obj.search_count(domain + [('verification_status', '=', state)])
                        stats[state] = count
                
                total_payments = sum(stats.values())
                
                # Format statistics
                stats_lines = [f"Total Payments: {total_payments}"]
                for state, count in stats.items():
                    stats_lines.append(f"• {state.replace('_', ' ').title()}: {count}")
                
                record.payment_voucher_statistics = '\n'.join(stats_lines)
            else:
                record.payment_voucher_statistics = "No company selected"
    
    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================
    
    @api.constrains('max_approval_amount', 'authorization_threshold')
    def _check_amount_thresholds(self):
        """Validate amount thresholds"""
        for record in self:
            if record.max_approval_amount <= 0:
                raise ValidationError(_("Maximum approval amount must be greater than zero"))
            
            if record.authorization_threshold < 0:
                raise ValidationError(_("Authorization threshold cannot be negative"))
    
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
                'group_by': 'approval_state' if 'approval_state' in self.env['account.payment']._fields else 'verification_status',
            }
        }
    
    def action_test_qr_generation(self):
        """Test QR code generation functionality"""
        # Create a test payment
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
                    'title': _('QR Code Test Successful'),
                    'message': _('QR code generated successfully for test payment: %s') % test_payment.voucher_number,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('QR Code Test Failed'),
                    'message': _('QR code generation failed. Please check your configuration and ensure qrcode library is installed.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
