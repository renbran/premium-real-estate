# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Billing Information
    billing_ids = fields.One2many('medical.billing', 'partner_id', 'Medical Billings')
    billing_count = fields.Integer('Billing Count', compute='_compute_billing_count')
    payment_ids = fields.One2many('medical.payment', 'partner_id', 'Payments')
    payment_count = fields.Integer('Payment Count', compute='_compute_payment_count')
    
    # Financial Information
    total_billed = fields.Monetary('Total Billed', compute='_compute_financial_info', currency_field='currency_id')
    total_paid = fields.Monetary('Total Paid', compute='_compute_financial_info', currency_field='currency_id')
    outstanding_balance = fields.Monetary('Outstanding Balance', compute='_compute_financial_info', currency_field='currency_id')
    
    # Billing Preferences
    preferred_payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
    ], 'Preferred Payment Method')
    
    billing_address_same = fields.Boolean('Billing Address Same as Contact', default=True)
    billing_street = fields.Char('Billing Street')
    billing_street2 = fields.Char('Billing Street2')
    billing_city = fields.Char('Billing City')
    billing_state_id = fields.Many2one('res.country.state', 'Billing State')
    billing_zip = fields.Char('Billing Zip')
    billing_country_id = fields.Many2one('res.country', 'Billing Country')
    
    # Insurance Information
    primary_insurance_id = fields.Many2one('medical.insurance', 'Primary Insurance')
    secondary_insurance_id = fields.Many2one('medical.insurance', 'Secondary Insurance')
    insurance_member_id = fields.Char('Insurance Member ID')
    insurance_group_id = fields.Char('Insurance Group ID')
    
    # Credit Management
    credit_limit = fields.Monetary('Credit Limit', currency_field='currency_id')
    payment_terms = fields.Many2one('account.payment.term', 'Payment Terms')
    
    @api.depends('billing_ids')
    def _compute_billing_count(self):
        for partner in self:
            partner.billing_count = len(partner.billing_ids)
    
    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for partner in self:
            partner.payment_count = len(partner.payment_ids)
    
    @api.depends('billing_ids.total_amount', 'billing_ids.paid_amount')
    def _compute_financial_info(self):
        for partner in self:
            billings = partner.billing_ids.filtered(lambda b: b.state != 'cancel')
            partner.total_billed = sum(billings.mapped('total_amount'))
            partner.total_paid = sum(billings.mapped('paid_amount'))
            partner.outstanding_balance = partner.total_billed - partner.total_paid
    
    def action_view_billings(self):
        """View partner's medical billings"""
        action = self.env.ref('hms_billing.action_medical_billing').read()[0]
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action
    
    def action_view_payments(self):
        """View partner's payments"""
        action = self.env.ref('hms_billing.action_medical_payment').read()[0]
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action
    
    def get_billing_address(self):
        """Get billing address formatted"""
        if self.billing_address_same:
            return self.contact_address
        else:
            address_parts = []
            if self.billing_street:
                address_parts.append(self.billing_street)
            if self.billing_street2:
                address_parts.append(self.billing_street2)
            
            city_part = []
            if self.billing_city:
                city_part.append(self.billing_city)
            if self.billing_state_id:
                city_part.append(self.billing_state_id.name)
            if self.billing_zip:
                city_part.append(self.billing_zip)
            
            if city_part:
                address_parts.append(', '.join(city_part))
            
            if self.billing_country_id:
                address_parts.append(self.billing_country_id.name)
            
            return '\n'.join(address_parts)