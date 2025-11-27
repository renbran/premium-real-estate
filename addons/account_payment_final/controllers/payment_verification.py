# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import logging
import json
import hashlib
import datetime

_logger = logging.getLogger(__name__)


class PaymentQRVerification(models.Model):
    """Model to track QR code verifications and provide verification services"""
    _name = 'payment.qr.verification'
    _description = 'Payment QR Code Verification'
    _order = 'verification_date desc'
    _rec_name = 'verification_code'

    # ============================================================================
    # FIELDS
    # ============================================================================

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        ondelete='cascade',
        index=True,
        help="Related payment voucher"
    )

    verification_code = fields.Char(
        string='Verification Code',
        required=True,
        index=True,
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
    ], string='Verification Method', default='qr_scan', required=True)

    additional_data = fields.Text(
        string='Additional Data',
        help="Additional verification context in JSON format"
    )

    # Related fields for easy access
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

    payment_approval_state = fields.Selection(
        related='payment_id.approval_state',
        string='Payment Status',
        store=True
    )

    company_id = fields.Many2one(
        related='payment_id.company_id',
        string='Company',
        store=True
    )

    # ============================================================================
    # METHODS
    # ============================================================================

    @api.model
    def generate_verification_code(self, payment_id):
        """Generate a unique verification code for a payment"""
        payment = self.env['account.payment'].browse(payment_id)
        if not payment:
            return False

        # Create a unique hash based on payment data and timestamp
        data_string = f"{payment.id}_{payment.voucher_number}_{payment.amount}_{datetime.datetime.now().isoformat()}"
        verification_code = hashlib.sha256(data_string.encode()).hexdigest()[:16].upper()
        
        return verification_code

    @api.model
    def verify_payment_qr(self, payment_id, verification_context=None):
        """Verify a payment QR code and create verification record"""
        try:
            payment = self.env['account.payment'].browse(payment_id)
            if not payment.exists():
                return {
                    'success': False,
                    'error_code': 'PAYMENT_NOT_FOUND',
                    'message': _('Payment voucher not found.')
                }

            # Generate verification code
            verification_code = self.generate_verification_code(payment_id)
            
            # Prepare verification data
            verification_vals = {
                'payment_id': payment_id,
                'verification_code': verification_code,
                'verification_status': 'success',
                'verification_method': 'qr_scan',
            }

            # Add context data if provided
            if verification_context:
                verification_vals.update({
                    'verifier_ip': verification_context.get('ip_address'),
                    'verifier_user_agent': verification_context.get('user_agent'),
                    'additional_data': json.dumps(verification_context.get('additional_data', {}))
                })

            # Create verification record
            verification = self.create(verification_vals)

            # Prepare response data
            response_data = {
                'success': True,
                'verification_code': verification_code,
                'payment_data': {
                    'voucher_number': payment.voucher_number,
                    'payment_reference': payment.name,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'currency_symbol': payment.currency_id.symbol,
                    'partner_name': payment.partner_id.name,
                    'payment_date': payment.date.strftime('%Y-%m-%d') if payment.date else None,
                    'payment_type': payment.payment_type,
                    'payment_type_display': 'Customer Receipt' if payment.payment_type == 'inbound' else 'Vendor Payment',
                    'approval_state': payment.approval_state,
                    'approval_state_display': dict(payment._fields['approval_state'].selection)[payment.approval_state],
                    'journal_name': payment.journal_id.name,
                    'company_name': payment.company_id.name,
                    'is_verified': payment.approval_state in ['approved', 'posted'],
                    'verification_timestamp': verification.verification_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'qr_code_data': payment.qr_code if payment.qr_in_report else None,
                }
            }

            return response_data

        except Exception as e:
            _logger.error(f"Error verifying payment QR code: {e}")
            
            # Create failed verification record
            try:
                self.create({
                    'payment_id': payment_id,
                    'verification_code': 'FAILED',
                    'verification_status': 'failed',
                    'verification_method': 'qr_scan',
                    'additional_data': json.dumps({'error': str(e)})
                })
            except:
                pass  # Don't fail if we can't log the failure

            return {
                'success': False,
                'error_code': 'VERIFICATION_ERROR',
                'message': _('An error occurred during verification. Please try again.')
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

    # ============================================================================
    # SECURITY METHODS
    # ============================================================================

    def unlink(self):
        """Prevent deletion of verification records for audit purposes"""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("QR verification records cannot be deleted for audit purposes."))
        return super(PaymentQRVerification, self).unlink()

    def write(self, vals):
        """Prevent modification of verification records for audit purposes"""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("QR verification records cannot be modified for audit purposes."))
        return super(PaymentQRVerification, self).write(vals)


