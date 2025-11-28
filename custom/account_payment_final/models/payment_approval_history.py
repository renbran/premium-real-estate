# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PaymentApprovalHistory(models.Model):
    """
    Payment Approval History
    
    Tracks the complete approval workflow history for audit purposes.
    Follows Odoo 17 patterns for logging and audit trail functionality.
    """
    _name = 'payment.approval.history'
    _description = 'Payment Approval History'
    _order = 'create_date desc'
    _rec_name = 'display_name'
    
    # Relations
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        ondelete='cascade',
        index=True,
        help="Related payment record"
    )
    
    # Approval details
    stage_from = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approve', 'Approved'),
        ('authorize', 'Authorized'),
        ('post', 'Posted'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected'),
    ], string='From Stage', required=True, help="Previous stage")
    
    stage_to = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approve', 'Approved'),
        ('authorize', 'Authorized'),
        ('post', 'Posted'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected'),
    ], string='To Stage', required=True, help="New stage")
    
    action_type = fields.Selection([
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('submit', 'Submit for Review'),
        ('reset', 'Reset to Draft'),
        ('post', 'Post Payment'),
        ('cancel', 'Cancel'),
    ], string='Action Type', required=True, help="Type of action performed")
    
    # User and timing
    user_id = fields.Many2one(
        'res.users',
        string='Performed by',
        required=True,
        default=lambda self: self.env.user,
        help="User who performed this action"
    )
    
    date_action = fields.Datetime(
        string='Action Date',
        required=True,
        default=fields.Datetime.now,
        help="When this action was performed"
    )
    
    # Additional information
    comments = fields.Text(
        string='Comments',
        help="Additional comments or reasons for this action"
    )
    
    ip_address = fields.Char(
        string='IP Address',
        help="IP address from which action was performed"
    )
    
    user_agent = fields.Text(
        string='User Agent',
        help="Browser/client information"
    )
    
    # Computed fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help="Human readable name for this history record"
    )
    
    duration_in_stage = fields.Float(
        string='Duration in Previous Stage (Hours)',
        compute='_compute_duration_in_stage',
        store=True,
        help="How long payment spent in previous stage"
    )
    
    # Company
    company_id = fields.Many2one(
        related='payment_id.company_id',
        store=True,
        string='Company'
    )
    
    @api.depends('payment_id', 'stage_from', 'stage_to', 'action_type', 'user_id')
    def _compute_display_name(self):
        """Compute display name for history records"""
        for record in self:
            payment_name = record.payment_id.name or f"Payment #{record.payment_id.id}"
            action_desc = dict(record._fields['action_type'].selection)[record.action_type]
            user_name = record.user_id.name
            record.display_name = f"{payment_name} - {action_desc} by {user_name}"
    
    @api.depends('payment_id', 'stage_from', 'date_action')
    def _compute_duration_in_stage(self):
        """Compute how long payment spent in previous stage"""
        for record in self:
            if not record.payment_id:
                record.duration_in_stage = 0.0
                continue
            
            # Find previous history record for same payment
            previous_record = self.search([
                ('payment_id', '=', record.payment_id.id),
                ('date_action', '<', record.date_action),
            ], order='date_action desc', limit=1)
            
            if previous_record:
                time_diff = record.date_action - previous_record.date_action
                record.duration_in_stage = time_diff.total_seconds() / 3600.0  # Convert to hours
            else:
                # First record - duration from payment creation
                if record.payment_id.create_date:
                    time_diff = record.date_action - record.payment_id.create_date
                    record.duration_in_stage = time_diff.total_seconds() / 3600.0
                else:
                    record.duration_in_stage = 0.0
    
    @api.model
    def log_approval_action(self, payment_id, stage_from, stage_to, action_type, comments=None):
        """
        Log an approval action for audit trail
        
        Args:
            payment_id (int): ID of the payment record
            stage_from (str): Previous stage
            stage_to (str): New stage  
            action_type (str): Type of action performed
            comments (str, optional): Additional comments
            
        Returns:
            payment.approval.history: Created history record
        """
        # Get request information for audit
        request = self.env.context.get('request')
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.httprequest.environ.get('REMOTE_ADDR')
            user_agent = request.httprequest.environ.get('HTTP_USER_AGENT')
        
        # Create history record
        history_record = self.create({
            'payment_id': payment_id,
            'stage_from': stage_from,
            'stage_to': stage_to,
            'action_type': action_type,
            'comments': comments,
            'ip_address': ip_address,
            'user_agent': user_agent,
        })
        
        return history_record
    
    @api.model
    def get_payment_audit_trail(self, payment_id):
        """
        Get complete audit trail for a payment
        
        Args:
            payment_id (int): Payment ID
            
        Returns:
            dict: Formatted audit trail data
        """
        history_records = self.search([
            ('payment_id', '=', payment_id)
        ], order='date_action')
        
        audit_trail = []
        for record in history_records:
            audit_trail.append({
                'id': record.id,
                'date': record.date_action,
                'user': record.user_id.name,
                'action': dict(record._fields['action_type'].selection)[record.action_type],
                'from_stage': dict(record._fields['stage_from'].selection)[record.stage_from],
                'to_stage': dict(record._fields['stage_to'].selection)[record.stage_to],
                'comments': record.comments,
                'duration': record.duration_in_stage,
                'ip_address': record.ip_address,
            })
        
        return {
            'total_records': len(audit_trail),
            'audit_trail': audit_trail,
        }
    
    def action_view_payment(self):
        """Action to view related payment"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def get_approval_statistics(self, date_from=None, date_to=None):
        """
        Get approval workflow statistics
        
        Args:
            date_from (date, optional): Start date for statistics
            date_to (date, optional): End date for statistics
            
        Returns:
            dict: Statistics data
        """
        domain = []
        if date_from:
            domain.append(('date_action', '>=', date_from))
        if date_to:
            domain.append(('date_action', '<=', date_to))
        
        records = self.search(domain)
        
        # Count by action type
        action_counts = {}
        for action_type, label in self._fields['action_type'].selection:
            action_counts[action_type] = records.filtered(
                lambda r: r.action_type == action_type
            ).mapped('id').__len__()
        
        # Average duration by stage
        stage_durations = {}
        for stage, label in self._fields['stage_from'].selection:
            stage_records = records.filtered(lambda r: r.stage_from == stage)
            if stage_records:
                avg_duration = sum(stage_records.mapped('duration_in_stage')) / len(stage_records)
                stage_durations[stage] = avg_duration
            else:
                stage_durations[stage] = 0.0
        
        # Most active users
        user_counts = {}
        for user in records.mapped('user_id'):
            user_records = records.filtered(lambda r: r.user_id.id == user.id)
            user_counts[user.name] = len(user_records)
        
        return {
            'total_actions': len(records),
            'action_counts': action_counts,
            'average_durations': stage_durations,
            'user_activity': user_counts,
            'date_range': {
                'from': date_from,
                'to': date_to,
            }
        }
