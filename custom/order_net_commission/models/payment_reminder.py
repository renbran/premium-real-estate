# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PaymentReminderManager(models.Model):
    """
    Payment Approval Reminder Manager & Notification System
    
    This model manages the automatic sending of reminder emails and notifications
    for payments that have been pending approval for too long.
    
    Features:
    - Send reminders to reviewers, approvers, authorizers, and posters
    - Escalation notifications for overdue items
    - Smart spam prevention
    - Workflow-specific notifications
    
    Dependencies:
    - Uses AccountPayment notification methods
    - Uses email templates defined in mail_template_data.xml
    """
    _name = 'payment.reminder.manager'
    _description = 'Payment Approval Reminder Manager & Notification System'

    @api.model
    def send_payment_notifications(self):
        """
        Main notification method for payment workflow
        
        This method sends notifications to relevant users based on payment
        approval workflow states. Called by cron job.
        
        Workflow Notifications:
        - Under Review: Notify assigned reviewers
        - For Approval: Notify approvers
        - For Authorization: Notify authorizers  
        - Approved: Notify posters to finalize posting
        """
        try:
            _logger.info("Starting payment notification process...")
            
            # Get current time
            now = datetime.now()
            
            # Notification counters
            notifications_sent = {
                'reviewer': 0,
                'approver': 0,
                'authorizer': 0,
                'poster': 0,
                'escalation': 0
            }
            
            # Find payments in different workflow states
            workflows = [
                ('under_review', 'reviewer'),
                ('for_approval', 'approver'),
                ('for_authorization', 'authorizer'),
                ('approved', 'poster')  # Ready for posting
            ]
            
            for state, role in workflows:
                payments = self.env['account.payment'].search([
                    ('approval_state', '=', state),
                    ('state', '!=', 'posted'),
                ])
                
                for payment in payments:
                    if self._should_send_notification(payment, role):
                        success = self._send_workflow_notification(payment, role)
                        if success:
                            notifications_sent[role] += 1
            
            # Send escalation notifications for overdue items
            escalations = self._send_escalation_notifications()
            notifications_sent['escalation'] = escalations
            
            _logger.info("Payment notifications sent: %s", notifications_sent)
            return notifications_sent
            
        except Exception as e:
            _logger.error("Error in send_payment_notifications: %s", str(e))
            return False

    def _send_workflow_notification(self, payment, role):
        """Send notification to specific role for payment"""
        try:
            # Determine recipient and template based on role
            recipient = None
            template_name = None
            
            if role == 'reviewer':
                # Send to assigned reviewer or default reviewers
                recipient = self._get_reviewer_for_payment(payment)
                template_name = 'payment_account_enhanced.mail_template_review_notification'
                
            elif role == 'approver':
                # Send to designated approvers
                recipient = self._get_approver_for_payment(payment)
                template_name = 'payment_account_enhanced.mail_template_approval_notification'
                
            elif role == 'authorizer':
                # Send to authorized users
                recipient = self._get_authorizer_for_payment(payment)
                template_name = 'payment_account_enhanced.mail_template_authorization_notification'
                
            elif role == 'poster':
                # Send to users who can post payments
                recipient = self._get_poster_for_payment(payment)
                template_name = 'payment_account_enhanced.mail_template_posting_notification'
            
            if recipient and template_name:
                # Send email notification
                payment.with_context(recipient_user=recipient).message_post_with_template(
                    template_id=self.env.ref(template_name, raise_if_not_found=False).id,
                    composition_mode='comment',
                    partner_ids=[recipient.partner_id.id] if recipient.partner_id else []
                )
                
                # Log notification
                self._log_notification_sent(payment, role, recipient)
                return True
                
        except Exception as e:
            _logger.error("Error sending %s notification for payment %s: %s", role, payment.id, str(e))
            
        return False

    def _get_reviewer_for_payment(self, payment):
        """Get reviewer user for payment"""
        # Priority: assigned reviewer > company default > accounting manager
        if hasattr(payment, 'reviewer_id') and payment.reviewer_id:
            return payment.reviewer_id
            
        # Get users with review permission
        reviewers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('payment_account_enhanced.group_payment_reviewer').ids),
            ('active', '=', True)
        ], limit=1)
        
        return reviewers[0] if reviewers else None

    def _get_approver_for_payment(self, payment):
        """Get approver user for payment"""
        # Get users with approval permission
        approvers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('payment_account_enhanced.group_payment_approver').ids),
            ('active', '=', True)
        ], limit=1)
        
        return approvers[0] if approvers else None

    def _get_authorizer_for_payment(self, payment):
        """Get authorizer user for payment"""
        # Get users with authorization permission
        authorizers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('payment_account_enhanced.group_payment_authorizer').ids),
            ('active', '=', True)
        ], limit=1)
        
        return authorizers[0] if authorizers else None

    def _get_poster_for_payment(self, payment):
        """Get poster user for payment"""
        # Get users with posting permission
        posters = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('account.group_account_user').ids),
            ('active', '=', True)
        ], limit=1)
        
        return posters[0] if posters else None

    def _should_send_notification(self, payment, role):
        """Check if notification should be sent to avoid spam"""
        # Check if notification was already sent recently
        hours_threshold = 24  # Send max once per day
        cutoff_time = datetime.now() - timedelta(hours=hours_threshold)
        
        recent_notifications = self.env['mail.message'].search([
            ('model', '=', 'account.payment'),
            ('res_id', '=', payment.id),
            ('create_date', '>=', cutoff_time),
            ('body', 'ilike', f'{role} notification'),
        ], limit=1)
        
        return not recent_notifications

    def _send_escalation_notifications(self):
        """Send escalation notifications for overdue payments"""
        escalation_count = 0
        escalation_threshold_hours = 72  # 3 days
        cutoff_time = datetime.now() - timedelta(hours=escalation_threshold_hours)
        
        # Find overdue payments
        overdue_payments = self.env['account.payment'].search([
            ('approval_state', 'in', ['under_review', 'for_approval', 'for_authorization']),
            ('state', '!=', 'posted'),
            ('create_date', '<=', cutoff_time),
        ])
        
        for payment in overdue_payments:
            if self._should_send_escalation(payment):
                # Send to all managers
                managers = self.env['res.users'].search([
                    ('groups_id', 'in', self.env.ref('payment_account_enhanced.group_payment_manager').ids),
                    ('active', '=', True)
                ])
                
                for manager in managers:
                    try:
                        payment.with_context(recipient_user=manager).message_post_with_template(
                            template_id=self.env.ref('payment_account_enhanced.mail_template_escalation_notification', raise_if_not_found=False).id,
                            composition_mode='comment',
                            partner_ids=[manager.partner_id.id] if manager.partner_id else []
                        )
                        escalation_count += 1
                        
                    except Exception as e:
                        _logger.error("Error sending escalation to manager %s: %s", manager.name, str(e))
        
        return escalation_count

    def _log_notification_sent(self, payment, role, recipient):
        """Log notification in payment message history"""
        payment.message_post(
            body=_("Automatic %s notification sent to %s") % (role.title(), recipient.name),
            subtype_xmlid='mail.mt_note'
        )

    @api.model
    def send_approval_reminders(self):
        """
        Cron job method to send approval reminders
        
        This method is triggered by a scheduled action defined in cron_data.xml
        to automatically send reminder emails for payments that have been
        pending in the approval workflow for too long.
        """
        try:
            # Get current time
            now = datetime.now()
            
            # Define reminder thresholds (in hours)
            reminder_after_hours = 24  # Send reminder after 24 hours
            escalation_after_hours = 72  # Send escalation after 72 hours
            
            # Calculate cutoff times
            reminder_cutoff = now - timedelta(hours=reminder_after_hours)
            escalation_cutoff = now - timedelta(hours=escalation_after_hours)
            
            # Find payments needing reminders
            pending_payments = self.env['account.payment'].search([
                ('approval_state', 'in', ['under_review', 'for_approval', 'for_authorization']),
                ('state', '!=', 'posted'),
            ])
            
            reminder_count = 0
            escalation_count = 0
            
            for payment in pending_payments:
                # Determine which date to use based on current state
                check_date = None
                
                if payment.approval_state == 'under_review':
                    # Check when it was submitted (created or state changed)
                    check_date = payment.create_date
                elif payment.approval_state == 'for_approval' and payment.reviewer_date:
                    check_date = payment.reviewer_date
                elif payment.approval_state == 'for_authorization' and payment.approver_date:
                    check_date = payment.approver_date
                
                if not check_date:
                    continue
                
                # Check if reminder is needed
                if check_date <= escalation_cutoff:
                    # Send escalation email
                    if self._should_send_escalation(payment):
                        payment.send_workflow_email('payment_account_enhanced.mail_template_approval_escalation')
                        self._log_reminder_sent(payment, 'escalation')
                        escalation_count += 1
                        
                elif check_date <= reminder_cutoff:
                    # Send reminder email
                    if self._should_send_reminder(payment):
                        payment.send_workflow_email('payment_account_enhanced.mail_template_approval_reminder')
                        self._log_reminder_sent(payment, 'reminder')
                        reminder_count += 1
            
            _logger.info("Sent %s reminders and %s escalations", reminder_count, escalation_count)
            
        except (ValueError, TypeError, AttributeError) as e:
            _logger.error("Error in send_approval_reminders: %s", str(e))

    def _should_send_reminder(self, payment):
        """Check if reminder should be sent (avoid spam)"""
        # Check if reminder was already sent today
        today = fields.Date.today()
        recent_reminders = self.env['mail.mail'].search([
            ('model', '=', 'account.payment'),
            ('res_id', '=', payment.id),
            ('subject', 'ilike', 'Approval Reminder'),
            ('date', '>=', today),
        ], limit=1)
        
        return not recent_reminders

    def _should_send_escalation(self, payment):
        """Check if escalation should be sent (avoid spam)"""
        # Check if escalation was already sent this week
        week_ago = fields.Date.today() - timedelta(days=7)
        recent_escalations = self.env['mail.mail'].search([
            ('model', '=', 'account.payment'),
            ('res_id', '=', payment.id),
            ('subject', 'ilike', 'Escalation'),
            ('date', '>=', week_ago),
        ], limit=1)
        
        return not recent_escalations

    def _log_reminder_sent(self, payment, reminder_type):
        """Log reminder in payment history"""
        payment.message_post(
            body=_("Automatic %s sent for pending approval") % reminder_type.title(),
            subtype_xmlid='mail.mt_note'
        )