class PaymentQRGenerator(models.TransientModel):
    """Wizard for generating QR codes for multiple payments"""
    _name = 'payment.qr.generator'
    _description = 'Payment QR Code Generator'

    # ============================================================================
    # FIELDS
    # ============================================================================

    payment_ids = fields.Many2many(
        'account.payment',
        string='Payments',
        required=True,
        domain="[('approval_state', '!=', 'draft'), ('voucher_number', '!=', False)]",
        help="Payments for which to generate QR codes"
    )

    regenerate_existing = fields.Boolean(
        string='Regenerate Existing QR Codes',
        default=False,
        help="Regenerate QR codes even if they already exist"
    )

    # ============================================================================
    # METHODS
    # ============================================================================

    def action_generate_qr_codes(self):
        """Generate QR codes for selected payments"""
        generated_count = 0
        skipped_count = 0

        for payment in self.payment_ids:
            if payment.qr_code and not self.regenerate_existing:
                skipped_count += 1
                continue

            # Enable QR code for this payment if not already enabled
            if not payment.qr_in_report:
                payment.qr_in_report = True

            # Generate QR code
            payment._compute_payment_qr_code()
            
            if payment.qr_code:
                generated_count += 1
            else:
                _logger.warning(f"Failed to generate QR code for payment {payment.voucher_number}")

        # Show result message
        message = f"Successfully generated QR codes for {generated_count} payments."
        if skipped_count > 0:
            message += f" Skipped {skipped_count} payments with existing QR codes."

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('QR Code Generation Complete'),
                'message': _(message),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.onchange('payment_ids')
    def _onchange_payment_ids(self):
        """Update domain and show info about selected payments"""
        if self.payment_ids:
            # Count payments with and without QR codes
            with_qr = len([p for p in self.payment_ids if p.qr_code])
            without_qr = len(self.payment_ids) - with_qr
            
            return {
                'warning': {
                    'title': _('QR Code Status'),
                    'message': _('%d payments selected. %d already have QR codes, %d need generation.') % 
                              (len(self.payment_ids), with_qr, without_qr)
                }
            }


class PaymentQRBulkVerification(models.TransientModel):
    """Wizard for bulk QR code verification"""
    _name = 'payment.qr.bulk.verification'
    _description = 'Payment QR Code Bulk Verification'

    # ============================================================================
    # FIELDS
    # ============================================================================

    payment_ids = fields.Many2many(
        'account.payment',
        string='Payments to Verify',
        required=True,
        domain="[('qr_code', '!=', False)]",
        help="Payments with QR codes to verify"
    )

    verification_results = fields.Text(
        string='Verification Results',
        readonly=True,
        help="Results of the bulk verification process"
    )

    # ============================================================================
    # METHODS
    # ============================================================================

    def action_bulk_verify(self):
        """Perform bulk verification of QR codes"""
        results = []
        success_count = 0
        failure_count = 0

        for payment in self.payment_ids:
            try:
                # Verify QR code
                verification_result = self.env['payment.qr.verification'].verify_payment_qr(
                    payment.id,
                    {'verification_method': 'api_call', 'source': 'bulk_verification'}
                )

                if verification_result['success']:
                    success_count += 1
                    results.append(f"✓ {payment.voucher_number}: Verification successful")
                else:
                    failure_count += 1
                    results.append(f"✗ {payment.voucher_number}: {verification_result.get('message', 'Unknown error')}")

            except Exception as e:
                failure_count += 1
                results.append(f"✗ {payment.voucher_number}: Exception - {str(e)}")
                _logger.error(f"Bulk verification error for payment {payment.voucher_number}: {e}")

        # Update results
        summary = f"Bulk Verification Complete:\n✓ Success: {success_count}\n✗ Failed: {failure_count}\n\nDetails:\n"
        self.verification_results = summary + "\n".join(results)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Bulk Verification Results',
            'res_model': 'payment.qr.bulk.verification',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }