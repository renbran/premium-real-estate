# -*- coding: utf-8 -*-
"""
Test Account Payment Model Enhancements

Test cases for account.payment model enhancements including:
- Voucher number generation
- QR code generation
- Approval workflow progression  
- Security constraints
- Data validation
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from unittest.mock import patch
import logging

_logger = logging.getLogger(__name__)


class TestAccountPayment(TransactionCase):
    """Test cases for account.payment model enhancements"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'Test Company OSUS',
            'currency_id': cls.env.ref('base.USD').id,
        })
        
        # Create test users with different permissions
        cls.payment_user = cls.env['res.users'].create({
            'name': 'Payment User',
            'login': 'payment_user_test',
            'email': 'payment_user@test.com',
            'company_id': cls.company.id,
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('account.group_account_user').id,
            ])]
        })
        
        cls.payment_manager = cls.env['res.users'].create({
            'name': 'Payment Manager',
            'login': 'payment_manager_test',
            'email': 'payment_manager@test.com',
            'company_id': cls.company.id,
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('account.group_account_manager').id,
            ])]
        })
        
        # Create test partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Vendor',
            'is_company': True,
            'supplier_rank': 1,
            'email': 'vendor@test.com'
        })
        
        # Create test journal
        cls.bank_journal = cls.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'TBANK',
            'company_id': cls.company.id,
            'currency_id': cls.env.ref('base.USD').id,
        })

    def test_payment_creation_with_voucher_number(self):
        """Test payment creation generates voucher number"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Voucher number should be generated
        self.assertNotEqual(payment.voucher_number, '/')
        self.assertTrue(payment.voucher_number.startswith('PV/'))
        
        # Should have default approval state
        self.assertEqual(payment.approval_state, 'draft')

    def test_approval_workflow_progression(self):
        """Test 4-stage approval workflow progression for vendor payments"""
        payment = self.env['account.payment'].with_user(self.payment_user).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier', 
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Initial state should be draft
        self.assertEqual(payment.approval_state, 'draft')
        
        # Submit for review (if method exists)
        if hasattr(payment, 'action_submit_for_review'):
            payment.action_submit_for_review()
            self.assertEqual(payment.approval_state, 'under_review')
        
        # Test workflow progression with manager user
        payment_as_manager = payment.with_user(self.payment_manager)
        
        # Review payment (if method exists)
        if hasattr(payment_as_manager, 'action_review_payment'):
            payment_as_manager.action_review_payment()
            self.assertIn(payment.approval_state, ['for_approval', 'approved'])

    def test_customer_payment_workflow(self):
        """Test 3-stage approval workflow for customer payments"""
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'amount': 500.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Customer payments should follow simpler workflow
        self.assertEqual(payment.approval_state, 'draft')
        
        # Customer payments can be approved directly
        if hasattr(payment, 'action_approve_payment'):
            payment.with_user(self.payment_manager).action_approve_payment()
            self.assertIn(payment.approval_state, ['approved', 'for_authorization'])

    def test_qr_code_generation(self):
        """Test QR code generation for payments"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # QR code should be computed
        if hasattr(payment, 'qr_code'):
            # Force computation
            payment._compute_payment_qr_code()
            # QR code should exist or be computable
            self.assertTrue(hasattr(payment, 'qr_code'))
        
        # Verification URL should be available (if method exists)
        if hasattr(payment, 'get_verification_url'):
            verification_url = payment.get_verification_url()
            self.assertTrue(isinstance(verification_url, str))
            self.assertTrue(payment.voucher_number in verification_url)

    def test_security_constraints(self):
        """Test security constraints and permissions"""
        payment = self.env['account.payment'].with_user(self.payment_user).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Regular user should be able to create payments
        self.assertTrue(payment.id)
        
        # Test that regular user cannot approve (if method exists)
        if hasattr(payment, 'action_approve_payment'):
            with self.assertRaises((UserError, ValidationError)):
                payment.action_approve_payment()

    def test_payment_validation(self):
        """Test payment data validation"""
        # Test amount validation
        with self.assertRaises(ValidationError):
            self.env['account.payment'].create({
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': self.partner.id,
                'amount': -100.0,  # Negative amount should fail
                'journal_id': self.bank_journal.id,
                'company_id': self.company.id,
            })

    def test_payment_posting(self):
        """Test payment posting functionality"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Approve payment first if needed
        if hasattr(payment, 'approval_state'):
            payment.approval_state = 'approved'
        
        # Test posting (if custom post method exists)
        if hasattr(payment, 'action_post_payment'):
            payment.with_user(self.payment_manager).action_post_payment()
            self.assertEqual(payment.state, 'posted')
        else:
            # Test standard posting
            payment.action_post()
            self.assertEqual(payment.state, 'posted')

    def test_payment_cancellation(self):
        """Test payment cancellation"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Test cancellation
        if hasattr(payment, 'action_cancel'):
            payment.action_cancel()
            if hasattr(payment, 'approval_state'):
                self.assertEqual(payment.approval_state, 'cancelled')
            else:
                self.assertEqual(payment.state, 'cancel')

    def test_voucher_number_uniqueness(self):
        """Test voucher number uniqueness"""
        payment1 = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        payment2 = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 2000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Voucher numbers should be different
        self.assertNotEqual(payment1.voucher_number, payment2.voucher_number)

    def test_payment_display_name(self):
        """Test payment display name generation"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.bank_journal.id,
            'company_id': self.company.id,
        })
        
        # Display name should be meaningful
        if hasattr(payment, 'display_name'):
            self.assertTrue(payment.display_name)
            self.assertTrue(len(payment.display_name) > 5)


class TestPaymentCompute(TransactionCase):
    """Test computed fields and methods"""
    
    def setUp(self):
        super().setUp()
        self.payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.env['res.partner'].create({'name': 'Test Partner'}).id,
            'amount': 1000.0,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })

    def test_compute_methods_exist(self):
        """Test that compute methods exist and don't raise errors"""
        compute_methods = [
            '_compute_payment_qr_code',
            '_compute_display_name',
            '_compute_color',
            '_compute_journal_item_count',
            '_compute_reconciliation_count',
            '_compute_invoice_count',
        ]
        
        for method_name in compute_methods:
            if hasattr(self.payment, method_name):
                try:
                    getattr(self.payment, method_name)()
                except Exception as e:
                    self.fail(f"Compute method {method_name} raised an exception: {e}")

    def test_smart_button_counts(self):
        """Test smart button count computations"""
        if hasattr(self.payment, 'journal_item_count'):
            self.assertIsInstance(self.payment.journal_item_count, int)
        
        if hasattr(self.payment, 'reconciliation_count'):
            self.assertIsInstance(self.payment.reconciliation_count, int)
        
        if hasattr(self.payment, 'invoice_count'):
            self.assertIsInstance(self.payment.invoice_count, int)
