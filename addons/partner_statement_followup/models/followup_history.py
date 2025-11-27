# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FollowupHistory(models.Model):
    _name = 'res.partner.followup.history'
    _description = 'Partner Follow-up History'
    _order = 'followup_date desc'
    _rec_name = 'display_name'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
        help="Related journal item if follow-up was for specific transaction"
    )
    
    followup_level = fields.Integer(
        string='Follow-up Level',
        required=True,
        help="Level of follow-up (1, 2, 3, etc.)"
    )
    
    followup_date = fields.Date(
        string='Follow-up Date',
        required=True,
        default=fields.Date.context_today,
        index=True
    )
    
    template_id = fields.Many2one(
        'mail.template',
        string='Email Template Used',
        help="Email template that was used for this follow-up"
    )
    
    balance_due = fields.Monetary(
        string='Balance Due at Time',
        currency_field='company_currency_id',
        help="Outstanding balance when follow-up was sent"
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Sent By',
        required=True,
        default=lambda self: self.env.user
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )
    
    method = fields.Selection([
        ('email', 'Email'),
        ('manual', 'Manual'),
        ('print', 'Print'),
        ('sms', 'SMS')
    ], string='Method', default='email', required=True)
    
    email_sent = fields.Boolean(
        string='Email Sent',
        default=False,
        help="Whether the email was successfully sent"
    )
    
    notes = fields.Text(
        string='Notes',
        help="Additional notes or comments about this follow-up"
    )
    
    # Related mail message for tracking
    mail_message_id = fields.Many2one(
        'mail.message',
        string='Related Message',
        help="Mail message created when sending this follow-up"
    )
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('partner_id', 'followup_level', 'followup_date')
    def _compute_display_name(self):
        """Compute display name for follow-up history"""
        for record in self:
            record.display_name = _("Level %s - %s (%s)") % (
                record.followup_level,
                record.partner_id.name,
                record.followup_date
            )

    def action_view_email(self):
        """View the sent email message"""
        self.ensure_one()
        
        if not self.mail_message_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Follow-up Email'),
            'res_model': 'mail.message',
            'res_id': self.mail_message_id.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_resend_followup(self):
        """Resend this follow-up"""
        self.ensure_one()
        
        if not self.template_id:
            return False
        
        # Send email using the same template
        self.template_id.send_mail(self.partner_id.id, force_send=True)
        
        # Create new history record
        new_history = self.copy({
            'followup_date': fields.Date.today(),
            'user_id': self.env.user.id,
            'balance_due': self.partner_id.balance_due_company_currency,
            'notes': _("Resent from previous follow-up")
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Follow-up History'),
            'res_model': 'res.partner.followup.history',
            'res_id': new_history.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def get_followup_statistics(self, date_from=None, date_to=None, company_id=None):
        """Get follow-up statistics for reporting"""
        if not company_id:
            company_id = self.env.company.id
        
        domain = [('company_id', '=', company_id)]
        
        if date_from:
            domain.append(('followup_date', '>=', date_from))
        
        if date_to:
            domain.append(('followup_date', '<=', date_to))
        
        # Get statistics by level
        stats = {}
        
        for level in range(1, 4):  # Levels 1, 2, 3
            level_domain = domain + [('followup_level', '=', level)]
            level_records = self.search(level_domain)
            
            stats[f'level_{level}'] = {
                'count': len(level_records),
                'total_balance': sum(level_records.mapped('balance_due')),
                'unique_partners': len(level_records.mapped('partner_id')),
                'email_success_rate': (
                    len(level_records.filtered('email_sent')) / len(level_records) * 100
                    if level_records else 0
                )
            }
        
        # Overall statistics
        all_records = self.search(domain)
        stats['overall'] = {
            'total_followups': len(all_records),
            'total_balance': sum(all_records.mapped('balance_due')),
            'unique_partners': len(all_records.mapped('partner_id')),
            'methods': {
                method: len(all_records.filtered(lambda r: r.method == method))
                for method in ['email', 'manual', 'print', 'sms']
            }
        }
        
        return stats

    def action_bulk_resend(self):
        """Bulk resend follow-ups"""
        for record in self:
            if record.template_id:
                record.action_resend_followup()

    @api.model
    def cleanup_old_history(self, days_to_keep=365):
        """Clean up old follow-up history records"""
        cutoff_date = fields.Date.subtract(fields.Date.today(), days=days_to_keep)
        
        old_records = self.search([
            ('followup_date', '<', cutoff_date),
            ('partner_id.balance_due_company_currency', '=', 0)  # Only for partners with no balance
        ])
        
        count = len(old_records)
        old_records.unlink()
        
        return count
