from odoo import http, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PaymentVerificationController(http.Controller):

    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', website=True, csrf=False)
    def verify_payment(self, payment_id, **kwargs):
        """Public payment verification page"""
        try:
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return request.render('account_payment_final.payment_not_found')
            
            # Log verification
            request.env['payment.qr.verification'].sudo().log_verification(
                payment_id, request.httprequest.environ.get('REMOTE_ADDR')
            )
            
            # Status mapping
            status_info = {
                'draft': ('info', 'Draft - Not Processed'),
                'under_review': ('warning', 'Under Review'),
                'for_approval': ('warning', 'Pending Approval'),
                'for_authorization': ('warning', 'Pending Authorization'),
                'approved': ('success', 'Approved'),
                'posted': ('success', 'VERIFIED & POSTED'),
                'cancelled': ('danger', 'Cancelled')
            }
            
            status_class, status_message = status_info.get(payment.approval_state, ('secondary', 'Unknown'))
            
            context = {
                'payment': payment,
                'status_class': f'bg-{status_class}',
                'status_message': status_message,
                'company': payment.company_id,
                'verification_time': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return request.render('account_payment_final.payment_verification_page', context)
            
        except Exception as e:
            _logger.error(f"Verification error: {e}")
            return request.render('account_payment_final.payment_not_found')
