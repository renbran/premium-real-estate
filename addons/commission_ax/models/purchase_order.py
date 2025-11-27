from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    def action_force_post(self):
        """Post the purchase order (set state to 'purchase' if possible)."""
        self.ensure_one()
        if self.state not in ['draft', 'sent']:
            raise UserError("Only draft or sent purchase orders can be posted.")
        self.button_confirm()
        return True
    _inherit = 'purchase.order'

    # Commission-related fields for purchase orders
    description = fields.Text(
        string="Description",
        help="Additional description for the purchase order"
    )
    origin_so_id = fields.Many2one(
        'sale.order', 
        string="Origin Sale Order",
        help="The sale order that generated this commission purchase order"
    )
    commission_posted = fields.Boolean(
        string="Commission Posted", 
        default=False,
        help="Indicates if this commission purchase order has been posted"
    )
    is_commission_po = fields.Boolean(
        string="Is Commission PO",
        compute="_compute_is_commission_po",
        store=True,
        help="Indicates if this is a commission-related purchase order"
    )
    
    # Commission-related computed fields from origin sale order
    agent1_partner_id = fields.Many2one(
        'res.partner',
        string="Agent 1",
        compute="_compute_commission_fields",
        store=True,  # CRITICAL FIX: Changed to True for email template access
        help="Agent 1 from the origin sale order"
    )
    agent2_partner_id = fields.Many2one(
        'res.partner',
        string="Agent 2", 
        compute="_compute_commission_fields",
        store=True,  # CRITICAL FIX: Changed to True for email template access
        help="Agent 2 from the origin sale order"
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        compute="_compute_commission_fields",
        store=True,  # CRITICAL FIX: Changed to True for email template access
        help="Project from the origin sale order"
    )
    unit_id = fields.Many2one(
        'product.product',
        string="Unit",
        compute="_compute_commission_fields", 
        store=True,  # CRITICAL FIX: Changed to True for email template access
        help="Unit from the origin sale order"
    )

    @api.depends('origin_so_id')
    def _compute_is_commission_po(self):
        """Compute if this is a commission purchase order."""
        for po in self:
            po.is_commission_po = bool(po.origin_so_id)
    
    @api.depends('origin_so_id', 'origin_so_id.agent1_partner_id', 'origin_so_id.agent2_partner_id')
    def _compute_commission_fields(self):
        """Compute commission-related fields from origin sale order."""
        for po in self:
            if po.origin_so_id:
                # Safe field access with hasattr checks
                po.agent1_partner_id = po.origin_so_id.agent1_partner_id if hasattr(po.origin_so_id, 'agent1_partner_id') else False
                po.agent2_partner_id = po.origin_so_id.agent2_partner_id if hasattr(po.origin_so_id, 'agent2_partner_id') else False
                # project_id and unit_id might not exist in all sale.order implementations
                po.project_id = po.origin_so_id.project_id if hasattr(po.origin_so_id, 'project_id') else False
                po.unit_id = po.origin_so_id.unit_id if hasattr(po.origin_so_id, 'unit_id') else False
            else:
                po.agent1_partner_id = False
                po.agent2_partner_id = False
                po.project_id = False
                po.unit_id = False
                po.agent2_partner_id = False
                po.project_id = False
                po.unit_id = False

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle commission purchase orders."""
        for vals in vals_list:
            # If this is a commission PO with an origin sale order
            if vals.get('origin_so_id'):
                sale_order = self.env['sale.order'].browse(vals['origin_so_id'])
                if sale_order.exists():
                    _logger.info(
                        f"Creating commission PO from SO: {sale_order.name}"
                    )
        
        return super(PurchaseOrder, self).create(vals_list)

    def write(self, vals):
        """Override write to handle commission purchase order updates."""
        return super(PurchaseOrder, self).write(vals)

    def action_view_origin_sale_order(self):
        """Action to view the origin sale order."""
        self.ensure_one()
        if not self.origin_so_id:
            raise UserError("No origin sale order found for this purchase order.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Origin Sale Order',
            'res_model': 'sale.order',
            'res_id': self.origin_so_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.constrains('origin_so_id', 'partner_id')
    def _check_commission_partner(self):
        """Validate that commission partner is valid for the origin sale order."""
        for po in self:
            if po.origin_so_id and po.partner_id:
                # Get all commission partners from the origin sale order
                commission_partners = po.origin_so_id._get_all_commission_partners()
                if po.partner_id.id not in commission_partners:
                    raise ValidationError(
                        f"Partner '{po.partner_id.name}' is not configured as a commission "
                        f"partner in the origin sale order '{po.origin_so_id.name}'"
                    )

    def _get_commission_info(self):
        """Get commission information for this purchase order."""
        self.ensure_one()
        if not self.origin_so_id:
            return {}
        
        # Find which commission type this PO represents
        commission_info = {}
        sale_order = self.origin_so_id
        
        # Check all commission partners to find which one matches this PO
        commission_mappings = {
            'consultant': sale_order.consultant_id,
            'manager': sale_order.manager_id,
            'director': sale_order.director_id,
            'second_agent': sale_order.second_agent_id,
            'broker': sale_order.broker_partner_id,
            'referrer': sale_order.referrer_partner_id,
            'cashback': sale_order.cashback_partner_id,
            'other_external': sale_order.other_external_partner_id,
            'agent1': sale_order.agent1_partner_id,
            'agent2': sale_order.agent2_partner_id,
            'manager_partner': sale_order.manager_partner_id,
            'director_partner': sale_order.director_partner_id,
        }
        
        for commission_type, partner in commission_mappings.items():
            if partner and partner.id == self.partner_id.id:
                commission_info = {
                    'type': commission_type,
                    'partner': partner,
                    'sale_order': sale_order,
                    'customer_reference': sale_order.client_order_ref,
                }
                break
        
        return commission_info

    def unlink(self):
        """Override unlink to handle commission status updates."""
        for po in self:
            if po.origin_so_id and po.state not in ['draft', 'cancel']:
                raise UserError(
                    f"Cannot delete confirmed commission purchase order {po.name}. "
                    f"Please cancel it first."
                )
        
        return super(PurchaseOrder, self).unlink()
