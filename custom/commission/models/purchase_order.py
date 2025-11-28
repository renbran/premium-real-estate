from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    description = fields.Char(string="Description")
    origin_so_id = fields.Many2one('sale.order', string="Source Sale Order", readonly=True)
    commission_posted = fields.Boolean(string="Commission Posted", default=False)

    @api.depends('origin_so_id')
    def _compute_display_name(self):
        """Override display name for commission purchase orders."""
        super(PurchaseOrder, self)._compute_display_name()
        for po in self:
            if po.origin_so_id:
                po.display_name = f"{po.name} (Commission from {po.origin_so_id.name})"

    def _prepare_account_move_line(self, line, move):
        """Override to add commission-specific account configuration."""
        result = super(PurchaseOrder, self)._prepare_account_move_line(line, move)
        
        # If this is a commission PO, we might want to use specific accounts
        if self.origin_so_id:
            # You can customize the account used for commission expenses here
            commission_account = self.env['ir.config_parameter'].sudo().get_param(
                'commission_ax.commission_expense_account_id'
            )
            if commission_account:
                try:
                    account = self.env['account.account'].browse(int(commission_account))
                    if account.exists():
                        result['account_id'] = account.id
                except (ValueError, TypeError):
                    _logger.warning("Invalid commission expense account configuration")
        
        return result

    def _post_commission_on_receipt_validation(self):
        """Post commission when receipt is validated."""
        for order in self:
            if order.origin_so_id and not order.commission_posted:
                # Check if all receipts are done
                all_receipts_done = all(
                    picking.state == 'done' for picking in order.picking_ids
                )
                
                if all_receipts_done and order.picking_ids:
                    try:
                        if order.state == 'draft':
                            order.button_confirm()
                        order.commission_posted = True
                        
                        # Log the posting
                        _logger.info(f"Commission posted for PO {order.name} from SO {order.origin_so_id.name}")
                        
                        # Add message to the sale order
                        order.origin_so_id.message_post(
                            body=f"Commission purchase order {order.name} has been automatically posted due to receipt validation."
                        )
                        
                    except Exception as e:
                        _logger.error(f"Error posting commission PO {order.name}: {str(e)}")
                        # Don't raise the error to avoid blocking other operations

    def _post_commission_on_payment(self):
        """Post commission when payment is recorded."""
        for order in self:
            if order.origin_so_id and not order.commission_posted:
                # Check if there are any payments for this PO
                invoice_lines = self.env['account.move.line'].search([
                    ('purchase_line_id', 'in', order.order_line.ids)
                ])
                
                if invoice_lines:
                    invoices = invoice_lines.mapped('move_id').filtered(
                        lambda inv: inv.move_type == 'in_invoice' and inv.state == 'posted'
                    )
                    
                    # Check if any invoice has payments
                    paid_invoices = invoices.filtered(
                        lambda inv: inv.payment_state in ['in_payment', 'paid']
                    )
                    
                    if paid_invoices:
                        try:
                            if order.state == 'draft':
                                order.button_confirm()
                            order.commission_posted = True
                            
                            _logger.info(f"Commission posted for PO {order.name} due to payment")
                            
                            order.origin_so_id.message_post(
                                body=f"Commission purchase order {order.name} has been automatically posted due to payment."
                            )
                            
                        except Exception as e:
                            _logger.error(f"Error posting commission PO on payment {order.name}: {str(e)}")

    def action_view_picking(self):
        """Override to trigger commission posting check."""
        result = super(PurchaseOrder, self).action_view_picking()
        self._post_commission_on_receipt_validation()
        return result

    def action_force_post(self):
        """Manual action to force post the purchase order."""
        for order in self:
            if not order.commission_posted:
                try:
                    if order.state == 'draft':
                        order.button_confirm()
                    order.commission_posted = True
                    
                    # Add message
                    order.origin_so_id.message_post(
                        body=f"Commission purchase order {order.name} has been manually forced to post."
                    )
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Success',
                            'message': f'Commission purchase order {order.name} has been posted.',
                            'type': 'success',
                        }
                    }
                except Exception as e:
                    raise UserError(f"Failed to post commission: {str(e)}")
        
        return True

    def button_confirm(self):
        """Override confirm to add commission-specific logic."""
        result = super(PurchaseOrder, self).button_confirm()
        
        # For commission POs, we might want to auto-create receipts or handle differently
        for order in self.filtered('origin_so_id'):
            order.message_post(
                body=f"Commission purchase order confirmed for sale order {order.origin_so_id.name}"
            )
        
        return result

    def button_cancel(self):
        """Override cancel to handle commission-specific logic."""
        for order in self.filtered('origin_so_id'):
            if order.commission_posted:
                raise UserError(
                    f"Cannot cancel commission purchase order {order.name} "
                    "because it has already been posted."
                )
        
        result = super(PurchaseOrder, self).button_cancel()
        
        # Reset commission status on source sale order if needed
        for order in self.filtered('origin_so_id'):
            order.origin_so_id.message_post(
                body=f"Commission purchase order {order.name} has been cancelled."
            )
        
        return result

    def unlink(self):
        """Override unlink to prevent deletion of posted commission POs."""
        for order in self:
            if order.origin_so_id and order.commission_posted:
                raise UserError(
                    f"Cannot delete commission purchase order {order.name} "
                    "because it has been posted."
                )
        
        return super(PurchaseOrder, self).unlink()

    @api.model
    def _cron_check_commission_purchase_orders(self):
        """
        Scheduled action to check and post commission purchase orders 
        when their receipts are validated or payments are made.
        """
        # Find unposted commission purchase orders
        unposted_commission_pos = self.search([
            ('commission_posted', '=', False),
            ('origin_so_id', '!=', False),
            ('state', 'in', ['purchase', 'done'])
        ])
        
        _logger.info(f"Checking {len(unposted_commission_pos)} unposted commission POs")
        
        for purchase_order in unposted_commission_pos:
            try:
                # Check receipt validation
                purchase_order._post_commission_on_receipt_validation()
                
                # If still not posted, check payments
                if not purchase_order.commission_posted:
                    purchase_order._post_commission_on_payment()
                    
            except Exception as e:
                _logger.error(f"Error in cron job for PO {purchase_order.name}: {str(e)}")

    def write(self, vals):
        """Override write to track important changes."""
        result = super(PurchaseOrder, self).write(vals)
        
        # Track state changes for commission POs
        if 'state' in vals:
            for order in self.filtered('origin_so_id'):
                order.origin_so_id.message_post(
                    body=f"Commission purchase order {order.name} state changed to {order.state}"
                )
        
        return result

    @api.model
    def create(self, vals):
        """Override create to add commission-specific setup."""
        order = super(PurchaseOrder, self).create(vals)
        
        # Add message to source sale order if this is a commission PO
        if order.origin_so_id:
            order.origin_so_id.message_post(
                body=f"Commission purchase order {order.name} has been created for {order.partner_id.name}"
            )
        
        return order