# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BatchFollowupWizard(models.TransientModel):
    _name = 'batch.followup.wizard'
    _description = 'Batch Follow-up Wizard'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    followup_level = fields.Selection([
        ('1', 'Level 1 - Friendly Reminder'),
        ('2', 'Level 2 - Urgent Notice'),
        ('3', 'Level 3 - Final Notice'),
        ('auto', 'Automatic (Next Level)')
    ], string='Follow-up Level', default='auto', required=True)
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        domain=[('is_company', '=', True)],
        help="Leave empty to process all eligible partners"
    )
    
    min_balance = fields.Monetary(
        string='Minimum Balance',
        default=1.0,
        currency_field='currency_id',
        help="Only process partners with balance above this amount"
    )
    
    overdue_days = fields.Integer(
        string='Minimum Overdue Days',
        default=1,
        help="Only process partners with invoices overdue by this many days"
    )
    
    preview_mode = fields.Boolean(
        string='Preview Mode',
        default=True,
        help="Generate preview without sending emails"
    )
    
    exclude_blocked = fields.Boolean(
        string='Exclude Blocked Partners',
        default=True,
        help="Exclude partners with follow-up blocked"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id'
    )
    
    # Results
    eligible_partner_ids = fields.One2many(
        'batch.followup.partner',
        'wizard_id',
        string='Eligible Partners',
        readonly=True
    )
    
    total_partners = fields.Integer(
        string='Total Partners',
        readonly=True
    )
    
    total_balance = fields.Monetary(
        string='Total Balance',
        currency_field='currency_id',
        readonly=True
    )

    @api.onchange('company_id', 'followup_level', 'min_balance', 'overdue_days', 'exclude_blocked')
    def _onchange_refresh_partners(self):
        """Refresh eligible partners when criteria changes"""
        self._compute_eligible_partners()

    def _compute_eligible_partners(self):
        """Compute list of eligible partners for follow-up"""
        if not self.company_id:
            return
        
        config = self.env['res.partner.statement.config'].get_company_config(self.company_id.id)
        
        # Base domain for partners
        domain = [
            ('is_company', '=', True),
            ('balance_due_company_currency', '>=', self.min_balance),
            ('company_id', '=', self.company_id.id)
        ]
        
        if self.exclude_blocked:
            domain.append(('followup_blocked', '=', False))
        
        if self.partner_ids:
            domain.append(('id', 'in', self.partner_ids.ids))
        
        # Additional filters based on follow-up level
        if self.followup_level == 'auto':
            # Partners due for next follow-up
            domain.extend([
                ('next_followup_date', '<=', fields.Date.today()),
                ('current_followup_level', '<', config.max_followup_level)
            ])
        else:
            # Specific level - check if partner qualifies
            level = int(self.followup_level)
            if level == 1:
                # Level 1: Partners with no previous follow-up and overdue invoices
                domain.append(('current_followup_level', '=', 0))
            else:
                # Higher levels: Partners at previous level
                domain.append(('current_followup_level', '=', level - 1))
        
        partners = self.env['res.partner'].search(domain)
        
        # Additional filtering based on overdue days
        eligible_partners = []
        total_balance = 0.0
        
        for partner in partners:
            # Check if partner has invoices overdue by minimum days
            overdue_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('account_id.account_type', '=', 'asset_receivable'),
                ('reconciled', '=', False),
                ('amount_residual', '>', 0),
                ('days_overdue', '>=', self.overdue_days)
            ])
            
            if overdue_lines:
                next_level = self._get_next_followup_level(partner)
                eligible_partners.append({
                    'partner_id': partner.id,
                    'current_level': partner.current_followup_level,
                    'next_level': next_level,
                    'balance_due': partner.balance_due_company_currency,
                    'days_overdue': max(overdue_lines.mapped('days_overdue')),
                    'last_followup': partner.last_followup_date,
                })
                total_balance += partner.balance_due_company_currency
        
        # Clear existing lines and create new ones
        self.eligible_partner_ids.unlink()
        
        lines = [(0, 0, vals) for vals in eligible_partners]
        self.eligible_partner_ids = lines
        self.total_partners = len(eligible_partners)
        self.total_balance = total_balance

    def _get_next_followup_level(self, partner):
        """Get next follow-up level for partner"""
        if self.followup_level == 'auto':
            return min(partner.current_followup_level + 1, 3)
        else:
            return int(self.followup_level)

    def action_preview_followup(self):
        """Preview follow-up without sending"""
        self._compute_eligible_partners()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Batch Follow-up Preview'),
            'res_model': 'batch.followup.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context, preview_mode=True),
        }

    def action_send_followup(self):
        """Send follow-up emails to all eligible partners"""
        if not self.eligible_partner_ids:
            raise UserError(_("No eligible partners found for follow-up"))
        
        success_count = 0
        error_count = 0
        errors = []
        
        for line in self.eligible_partner_ids:
            if not line.selected:
                continue
            
            try:
                partner = line.partner_id
                
                # Set the follow-up level
                if self.followup_level != 'auto':
                    level = int(self.followup_level)
                    partner.current_followup_level = level - 1  # Will be incremented in action_send_followup
                
                # Send follow-up
                partner.action_send_followup()
                success_count += 1
                _logger.info("Follow-up sent to partner %s", partner.name)
                
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                errors.append(f"{line.partner_id.name}: {error_msg}")
                _logger.error("Failed to send follow-up to partner %s: %s", line.partner_id.name, error_msg)
        
        # Show results
        message = _("Follow-up process completed:\n")
        message += _("Success: %d partners\n") % success_count
        
        if error_count > 0:
            message += _("Errors: %d partners\n") % error_count
            message += _("Error details:\n") + "\n".join(errors[:10])  # Show first 10 errors
            if len(errors) > 10:
                message += _("\n... and %d more errors") % (len(errors) - 10)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Batch Follow-up Results"),
                'message': message,
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': True,
            }
        }

    def action_select_all(self):
        """Select all eligible partners"""
        self.eligible_partner_ids.write({'selected': True})

    def action_deselect_all(self):
        """Deselect all partners"""
        self.eligible_partner_ids.write({'selected': False})

    def action_generate_statements(self):
        """Generate statements for selected partners"""
        selected_partners = self.eligible_partner_ids.filtered('selected')
        
        if not selected_partners:
            raise UserError(_("No partners selected"))
        
        partner_ids = selected_partners.mapped('partner_id.id')
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner Statements'),
            'res_model': 'statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_company_id': self.company_id.id,
                'batch_mode': True,
                'partner_ids': partner_ids,
            }
        }


class BatchFollowupPartner(models.TransientModel):
    _name = 'batch.followup.partner'
    _description = 'Batch Follow-up Partner Line'
    _order = 'balance_due desc'

    wizard_id = fields.Many2one(
        'batch.followup.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True
    )
    
    selected = fields.Boolean(
        string='Selected',
        default=True
    )
    
    current_level = fields.Integer(
        string='Current Level'
    )
    
    next_level = fields.Integer(
        string='Next Level'
    )
    
    balance_due = fields.Monetary(
        string='Balance Due',
        currency_field='currency_id'
    )
    
    days_overdue = fields.Integer(
        string='Max Days Overdue'
    )
    
    last_followup = fields.Date(
        string='Last Follow-up'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='wizard_id.currency_id'
    )

    def action_view_partner(self):
        """View partner form"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': self.partner_id.name,
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_statement(self):
        """View partner statement"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner Statement'),
            'res_model': 'statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_company_id': self.wizard_id.company_id.id,
            }
        }
