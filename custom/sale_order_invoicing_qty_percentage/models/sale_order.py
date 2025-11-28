from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        """If invoicing by quantity percentage, modify quantities."""
        res = super()._prepare_invoice_line(**optional_values)

        # Check if qty_percentage is provided in the context
        qty_percentage = self.env.context.get("qty_percentage")
        if qty_percentage:
            # Validate qty_percentage
            if not isinstance(qty_percentage, (int, float)) or qty_percentage <= 0:
                raise ValidationError(_("Invalid qty_percentage value. It must be a positive number."))

            # Adjust quantity and round it to 6 decimal places for precision
            res["quantity"] = fields.Float.round(res["quantity"] * qty_percentage, precision_digits=6)

        return res