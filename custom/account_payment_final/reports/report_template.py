# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PaymentVoucherReport(models.AbstractModel):
    _name = 'report.account_payment_final.payment_voucher_template'
    _description = 'Payment Voucher Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override to ensure proper report rendering and prevent cut-off issues
        """
        try:
            docs = self.env['account.payment'].browse(docids)
            
            # Ensure we have valid documents
            if not docs:
                raise UserError("No payment vouchers found for the given IDs.")
            
            # Prepare data for each voucher
            voucher_data = []
            for doc in docs:
                voucher_info = {
                    'voucher': doc,
                    'company': doc.company_id,
                    'currency': doc.currency_id,
                    'partner': doc.partner_id,
                    'journal': doc.journal_id,
                    'amount_words': self._amount_to_words(doc.amount, doc.currency_id),
                    'approval_stages': self._get_approval_stages(doc),
                    'qr_code': self._generate_qr_code(doc),
                    'signature_data': self._get_signature_data(doc),
                }
                voucher_data.append(voucher_info)
            
            return {
                'doc_ids': docids,
                'doc_model': 'account.payment',
                'docs': docs,
                'voucher_data': voucher_data,
                'company': docs[0].company_id if docs else self.env.company,
                'report_type': 'pdf',
                'print_mode': True,
            }
            
        except Exception as e:
            _logger.error(f"Error generating payment voucher report: {e}")
            raise UserError(f"Error generating report: {e}")

    def _amount_to_words(self, amount, currency):
        """Convert amount to words"""
        try:
            # Use Odoo's built-in currency tools if available
            if hasattr(currency, 'amount_to_text'):
                return currency.amount_to_text(amount)
            else:
                # Fallback to simple conversion
                return f"{currency.symbol} {amount:,.2f}"
        except:
            return f"{amount:,.2f}"

    def _get_approval_stages(self, payment):
        """Get approval workflow stages"""
        stages = []
        
        # Define the standard approval stages
        stage_definitions = [
            {'name': 'Draft', 'state': 'draft', 'icon': 'fa-edit'},
            {'name': 'Under Review', 'state': 'under_review', 'icon': 'fa-search'},
            {'name': 'For Approval', 'state': 'for_approval', 'icon': 'fa-check-circle'},
            {'name': 'Authorized', 'state': 'authorized', 'icon': 'fa-key'},
            {'name': 'Posted', 'state': 'posted', 'icon': 'fa-check'},
        ]
        
        current_state = getattr(payment, 'approval_state', payment.state)
        
        for stage in stage_definitions:
            stage_status = 'completed' if self._is_stage_completed(stage['state'], current_state, payment) else 'pending'
            if stage['state'] == current_state:
                stage_status = 'current'
                
            stages.append({
                'name': stage['name'],
                'state': stage['state'],
                'icon': stage['icon'],
                'status': stage_status,
                'date': self._get_stage_date(stage['state'], payment),
                'user': self._get_stage_user(stage['state'], payment),
            })
        
        return stages

    def _is_stage_completed(self, stage_state, current_state, payment):
        """Check if a stage is completed"""
        stage_order = ['draft', 'under_review', 'for_approval', 'authorized', 'posted']
        try:
            current_index = stage_order.index(current_state)
            stage_index = stage_order.index(stage_state)
            return stage_index < current_index
        except ValueError:
            return False

    def _get_stage_date(self, stage_state, payment):
        """Get the date when a stage was completed"""
        # Try to get from activity logs or tracking
        date_field_map = {
            'draft': 'create_date',
            'posted': 'date',
        }
        
        field_name = date_field_map.get(stage_state)
        if field_name and hasattr(payment, field_name):
            return getattr(payment, field_name)
        
        return None

    def _get_stage_user(self, stage_state, payment):
        """Get the user who completed a stage"""
        user_field_map = {
            'draft': 'create_uid',
        }
        
        field_name = user_field_map.get(stage_state)
        if field_name and hasattr(payment, field_name):
            return getattr(payment, field_name)
        
        return None

    def _generate_qr_code(self, payment):
        """Generate QR code data for payment verification"""
        try:
            # Create verification URL or code
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            verification_code = f"PAY-{payment.id}-{payment.name or 'DRAFT'}"
            verification_url = f"{base_url}/payment/verify/{verification_code}"
            
            return {
                'code': verification_code,
                'url': verification_url,
                'data': f"Payment: {payment.name}\nAmount: {payment.amount}\nPartner: {payment.partner_id.name if payment.partner_id else 'N/A'}",
            }
        except Exception as e:
            _logger.warning(f"Could not generate QR code: {e}")
            return None

    def _get_signature_data(self, payment):
        """Get signature and approval data"""
        signatures = []
        
        # Define signature roles
        signature_roles = [
            {'title': 'Prepared By', 'user': payment.create_uid, 'date': payment.create_date},
            {'title': 'Reviewed By', 'user': None, 'date': None},
            {'title': 'Approved By', 'user': None, 'date': None},
            {'title': 'Authorized By', 'user': None, 'date': None},
        ]
        
        for role in signature_roles:
            signature_data = {
                'title': role['title'],
                'user_name': role['user'].name if role['user'] else 'Pending',
                'date': role['date'].strftime('%Y-%m-%d') if role['date'] else 'Pending',
                'is_pending': not role['user'],
            }
            signatures.append(signature_data)
        
        return signatures


class PaymentVoucherReportWizard(models.TransientModel):
    _name = 'payment.voucher.report.wizard'
    _description = 'Payment Voucher Report Wizard'

    payment_ids = fields.Many2many('account.payment', string='Payments')
    report_format = fields.Selection([
        ('pdf', 'PDF'),
        ('html', 'HTML Preview'),
    ], default='pdf', string='Format')

    def print_report(self):
        """Print the payment voucher report"""
        if not self.payment_ids:
            raise UserError("Please select at least one payment to print.")
        
        return self.env.ref('account_payment_final.action_payment_voucher_report').report_action(
            self.payment_ids.ids, 
            data={'report_format': self.report_format}
        )