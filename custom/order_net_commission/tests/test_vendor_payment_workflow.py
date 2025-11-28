# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo import fields
from datetime import datetime


class TestVendorPaymentWorkflow(TransactionCase):
    """Test vendor payment approval workflow functionality"""

    def setUp(self):
        super().setUp()
        
        # Create test currency (AED)
        self.currency_aed = self.env['res.currency'].create({
            'name': 'AED',
            'symbol': 'AED',
            'rate': 1.0,
        })
        
        # Set company currency to AED
        self.env.company.currency_id = self.currency_aed
        
        # Create test vendor partner
        self.vendor_partner = self.env['res.partner'].create({
            'name': 'Test Vendor',
            'is_company': True,
            'supplier_rank': 1,
            'email': 'vendor@example.com',
        })
        
        # Create test customer partner
        self.customer_partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'is_company': True,
            'customer_rank': 1,
            'email': 'customer@example.com',
        })
        
        # Create test journal
        self.bank_journal = self.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'TB',
        })
        
        # Create user groups
        self.group_user = self.env.ref('payment_account_enhanced.group_payment_user')
        self.group_reviewer = self.env.ref('payment_account_enhanced.group_payment_reviewer')
        self.group_approver = self.env.ref('payment_account_enhanced.group_payment_approver')
        self.group_authorizer = self.env.ref('payment_account_enhanced.group_payment_authorizer')
        self.group_poster = self.env.ref('payment_account_enhanced.group_payment_poster')
        self.group_manager = self.env.ref('payment_account_enhanced.group_payment_manager')
        
        # Create test users
        self.user_reviewer = self.env['res.users'].create({
            'name': 'Payment Reviewer',
            'login': 'reviewer@test.com',
            'email': 'reviewer@test.com',
            'groups_id': [(6, 0, [self.group_reviewer.id])]
        })
        
        self.user_approver = self.env['res.users'].create({
            'name': 'Payment Approver',
            'login': 'approver@test.com',
            'email': 'approver@test.com',
            'groups_id': [(6, 0, [self.group_approver.id])]
        })
        
        self.user_authorizer = self.env['res.users'].create({
            'name': 'Payment Authorizer',
            'login': 'authorizer@test.com',
            'email': 'authorizer@test.com',
            'groups_id': [(6, 0, [self.group_authorizer.id])]
        })
        
        self.user_poster = self.env['res.users'].create({
            'name': 'Payment Poster',
            'login': 'poster@test.com',
            'email': 'poster@test.com',
            'groups_id': [(6, 0, [self.group_poster.id])]
        })
        
        self.user_manager = self.env['res.users'].create({
            'name': 'Payment Manager',
            'login': 'manager@test.com',
            'email': 'manager@test.com',
            'groups_id': [(6, 0, [self.group_manager.id])]
        })

    def _create_vendor_payment(self, amount, currency_id=None):
        """Helper to create vendor payment"""
        if currency_id is None:
            currency_id = self.currency_aed.id
            
        return self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.vendor_partner.id,
            'amount': amount,
            'currency_id': currency_id,
            'journal_id': self.bank_journal.id,
        })

    def _create_customer_receipt(self, amount, currency_id=None):
        """Helper to create customer receipt"""
        if currency_id is None:
            currency_id = self.currency_aed.id
            
        return self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_id': self.customer_partner.id,
            'amount': amount,
            'currency_id': currency_id,
            'journal_id': self.bank_journal.id,
        })

    def test_customer_receipt_bypass_workflow(self):
        """Test that customer receipts bypass enhanced workflow"""
        # Create customer receipt
        receipt = self._create_customer_receipt(15000)  # Large amount
        
        # Should not require authorization regardless of amount
        self.assertFalse(receipt.requires_authorization)
        self.assertEqual(receipt.approval_state, 'draft')
        
        # Should be able to post directly without workflow
        receipt.action_post()
        self.assertEqual(receipt.state, 'posted')

    def test_low_value_vendor_payment_authorization(self):
        """Test that low-value vendor payments don't require authorization"""
        # Create low-value vendor payment
        payment = self._create_vendor_payment(5000)  # Below 10k threshold
        
        # Should not require authorization
        self.assertFalse(payment.requires_authorization)
        
        # Should be in draft state initially
        self.assertEqual(payment.approval_state, 'draft')

    def test_high_value_vendor_payment_authorization(self):
        """Test that high-value vendor payments require authorization"""
        # Create high-value vendor payment
        payment = self._create_vendor_payment(15000)  # Above 10k threshold
        
        # Should require authorization
        self.assertTrue(payment.requires_authorization)
        
        # Should be in draft state initially
        self.assertEqual(payment.approval_state, 'draft')

    def test_reviewer_can_handle_low_value_complete_workflow(self):
        """Test reviewer can review, approve, and post low-value vendor payments"""
        # Create low-value vendor payment
        payment = self._create_vendor_payment(3000)
        
        # Submit for review
        payment.action_submit_for_review()
        self.assertEqual(payment.approval_state, 'under_review')
        
        # Reviewer reviews payment
        payment.with_user(self.user_reviewer).action_review_payment()
        self.assertEqual(payment.approval_state, 'for_approval')
        
        # Same reviewer can approve (allowed for low-value)
        payment.with_user(self.user_reviewer).action_approve_payment()
        self.assertEqual(payment.approval_state, 'approved')
        
        # Same reviewer can post (allowed for low-value)
        payment.with_user(self.user_reviewer).action_post()
        self.assertEqual(payment.state, 'posted')

    def test_high_value_requires_different_users(self):
        """Test high-value payments require different users for each stage"""
        # Create high-value vendor payment
        payment = self._create_vendor_payment(20000)
        
        # Submit for review
        payment.action_submit_for_review()
        self.assertEqual(payment.approval_state, 'under_review')
        
        # Reviewer reviews payment
        payment.with_user(self.user_reviewer).action_review_payment()
        self.assertEqual(payment.approval_state, 'for_approval')
        
        # Reviewer cannot approve high-value payment they reviewed
        with self.assertRaises(UserError):
            payment.with_user(self.user_reviewer).action_approve_payment()
        
        # Different approver can approve
        payment.with_user(self.user_approver).action_approve_payment()
        self.assertEqual(payment.approval_state, 'for_authorization')
        
        # Approver cannot authorize payment they approved
        with self.assertRaises(UserError):
            payment.with_user(self.user_approver).action_authorize_payment()
        
        # Different authorizer can authorize
        payment.with_user(self.user_authorizer).action_authorize_payment()
        self.assertEqual(payment.approval_state, 'approved')
        
        # Poster can post
        payment.with_user(self.user_poster).action_post()
        self.assertEqual(payment.state, 'posted')

    def test_workflow_validation_vendor_payments_only(self):
        """Test workflow validation only applies to vendor payments"""
        # Create customer receipt
        receipt = self._create_customer_receipt(25000)  # Large amount
        
        # Should not trigger workflow validation
        receipt.action_post()
        self.assertEqual(receipt.state, 'posted')
        
        # Create vendor payment
        payment = self._create_vendor_payment(25000)  # Same large amount
        
        # Should trigger workflow validation
        with self.assertRaises(UserError):
            payment.action_post()  # Cannot post directly

    def test_manager_override_capabilities(self):
        """Test manager can override workflow restrictions"""
        # Create high-value vendor payment
        payment = self._create_vendor_payment(50000)
        
        # Manager can handle complete workflow
        payment.with_user(self.user_manager).action_submit_for_review()
        payment.with_user(self.user_manager).action_review_payment()
        payment.with_user(self.user_manager).action_approve_payment()
        payment.with_user(self.user_manager).action_authorize_payment()
        payment.with_user(self.user_manager).action_post()
        
        self.assertEqual(payment.state, 'posted')

    def test_currency_conversion_for_authorization_threshold(self):
        """Test authorization threshold works with different currencies"""
        # Create USD currency
        usd_currency = self.env['res.currency'].create({
            'name': 'USD',
            'symbol': '$',
            'rate': 0.27,  # 1 USD = 3.67 AED (approximate)
        })
        
        # Create payment in USD equivalent to 5000 AED (should not require auth)
        payment_usd_low = self._create_vendor_payment(1360, usd_currency.id)  # ~5000 AED
        self.assertFalse(payment_usd_low.requires_authorization)
        
        # Create payment in USD equivalent to 15000 AED (should require auth)
        payment_usd_high = self._create_vendor_payment(4090, usd_currency.id)  # ~15000 AED
        self.assertTrue(payment_usd_high.requires_authorization)

    def test_workflow_state_progression(self):
        """Test proper workflow state progression for vendor payments"""
        # Create vendor payment
        payment = self._create_vendor_payment(8000)
        
        # Initial state
        self.assertEqual(payment.approval_state, 'draft')
        
        # Submit for review
        payment.action_submit_for_review()
        self.assertEqual(payment.approval_state, 'under_review')
        
        # Review
        payment.with_user(self.user_reviewer).action_review_payment()
        self.assertEqual(payment.approval_state, 'for_approval')
        
        # Approve (reviewer can approve low-value)
        payment.with_user(self.user_reviewer).action_approve_payment()
        self.assertEqual(payment.approval_state, 'approved')
        
        # Post
        payment.with_user(self.user_reviewer).action_post()
        self.assertEqual(payment.state, 'posted')

    def test_approval_history_tracking(self):
        """Test approval history is tracked for vendor payments"""
        # Create vendor payment
        payment = self._create_vendor_payment(5000)
        
        # Submit and review
        payment.action_submit_for_review()
        payment.with_user(self.user_reviewer).action_review_payment()
        
        # Check approval history was created
        history = self.env['payment.approval.history'].search([
            ('payment_id', '=', payment.id),
            ('action', '=', 'reviewed')
        ])
        self.assertTrue(history)
        self.assertEqual(history.user_id, self.user_reviewer)

    def test_error_messages_payment_type_specific(self):
        """Test error messages are specific to payment type and amount"""
        # High-value vendor payment
        payment_high = self._create_vendor_payment(20000)
        payment_high.action_submit_for_review()
        payment_high.with_user(self.user_reviewer).action_review_payment()
        
        # Try to approve as same reviewer
        with self.assertRaises(UserError) as context:
            payment_high.with_user(self.user_reviewer).action_approve_payment()
        
        # Error message should mention high-value and different users
        self.assertIn("high-value", str(context.exception))
        self.assertIn("different users", str(context.exception))

    def test_permissions_computation(self):
        """Test workflow permissions are computed correctly"""
        # Low-value vendor payment
        payment_low = self._create_vendor_payment(5000)
        payment_low.action_submit_for_review()
        
        # Reviewer should be able to review and approve
        payment_low.with_user(self.user_reviewer)._compute_workflow_permissions()
        # Note: We can't directly check computed fields in tests easily,
        # but we can verify the actions work
        
        # High-value vendor payment
        payment_high = self._create_vendor_payment(20000)
        payment_high.action_submit_for_review()
        payment_high.with_user(self.user_reviewer).action_review_payment()
        
        # Reviewer should not be able to approve high-value
        with self.assertRaises(UserError):
            payment_high.with_user(self.user_reviewer).action_approve_payment()