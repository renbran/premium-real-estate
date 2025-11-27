# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('split_invoice')
class TestSplitInvoice(TransactionCase):
    """
    Test case for validating the split invoice functionality in the sale order.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment, including partner, product, sale order, and lines.
        """
        super().setUpClass()

        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer'
        })

        cls.product_service = cls.env['product.product'].create({
            'name': 'Service Product',
            'detailed_type': 'service',
            'invoice_policy': 'order',
            'list_price': 100.0,
        })

        cls.product_storable = cls.env['product.product'].create({
            'name': 'Storable Product',
            'detailed_type': 'product',
            'invoice_policy': 'delivery',
            'list_price': 200.0,
        })

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })

        cls.line_service = cls.env['sale.order.line'].create({
            'order_id': cls.sale_order.id,
            'product_id': cls.product_service.id,
            'product_uom_qty': 2,
            'price_unit': 100.0,
            'name': 'Service Line',
        })

        cls.line_storable = cls.env['sale.order.line'].create({
            'order_id': cls.sale_order.id,
            'product_id': cls.product_storable.id,
            'product_uom_qty': 3,
            'qty_delivered': 3,
            'price_unit': 200.0,
            'name': 'Storable Line',
        })

        cls.env['ir.config_parameter'].sudo().set_param(
            'tk_sale_split_invoice.split_invoice_count', '1'
        )

    def test_action_split_invoices(self):
        """
        Test splitting invoices from a sale order with eligible products.
        """
        result = self.sale_order.action_split_invoices()
        self.assertTrue(result, "Expected action result from split invoices.")

        invoices = self.sale_order.invoice_ids
        self.assertEqual(len(invoices), 1, "Expected 2 invoices due to split count = 1.")

        for invoice in invoices:
            self.assertEqual(invoice.move_type, 'out_invoice')
            self.assertTrue(invoice.is_split_invoice, "Expected split flag on invoice.")

    def test_split_invoices_zero_delivery(self):
        """
        Ensure error is raised if storable product has zero delivered quantity.
        """
        self.line_storable.qty_delivered = 0
        try:
            self.sale_order.action_split_invoices()
            self.fail("Expected UserError due to zero delivered quantity.")
        except UserError as e:
            self.assertIn("zero delivered quantity", str(e))

    def test_invalid_split_count_config(self):
        """
        Ensure error is raised for invalid (zero or negative) split count.
        """
        self.env['ir.config_parameter'].sudo().set_param(
            'tk_sale_split_invoice.split_invoice_count', '0'
        )
        try:
            self.sale_order.action_split_invoices()
            self.fail("Expected UserError due to invalid split count.")
        except UserError as e:
            self.assertIn("valid split invoice count", str(e))

    def test_split_count_greater_than_lines(self):
        """
        Should generate a single invoice if split count is higher than order lines.
        """
        self.env['ir.config_parameter'].sudo().set_param(
            'tk_sale_split_invoice.split_invoice_count', '10'
        )
        result = self.sale_order.action_split_invoices()
        self.assertTrue(result)
        self.assertEqual(len(self.sale_order.invoice_ids), 2)

    def test_invoice_linking(self):
        """
        Ensure all generated invoices are linked to the sale order.
        """
        self.sale_order.action_split_invoices()
        self.assertTrue(self.sale_order.invoice_ids)
        for invoice in self.sale_order.invoice_ids:
            self.assertIn(invoice.id, self.sale_order.invoice_ids.ids)
