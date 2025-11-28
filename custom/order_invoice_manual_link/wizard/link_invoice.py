from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LinkInvoice(models.TransientModel):
    """
    This model handles the linking of invoices to sale orders.
    """
    _name = 'link.invoice'
    _description = "Link Invoice"

    invoice_ids = fields.Many2many(
        "account.move", string="Invoices",
        help="Select the invoices you want to link to the sale order.",
        domain=lambda self: self._get_available_invoices())
    sale_order_id = fields.Many2one(
        'sale.order', string="Default Sale Order",
        readonly=True, help="The default sale order to which the "
                            "selected invoices will be linked.")

    def _get_available_invoices(self):
        """
        Dynamically filter the available invoices that are not linked
        to any sale order.
        """
        return [('id', 'not in', self._get_linked_invoice_ids())]

    @api.model
    def _get_linked_invoice_ids(self):
        """
        Fetch all invoice IDs that are already linked to sale orders.
        """
        return self.env['sale.order.line'].mapped('invoice_lines').ids

    def action_add_invoices(self):
        """
        Add selected invoices to the associated sale order.
        Only validates partner matching, allows any products to be linked.
        """
        if self.sale_order_id:
            for invoice in self.invoice_ids:
                if invoice.link_invoice:
                    # Link the invoice to the sale order
                    invoice.sale_order_id = self.sale_order_id.id
                    
                    # Optional: Update qty_invoiced for matching products only
                    # This will only affect products that exist in both invoice and sale order
                    for invoice_line in invoice.invoice_line_ids:
                        matching_order_lines = self.sale_order_id.order_line.filtered(
                            lambda x: x.product_id == invoice_line.product_id
                        )
                        if matching_order_lines:
                            for order_line in matching_order_lines:
                                # Only update if not already invoiced
                                if order_line.qty_invoiced < order_line.product_uom_qty:
                                    order_line.qty_invoiced = min(
                                        order_line.product_uom_qty,
                                        order_line.qty_invoiced + abs(invoice_line.quantity)
                                    )
                                    order_line.invoice_lines |= invoice_line

    @api.constrains('invoice_ids')
    def invoice_ids_field(self):
        """
        Check for partner mismatch between sale order and selected invoices.
        """
        for record in self:
            if record.sale_order_id:
                sale_order_partner_id = record.sale_order_id.partner_id
                for invoice in record.invoice_ids:
                    if invoice.partner_id != sale_order_partner_id:
                        raise ValidationError(_(
                            "Partner mismatch between Sale Order and Invoice '%s'. "
                            "Sale Order partner: %s, Invoice partner: %s. "
                            "Please remove this invoice to proceed with linking.") % (
                                invoice.name or 'Draft',
                                sale_order_partner_id.name,
                                invoice.partner_id.name
                            ))
