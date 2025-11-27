# models/account_journal.py
from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    enable_payment_verification = fields.Boolean(
        string="Enable Payment Verification",
        default=True,
        help="Enable QR verification for payments in this journal"
    )
    
    payment_approval_required = fields.Boolean(
        string='Require Payment Approval',
        default=True,
        help="Require approval workflow for payments in this journal"
    )

# models/res_partner.py
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    payment_count = fields.Integer(
        string="Payment Count",
        compute='_compute_payment_count',
        help="Total number of payments with this partner"
    )
    
    @api.depends('name')
    def _compute_payment_count(self):
        for partner in self:
            partner.payment_count = self.env['account.payment'].search_count([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['posted', 'sent', 'reconciled'])
            ])
    
    def action_view_partner_payments(self):
        """View payments for this partner"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payments for %s') % self.display_name,
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

# models/payment_workflow_stage.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PaymentWorkflowStage(models.Model):
    _name = 'payment.workflow.stage'
    _description = 'Payment Workflow Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    code = fields.Char(string='Stage Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description', translate=True)
    
    is_initial_stage = fields.Boolean(string='Initial Stage')
    is_final_stage = fields.Boolean(string='Final Stage')
    allow_edit = fields.Boolean(string='Allow Edit', default=True)
    require_approval = fields.Boolean(string='Require Approval')
    
    approval_group_ids = fields.Many2many('res.groups', string='Approval Groups')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    @api.constrains('is_initial_stage')
    def _check_single_initial_stage(self):
        for record in self:
            if record.is_initial_stage:
                existing = self.search([
                    ('is_initial_stage', '=', True),
                    ('company_id', '=', record.company_id.id),
                    ('id', '!=', record.id),
                ])
                if existing:
                    raise ValidationError(_("Only one initial stage allowed per company"))

# models/account_payment_register.py
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    force_approval_workflow = fields.Boolean(
        string='Force Approval Workflow',
        default=True,
        help="Force payments through approval workflow"
    )
    
    remarks = fields.Text(string='Remarks/Memo')

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        if self.remarks:
            payment_vals['remarks'] = self.remarks
            
        # Force approval workflow for invoice payments
        active_model = self.env.context.get('active_model')
        if active_model == 'account.move' and self.force_approval_workflow:
            payment_vals.update({
                'approval_state': 'draft',
                'state': 'draft',
                'verification_status': 'pending'
            })
        
        return payment_vals

    def _create_payments(self):
        payments = super()._create_payments()
        
        # Ensure approval workflow for created payments
        for payment in payments:
            if hasattr(payment, 'approval_state') and payment.approval_state != 'draft':
                payment.approval_state = 'draft'
            if payment.state != 'draft':
                payment.state = 'draft'
            
            payment.message_post(
                body=_("Payment created from invoice/bill. Approval workflow required before posting.")
            )
        
        return payments
