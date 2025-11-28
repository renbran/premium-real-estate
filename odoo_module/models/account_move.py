# -*- coding: utf-8 -*-
"""
Account Move Extension for Bill Automation
==========================================

Extends the account.move model to add webhook-related functionality
and track bills created via automation.

Features:
- Webhook origin tracking
- Automation metadata
- Enhanced duplicate detection
- Custom actions for automated bills

Author: Bill Automation Project Team
"""

from odoo import models, fields, api, _


class AccountMove(models.Model):
    """Extension of account.move for webhook integration"""
    
    _inherit = 'account.move'

    # Webhook Integration Fields
    created_by_webhook = fields.Boolean(
        string='Created by Webhook',
        default=False,
        help='Indicates if this bill was created via webhook automation'
    )
    
    webhook_log_id = fields.Many2one(
        'webhook.log',
        string='Webhook Log',
        ondelete='set null',
        help='The webhook log entry that created this bill'
    )
    
    automation_metadata = fields.Text(
        string='Automation Metadata',
        help='JSON metadata from the automation process'
    )
    
    original_file_name = fields.Char(
        string='Original File Name',
        help='Original filename from the webhook request'
    )
    
    automation_confidence = fields.Float(
        string='Automation Confidence',
        help='Confidence score of the automated data extraction (0-100)',
        default=0.0
    )

    # Display Fields
    automation_source = fields.Char(
        string='Automation Source',
        compute='_compute_automation_source',
        store=True,
        help='Source system that created this bill'
    )
    
    needs_review = fields.Boolean(
        string='Needs Review',
        compute='_compute_needs_review',
        store=True,
        help='Indicates if this automated bill needs manual review'
    )

    @api.depends('created_by_webhook', 'automation_metadata')
    def _compute_automation_source(self):
        """Determine the automation source"""
        for record in self:
            if record.created_by_webhook:
                if record.automation_metadata:
                    try:
                        import json
                        metadata = json.loads(record.automation_metadata)
                        record.automation_source = metadata.get('source', 'Webhook')
                    except (json.JSONDecodeError, TypeError):
                        record.automation_source = 'Webhook'
                else:
                    record.automation_source = 'Webhook'
            else:
                record.automation_source = 'Manual'

    @api.depends('automation_confidence', 'created_by_webhook')
    def _compute_needs_review(self):
        """Determine if bill needs manual review"""
        for record in self:
            if record.created_by_webhook:
                # Bills with low confidence or missing key data need review
                record.needs_review = (
                    record.automation_confidence < 85.0 or
                    not record.partner_id or
                    record.amount_total <= 0
                )
            else:
                record.needs_review = False

    def action_mark_reviewed(self):
        """Mark bill as reviewed"""
        self.write({'needs_review': False})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Bill marked as reviewed'),
                'type': 'success',
            }
        }

    def action_view_webhook_log(self):
        """View the webhook log that created this bill"""
        if self.webhook_log_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'webhook.log',
                'res_id': self.webhook_log_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    @api.model
    def get_automated_bills_stats(self):
        """Get statistics about automated bills"""
        # Total automated bills
        automated_bills = self.search([('created_by_webhook', '=', True)])
        
        # Recent automated bills (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_automated = automated_bills.filtered(
            lambda b: b.create_date >= week_ago
        )
        
        # Bills needing review
        needs_review = automated_bills.filtered('needs_review')
        
        return {
            'total_automated': len(automated_bills),
            'recent_automated': len(recent_automated),
            'needs_review': len(needs_review),
            'automation_rate': round(
                (len(automated_bills) / len(self.search([])) * 100) 
                if self.search([]) else 0, 1
            )
        }

    def _prepare_webhook_metadata(self, request_data, confidence=0.0):
        """Prepare automation metadata from webhook request"""
        import json
        from datetime import datetime
        
        metadata = {
            'source': 'Bill Automation Webhook',
            'created_at': datetime.now().isoformat(),
            'confidence': confidence,
            'original_data': request_data,
            'processing_info': {
                'vendor_auto_created': False,
                'file_attached': False,
                'ocr_used': True if request_data.get('file_url') else False
            }
        }
        
        return json.dumps(metadata, indent=2)

    @api.model
    def create_from_webhook(self, webhook_data, webhook_log=None):
        """
        Create bill from webhook data with proper tracking
        
        This method should be used instead of regular create()
        when creating bills from webhook automation.
        """
        # Extract bill creation data
        bill_vals = webhook_data.get('bill_vals', {})
        
        # Add webhook tracking fields
        bill_vals.update({
            'created_by_webhook': True,
            'webhook_log_id': webhook_log.id if webhook_log else False,
            'original_file_name': webhook_data.get('file_name', ''),
            'automation_confidence': webhook_data.get('confidence', 0.0),
            'automation_metadata': self._prepare_webhook_metadata(
                webhook_data, webhook_data.get('confidence', 0.0)
            )
        })
        
        # Create the bill
        bill = self.create(bill_vals)
        
        # Update webhook log with created bill
        if webhook_log:
            webhook_log.write({'bill_id': bill.id})
        
        return bill