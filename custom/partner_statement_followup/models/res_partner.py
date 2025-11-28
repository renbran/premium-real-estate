# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Follow-up fields
    balance_due_company_currency = fields.Monetary(
        string='Balance Due',
        compute='_compute_balance_due_company_currency',
        currency_field='company_currency_id',
        help="Total amount due in company currency"
    )
    
    statement_ids = fields.One2many(
        'res.partner.followup.history',
        'partner_id',
        string='Follow-up History'
    )
    
    current_followup_level = fields.Integer(
        string='Current Follow-up Level',
        default=0,
        help="Current follow-up level (0 = no follow-up)"
    )
    
    last_followup_date = fields.Date(
        string='Last Follow-up Date',
        help="Date of last follow-up action"
    )
    
    next_followup_date = fields.Date(
        string='Next Follow-up Date',
        compute='_compute_next_followup_date',
        store=True,
        help="Calculated next follow-up date"
    )
    
    followup_blocked = fields.Boolean(
        string='Block Follow-up',
        default=False,
        help="Block automatic follow-up for this partner"
    )
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    @api.depends('credit', 'debit')
    def _compute_balance_due_company_currency(self):
        """Compute balance due in company currency"""
        for partner in self:
            domain = [
                ('partner_id', '=', partner.id),
                ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
                ('reconciled', '=', False),
                ('company_id', '=', self.env.company.id)
            ]
            
            lines = self.env['account.move.line'].search(domain)
            balance = sum(lines.mapped('amount_residual'))
            
            # Only consider positive balances (amounts owed to us)
            partner.balance_due_company_currency = max(balance, 0.0)

    @api.depends('last_followup_date', 'current_followup_level')
    def _compute_next_followup_date(self):
        """Compute next follow-up date based on configuration"""
        config = self.env['res.partner.statement.config'].get_company_config()
        
        for partner in self:
            if (partner.followup_blocked or 
                partner.current_followup_level >= config.max_followup_level or
                partner.balance_due_company_currency <= 0):
                partner.next_followup_date = False
                continue
                
            if partner.last_followup_date:
                next_date = partner.last_followup_date
                days_to_add = config.days_between_levels
                partner.next_followup_date = fields.Date.add(next_date, days=days_to_add)
            else:
                # First follow-up based on oldest overdue invoice
                oldest_line = self.env['account.move.line'].search([
                    ('partner_id', '=', partner.id),
                    ('account_id.account_type', '=', 'asset_receivable'),
                    ('reconciled', '=', False),
                    ('amount_residual', '>', 0),
                    ('date_maturity', '<', fields.Date.today())
                ], order='date_maturity asc', limit=1)
                
                if oldest_line:
                    days_overdue = (fields.Date.today() - oldest_line.date_maturity).days
                    if days_overdue >= config.ageing_bucket_1:
                        partner.next_followup_date = fields.Date.today()
                    else:
                        partner.next_followup_date = False
                else:
                    partner.next_followup_date = False

    def action_send_followup(self):
        """Send follow-up email for this partner"""
        self.ensure_one()
        
        if self.followup_blocked:
            raise UserError(_("Follow-up is blocked for this partner."))
        
        config = self.env['res.partner.statement.config'].get_company_config()
        
        if self.current_followup_level >= config.max_followup_level:
            raise UserError(_("Maximum follow-up level reached for this partner."))
        
        # Increment follow-up level
        new_level = self.current_followup_level + 1
        
        # Get appropriate mail template
        template = self._get_followup_template(new_level)
        
        if not template:
            raise UserError(_("No mail template configured for follow-up level %s") % new_level)
        
        # Send email
        template.send_mail(self.id, force_send=True)
        
        # Update partner
        self.write({
            'current_followup_level': new_level,
            'last_followup_date': fields.Date.today()
        })
        
        # Create history record
        self.env['res.partner.followup.history'].create({
            'partner_id': self.id,
            'followup_level': new_level,
            'followup_date': fields.Date.today(),
            'template_id': template.id,
            'balance_due': self.balance_due_company_currency,
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
        })
        
        return True

    def _get_followup_template(self, level):
        """Get mail template for specific follow-up level"""
        template_mapping = {
            1: 'partner_statement_followup.followup_level_1_template',
            2: 'partner_statement_followup.followup_level_2_template',
            3: 'partner_statement_followup.followup_level_3_template',
        }
        
        template_xmlid = template_mapping.get(level)
        if template_xmlid:
            return self.env.ref(template_xmlid, raise_if_not_found=False)
        
        return False

    def action_reset_followup(self):
        """Reset follow-up level to 0"""
        self.write({
            'current_followup_level': 0,
            'last_followup_date': False
        })

    def action_open_statement_wizard(self):
        """Open statement wizard for this partner"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner Statement'),
            'res_model': 'statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_company_id': self.env.company.id,
            }
        }

    @api.model
    def _cron_partner_followup_check(self):
        """Cron job to check and send automatic follow-ups"""
        config = self.env['res.partner.statement.config'].get_company_config()
        
        if not config.auto_followup:
            return
        
        # Find partners due for follow-up
        domain = [
            ('is_company', '=', True),
            ('followup_blocked', '=', False),
            ('balance_due_company_currency', '>', 0),
            ('next_followup_date', '<=', fields.Date.today()),
            ('current_followup_level', '<', config.max_followup_level)
        ]
        
        partners = self.search(domain)
        
        for partner in partners:
            try:
                partner.action_send_followup()
                _logger.info("Automatic follow-up sent to partner %s", partner.name)
            except Exception as e:
                _logger.error("Failed to send follow-up to partner %s: %s", partner.name, str(e))

    def get_statement_data(self):
        """Get statement data for this partner"""
        self.ensure_one()
        
        config = self.env['res.partner.statement.config'].get_company_config()
        
        # Get all unreconciled receivable lines
        domain = [
            ('partner_id', '=', self.id),
            ('account_id.account_type', '=', 'asset_receivable'),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0),
            ('company_id', '=', self.env.company.id)
        ]
        
        lines = self.env['account.move.line'].search(domain, order='date_maturity asc')
        
        # Calculate ageing buckets
        today = fields.Date.today()
        ageing_data = {
            'current': 0.0,
            'bucket_1': 0.0,  # 1-30 days
            'bucket_2': 0.0,  # 31-60 days
            'bucket_3': 0.0,  # 61-90 days
            'bucket_4': 0.0,  # 90+ days
            'total': 0.0
        }
        
        for line in lines:
            amount = line.amount_residual
            ageing_data['total'] += amount
            
            if line.date_maturity > today:
                ageing_data['current'] += amount
            else:
                days_overdue = (today - line.date_maturity).days
                if days_overdue <= config.ageing_bucket_1:
                    ageing_data['bucket_1'] += amount
                elif days_overdue <= config.ageing_bucket_2:
                    ageing_data['bucket_2'] += amount
                elif days_overdue <= config.ageing_bucket_3:
                    ageing_data['bucket_3'] += amount
                else:
                    ageing_data['bucket_4'] += amount
        
        return {
            'lines': lines,
            'ageing': ageing_data,
            'config': config
        }
