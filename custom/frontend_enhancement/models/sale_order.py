# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """
    Extended Sale Order model to enhance frontend display of client order references
    """
    _inherit = 'sale.order'
    
    # Enhanced client order reference field with better display
    client_order_ref_display = fields.Char(
        string='Client Order Reference',
        compute='_compute_client_order_ref_display',
        store=True,
        help="Enhanced display of client order reference for frontend views"
    )
    
    # Additional fields for enhanced functionality
    order_reference_notes = fields.Text(
        string='Reference Notes',
        help="Additional notes related to the order reference"
    )
    
    reference_priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'), 
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='normal', string='Reference Priority')
    
    @api.depends('client_order_ref', 'name')
    def _compute_client_order_ref_display(self):
        """
        Compute enhanced display for client order reference
        """
        for order in self:
            if order.client_order_ref:
                order.client_order_ref_display = f"{order.client_order_ref} ({order.name})"
            else:
                order.client_order_ref_display = order.name or _('No Reference')
    
    @api.model
    def create(self, vals):
        """
        Override create to ensure proper reference handling
        """
        result = super(SaleOrder, self).create(vals)
        
        # Log order creation with reference information
        if result.client_order_ref:
            result.message_post(
                body=_("Order created with client reference: %s") % result.client_order_ref,
                subject=_("Order Reference Set")
            )
        
        return result
    
    def write(self, vals):
        """
        Override write to track reference changes
        """
        # Track changes to client order reference
        for order in self:
            old_ref = order.client_order_ref
            
        result = super(SaleOrder, self).write(vals)
        
        # Log reference changes
        if 'client_order_ref' in vals:
            for order in self:
                if order.client_order_ref != old_ref:
                    order.message_post(
                        body=_("Client order reference changed from '%s' to '%s'") % (
                            old_ref or _('None'), 
                            order.client_order_ref or _('None')
                        ),
                        subject=_("Order Reference Updated")
                    )
        
        return result
    
    def action_confirm(self):
        """
        Override action_confirm to transfer reference to invoice
        """
        result = super(SaleOrder, self).action_confirm()
        
        # Ensure client reference is transferred to invoices
        for order in self:
            if order.client_order_ref and order.invoice_ids:
                for invoice in order.invoice_ids:
                    if not invoice.ref:
                        invoice.ref = order.client_order_ref
                        invoice.message_post(
                            body=_("Customer reference inherited from sale order: %s") % order.client_order_ref,
                            subject=_("Reference Inherited")
                        )
        
        return result
    
    @api.model
    def search_by_reference(self, reference):
        """
        Enhanced search method for finding orders by reference
        """
        domain = [
            '|',
            ('client_order_ref', 'ilike', reference),
            ('name', 'ilike', reference)
        ]
        return self.search(domain)
    
    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
        Override to include reference information in portal URLs
        """
        url = super(SaleOrder, self).get_portal_url(
            suffix=suffix, 
            report_type=report_type, 
            download=download, 
            query_string=query_string, 
            anchor=anchor
        )
        
        # Add reference information to URL if available
        if self.client_order_ref:
            separator = '&' if '?' in url else '?'
            url += f"{separator}ref={self.client_order_ref}"
            
        return url
