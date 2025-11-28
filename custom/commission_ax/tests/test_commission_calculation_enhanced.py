# -*- coding: utf-8 -*-
"""
Enhanced Commission Calculation Tests
====================================

Comprehensive test suite for the refactored commission system validating:
- Calculation accuracy across all methods
- Performance optimizations  
- Workflow state management
- Integration functionality
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from decimal import Decimal
import time


class TestCommissionCalculationEnhanced(TransactionCase):
    """Test suite for enhanced commission calculation system"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test data
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Commission Partner',
            'supplier_rank': 1,  # Make them a vendor
            'is_company': True,
        })
        
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
            'list_price': 1000.0,
        })
        
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })
        
        cls.order_line = cls.env['sale.order.line'].create({
            'order_id': cls.sale_order.id,
            'product_id': cls.product.id,
            'product_uom_qty': 2.0,
            'price_unit': 1000.0,
        })

    def test_percentage_unit_calculation(self):
        """Test percentage of unit price calculation method"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'calculation_method': 'percentage_unit',
            'rate': 15.0,  # 15%
        })
        
        # Verify calculation: 15% of (1000 * 2) = 300
        expected_base = 1000.0 * 2.0  # 2000.0
        expected_commission = expected_base * 0.15  # 300.0
        
        self.assertEqual(commission.base_amount, expected_base)
        self.assertEqual(commission.commission_amount, expected_commission)
        
        # Test the original issue: 15% of 868,800 should be ~130,320
        commission.write({
            'unit_price': 868800.0,
            'commission_qty': 1.0,
        })
        commission._calculate_commission()
        
        expected_commission = 868800.0 * 0.15  # 130,320
        self.assertEqual(commission.commission_amount, expected_commission)

    def test_percentage_subtotal_calculation(self):
        """Test percentage of subtotal calculation method"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'calculation_method': 'percentage_subtotal',
            'rate': 10.0,  # 10%
        })
        
        # Should use line subtotal as base
        expected_commission = commission.subtotal * 0.10
        self.assertEqual(commission.commission_amount, expected_commission)

    def test_fixed_amount_calculation(self):
        """Test fixed amount calculation method"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'calculation_method': 'fixed_amount',
            'rate': 250.0,  # Fixed $250
        })
        
        # Should use rate as commission amount directly
        self.assertEqual(commission.base_amount, 1.0)  # Base is 1 for fixed
        self.assertEqual(commission.commission_amount, 250.0)

    def test_commission_quantity_with_percentage(self):
        """Test commission quantity calculation with percentage from order line"""
        # Add qty_percentage to order line (simulate the enhancement)
        self.order_line.qty_percentage = 50.0  # 50% of quantity
        
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'calculation_method': 'percentage_unit',
            'rate': 15.0,
        })
        
        # Commission qty should be 50% of order quantity: 2.0 * 0.5 = 1.0
        expected_commission_qty = 2.0 * 0.5
        self.assertEqual(commission.commission_qty, expected_commission_qty)
        
        # Commission amount should be based on commission_qty
        expected_commission = 1000.0 * 1.0 * 0.15  # 150.0
        self.assertEqual(commission.commission_amount, expected_commission)

    def test_completion_percentage_calculation(self):
        """Test completion percentage based on invoiced quantity"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'commission_qty': 2.0,
            'invoiced_qty': 1.0,
        })
        
        # 1.0 / 2.0 = 50%
        self.assertEqual(commission.completion_percentage, 50.0)
        
        # Test 100% completion
        commission.invoiced_qty = 2.0
        self.assertEqual(commission.completion_percentage, 100.0)
        
        # Test over-invoicing (should cap at 100%)
        commission.invoiced_qty = 3.0
        self.assertEqual(commission.completion_percentage, 100.0)

    def test_multi_currency_support(self):
        """Test commission calculation with multiple currencies"""
        # Create USD currency sale order
        usd_currency = self.env.ref('base.USD')
        
        usd_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'currency_id': usd_currency.id,
        })
        
        usd_line = self.env['sale.order.line'].create({
            'order_id': usd_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1.0,
            'price_unit': 1000.0,  # $1000 USD
        })
        
        commission = self.env['commission.line'].create({
            'sale_order_id': usd_order.id,
            'sale_order_line_id': usd_line.id,
            'partner_id': self.partner.id,
            'calculation_method': 'percentage_unit',
            'rate': 10.0,
        })
        
        # Should have commission in USD and company currency
        self.assertEqual(commission.currency_id, usd_currency)
        self.assertEqual(commission.commission_amount, 100.0)  # 10% of $1000
        self.assertTrue(commission.commission_amount_company > 0)  # Converted amount

    def test_workflow_state_management(self):
        """Test commission workflow state transitions"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'rate': 15.0,
        })
        
        # Initial state should be draft
        self.assertEqual(commission.state, 'draft')
        
        # Calculate commission
        commission.action_calculate()
        self.assertEqual(commission.state, 'calculated')
        
        # Confirm commission
        commission.action_confirm()
        self.assertEqual(commission.state, 'confirmed')
        
        # Create purchase order
        po_action = commission.action_create_purchase_order()
        self.assertEqual(commission.state, 'invoiced')
        self.assertTrue(commission.purchase_order_id)
        
        # Mark as paid
        commission.action_mark_paid()
        self.assertEqual(commission.state, 'paid')

    def test_validation_constraints(self):
        """Test validation rules and constraints"""
        # Test negative rate validation
        with self.assertRaises(ValidationError):
            self.env['commission.line'].create({
                'sale_order_id': self.sale_order.id,
                'partner_id': self.partner.id,
                'rate': -5.0,
            })
        
        # Test percentage rate over 100%
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.partner.id,
            'calculation_method': 'percentage_unit',
            'rate': 150.0,  # 150% - should raise error
        })
        
        with self.assertRaises(ValidationError):
            commission._check_rate()
        
        # Test partner must be vendor
        non_vendor_partner = self.env['res.partner'].create({
            'name': 'Non-Vendor Partner',
            'supplier_rank': 0,  # Not a vendor
        })
        
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': non_vendor_partner.id,
            'rate': 10.0,
        })
        
        with self.assertRaises(ValidationError):
            commission._check_partner()

    def test_performance_batch_operations(self):
        """Test performance of batch operations"""
        start_time = time.time()
        
        # Create 100 commission lines
        commission_data = []
        for i in range(100):
            commission_data.append({
                'sale_order_id': self.sale_order.id,
                'sale_order_line_id': self.order_line.id,
                'partner_id': self.partner.id,
                'rate': 15.0,
                'calculation_method': 'percentage_unit',
            })
        
        commissions = self.env['commission.line'].create(commission_data)
        
        create_time = time.time() - start_time
        
        # Should create 100 commissions in under 2 seconds
        self.assertLess(create_time, 2.0, f"Batch creation took {create_time:.2f}s, should be under 2s")
        
        # Test batch calculation
        start_time = time.time()
        commissions._calculate_commission()
        calc_time = time.time() - start_time
        
        # Should calculate 100 commissions in under 1 second
        self.assertLess(calc_time, 1.0, f"Batch calculation took {calc_time:.2f}s, should be under 1s")
        
        # Verify all calculations are correct
        for commission in commissions:
            expected = commission.unit_price * commission.commission_qty * 0.15
            self.assertEqual(commission.commission_amount, expected)

    def test_precision_decimal_handling(self):
        """Test decimal precision in commission calculations"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'calculation_method': 'percentage_unit',
            'rate': 15.555555,  # Many decimal places
        })
        
        # Update with precise values
        commission.write({
            'unit_price': 999.99,
            'commission_qty': 1.333333,
        })
        commission._calculate_commission()
        
        # Result should be rounded to 2 decimal places
        expected = 999.99 * 1.333333 * (15.555555 / 100)
        expected_rounded = float(Decimal(str(expected)).quantize(Decimal('0.01')))
        
        self.assertEqual(commission.commission_amount, expected_rounded)

    def test_create_from_sale_order_integration(self):
        """Test commission creation from sale order integration"""
        # Mock commission data from sale order
        commission_data = [{
            'order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'category': 'internal',
            'role': 'agent',
            'method': 'percentage_unit',
            'rate': 15.0,
            'description': 'Sales Agent Commission',
        }]
        
        # Create commissions from sale order
        commissions = self.env['commission.line'].create_from_sale_order(
            self.sale_order, 
            commission_data
        )
        
        self.assertEqual(len(commissions), 1)
        commission = commissions[0]
        
        # Verify proper population
        self.assertEqual(commission.sale_order_id, self.sale_order)
        self.assertEqual(commission.sale_order_line_id, self.order_line)
        self.assertEqual(commission.partner_id, self.partner)
        self.assertEqual(commission.calculation_method, 'percentage_unit')
        self.assertEqual(commission.rate, 15.0)
        self.assertEqual(commission.commission_category, 'internal')
        self.assertEqual(commission.commission_role, 'agent')

    def test_purchase_order_creation(self):
        """Test purchase order creation for commission payment"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'rate': 15.0,
            'state': 'confirmed',
        })
        
        # Create purchase order
        po_action = commission.action_create_purchase_order()
        
        # Verify purchase order creation
        self.assertTrue(commission.purchase_order_id)
        self.assertTrue(commission.purchase_line_id)
        self.assertEqual(commission.state, 'invoiced')
        
        # Verify PO details
        purchase_order = commission.purchase_order_id
        self.assertEqual(purchase_order.partner_id, self.partner)
        self.assertTrue(purchase_order.origin.startswith('Commission:'))
        
        # Verify PO line
        purchase_line = commission.purchase_line_id
        self.assertEqual(purchase_line.price_unit, commission.commission_amount)
        self.assertEqual(purchase_line.product_qty, 1.0)

    def test_commission_service_product_creation(self):
        """Test automatic creation of commission service product"""
        # Ensure no existing commission product
        existing_product = self.env['product.product'].search([
            ('default_code', '=', 'COMMISSION_SERVICE')
        ])
        existing_product.unlink()
        
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'sale_order_line_id': self.order_line.id,
            'partner_id': self.partner.id,
            'rate': 15.0,
            'state': 'confirmed',
        })
        
        # Get commission product (should create if not exists)
        commission_product = commission._get_commission_product()
        
        # Verify product creation
        self.assertTrue(commission_product)
        self.assertEqual(commission_product.default_code, 'COMMISSION_SERVICE')
        self.assertEqual(commission_product.type, 'service')
        self.assertTrue(commission_product.purchase_ok)
        self.assertFalse(commission_product.sale_ok)

    def test_error_handling_and_recovery(self):
        """Test error handling and graceful recovery"""
        # Test missing sale order line
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            # No sale_order_line_id
            'partner_id': self.partner.id,
            'rate': 15.0,
        })
        
        # Should handle gracefully without errors
        commission._populate_from_order_line()
        commission._calculate_commission()
        
        # Commission amount should be 0 due to missing data
        self.assertEqual(commission.commission_amount, 0.0)
        
        # Test invalid workflow transition
        commission.state = 'paid'
        with self.assertRaises(UserError):
            commission.action_cancel()  # Cannot cancel paid commissions

    def test_display_name_computation(self):
        """Test display name computation"""
        commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.partner.id,
            'commission_role': 'agent',
        })
        
        # Should include partner name, role, and order name
        expected_parts = [
            self.partner.name,
            'Sales Agent',  # Role display name
            self.sale_order.name,
        ]
        expected_display = ' - '.join(expected_parts)
        
        self.assertEqual(commission.display_name, expected_display)

    def tearDown(self):
        """Clean up test data"""
        super().tearDown()
        # Clean up is handled automatically by TransactionCase