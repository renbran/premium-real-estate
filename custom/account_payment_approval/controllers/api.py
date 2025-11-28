# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, UserError, ValidationError
import json
import base64
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class PaymentApprovalAPIController(http.Controller):
    """REST API controller for payment approval system."""

    def _check_api_access(self):
        """Check if user has API access rights."""
        if not request.env.user.has_group('account_payment_approval.payment_approval_user'):
            raise AccessError("API access denied: insufficient permissions")

    def _get_payment_domain(self, user):
        """Get domain filter based on user permissions."""
        domain = [('company_id', '=', request.env.company.id)]
        
        if user.has_group('account_payment_approval.payment_approval_manager'):
            pass  # Managers can see all payments
        elif user.has_group('account_payment_approval.payment_approval_authorizer'):
            domain.append(('state', 'in', ['approved', 'authorized', 'posted']))
        elif user.has_group('account_payment_approval.payment_approval_approver'):
            domain.append(('state', 'in', ['under_review', 'approved']))
        else:
            domain.append(('create_uid', '=', user.id))
            
        return domain

    def _serialize_payment(self, payment):
        """Serialize payment object to dict."""
        return {
            'id': payment.id,
            'name': payment.name,
            'reference': payment.ref or '',
            'partner_id': payment.partner_id.id,
            'partner_name': payment.partner_id.name,
            'amount': payment.amount,
            'currency_id': payment.currency_id.id,
            'currency_name': payment.currency_id.name,
            'payment_type': payment.payment_type,
            'payment_method_id': payment.payment_method_line_id.id if payment.payment_method_line_id else None,
            'payment_method_name': payment.payment_method_line_id.name if payment.payment_method_line_id else '',
            'journal_id': payment.journal_id.id,
            'journal_name': payment.journal_id.name,
            'state': payment.state,
            'state_label': dict(payment._fields['state'].selection)[payment.state],
            'create_date': payment.create_date.isoformat() if payment.create_date else '',
            'payment_date': payment.date.isoformat() if payment.date else '',
            'memo': payment.communication or '',
            'urgency_level': getattr(payment, 'urgency_level', 'normal'),
            'approval_tier': getattr(payment, 'approval_tier', 1),
            'approval_amount_threshold': getattr(payment, 'approval_amount_threshold', 0),
            'qr_code': getattr(payment, 'qr_code', ''),
            'has_digital_signature': bool(getattr(payment, 'digital_signature', False)),
            'signature_date': getattr(payment, 'signature_date', None),
            'approval_history': self._get_approval_history(payment),
        }

    def _get_approval_history(self, payment):
        """Get approval history for payment."""
        # This would fetch from approval history model
        # For now, return basic tracking
        return []

    # API Endpoints

    @http.route('/api/v1/payments', type='json', auth='user', methods=['GET'])
    def api_get_payments(self, limit=50, offset=0, state=None, **kwargs):
        """Get list of payments with filtering."""
        try:
            self._check_api_access()
            
            domain = self._get_payment_domain(request.env.user)
            
            if state:
                domain.append(('state', '=', state))
            
            Payment = request.env['account.payment']
            total_count = Payment.search_count(domain)
            
            payments = Payment.search(
                domain,
                limit=limit,
                offset=offset,
                order='create_date desc'
            )
            
            payment_data = [self._serialize_payment(p) for p in payments]
            
            return {
                'status': 'success',
                'data': {
                    'payments': payment_data,
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                }
            }
            
        except Exception as e:
            _logger.error(f"API Error getting payments: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/v1/payments/<int:payment_id>', type='json', auth='user', methods=['GET'])
    def api_get_payment(self, payment_id, **kwargs):
        """Get specific payment details."""
        try:
            self._check_api_access()
            
            payment = request.env['account.payment'].browse(payment_id)
            
            if not payment.exists():
                return {'status': 'error', 'message': 'Payment not found'}
            
            # Check user access to this payment
            domain = self._get_payment_domain(request.env.user)
            domain.append(('id', '=', payment_id))
            
            accessible_payment = request.env['account.payment'].search(domain)
            if not accessible_payment:
                return {'status': 'error', 'message': 'Access denied'}
            
            return {
                'status': 'success',
                'data': self._serialize_payment(payment)
            }
            
        except Exception as e:
            _logger.error(f"API Error getting payment {payment_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/v1/payments/<int:payment_id>/approve', type='json', auth='user', methods=['POST'])
    def api_approve_payment(self, payment_id, signature=None, **kwargs):
        """Approve a specific payment."""
        try:
            self._check_api_access()
            
            payment = request.env['account.payment'].browse(payment_id)
            
            if not payment.exists():
                return {'status': 'error', 'message': 'Payment not found'}
            
            user = request.env.user
            
            # Check state and permissions
            if payment.state == 'under_review' and user.has_group('account_payment_approval.payment_approval_approver'):
                if signature:
                    payment.digital_signature = signature
                    payment.signature_date = fields.Datetime.now()
                    payment.signature_user_id = user.id
                
                payment.action_approve_payment()
                
                return {
                    'status': 'success',
                    'message': 'Payment approved successfully',
                    'data': self._serialize_payment(payment)
                }
            else:
                return {'status': 'error', 'message': 'Invalid state or insufficient permissions'}
            
        except Exception as e:
            _logger.error(f"API Error approving payment {payment_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/v1/payments/<int:payment_id>/authorize', type='json', auth='user', methods=['POST'])
    def api_authorize_payment(self, payment_id, signature=None, **kwargs):
        """Authorize a specific payment."""
        try:
            self._check_api_access()
            
            payment = request.env['account.payment'].browse(payment_id)
            
            if not payment.exists():
                return {'status': 'error', 'message': 'Payment not found'}
            
            user = request.env.user
            
            # Check state and permissions
            if payment.state == 'approved' and user.has_group('account_payment_approval.payment_approval_authorizer'):
                if signature:
                    payment.digital_signature = signature
                    payment.signature_date = fields.Datetime.now()
                    payment.signature_user_id = user.id
                
                payment.action_authorize_payment()
                
                return {
                    'status': 'success',
                    'message': 'Payment authorized successfully',
                    'data': self._serialize_payment(payment)
                }
            else:
                return {'status': 'error', 'message': 'Invalid state or insufficient permissions'}
            
        except Exception as e:
            _logger.error(f"API Error authorizing payment {payment_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/v1/payments/<int:payment_id>/reject', type='json', auth='user', methods=['POST'])
    def api_reject_payment(self, payment_id, reason, category='other', **kwargs):
        """Reject a specific payment."""
        try:
            self._check_api_access()
            
            payment = request.env['account.payment'].browse(payment_id)
            
            if not payment.exists():
                return {'status': 'error', 'message': 'Payment not found'}
            
            user = request.env.user
            
            # Check permissions
            if not (user.has_group('account_payment_approval.payment_approval_reviewer') or
                   user.has_group('account_payment_approval.payment_approval_approver') or
                   user.has_group('account_payment_approval.payment_approval_authorizer')):
                return {'status': 'error', 'message': 'Insufficient permissions'}
            
            payment.action_reject_payment(reason)
            
            return {
                'status': 'success',
                'message': 'Payment rejected successfully',
                'data': self._serialize_payment(payment)
            }
            
        except Exception as e:
            _logger.error(f"API Error rejecting payment {payment_id}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/v1/payments/bulk_approve', type='json', auth='user', methods=['POST'])
    def api_bulk_approve(self, payment_ids, signature=None, **kwargs):
        """Bulk approve multiple payments."""
        try:
            self._check_api_access()
            
            if not request.env.user.has_group('account_payment_approval.payment_approval_approver'):
                return {'status': 'error', 'message': 'Insufficient permissions'}
            
            payments = request.env['account.payment'].browse(payment_ids)
            
            results = []
            for payment in payments:
                try:
                    if payment.state == 'under_review':
                        if signature:
                            payment.digital_signature = signature
                            payment.signature_date = fields.Datetime.now()
                            payment.signature_user_id = request.env.user.id
                        
                        payment.action_approve_payment()
                        results.append({
                            'payment_id': payment.id,
                            'status': 'success',
                            'message': 'Approved successfully'
                        })
                    else:
                        results.append({
                            'payment_id': payment.id,
                            'status': 'error',
                            'message': f'Invalid state: {payment.state}'
                        })
                except Exception as e:
                    results.append({
                        'payment_id': payment.id,
                        'status': 'error',
                        'message': str(e)
                    })
            
            successful = len([r for r in results if r['status'] == 'success'])
            failed = len([r for r in results if r['status'] == 'error'])
            
            return {
                'status': 'success',
                'message': f'Bulk approval completed: {successful} successful, {failed} failed',
                'results': results,
                'summary': {'successful': successful, 'failed': failed}
            }
            
        except Exception as e:
            _logger.error(f"API Error bulk approving: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/v1/payments/statistics', type='json', auth='user', methods=['GET'])
    def api_get_statistics(self, period='month', **kwargs):
        """Get payment approval statistics."""
        try:
            self._check_api_access()
            
            domain = self._get_payment_domain(request.env.user)
            
            # Add date filter based on period
            if period == 'day':
                start_date = fields.Date.today()
            elif period == 'week':
                start_date = fields.Date.today() - timedelta(days=7)
            elif period == 'month':
                start_date = fields.Date.today() - timedelta(days=30)
            else:
                start_date = fields.Date.today() - timedelta(days=365)
            
            domain.append(('create_date', '>=', start_date))
            
            Payment = request.env['account.payment']
            
            stats = {
                'total_payments': Payment.search_count(domain),
                'by_state': {},
                'total_amount': 0,
                'average_amount': 0,
                'by_currency': {},
                'by_urgency': {},
                'approval_efficiency': {
                    'average_approval_time': 0,
                    'fastest_approval': 0,
                    'slowest_approval': 0,
                }
            }
            
            # Get payments for detailed analysis
            payments = Payment.search(domain)
            
            if payments:
                # Calculate statistics
                stats['total_amount'] = sum(payments.mapped('amount'))
                stats['average_amount'] = stats['total_amount'] / len(payments)
                
                # Group by state
                for state in ['draft', 'submitted', 'under_review', 'approved', 'authorized', 'posted', 'cancelled', 'rejected']:
                    count = len(payments.filtered(lambda p: p.state == state))
                    if count > 0:
                        stats['by_state'][state] = count
                
                # Group by currency
                for currency in payments.mapped('currency_id'):
                    currency_payments = payments.filtered(lambda p: p.currency_id == currency)
                    stats['by_currency'][currency.name] = {
                        'count': len(currency_payments),
                        'total_amount': sum(currency_payments.mapped('amount'))
                    }
                
                # Group by urgency level
                for urgency in ['low', 'normal', 'high', 'urgent']:
                    count = len(payments.filtered(lambda p: getattr(p, 'urgency_level', 'normal') == urgency))
                    if count > 0:
                        stats['by_urgency'][urgency] = count
            
            return {
                'status': 'success',
                'data': stats,
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': fields.Date.today().isoformat()
            }
            
        except Exception as e:
            _logger.error(f"API Error getting statistics: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/v1/payments/export', type='http', auth='user', methods=['GET'])
    def api_export_payments(self, format='csv', state=None, **kwargs):
        """Export payments data."""
        try:
            self._check_api_access()
            
            domain = self._get_payment_domain(request.env.user)
            
            if state:
                domain.append(('state', '=', state))
            
            payments = request.env['account.payment'].search(domain, order='create_date desc')
            
            if format == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'ID', 'Name', 'Partner', 'Amount', 'Currency', 'State', 
                    'Create Date', 'Payment Date', 'Reference'
                ])
                
                # Write data
                for payment in payments:
                    writer.writerow([
                        payment.id,
                        payment.name or '',
                        payment.partner_id.name,
                        payment.amount,
                        payment.currency_id.name,
                        payment.state,
                        payment.create_date.strftime('%Y-%m-%d %H:%M:%S') if payment.create_date else '',
                        payment.date.strftime('%Y-%m-%d') if payment.date else '',
                        payment.ref or ''
                    ])
                
                response = request.make_response(
                    output.getvalue(),
                    headers=[
                        ('Content-Type', 'text/csv'),
                        ('Content-Disposition', f'attachment; filename=payments_export_{fields.Date.today()}.csv')
                    ]
                )
                return response
            
            else:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Unsupported format'}),
                    headers=[('Content-Type', 'application/json')]
                )
            
        except Exception as e:
            _logger.error(f"API Error exporting payments: {str(e)}")
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
