# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError


class MedicalInsuranceClaim(models.Model):
    _name = 'medical.insurance.claim'
    _description = 'Medical Insurance Claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'claim_date desc'

    name = fields.Char('Claim Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    billing_id = fields.Many2one('medical.billing', 'Billing', required=True)
    patient_id = fields.Many2one('medical.patient', related='billing_id.patient_id', string='Patient', store=True)
    insurance_id = fields.Many2one('medical.insurance', 'Insurance', required=True)
    
    claim_date = fields.Date('Claim Date', required=True, default=fields.Date.today)
    service_date_from = fields.Date('Service Date From')
    service_date_to = fields.Date('Service Date To')
    
    # Claim Details
    claim_amount = fields.Monetary('Claim Amount', required=True, currency_field='currency_id')
    approved_amount = fields.Monetary('Approved Amount', currency_field='currency_id')
    paid_amount = fields.Monetary('Paid Amount', currency_field='currency_id')
    rejected_amount = fields.Monetary('Rejected Amount', currency_field='currency_id')
    currency_id = fields.Many2one(related='billing_id.currency_id', store=True)
    
    # Status and Processing
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('partial_approved', 'Partially Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], 'Status', default='draft', tracking=True)
    
    # External References
    insurance_claim_number = fields.Char('Insurance Claim Number')
    authorization_number = fields.Char('Authorization Number')
    
    # Dates
    submission_date = fields.Date('Submission Date')
    response_date = fields.Date('Response Date')
    payment_date = fields.Date('Payment Date')
    
    # Additional Information
    diagnosis_codes = fields.Text('Diagnosis Codes')
    procedure_codes = fields.Text('Procedure Codes')
    notes = fields.Text('Notes')
    rejection_reason = fields.Text('Rejection Reason')
    
    # Attachments
    claim_document_ids = fields.One2many('ir.attachment', 'res_id', 
                                        domain=[('res_model', '=', 'medical.insurance.claim')],
                                        string='Claim Documents')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.insurance.claim') or _('New')
        return super(MedicalInsuranceClaim, self).create(vals)

    def action_submit(self):
        """Submit claim to insurance"""
        self.write({
            'state': 'submitted',
            'submission_date': fields.Date.today()
        })
        return True

    def action_approve(self):
        """Approve claim"""
        self.write({
            'state': 'approved',
            'response_date': fields.Date.today(),
            'approved_amount': self.claim_amount
        })
        return True

    def action_partial_approve(self):
        """Partially approve claim"""
        self.write({
            'state': 'partial_approved',
            'response_date': fields.Date.today()
        })
        return True

    def action_reject(self):
        """Reject claim"""
        self.write({
            'state': 'rejected',
            'response_date': fields.Date.today(),
            'rejected_amount': self.claim_amount
        })
        return True

    def action_mark_paid(self):
        """Mark claim as paid"""
        if not self.paid_amount:
            self.paid_amount = self.approved_amount
        
        self.write({
            'state': 'paid',
            'payment_date': fields.Date.today()
        })
        
        # Create payment record in billing
        if self.billing_id and self.paid_amount:
            self.env['medical.payment'].create({
                'billing_id': self.billing_id.id,
                'amount': self.paid_amount,
                'payment_method': 'insurance',
                'payment_date': self.payment_date,
                'reference': self.name,
                'notes': f'Insurance payment for claim {self.name}',
                'state': 'posted'
            })
        return True

    def action_cancel(self):
        """Cancel claim"""
        self.write({'state': 'cancelled'})
        return True


class MedicalInsurance(models.Model):
    _inherit = 'medical.insurance'

    # Add claim tracking
    claim_ids = fields.One2many('medical.insurance.claim', 'insurance_id', 'Claims')
    claim_count = fields.Integer('Claim Count', compute='_compute_claim_count')
    
    # Insurance processing information
    contact_person = fields.Char('Contact Person')
    contact_phone = fields.Char('Contact Phone')
    contact_email = fields.Char('Contact Email')
    claim_submission_method = fields.Selection([
        ('online', 'Online Portal'),
        ('email', 'Email'),
        ('fax', 'Fax'),
        ('mail', 'Postal Mail'),
    ], 'Claim Submission Method')
    
    processing_time_days = fields.Integer('Processing Time (Days)')
    auto_approval_limit = fields.Monetary('Auto Approval Limit', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id)

    @api.depends('claim_ids')
    def _compute_claim_count(self):
        for insurance in self:
            insurance.claim_count = len(insurance.claim_ids)

    def action_view_claims(self):
        """View insurance claims"""
        action = self.env.ref('hms_billing.action_medical_insurance_claim').read()[0]
        action['domain'] = [('insurance_id', '=', self.id)]
        action['context'] = {'default_insurance_id': self.id}
        return action