# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import json
import hashlib
import datetime

_logger = logging.getLogger(__name__)


class PaymentQRVerification(models.Model):
    """Comprehensive QR code verification logging and management"""
    _name = 'payment.qr.verification'
    _description = 'Payment QR Code Verification Log'
    _order = 'verification_date desc'
    _rec_name = 'verification_code'

    # ============================================================================
    # CORE FIELDS
    # ============================================================================

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        ondelete='cascade',
        index=True,
        help="Related payment voucher that was verified"
    )

    verification_code = fields.Char(
        string='Verification Code',
        required=True,
        index=True,
        copy=False,
        help="Unique verification code for this QR scan"
    )

    verification_date = fields.Datetime(
        string='Verification Date',
        required=True,
        default=fields.Datetime.now,
        help="Date and time of verification"
    )

    verifier_ip = fields.Char(
        string='Verifier IP Address',
        help="IP address of the person who scanned the QR code"
    )

    verifier_user_agent = fields.Text(
        string='User Agent',
        help="Browser/device information of the verifier"
    )

    verification_status = fields.Selection([
        ('success', 'Successful Verification'),
        ('failed', 'Failed Verification'),
        ('expired', 'Expired QR Code'),
        ('invalid', 'Invalid QR Code'),
    ], string='Verification Status', default='success', required=True)

    verification_method = fields.Selection([
        ('qr_scan', 'QR Code Scan'),
        ('manual_entry', 'Manual Entry'),
        ('api_call', 'API Call'),
        ('bulk_verify', 'Bulk Verification'),
    ], string='Verification Method', default='qr_scan', required=True)

    additional_data = fields.Text(
        string='Additional Data',
        help="Additional verification context in JSON format"
    )

    # ============================================================================
    # RELATED FIELDS FOR REPORTING
    # ============================================================================

    payment_name = fields.Char(
        related='payment_id.name',
        string='Payment Reference',
        store=True
    )

    payment_voucher_number = fields.Char(
        related='payment_id.voucher_number',
        string='Voucher Number',
        store=True
    )

    payment_partner_id = fields.Many2one(
        related='payment_id.partner_id',
        string='Partner',
        store=True
    )

    payment_amount = fields.Monetary(
        related='payment_id.amount',
        string='Amount',
        currency_field='payment_currency_id',
        store=True
    )

    payment_currency_id = fields.Many2one(
        related='payment_id.currency_id',
        string='Currency',
        store=True
    )

    payment_verification_status = fields.Selection(
        related='payment_id.verification_status',
        string='Payment Status',
        store=True
    )

    company_id = fields.Many2one(
        related='payment_id.company_id',
        string='Company',
        store=True
    )

    # ============================================================================
    # BUSINESS METHODS
    # ============================================================================

    @api.model
    def create(self, vals):
        """Auto-generate verification code if not provided"""
        if not vals.get('verification_code'):
            payment_id = vals.get('payment_id', 0)
            timestamp = datetime.datetime.now().isoformat()
            user_id = self.env.user.id
            
            vals['verification_code'] = hashlib.md5(
                f"{payment_id}-{timestamp}-{user_id}".encode()
            ).hexdigest()[:16].upper()
        
        return super().create(vals)

    @api.model
    def log_verification(self, payment_id, ip_address=None, user_agent=None, method='qr_scan', additional_data=None):
        """Convenient method to log verification attempts"""
        verification_data = {
            'payment_id': payment_id,
            'verification_method': method,
            'verification_status': 'success',
        }
        
        if ip_address:
            verification_data['verifier_ip'] = ip_address
        if user_agent:
            verification_data['verifier_user_agent'] = user_agent
        if additional_data:
            verification_data['additional_data'] = json.dumps(additional_data)
        
        return self.create(verification_data)

    def action_view_payment(self):
        """Open the related payment voucher"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Payment Voucher - {self.payment_voucher_number}',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def get_verification_statistics(self, domain=None):
        """Get QR verification statistics for dashboard"""
        if domain is None:
            domain = []

        # Count verifications by status
        status_stats = {}
        for status, label in self._fields['verification_status'].selection:
            count = self.search_count(domain + [('verification_status', '=', status)])
            status_stats[status] = {'label': label, 'count': count}

        # Count verifications by method
        method_stats = {}
        for method, label in self._fields['verification_method'].selection:
            count = self.search_count(domain + [('verification_method', '=', method)])
            method_stats[method] = {'label': label, 'count': count}

        # Recent verifications (last 7 days)
        recent_date = fields.Datetime.now() - datetime.timedelta(days=7)
        recent_count = self.search_count(domain + [('verification_date', '>=', recent_date)])

        # Total verifications
        total_count = self.search_count(domain)

        return {
            'status_stats': status_stats,
            'method_stats': method_stats,
            'recent_count': recent_count,
            'total_count': total_count
        }

    # ============================================================================
    # CONSTRAINTS AND SECURITY
    # ============================================================================

    _sql_constraints = [
        ('verification_code_unique', 'UNIQUE(verification_code)', 
         'Verification code must be unique across all verifications'),
    ]

    def unlink(self):
        """Prevent deletion of verification records for audit purposes"""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("QR verification records cannot be deleted for audit purposes"))
        return super().unlink()

    def write(self, vals):
        """Prevent modification of verification records for audit purposes"""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("QR verification records cannot be modified for audit purposes"))
        return super().write(vals)
