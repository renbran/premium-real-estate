from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    """Extended Purchase Order with commission tracking capabilities"""
    _inherit = 'purchase.order'

    # Commission-related fields
    commission_sale_order_id = fields.Many2one(
        'sale.order', 
        string="Commission Sale Order", 
        readonly=True,
        help="Sale order this commission purchase order was created from"
    )
    
    commission_line_id = fields.Many2one(
        'commission.line',
        string="Commission Line",
        readonly=True,
        help="Commission line this purchase order is for"
    )
    
    origin_so_id = fields.Many2one('sale.order', string="Source Sale Order", readonly=True)
    commission_posted = fields.Boolean(string="Commission Posted", default=False)
    is_commission_po = fields.Boolean(
        string="Is Commission Purchase Order", 
        compute='_compute_is_commission_po', 
        store=True,
        help="Indicates if this PO was created for commission payments"
    )
    
    # Project fields - Temporarily disabled until project module is available
    # project_id = fields.Many2one(
    #     'project.project',
    #     string='Project',
    #     help='Related project for this purchase order',
    # )

    # unit_id = fields.Many2one(
    #     'project.unit',
    #     string='Unit',
    #     help='Related unit for this purchase order',
    # )
    
    description = fields.Char(string="Description")

    @api.depends('origin_so_id', 'commission_sale_order_id')
    def _compute_is_commission_po(self):
        """Compute if this is a commission purchase order."""
        for po in self:
            po.is_commission_po = bool(po.origin_so_id or po.commission_sale_order_id)

    @api.model_create_multi
    def create(self, vals_list):
        """Override to ensure vendor reference for commission POs."""
        for vals in vals_list:
            commission_so = None
            if vals.get('origin_so_id'):
                commission_so = self.env['sale.order'].browse(vals['origin_so_id'])
            elif vals.get('commission_sale_order_id'):
                commission_so = self.env['sale.order'].browse(vals['commission_sale_order_id'])
                
            if commission_so and commission_so.client_order_ref and not vals.get('partner_ref'):
                vals['partner_ref'] = commission_so.client_order_ref
        return super().create(vals_list)

    def action_view_origin_sale_order(self):
        """Smart button to view origin sale order."""
        self.ensure_one()
        sale_order = self.origin_so_id or self.commission_sale_order_id
        if not sale_order:
            raise UserError("This purchase order is not linked to any sale order.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Origin Sale Order',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.depends('origin_so_id', 'commission_sale_order_id')
    def _compute_display_name(self):
        """Override display name for commission purchase orders."""
        super()._compute_display_name()
        for po in self:
            sale_order = po.origin_so_id or po.commission_sale_order_id
            if sale_order:
                po.display_name = f"{po.name} (Commission from {sale_order.name})"

    def _prepare_account_move_line(self, line, move):
        """Override to add commission-specific account configuration."""
        result = super()._prepare_account_move_line(line, move)
        
        # If this is a commission PO, we might want to use specific accounts
        sale_order = self.origin_so_id or self.commission_sale_order_id
        if sale_order:
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
            sale_order = order.origin_so_id or order.commission_sale_order_id
            if sale_order and not order.commission_posted:
                # Check if all receipts are done - safely access picking_ids
                if not hasattr(order, 'picking_ids') or not order.picking_ids:
                    continue
                    
                all_receipts_done = all(
                    picking.state == 'done' for picking in order.picking_ids
                )
                
                if all_receipts_done:
                    try:
                        if order.state == 'draft':
                            order.button_confirm()
                        order.commission_posted = True
                        
                        # Log the posting
                        _logger.info(f"Commission posted for PO {order.name} from SO {sale_order.name}")
                        
                        # Add message to the sale order
                        sale_order.message_post(
                            body=f"Commission purchase order {order.name} has been automatically posted due to receipt validation."
                        )
                        
                    except Exception as e:
                        _logger.error(f"Error posting commission PO {order.name}: {str(e)}")
                        # Don't raise the error to avoid blocking other operations

    def _post_commission_on_payment(self):
        """Post commission when payment is recorded."""
        for order in self:
            sale_order = order.origin_so_id or order.commission_sale_order_id
            if sale_order and not order.commission_posted:
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
                            
                            sale_order.message_post(
                                body=f"Commission purchase order {order.name} has been automatically posted due to payment."
                            )
                            
                        except Exception as e:
                            _logger.error(f"Error posting commission PO on payment {order.name}: {str(e)}")

    def action_view_picking(self):
        """Override to trigger commission posting check."""
        result = super().action_view_picking()
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
                    sale_order = order.origin_so_id or order.commission_sale_order_id
                    if sale_order:
                        sale_order.message_post(
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
        result = super().button_confirm()
        
        # For commission POs, we might want to auto-create receipts or handle differently
        for order in self.filtered(lambda o: o.origin_so_id or o.commission_sale_order_id):
            sale_order = order.origin_so_id or order.commission_sale_order_id
            order.message_post(
                body=f"Commission purchase order confirmed for sale order {sale_order.name}"
            )
        
        return result

    def button_cancel(self):
        """Override cancel to handle commission-specific logic."""
        for order in self.filtered(lambda o: o.origin_so_id or o.commission_sale_order_id):
            if order.commission_posted:
                raise UserError(
                    f"Cannot cancel commission purchase order {order.name} "
                    "because it has already been posted."
                )
        
        result = super().button_cancel()
        
        # Reset commission status on source sale order if needed
        for order in self.filtered(lambda o: o.origin_so_id or o.commission_sale_order_id):
            sale_order = order.origin_so_id or order.commission_sale_order_id
            if sale_order:
                sale_order.message_post(
                    body=f"Commission purchase order {order.name} has been cancelled."
                )
        
        return result

    def unlink(self):
        """Override unlink to prevent deletion of posted commission POs."""
        for order in self:
            sale_order = order.origin_so_id or order.commission_sale_order_id
            if sale_order and order.commission_posted:
                raise UserError(
                    f"Cannot delete commission purchase order {order.name} "
                    "because it has been posted."
                )
        
        return super().unlink()

    @api.model
    def _cron_check_commission_purchase_orders(self):
        """
        Scheduled action to check and post commission purchase orders 
        when their receipts are validated or payments are made.
        """
        # Find unposted commission purchase orders
        unposted_commission_pos = self.search([
            ('commission_posted', '=', False),
            '|',
            ('origin_so_id', '!=', False),
            ('commission_sale_order_id', '!=', False),
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
        result = super().write(vals)

        # Track state changes for commission POs
        if 'state' in vals:
            for order in self.filtered(lambda o: o.origin_so_id or o.commission_sale_order_id):
                sale_order = order.origin_so_id or order.commission_sale_order_id
                if sale_order:
                    sale_order.message_post(
                        body=f"Commission purchase order {order.name} state changed to {order.state}"
                    )

        return result

    def action_auto_create_commission(self):
        """Automatically create a commission line from this PO if not already created"""
        self.ensure_one()

        if self.commission_line_id:
            raise UserError("Commission line is already linked to this purchase order.")

        sale_order = self.origin_so_id or self.commission_sale_order_id
        if not sale_order:
            raise UserError("This purchase order is not linked to any sale order.")

        # Get the vendor partner
        vendor = self.partner_id

        # Calculate total PO amount
        po_amount = sum(line.price_subtotal for line in self.order_line)

        try:
            # Create commission line
            commission_line = self.env['commission.line'].create({
                'sale_order_id': sale_order.id,
                'partner_id': vendor.id,
                'role': 'broker',  # Default role for PO-based commissions
                'commission_category': 'external',
                'calculation_method': 'fixed',
                'calculation_base': 'order_total_untaxed',
                'rate': 0.0,
                'commission_amount': po_amount,
            })

            # Link the commission to this PO
            self.commission_line_id = commission_line.id
            commission_line.purchase_order_id = self.id

            _logger.info(f"Auto-created commission line {commission_line.id} for PO {self.name}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Commission line created automatically for {vendor.name}. Amount: {po_amount:.2f}',
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(f"Failed to create commission line: {str(e)}")