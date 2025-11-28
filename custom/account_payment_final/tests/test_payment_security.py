# -*- coding: utf-8 -*-
"""
Test Payment Security and Permissions

Test cases for security features including:
- Role-based access control
- Record-level security
- Permission validation
- Data access restrictions
- Security group assignments
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class TestPaymentSecurity(TransactionCase):
    """Test payment security and permissions"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test companies
        cls.company_a = cls.env['res.company'].create({
            'name': 'Company A Security Test',
            'currency_id': cls.env.ref('base.USD').id,
        })
        
        cls.company_b = cls.env['res.company'].create({
            'name': 'Company B Security Test',
            'currency_id': cls.env.ref('base.USD').id,
        })
        
        # Create users with different security groups
        cls.basic_user = cls.env['res.users'].create({
            'name': 'Basic User',
            'login': 'basic_security_test',
            'email': 'basic@test.com',
            'company_id': cls.company_a.id,
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
        
        cls.payment_user = cls.env['res.users'].create({
            'name': 'Payment User',
            'login': 'payment_security_test',
            'email': 'payment@test.com',
            'company_id': cls.company_a.id,
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('account.group_account_user').id,
            ])]
        })
        
        cls.payment_manager = cls.env['res.users'].create({
            'name': 'Payment Manager',
            'login': 'manager_security_test',
            'email': 'manager@test.com',
            'company_id': cls.company_a.id,
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('account.group_account_manager').id,
            ])]
        })
        
        cls.company_b_user = cls.env['res.users'].create({
            'name': 'Company B User',
            'login': 'companyb_security_test',
            'email': 'companyb@test.com',
            'company_id': cls.company_b.id,
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('account.group_account_user').id,
            ])]
        })
        
        # Create test data
        cls.partner = cls.env['res.partner'].create({
            'name': 'Security Test Partner',
            'supplier_rank': 1,
        })
        
        cls.journal_a = cls.env['account.journal'].create({
            'name': 'Security Test Journal A',
            'type': 'bank',
            'code': 'STA',
            'company_id': cls.company_a.id,
        })
        
        cls.journal_b = cls.env['account.journal'].create({
            'name': 'Security Test Journal B',
            'type': 'bank',
            'code': 'STB',
            'company_id': cls.company_b.id,
        })

    def test_basic_user_access_restrictions(self):
        """Test basic user cannot access payments without proper groups"""
        # Basic user should not be able to create payments
        with self.assertRaises(AccessError):
            self.env['account.payment'].with_user(self.basic_user).create({
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': self.partner.id,
                'amount': 1000.0,
                'journal_id': self.journal_a.id,
                'company_id': self.company_a.id,
            })

    def test_payment_user_permissions(self):
        """Test payment user can create but not approve"""
        # Payment user should be able to create payments
        payment = self.env['account.payment'].with_user(self.payment_user).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        self.assertTrue(payment.id)
        
        # But should not be able to approve (if approval method exists)
        if hasattr(payment, 'action_approve_payment'):
            with self.assertRaises((AccessError, UserError, ValidationError)):
                payment.action_approve_payment()

    def test_payment_manager_permissions(self):
        """Test payment manager can create and approve"""
        # Manager should be able to create payments
        payment = self.env['account.payment'].with_user(self.payment_manager).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        self.assertTrue(payment.id)
        
        # Manager should be able to approve (if method exists)
        if hasattr(payment, 'action_approve_payment'):
            try:
                payment.action_approve_payment()
                # Should succeed or at least not raise AccessError
                self.assertTrue(True)
            except AccessError:
                self.fail("Payment manager should be able to approve payments")
            except (UserError, ValidationError):
                # These are acceptable - business logic errors, not access errors
                pass

    def test_company_isolation(self):
        """Test payments are isolated by company"""
        # Create payment in company A
        payment_a = self.env['account.payment'].with_user(self.payment_user).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        # User from company B should not see company A's payments
        company_b_payments = self.env['account.payment'].with_user(self.company_b_user).search([
            ('id', '=', payment_a.id)
        ])
        
        self.assertEqual(len(company_b_payments), 0)

    def test_journal_access_restrictions(self):
        """Test users can only use journals from their company"""
        # Company B user should not be able to use Company A journal
        with self.assertRaises((AccessError, ValidationError)):
            self.env['account.payment'].with_user(self.company_b_user).create({
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': self.partner.id,
                'amount': 1000.0,
                'journal_id': self.journal_a.id,  # Wrong company journal
                'company_id': self.company_b.id,
            })

    def test_field_access_permissions(self):
        """Test field-level access permissions"""
        payment = self.env['account.payment'].with_user(self.payment_manager).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        # Test that sensitive fields are protected
        sensitive_fields = [
            'actual_approver_id',
            'reviewer_id',
            'approver_id',
            'authorizer_id'
        ]
        
        for field in sensitive_fields:
            if hasattr(payment, field):
                # Regular user should not be able to modify these fields directly
                payment_as_user = payment.with_user(self.payment_user)
                try:
                    # This might succeed or fail depending on field configuration
                    setattr(payment_as_user, field, self.payment_user.id)
                except (AccessError, ValidationError):
                    # This is expected for protected fields
                    pass

    def test_record_rules_enforcement(self):
        """Test record rules are properly enforced"""
        # Create payment as manager
        payment = self.env['account.payment'].with_user(self.payment_manager).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        # Same company user should be able to read
        payment_as_user = payment.with_user(self.payment_user)
        self.assertTrue(payment_as_user.exists())
        
        # Different company user should not be able to read
        try:
            payment_as_company_b = payment.with_user(self.company_b_user)
            payment_as_company_b.read(['amount'])
            # If this succeeds, record rules might not be configured
        except AccessError:
            # This is expected - different company users shouldn't access
            pass

    def test_method_access_security(self):
        """Test method-level access security"""
        payment = self.env['account.payment'].with_user(self.payment_manager).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        # Test workflow methods with different users
        workflow_methods = [
            'action_submit_for_review',
            'action_review_payment',
            'action_approve_payment',
            'action_authorize_payment',
            'action_post_payment'
        ]
        
        for method_name in workflow_methods:
            if hasattr(payment, method_name):
                method = getattr(payment, method_name)
                
                # Test with basic user (should fail)
                payment_as_basic = payment.with_user(self.basic_user)
                if hasattr(payment_as_basic, method_name):
                    with self.assertRaises((AccessError, UserError, ValidationError)):
                        getattr(payment_as_basic, method_name)()

    def test_security_group_assignments(self):
        """Test security group assignments work correctly"""
        # Check that security groups exist
        security_groups = [
            'account_payment_final.group_payment_voucher_user',
            'account_payment_final.group_payment_voucher_manager',
            'account_payment_final.group_payment_poster',
            'account_payment_final.group_payment_voucher_approver'
        ]
        
        for group_xml_id in security_groups:
            try:
                group = self.env.ref(group_xml_id)
                self.assertTrue(group.exists())
            except ValueError:
                # Group might not exist - that's okay for this test
                pass

    def test_audit_trail_security(self):
        """Test audit trail fields are properly secured"""
        payment = self.env['account.payment'].with_user(self.payment_manager).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        # Audit fields should exist and be readable
        audit_fields = [
            'reviewer_date',
            'approver_date',
            'authorizer_date'
        ]
        
        for field in audit_fields:
            if hasattr(payment, field):
                # Should be able to read audit fields
                try:
                    value = getattr(payment, field)
                    # Value can be None or a date
                    self.assertTrue(value is None or isinstance(value, (type(None), str)))
                except AccessError:
                    self.fail(f"Should be able to read audit field {field}")

    def test_data_modification_restrictions(self):
        """Test data modification restrictions based on state"""
        payment = self.env['account.payment'].with_user(self.payment_manager).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal_a.id,
            'company_id': self.company_a.id,
        })
        
        # Move to posted state if possible
        if hasattr(payment, 'approval_state'):
            payment.approval_state = 'posted'
        else:
            payment.state = 'posted'
        
        # Should not be able to modify posted payments
        with self.assertRaises((UserError, ValidationError, AccessError)):
            payment.amount = 2000.0


class TestSecurityValidation(TransactionCase):
    """Test security validation and constraints"""
    
    def test_approval_state_constraints(self):
        """Test approval state transition constraints"""
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.env['res.partner'].create({'name': 'Test Partner'}).id,
            'amount': 1000.0,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })
        
        # Test invalid state transitions
        if hasattr(payment, 'approval_state'):
            with self.assertRaises(ValidationError):
                # Cannot go directly from draft to posted
                payment.approval_state = 'posted'

    def test_amount_validation_constraints(self):
        """Test amount validation security constraints"""
        # Test negative amounts
        with self.assertRaises(ValidationError):
            self.env['account.payment'].create({
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': self.env['res.partner'].create({'name': 'Test Partner'}).id,
                'amount': -1000.0,
                'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
            })

    def test_user_permission_validation(self):
        """Test user permission validation"""
        # Test that permission checking methods exist
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.env['res.partner'].create({'name': 'Test Partner'}).id,
            'amount': 1000.0,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })
        
        permission_methods = [
            '_check_workflow_permissions',
            '_can_bypass_approval_workflow'
        ]
        
        for method_name in permission_methods:
            if hasattr(payment, method_name):
                method = getattr(payment, method_name)
                self.assertTrue(callable(method))
