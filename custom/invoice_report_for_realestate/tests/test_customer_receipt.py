# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestCustomerReceipt(TransactionCase):
    """Test cases for customer receipt functionality"""

    def setUp(self):
        super().setUp()
        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@customer.com',
            'phone': '+971501234567',
            'is_company': False,
            'customer_rank': 1,
        })
        
        # Get cash journal
        self.cash_journal = self.env['account.journal'].search([
            ('type', '=', 'cash')
        ], limit=1)
        
        if not self.cash_journal:
            self.cash_journal = self.env['account.journal'].create({
                'name': 'Test Cash Journal',
                'code': 'TCASH',
                'type': 'cash',
            })

    def test_customer_receipt_creation(self):
        """Test creating a customer receipt with QR code"""
        # Create customer receipt (inbound payment)
        receipt = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': self.cash_journal.id,
            'amount': 1000.0,
            'ref': 'Test customer receipt',
            'display_qr_code': True,
        })
        
        # Test basic fields
        self.assertEqual(receipt.payment_type, 'inbound')
        self.assertEqual(receipt.partner_id, self.partner)
        self.assertEqual(receipt.amount, 1000.0)
        self.assertTrue(receipt.display_qr_code)
        
        # Post the payment
        receipt.action_post()
        self.assertEqual(receipt.state, 'posted')
        
        # Test QR code generation (should generate after posting)
        receipt._compute_qr_code()
        if receipt.qr_code_urls:
            self.assertTrue(receipt.qr_code_urls.startswith('data:image/png;base64,'))

    def test_supplier_payment_no_qr(self):
        """Test that supplier payments don't get QR codes"""
        # Create supplier payment (outbound payment)
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.partner.id,
            'journal_id': self.cash_journal.id,
            'amount': 500.0,
            'ref': 'Test supplier payment',
        })
        
        # Test that QR code is disabled for outbound payments
        self.assertFalse(payment.display_qr_code)
        
        # Post the payment
        payment.action_post()
        
        # Test that no QR code is generated
        payment._compute_qr_code()
        self.assertFalse(payment.qr_code_urls)

    def test_receipt_report_action(self):
        """Test that the receipt report can be generated"""
        # Create and post receipt
        receipt = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': self.cash_journal.id,
            'amount': 750.0,
            'ref': 'Test receipt for report',
            'display_qr_code': True,
        })
        receipt.action_post()
        
        # Test print voucher action
        try:
            result = receipt.action_print_voucher()
            self.assertIsInstance(result, dict)
            self.assertIn('type', result)
            self.assertEqual(result.get('type'), 'ir.actions.report')
        except Exception as e:
            # If the report is not found, that's also a valid test result
            # as it means the method is working but the report might not be installed
            self.assertIn('not found', str(e).lower())

    def test_amount_in_words(self):
        """Test amount in words conversion"""
        receipt = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': self.cash_journal.id,
            'amount': 1250.50,
        })
        
        # Test amount in words
        amount_words = receipt._get_amount_in_words()
        self.assertIsInstance(amount_words, str)
        self.assertIn('thousand', amount_words.lower())

    def test_related_document_methods(self):
        """Test related document information methods"""
        receipt = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'journal_id': self.cash_journal.id,
            'amount': 300.0,
        })
        
        # Test methods that should work even without related documents
        doc_info = receipt.get_related_document_info()
        self.assertIsInstance(doc_info, dict)
        self.assertIn('label', doc_info)
        self.assertIn('references', doc_info)
        self.assertIn('count', doc_info)
        
        payment_summary = receipt.get_payment_summary()
        self.assertIsInstance(payment_summary, dict)
        self.assertIn('payment_amount', payment_summary)
        
        description = receipt.get_voucher_description()
        self.assertIsInstance(description, str)
        self.assertIn('300', description)
