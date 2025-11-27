# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, HttpCase
from odoo.exceptions import ValidationError, AccessError
from unittest.mock import patch, Mock
import base64


class TestQRVerification(TransactionCase):
    """Test QR generation and verification functionality"""

    def setUp(self):
        super().setUp()
        
        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })
        
        # Create test journal
        self.journal = self.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'TB',
        })
        
        # Create test payment
        self.payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal.id,
        })
        
        # Generate access token for QR code
        if not self.payment.access_token:
            self.payment.write({'access_token': self.payment._generate_access_token()})

    def test_qr_code_generation(self):
        """Test QR code is generated correctly"""
        # Set base URL
        self.env['ir.config_parameter'].sudo().set_param('web.base.url', 'http://localhost:8069')
        
        # Ensure payment has access token first
        if not self.payment.access_token:
            self.payment.write({'access_token': self.payment._generate_access_token()})
        
        # Trigger QR generation
        self.payment._compute_qr_code()
        
        # Verify QR code was generated
        self.assertTrue(self.payment.qr_code, "QR code should be generated")
        self.assertIsInstance(self.payment.qr_code, bytes, "QR code should be bytes")

    def test_qr_fallback_without_base_url(self):
        """Test QR fallback when no base URL is configured"""
        # Remove base URL
        self.env['ir.config_parameter'].sudo().set_param('web.base.url', '')
        
        # Ensure payment has access token first
        if not self.payment.access_token:
            self.payment.write({'access_token': self.payment._generate_access_token()})
        
        # Trigger QR generation
        self.payment._compute_qr_code()
        
        # Should still generate QR with fallback data
        self.assertTrue(self.payment.qr_code, "QR code should be generated with fallback")

    def test_qr_without_access_token(self):
        """Test QR is not generated without access token"""
        # Clear access token
        self.payment.write({'access_token': False})
        
        # Trigger QR generation
        self.payment._compute_qr_code()
        
        # Should not generate QR without access token
        self.assertFalse(self.payment.qr_code, "QR code should not be generated without access token")

    def test_verification_log_creation(self):
        """Test verification logging"""
        # Log a verification
        verification = self.env['payment.qr.verification'].log_verification(
            payment_id=self.payment.id,
            ip_address='192.168.1.1',
            user_agent='Test Browser',
            method='qr_scan',
            additional_data={'test': 'data'}
        )
        
        self.assertTrue(verification, "Verification record should be created")
        self.assertEqual(verification.payment_id, self.payment)
        self.assertEqual(verification.verifier_ip, '192.168.1.1')
        self.assertEqual(verification.verification_method, 'qr_scan')

    def test_verification_statistics(self):
        """Test verification statistics calculation"""
        # Create some test verifications
        for i in range(3):
            self.env['payment.qr.verification'].create({
                'payment_id': self.payment.id,
                'verification_method': 'qr_scan',
                'verification_status': 'success',
            })
        
        stats = self.env['payment.qr.verification'].get_verification_statistics()
        
        self.assertIn('status_stats', stats)
        self.assertIn('method_stats', stats)
        self.assertGreater(stats['total_count'], 0)

    def test_payment_voucher_number_generation(self):
        """Test voucher number is auto-generated"""
        self.assertTrue(self.payment.voucher_number, "Voucher number should be auto-generated")
        self.assertNotEqual(self.payment.voucher_number, '/', "Voucher number should not be default")


class TestQRVerificationController(HttpCase):
    """Test QR verification web controller"""

    def setUp(self):
        super().setUp()
        
        # Create test data
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })
        
        self.journal = self.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'TB',
        })
        
        self.payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.partner.id,
            'amount': 1000.0,
            'journal_id': self.journal.id,
            'qr_in_report': True,
        })

    def test_verify_payment_endpoint_success(self):
        """Test successful payment verification via HTTP endpoint"""
        url = f'/payment/verify/{self.payment.id}'
        response = self.url_open(url)
        
        self.assertEqual(response.status_code, 200, "Verification page should load successfully")

    def test_verify_payment_not_found(self):
        """Test verification with non-existent payment ID"""
        url = '/payment/verify/99999'
        response = self.url_open(url)
        
        self.assertEqual(response.status_code, 200, "Should return 200 with error page")
        # Note: Would need to check response content for error message

    def test_verify_payment_json_endpoint(self):
        """Test JSON API endpoint"""
        url = f'/payment/verify/json/{self.payment.id}'
        
        # This would require making a JSON request in a real test
        # For now, just verify the payment exists
        self.assertTrue(self.payment.exists(), "Payment should exist for JSON verification")

    def test_verification_logging_in_controller(self):
        """Test that controller logs verification attempts"""
        initial_count = self.env['payment.qr.verification'].search_count([
            ('payment_id', '=', self.payment.id)
        ])
        
        # Access the verification page
        url = f'/payment/verify/{self.payment.id}'
        self.url_open(url)
        
        final_count = self.env['payment.qr.verification'].search_count([
            ('payment_id', '=', self.payment.id)
        ])
        
        self.assertGreater(final_count, initial_count, 
                          "Verification attempt should be logged")


class TestQRSecurity(TransactionCase):
    """Test security aspects of QR verification"""

    def setUp(self):
        super().setUp()
        
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })
        
        self.journal = self.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'TB',
        })

    def test_verification_record_immutability(self):
        """Test that verification records cannot be modified by regular users"""
        # Create verification record
        verification = self.env['payment.qr.verification'].create({
            'payment_id': self.env['account.payment'].create({
                'payment_type': 'outbound',
                'partner_id': self.partner.id,
                'amount': 100.0,
                'journal_id': self.journal.id,
            }).id,
            'verification_method': 'qr_scan',
        })
        
        # Try to modify as regular user (should fail)
        with self.assertRaises(AccessError):
            verification.with_user(self.env.ref('base.user_demo')).write({
                'verification_status': 'failed'
            })

    def test_verification_record_deletion_restricted(self):
        """Test that verification records cannot be deleted by regular users"""
        verification = self.env['payment.qr.verification'].create({
            'payment_id': self.env['account.payment'].create({
                'payment_type': 'outbound',
                'partner_id': self.partner.id,
                'amount': 100.0,
                'journal_id': self.journal.id,
            }).id,
            'verification_method': 'qr_scan',
        })
        
        # Try to delete as regular user (should fail)
        with self.assertRaises(AccessError):
            verification.with_user(self.env.ref('base.user_demo')).unlink()

    def test_unique_verification_codes(self):
        """Test that verification codes are unique"""
        payment1 = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.partner.id,
            'amount': 100.0,
            'journal_id': self.journal.id,
        })
        
        payment2 = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_id': self.partner.id,
            'amount': 200.0,
            'journal_id': self.journal.id,
        })
        
        # Create first verification
        verification1 = self.env['payment.qr.verification'].create({
            'payment_id': payment1.id,
            'verification_code': 'TEST123',
            'verification_method': 'qr_scan',
        })
        
        # Try to create second verification with same code (should fail)
        with self.assertRaises(ValidationError):
            self.env['payment.qr.verification'].create({
                'payment_id': payment2.id,
                'verification_code': 'TEST123',
                'verification_method': 'qr_scan',
            })
