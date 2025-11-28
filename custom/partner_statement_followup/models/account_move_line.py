# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Statement and follow-up related fields
    followup_history_ids = fields.One2many(
        'res.partner.followup.history',
        'move_line_id',
        string='Follow-up History'
    )
    
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_days_overdue',
        store=True,
        help="Number of days past due date"
    )
    
    ageing_bucket = fields.Selection([
        ('current', 'Current'),
        ('1_30', '1-30 Days'),
        ('31_60', '31-60 Days'),
        ('61_90', '61-90 Days'),
        ('90_plus', '90+ Days')
    ], string='Ageing Bucket', compute='_compute_ageing_bucket', store=True)
    
    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_days_overdue',
        store=True
    )

    @api.depends('date_maturity')
    def _compute_days_overdue(self):
        """Compute days overdue and overdue status"""
        today = fields.Date.today()
        
        for line in self:
            if line.date_maturity and line.amount_residual != 0:
                if line.date_maturity < today:
                    line.days_overdue = (today - line.date_maturity).days
                    line.is_overdue = True
                else:
                    line.days_overdue = 0
                    line.is_overdue = False
            else:
                line.days_overdue = 0
                line.is_overdue = False

    @api.depends('days_overdue')
    def _compute_ageing_bucket(self):
        """Compute ageing bucket based on days overdue"""
        config = self.env['res.partner.statement.config'].get_company_config()
        
        for line in self:
            if line.days_overdue == 0:
                line.ageing_bucket = 'current'
            elif line.days_overdue <= config.ageing_bucket_1:
                line.ageing_bucket = '1_30'
            elif line.days_overdue <= config.ageing_bucket_2:
                line.ageing_bucket = '31_60'
            elif line.days_overdue <= config.ageing_bucket_3:
                line.ageing_bucket = '61_90'
            else:
                line.ageing_bucket = '90_plus'

    def action_quick_reconcile(self):
        """Quick reconcile action for statement view"""
        self.ensure_one()
        
        if self.reconciled:
            return True
        
        # Find matching lines for reconciliation
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('account_id', '=', self.account_id.id),
            ('reconciled', '=', False),
            ('id', '!=', self.id),
            ('amount_residual', '=', -self.amount_residual)
        ]
        
        matching_lines = self.search(domain, limit=1)
        
        if matching_lines:
            # Perform reconciliation
            lines_to_reconcile = self + matching_lines
            lines_to_reconcile.reconcile()
            return True
        
        return False

    def get_payment_references(self):
        """Get related payment references for this line"""
        self.ensure_one()
        
        # Get payment references from move
        payment_refs = []
        
        if self.move_id.payment_reference:
            payment_refs.append(self.move_id.payment_reference)
        
        if self.move_id.ref:
            payment_refs.append(self.move_id.ref)
        
        # Get payment lines if this is a payment
        if self.move_id.move_type == 'entry':
            payment_lines = self.move_id.line_ids.filtered(
                lambda l: l.account_id.account_type in ['asset_cash', 'liability_credit_card']
            )
            
            for line in payment_lines:
                if line.name and line.name not in payment_refs:
                    payment_refs.append(line.name)
        
        return payment_refs

    def get_followup_status(self):
        """Get follow-up status for this line"""
        self.ensure_one()
        
        if not self.followup_history_ids:
            return {
                'level': 0,
                'status': 'none',
                'last_date': False
            }
        
        latest_followup = self.followup_history_ids.sorted('followup_date', reverse=True)[0]
        
        return {
            'level': latest_followup.followup_level,
            'status': 'sent',
            'last_date': latest_followup.followup_date
        }

    @api.model
    def get_ageing_analysis(self, partner_ids=None, company_id=None):
        """Get ageing analysis for partners"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.env['res.partner.statement.config'].get_company_config(company_id)
        
        domain = [
            ('account_id.account_type', '=', 'asset_receivable'),
            ('reconciled', '=', False),
            ('amount_residual', '>', 0),
            ('company_id', '=', company_id)
        ]
        
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))
        
        lines = self.search(domain)
        
        # Group by partner
        partner_data = {}
        
        for line in lines:
            partner_id = line.partner_id.id
            
            if partner_id not in partner_data:
                partner_data[partner_id] = {
                    'partner': line.partner_id,
                    'current': 0.0,
                    'bucket_1': 0.0,
                    'bucket_2': 0.0,
                    'bucket_3': 0.0,
                    'bucket_4': 0.0,
                    'total': 0.0,
                    'lines': []
                }
            
            amount = line.amount_residual
            partner_data[partner_id]['total'] += amount
            partner_data[partner_id]['lines'].append(line)
            
            # Determine bucket
            if line.ageing_bucket == 'current':
                partner_data[partner_id]['current'] += amount
            elif line.ageing_bucket == '1_30':
                partner_data[partner_id]['bucket_1'] += amount
            elif line.ageing_bucket == '31_60':
                partner_data[partner_id]['bucket_2'] += amount
            elif line.ageing_bucket == '61_90':
                partner_data[partner_id]['bucket_3'] += amount
            else:
                partner_data[partner_id]['bucket_4'] += amount
        
        return list(partner_data.values())

    def action_view_move(self):
        """Action to view the related move"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Journal Entry'),
            'res_model': 'account.move',
            'res_id': self.move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
