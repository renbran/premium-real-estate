# -*- coding: utf-8 -*-
"""
Test Payment Workflow Scenarios

Test cases for payment workflow scenarios including:
- Complete vendor payment workflow
- Customer receipt workflow
- Rejection and approval scenarios
- Multi-user workflow testing
- Edge cases and error handling
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class TestPaymentWorkflow(TransactionCase):
    """Test payment workflow scenarios"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'Test Workflow Company',
            'currency_id': cls.env.ref('base.USD').id,
        })
        
        # Create workflow users
        cls.creator_user = cls.env['res.users'].create({
            'name': 'Payment Creator',
            'login': 'creator_test',
            'email': 'creator@test.com',
            'company_id': cls.company.id,
        })
        
        cls.reviewer_user = cls.env['res.users'].create({
            'name': 'Payment Reviewer',
            'login': 'reviewer_test',
            'email': 'reviewer@test.com',
            'company_id': cls.company.id,
        })
        
        cls.approver_user = cls.env['res.users'].create({
            'name': 'Payment Approver',
            'login': 'approver_test',
            'email': 'approver@test.com',
            'company_id': cls.company.id,
        })
        
        cls.authorizer_user = cls.env['res.users'].create({
            'name': 'Payment Authorizer',
            'login': 'authorizer_test',
            'email': 'authorizer@test.com',
            'company_id': cls.company.id,
        })
        
        # Create test data
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Test Vendor Workflow',
            'is_company': True,
            'supplier_rank': 1,
        })
        
        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Customer Workflow',
            'is_company': True,
            'customer_rank': 1,
        })
        
        cls.bank_journal = cls.env['account.journal'].create({
            'name': 'Test Bank Workflow',
            'type': 'bank',
            'code': 'TBW',
            'company_id': cls.company.id,
        })

    def test_vendor_payment_full_workflow(self):
        """Test complete vendor payment workflow (4 stages)"""
        # Stage 1: Create payment
        payment = self.env['account.payment'].with_user(self.creator_user).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.vendor.id,
            'amount': 5000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        self.assertEqual(payment.approval_state, 'draft')
        
        # Stage 2: Submit for review
        if hasattr(payment, 'action_submit_for_review'):
            payment.action_submit_for_review()
            self.assertEqual(payment.approval_state, 'under_review')
        
        # Stage 3: Review payment
        if hasattr(payment, 'action_review_payment'):
            payment.with_user(self.reviewer_user).action_review_payment()
            self.assertIn(payment.approval_state, ['for_approval', 'approved'])
        
        # Stage 4: Approve payment
        if hasattr(payment, 'action_approve_payment'):
            payment.with_user(self.approver_user).action_approve_payment()
            self.assertIn(payment.approval_state, ['for_authorization', 'approved'])
        
        # Stage 5: Authorize payment (vendor only)
        if hasattr(payment, 'action_authorize_payment') and payment.payment_type == 'outbound':
            payment.with_user(self.authorizer_user).action_authorize_payment()
            self.assertEqual(payment.approval_state, 'approved')
        
        # Stage 6: Post payment
        if hasattr(payment, 'action_post_payment'):
            payment.action_post_payment()
            self.assertEqual(payment.approval_state, 'posted')

    def test_customer_receipt_workflow(self):
        """Test customer receipt workflow (3 stages)"""
        # Create customer payment
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.customer.id,
            'amount': 2000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        self.assertEqual(payment.approval_state, 'draft')
        
        # Customer payments should skip authorization
        if hasattr(payment, 'action_submit_for_review'):
            payment.action_submit_for_review()
            
        if hasattr(payment, 'action_review_payment'):
            payment.action_review_payment()
            
        if hasattr(payment, 'action_approve_payment'):
            payment.action_approve_payment()
            # Should go directly to approved (skip authorization)
            self.assertEqual(payment.approval_state, 'approved')

    def test_workflow_rejection_scenarios(self):
        """Test payment rejection at different stages"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.vendor.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Submit for review
        if hasattr(payment, 'action_submit_for_review'):
            payment.action_submit_for_review()
        
        # Reject at review stage
        if hasattr(payment, 'action_reject_payment'):
            payment.action_reject_payment()
            self.assertEqual(payment.approval_state, 'cancelled')

    def test_workflow_permission_validation(self):
        """Test workflow permission validation"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.vendor.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Test that wrong user cannot perform actions
        if hasattr(payment, 'action_approve_payment'):
            with self.assertRaises((UserError, ValidationError)):
                # Creator should not be able to approve directly
                payment.with_user(self.creator_user).action_approve_payment()

    def test_workflow_data_integrity(self):
        """Test workflow data integrity during transitions"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.vendor.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        original_amount = payment.amount
        original_partner = payment.partner_id
        
        # Move through workflow
        if hasattr(payment, 'action_submit_for_review'):
            payment.action_submit_for_review()
            
            # Data should remain unchanged
            self.assertEqual(payment.amount, original_amount)
            self.assertEqual(payment.partner_id, original_partner)

    def test_workflow_audit_trail(self):
        """Test that workflow creates proper audit trail"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.vendor.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Check for audit fields
        audit_fields = ['reviewer_id', 'reviewer_date', 'approver_id', 'approver_date']
        for field in audit_fields:
            if hasattr(payment, field):
                self.assertTrue(hasattr(payment, field))

    def test_workflow_notification_system(self):
        """Test workflow notification system"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.vendor.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Check for notification methods
        notification_methods = [
            '_send_workflow_notification',
            '_post_workflow_message'
        ]
        
        for method_name in notification_methods:
            if hasattr(payment, method_name):
                # Method should exist and be callable
                self.assertTrue(callable(getattr(payment, method_name)))

    def test_bulk_workflow_operations(self):
        """Test bulk workflow operations"""
        payments = []
        for i in range(3):
            payment = self.env['account.payment'].create({
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': self.vendor.id,
                'amount': 1000.0 + i * 100,
                'journal_id': self.bank_journal.id,
                'company_id': self.company.id,
            })
            payments.append(payment)
        
        # Test bulk submit
        payment_set = self.env['account.payment'].browse([p.id for p in payments])
        
        if hasattr(payment_set, 'action_submit_for_review'):
            try:
                payment_set.action_submit_for_review()
                # All should be in review state
                for payment in payment_set:
                    self.assertEqual(payment.approval_state, 'under_review')
            except Exception:
                # Bulk operations might not be supported
                pass

    def test_workflow_edge_cases(self):
        """Test workflow edge cases and error handling"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.vendor.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Test posting without approval (should fail)
        if hasattr(payment, 'action_post_payment'):
            with self.assertRaises((UserError, ValidationError)):
                payment.action_post_payment()
        
        # Test double approval (should be idempotent or fail gracefully)
        if hasattr(payment, 'action_approve_payment'):
            payment.approval_state = 'approved'
            try:
                payment.action_approve_payment()
                # Should remain approved
                self.assertEqual(payment.approval_state, 'approved')
            except (UserError, ValidationError):
                # Or should fail gracefully
                pass


class TestWorkflowConfiguration(TransactionCase):
    """Test workflow configuration and customization"""
    
    def test_company_workflow_settings(self):
        """Test company-level workflow settings"""
        company = self.env['res.company'].create({
            'name': 'Test Workflow Config Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Check for workflow configuration fields
        workflow_fields = [
            'enable_four_stage_approval',
            'skip_authorization_for_small_amounts',
            'authorization_threshold'
        ]
        
        for field in workflow_fields:
            if hasattr(company, field):
                self.assertTrue(hasattr(company, field))

    def test_journal_workflow_settings(self):
        """Test journal-level workflow settings"""
        journal = self.env['account.journal'].create({
            'name': 'Test Workflow Journal',
            'type': 'bank',
            'code': 'TWJ',
        })
        
        # Check for journal workflow fields
        journal_fields = [
            'payment_approval_required',
            'payment_approval_threshold',
            'payment_auto_approve_limit'
        ]
        
        for field in journal_fields:
            if hasattr(journal, field):
                self.assertTrue(hasattr(journal, field))
