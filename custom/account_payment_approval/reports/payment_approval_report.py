# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools


class PaymentApprovalReport(models.Model):
    """Payment Approval Analysis Report"""
    _name = 'payment.approval.report'
    _description = 'Payment Approval Analysis'
    _auto = False
    _rec_name = 'payment_id'
    
    payment_id = fields.Many2one('account.payment', string='Payment', readonly=True)
    payment_name = fields.Char(string='Payment Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    amount = fields.Monetary(string='Amount', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True)
    payment_date = fields.Date(string='Payment Date', readonly=True)
    voucher_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('authorized', 'Authorized'),
        ('posted', 'Posted'),
        ('rejected', 'Rejected')
    ], string='Approval State', readonly=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('sent', 'Sent'),
        ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled')
    ], string='Payment State', readonly=True)
    
    create_date = fields.Datetime(string='Created On', readonly=True)
    submission_date = fields.Datetime(string='Submitted On', readonly=True)
    approval_date = fields.Datetime(string='Approved On', readonly=True)
    authorization_date = fields.Datetime(string='Authorized On', readonly=True)
    rejection_date = fields.Datetime(string='Rejected On', readonly=True)
    
    create_uid = fields.Many2one('res.users', string='Created By', readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    authorized_by = fields.Many2one('res.users', string='Authorized By', readonly=True)
    rejected_by = fields.Many2one('res.users', string='Rejected By', readonly=True)
    
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)
    rejection_category = fields.Char(string='Rejection Category', readonly=True)
    
    processing_days = fields.Integer(string='Processing Days', readonly=True)
    approval_days = fields.Integer(string='Days to Approval', readonly=True)
    authorization_days = fields.Integer(string='Days to Authorization', readonly=True)
    
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        """Initialize the report view"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    ap.id as id,
                    ap.id as payment_id,
                    ap.name as payment_name,
                    ap.partner_id,
                    ap.amount,
                    ap.currency_id,
                    ap.journal_id,
                    ap.date as payment_date,
                    ap.voucher_state,
                    ap.state,
                    ap.create_date,
                    ap.submission_date,
                    ap.approval_date,
                    ap.authorization_date,
                    ap.rejection_date,
                    ap.create_uid,
                    ap.approved_by,
                    ap.authorized_by,
                    ap.rejected_by,
                    ap.rejection_reason,
                    ap.rejection_category,
                    ap.company_id,
                    CASE 
                        WHEN ap.authorization_date IS NOT NULL THEN 
                            EXTRACT(days FROM ap.authorization_date - ap.create_date)
                        WHEN ap.approval_date IS NOT NULL THEN 
                            EXTRACT(days FROM ap.approval_date - ap.create_date)
                        WHEN ap.rejection_date IS NOT NULL THEN 
                            EXTRACT(days FROM ap.rejection_date - ap.create_date)
                        ELSE NULL
                    END as processing_days,
                    CASE 
                        WHEN ap.approval_date IS NOT NULL THEN 
                            EXTRACT(days FROM ap.approval_date - ap.submission_date)
                        ELSE NULL
                    END as approval_days,
                    CASE 
                        WHEN ap.authorization_date IS NOT NULL THEN 
                            EXTRACT(days FROM ap.authorization_date - ap.approval_date)
                        ELSE NULL
                    END as authorization_days
                FROM account_payment ap
                WHERE ap.voucher_state IS NOT NULL
            )
        """ % self._table)


class PaymentApprovalPerformanceReport(models.Model):
    """Payment Approval Performance Report"""
    _name = 'payment.approval.performance.report'
    _description = 'Payment Approval Performance Analysis'
    _auto = False
    
    user_id = fields.Many2one('res.users', string='User', readonly=True)
    total_payments = fields.Integer(string='Total Payments', readonly=True)
    approved_payments = fields.Integer(string='Approved Payments', readonly=True)
    rejected_payments = fields.Integer(string='Rejected Payments', readonly=True)
    authorized_payments = fields.Integer(string='Authorized Payments', readonly=True)
    avg_approval_time = fields.Float(string='Avg Approval Time (Days)', readonly=True)
    avg_authorization_time = fields.Float(string='Avg Authorization Time (Days)', readonly=True)
    total_amount_approved = fields.Monetary(string='Total Amount Approved', readonly=True)
    total_amount_authorized = fields.Monetary(string='Total Amount Authorized', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    approval_rate = fields.Float(string='Approval Rate (%)', readonly=True)
    month = fields.Selection([
        ('01', 'January'), ('02', 'February'), ('03', 'March'),
        ('04', 'April'), ('05', 'May'), ('06', 'June'),
        ('07', 'July'), ('08', 'August'), ('09', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December')
    ], string='Month', readonly=True)
    year = fields.Char(string='Year', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        """Initialize the performance report view"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                WITH approval_stats AS (
                    SELECT
                        COALESCE(ap.approved_by, ap.authorized_by, ap.rejected_by) as user_id,
                        EXTRACT(month FROM ap.create_date) as month,
                        EXTRACT(year FROM ap.create_date) as year,
                        ap.company_id,
                        ap.currency_id,
                        COUNT(*) as total_payments,
                        COUNT(CASE WHEN ap.voucher_state = 'approved' THEN 1 END) as approved_payments,
                        COUNT(CASE WHEN ap.voucher_state = 'rejected' THEN 1 END) as rejected_payments,
                        COUNT(CASE WHEN ap.voucher_state = 'authorized' THEN 1 END) as authorized_payments,
                        AVG(CASE 
                            WHEN ap.approval_date IS NOT NULL AND ap.submission_date IS NOT NULL THEN 
                                EXTRACT(days FROM ap.approval_date - ap.submission_date)
                            ELSE NULL
                        END) as avg_approval_time,
                        AVG(CASE 
                            WHEN ap.authorization_date IS NOT NULL AND ap.approval_date IS NOT NULL THEN 
                                EXTRACT(days FROM ap.authorization_date - ap.approval_date)
                            ELSE NULL
                        END) as avg_authorization_time,
                        SUM(CASE WHEN ap.voucher_state = 'approved' THEN ap.amount ELSE 0 END) as total_amount_approved,
                        SUM(CASE WHEN ap.voucher_state = 'authorized' THEN ap.amount ELSE 0 END) as total_amount_authorized
                    FROM account_payment ap
                    WHERE ap.voucher_state IS NOT NULL
                    AND (ap.approved_by IS NOT NULL OR ap.authorized_by IS NOT NULL OR ap.rejected_by IS NOT NULL)
                    GROUP BY 
                        COALESCE(ap.approved_by, ap.authorized_by, ap.rejected_by),
                        EXTRACT(month FROM ap.create_date),
                        EXTRACT(year FROM ap.create_date),
                        ap.company_id,
                        ap.currency_id
                )
                SELECT
                    ROW_NUMBER() OVER () as id,
                    user_id,
                    total_payments,
                    approved_payments,
                    rejected_payments,
                    authorized_payments,
                    avg_approval_time,
                    avg_authorization_time,
                    total_amount_approved,
                    total_amount_authorized,
                    currency_id,
                    CASE 
                        WHEN total_payments > 0 THEN 
                            (approved_payments + authorized_payments) * 100.0 / total_payments
                        ELSE 0
                    END as approval_rate,
                    LPAD(month::text, 2, '0') as month,
                    year::text as year,
                    company_id
                FROM approval_stats
            )
        """ % self._table)
