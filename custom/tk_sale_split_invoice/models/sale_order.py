# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    """
        Inherits from 'sale.order' to customize behavior or add additional fields.
    """
    _inherit = 'sale.order'

    is_split = fields.Boolean(string="Invoice Split", default=False)

    def action_split_invoices(self):
        """Splits the sale order into invoices based on config settings."""

        split_count = int(self.env['ir.config_parameter'].sudo().get_param(
            'tk_sale_split_invoice.split_invoice_count', 0
        ))

        if split_count <= 0:
            raise UserError("Please set a valid split invoice count in settings.")

        if not self.order_line:
            raise UserError("No sale order lines found to split.")

        undelivered_products = [
            f"{line.product_id.display_name} (Qty Delivered: {line.qty_delivered})"
            for line in self.order_line
            if line.product_id.detailed_type == 'product' and line.qty_delivered <= 0
        ]

        if undelivered_products:
            raise UserError(
                "The following storable products have zero delivered quantity:\n\n- "
                + "\n- ".join(undelivered_products)
                + "\n\nEnsure all storable products are delivered before invoicing."
            )

        delivered_lines = self.order_line.filtered(
            lambda line: line.product_id and (
                    (line.product_id.detailed_type == 'product' and line.qty_delivered > 0)
                    or (line.product_id.detailed_type == 'service')
                    or (line.product_id.detailed_type == 'consu')
            )
        )

        if not delivered_lines:
            raise UserError("No valid products found to invoice.")

        invoices = []
        sale_order_lines = list(delivered_lines)

        chunks = [sale_order_lines[i::split_count] for i in range(split_count)]

        for lines_for_invoice in chunks:
            if lines_for_invoice:
                invoice_vals = {
                    'partner_id': self.partner_id.id,
                    'move_type': 'out_invoice',
                    'invoice_origin': self.name,
                    'is_split_invoice': True,
                    'invoice_line_ids': [
                        (0, 0, {
                            'product_id': line.product_id.id,
                            'quantity': line.product_uom_qty,
                            'price_unit': line.price_unit,
                            'name': line.name,
                            'sale_line_ids': [(6, 0, [line.id])]
                        }) for line in lines_for_invoice
                    ]
                }
                invoice = self.env['account.move'].create(invoice_vals)
                invoices.append(invoice)

        if invoices:
            self.write({
                'is_split': True,
                'invoice_ids': [(4, inv.id) for inv in invoices]
            })
            return {
                'name': 'Generated Invoices',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', [inv.id for inv in invoices])],
                'context': {'default_is_split_invoice': True},
            }
        else:
            raise UserError("No invoices were created.")
