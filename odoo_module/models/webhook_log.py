# -*- coding: utf-8 -*-
"""
Webhook Log Model
=================

This model tracks all webhook requests and their processing results.
It provides comprehensive logging for monitoring, debugging, and auditing
the bill automation system.

Features:
- Request/response logging
- Status tracking (processing, success, failed)
- IP address and user agent tracking
- Error message storage
- Automatic cleanup of old logs
- Search and filtering capabilities
- Performance metrics

Author: Bill Automation Project Team
"""

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import json


class WebhookLog(models.Model):
    """Log entries for webhook requests and processing results"""
    
    _name = 'webhook.log'
    _description = 'Webhook Processing Log'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # Basic Information
    display_name = fields.Char(
        string='Log Entry',
        compute='_compute_display_name',
        store=True
    )
    
    status = fields.Selection([
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], string='Status', default='processing', required=True)
    
    # Request Data
    request_data = fields.Text(
        string='Request Data',
        help='JSON data received in the webhook request'
    )
    
    response_data = fields.Text(
        string='Response Data',
        help='JSON data sent back in the response'
    )
    
    # Processing Information
    bill_id = fields.Many2one(
        'account.move',
        string='Created Bill',
        ondelete='set null',
        help='The bill that was created from this webhook request'
    )
    
    vendor_name = fields.Char(
        string='Vendor Name',
        compute='_compute_request_fields',
        store=True
    )
    
    bill_amount = fields.Float(
        string='Bill Amount',
        compute='_compute_request_fields',
        store=True
    )
    
    invoice_date = fields.Date(
        string='Invoice Date',
        compute='_compute_request_fields',
        store=True
    )
    
    # Error Information
    error_message = fields.Text(
        string='Error Message',
        help='Detailed error message if processing failed'
    )
    
    # Network Information
    ip_address = fields.Char(
        string='IP Address',
        help='IP address of the client that sent the request'
    )
    
    user_agent = fields.Char(
        string='User Agent',
        help='User agent of the client that sent the request'
    )
    
    # Timestamps
    processing_time = fields.Float(
        string='Processing Time (seconds)',
        help='Time taken to process the request',
        compute='_compute_processing_time',
        store=True
    )
    
    # Computed Fields for Dashboard
    is_recent = fields.Boolean(
        string='Recent (24h)',
        compute='_compute_is_recent'
    )
    
    # Colors for kanban view
    color = fields.Integer(
        string='Color',
        compute='_compute_color'
    )

    @api.depends('create_date', 'write_date', 'status')
    def _compute_processing_time(self):
        """Calculate processing time"""
        for record in self:
            if record.create_date and record.write_date and record.status != 'processing':
                delta = record.write_date - record.create_date
                record.processing_time = delta.total_seconds()
            else:
                record.processing_time = 0.0

    @api.depends('status', 'vendor_name', 'create_date')
    def _compute_display_name(self):
        """Generate display name for the log entry"""
        for record in self:
            if record.vendor_name:
                vendor_part = f" - {record.vendor_name}"
            else:
                vendor_part = ""
            
            create_time = ""
            if record.create_date:
                create_time = record.create_date.strftime('%Y-%m-%d %H:%M:%S')
            
            status_icon = {
                'processing': '🔄',
                'success': '✅',
                'failed': '❌'
            }.get(record.status, '')
            
            record.display_name = f"{status_icon} {create_time}{vendor_part}"

    @api.depends('request_data')
    def _compute_request_fields(self):
        """Extract fields from request JSON data"""
        for record in self:
            record.vendor_name = ''
            record.bill_amount = 0.0
            record.invoice_date = False
            
            if record.request_data:
                try:
                    data = json.loads(record.request_data)
                    record.vendor_name = data.get('vendor_name', '')
                    record.bill_amount = float(data.get('amount', 0))
                    
                    if data.get('invoice_date'):
                        try:
                            record.invoice_date = fields.Date.from_string(data.get('invoice_date'))
                        except:
                            pass
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass

    @api.depends('create_date')
    def _compute_is_recent(self):
        """Check if log entry is from last 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        for record in self:
            record.is_recent = record.create_date and record.create_date >= cutoff

    @api.depends('status')
    def _compute_color(self):
        """Set color for kanban view based on status"""
        color_map = {
            'processing': 4,  # Blue
            'success': 10,    # Green
            'failed': 1,      # Red
        }
        for record in self:
            record.color = color_map.get(record.status, 0)

    def action_view_bill(self):
        """Open the created bill"""
        if self.bill_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': self.bill_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def action_retry_processing(self):
        """Retry processing failed webhook"""
        if self.status == 'failed' and self.request_data:
            try:
                # Re-trigger webhook processing
                # This would call the webhook controller again
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('Retry functionality would be implemented here'),
                        'type': 'info',
                    }
                }
            except Exception as e:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('Retry failed: %s') % str(e),
                        'type': 'danger',
                    }
                }

    @api.model
    def cleanup_old_logs(self, days=30):
        """Clean up log entries older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_logs = self.search([('create_date', '<', cutoff_date)])
        
        if old_logs:
            count = len(old_logs)
            old_logs.unlink()
            return count
        
        return 0

    @api.model
    def get_statistics(self):
        """Get processing statistics for dashboard"""
        # Last 24 hours
        last_24h = datetime.now() - timedelta(hours=24)
        recent_logs = self.search([('create_date', '>=', last_24h)])
        
        # Last 7 days
        last_7d = datetime.now() - timedelta(days=7)
        week_logs = self.search([('create_date', '>=', last_7d)])
        
        # All time
        all_logs = self.search([])
        
        def get_stats(logs):
            total = len(logs)
            success = len(logs.filtered(lambda l: l.status == 'success'))
            failed = len(logs.filtered(lambda l: l.status == 'failed'))
            processing = len(logs.filtered(lambda l: l.status == 'processing'))
            
            return {
                'total': total,
                'success': success,
                'failed': failed,
                'processing': processing,
                'success_rate': round((success / total * 100) if total > 0 else 0, 1)
            }
        
        return {
            'last_24h': get_stats(recent_logs),
            'last_7d': get_stats(week_logs),
            'all_time': get_stats(all_logs)
        }

    @api.model
    def get_recent_failures(self, limit=10):
        """Get recent failed webhook attempts for troubleshooting"""
        failed_logs = self.search([
            ('status', '=', 'failed')
        ], limit=limit)
        
        failures = []
        for log in failed_logs:
            failures.append({
                'id': log.id,
                'date': log.create_date,
                'vendor_name': log.vendor_name,
                'error_message': log.error_message,
                'ip_address': log.ip_address,
            })
        
        return failures

    @api.model
    def get_performance_metrics(self):
        """Get performance metrics for monitoring"""
        logs = self.search([('status', '!=', 'processing')])
        
        if not logs:
            return {
                'avg_processing_time': 0,
                'max_processing_time': 0,
                'min_processing_time': 0,
                'total_processed': 0
            }
        
        processing_times = [log.processing_time for log in logs if log.processing_time > 0]
        
        return {
            'avg_processing_time': round(sum(processing_times) / len(processing_times), 2) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'total_processed': len(logs)
        }

    # Scheduled Actions
    @api.model
    def _cron_cleanup_old_logs(self):
        """Scheduled cleanup of old log entries"""
        cleaned = self.cleanup_old_logs(days=30)
        if cleaned > 0:
            # Log the cleanup activity
            self.env['ir.logging'].sudo().create({
                'name': 'webhook.log',
                'level': 'INFO',
                'message': f'Cleaned up {cleaned} old webhook log entries',
                'func': '_cron_cleanup_old_logs',
                'line': '1',
            })

    @api.model
    def _cron_check_stuck_processing(self):
        """Check for webhook requests stuck in processing state"""
        # Find requests stuck in processing for more than 5 minutes
        cutoff = datetime.now() - timedelta(minutes=5)
        stuck_logs = self.search([
            ('status', '=', 'processing'),
            ('create_date', '<', cutoff)
        ])
        
        if stuck_logs:
            # Mark them as failed
            stuck_logs.write({
                'status': 'failed',
                'error_message': 'Request timeout - stuck in processing state'
            })
            
            # Log the issue
            self.env['ir.logging'].sudo().create({
                'name': 'webhook.log',
                'level': 'WARNING',
                'message': f'Found {len(stuck_logs)} stuck webhook requests, marked as failed',
                'func': '_cron_check_stuck_processing',
                'line': '1',
            })