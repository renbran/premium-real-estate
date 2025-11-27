from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    approval_state = fields.Selection([
        ('draft', 'Draft'), ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'), ('approved', 'Approved'),
        ('posted', 'Posted'), ('cancelled', 'Cancelled')
    ], default='draft', tracking=True, copy=False)

    reviewer_id = fields.Many2one('res.users', copy=False)
    approver_id = fields.Many2one('res.users', copy=False)
    reviewer_date = fields.Datetime(copy=False)
    approver_date = fields.Datetime(copy=False)

    def action_submit_for_review(self):
        """Submit invoice/bill for approval workflow"""
        if self.move_type not in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            raise UserError(_("Only invoices and bills use approval workflow."))
        
        self.approval_state = 'under_review'
        self._post_message("submitted for review")
        return self._reload_view()

    def action_review_approve(self):
        """Review and approve for final approval"""
        self._check_permissions('review')
        self.write({
            'reviewer_id': self.env.user.id,
            'reviewer_date': fields.Datetime.now(),
            'approval_state': 'for_approval'
        })
        self._post_message("reviewed")
        return self._reload_view()

    def action_final_approve(self):
        """Final approval and auto-post"""
        self._check_permissions('approve')
        self.write({
            'approver_id': self.env.user.id,
            'approver_date': fields.Datetime.now(),
            'approval_state': 'approved'
        })
        
        try:
            self.action_post()
        except Exception:
            pass  # Allow manual posting if auto-post fails
        return self._reload_view()

    def action_post(self):
        """Override posting to enforce approval"""
        for record in self:
            if (record.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'] and
                hasattr(record, 'approval_state') and record.approval_state != 'approved'):
                raise UserError(_("Invoice/Bill must be approved before posting."))
        
        result = super().action_post()
        for record in self:
            if hasattr(record, 'approval_state'):
                record.approval_state = 'posted'
        return result

    def _check_permissions(self, stage):
        """Permission validation"""
        groups = {
            'review': 'account.group_account_user',
            'approve': 'account.group_account_manager'
        }
        if not self.env.user.has_group(groups[stage]):
            raise UserError(_('Insufficient permissions'))

    def _post_message(self, action):
        """Workflow message logging"""
        self.message_post(body=f"Invoice/Bill {action} by {self.env.user.name}")

    def _reload_view(self):
        """Standard view reload response"""
        return {'type': 'ir.actions.client', 'tag': 'reload'}
3. Web Controller (Compressed)
Copy# controllers/payment_verification.py
from odoo import http, _
from odoo.http import request
import logging
import hashlib
import datetime

_logger = logging.getLogger(__name__)

class PaymentVerificationController(http.Controller):

    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', website=True, csrf=False)
    def verify_payment(self, payment_id, **kwargs):
        """Public payment verification endpoint"""
        payment = request.env['account.payment'].sudo().browse(payment_id)
        
        if not payment.exists():
            return request.render('account_payment_final.payment_not_found')
        
        # Log verification attempt
        self._log_verification(payment, request.httprequest)
        
        # Status mapping
        status_map = {
            'draft': ('draft', 'Draft - Not processed', 'text-secondary'),
            'under_review': ('processing', 'Under Review', 'text-info'),
            'for_approval': ('processing', 'Pending Approval', 'text-warning'),
            'for_authorization': ('processing', 'Pending Authorization', 'text-warning'),
            'approved': ('approved', 'Approved', 'text-success'),
            'posted': ('verified', 'Verified and Posted', 'text-success'),
            'cancelled': ('cancelled', 'Cancelled', 'text-danger')
        }
        
        status, message, css_class = status_map.get(
            payment.approval_state, ('unknown', 'Unknown Status', 'text-muted')
        )
        
        context = {
            'payment': payment,
            'verification_status': status,
            'status_message': message,
            'status_class': css_class,
            'company': payment.company_id,
            'verification_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return request.render('account_payment_final.payment_verification_page', context)

    def _log_verification(self, payment, http_request):
        """Audit trail logging"""
        try:
            request.env['payment.qr.verification'].sudo().create({
                'payment_id': payment.id,
                'verification_code': hashlib.md5(f"{payment.id}-{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:12].upper(),
                'verification_date': datetime.datetime.now(),
                'verifier_ip': http_request.environ.get('REMOTE_ADDR'),
                'verification_method': 'qr_scan',
                'verification_status': 'success'
            })
        except Exception as e:
            _logger.warning(f"Verification logging failed: {e}")