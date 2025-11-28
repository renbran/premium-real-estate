# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """
    Extended Account Move (Invoice) model to enhance customer reference display
    """
    _inherit = 'account.move'
    
    # Enhanced customer reference field with better display
    customer_reference_display = fields.Char(
        string='Customer Reference',
        compute='_compute_customer_reference_display',
        store=True,
        help="Enhanced display of customer reference for frontend views"
    )
    
    # Additional fields for enhanced functionality
    reference_source = fields.Selection([
        ('manual', 'Manual Entry'),
        ('sale_order', 'From Sale Order'),
        ('purchase_order', 'From Purchase Order'),
        ('other', 'Other')
    ], default='manual', string='Reference Source')
    
    reference_validated = fields.Boolean(
        string='Reference Validated',
        default=False,
        help="Indicates if the customer reference has been validated"
    )
    
    reference_validation_date = fields.Datetime(
        string='Reference Validation Date',
        help="Date when the reference was validated"
    )
    
    @api.depends('ref', 'name', 'invoice_origin')
    def _compute_customer_reference_display(self):
        """
        Compute enhanced display for customer reference
        """
        for move in self:
            display_parts = []
            
            if move.ref:
                display_parts.append(move.ref)
                
            if move.invoice_origin:
                display_parts.append(f"Origin: {move.invoice_origin}")
                
            if display_parts:
                move.customer_reference_display = " | ".join(display_parts)
            else:
                move.customer_reference_display = move.name or _('No Reference')
    
    @api.model
    def create(self, vals):
        """
        Override create to handle reference inheritance and validation
        """
        # Inherit reference from sale order if not provided
        if 'invoice_origin' in vals and not vals.get('ref'):
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order and sale_order.client_order_ref:
                vals['ref'] = sale_order.client_order_ref
                vals['reference_source'] = 'sale_order'
        
        result = super(AccountMove, self).create(vals)
        
        # Log invoice creation with reference information
        if result.ref:
            result.message_post(
                body=_("Invoice created with customer reference: %s") % result.ref,
                subject=_("Customer Reference Set")
            )
        
        return result
    
    def write(self, vals):
        """
        Override write to track reference changes
        """
        # Track changes to customer reference
        old_refs = {}
        for move in self:
            old_refs[move.id] = move.ref
            
        result = super(AccountMove, self).write(vals)
        
        # Log reference changes
        if 'ref' in vals:
            for move in self:
                old_ref = old_refs.get(move.id)
                if move.ref != old_ref:
                    move.message_post(
                        body=_("Customer reference changed from '%s' to '%s'") % (
                            old_ref or _('None'), 
                            move.ref or _('None')
                        ),
                        subject=_("Customer Reference Updated")
                    )
        
        return result
    
    def action_validate_reference(self):
        """
        Action to validate customer reference
        """
        self.ensure_one()
        if not self.ref:
            raise ValidationError(_("Cannot validate an empty reference."))
            
        self.write({
            'reference_validated': True,
            'reference_validation_date': fields.Datetime.now()
        })
        
        self.message_post(
            body=_("Customer reference validated: %s") % self.ref,
            subject=_("Reference Validated")
        )
        
        return True
    
    def action_reset_reference_validation(self):
        """
        Action to reset reference validation
        """
        self.ensure_one()
        self.write({
            'reference_validated': False,
            'reference_validation_date': False
        })
        
        self.message_post(
            body=_("Customer reference validation reset for: %s") % (self.ref or _('No Reference')),
            subject=_("Reference Validation Reset")
        )
        
        return True
    
    @api.model
    def search_by_customer_reference(self, reference):
        """
        Enhanced search method for finding invoices by customer reference
        """
        domain = [
            '|', '|',
            ('ref', 'ilike', reference),
            ('name', 'ilike', reference),
            ('invoice_origin', 'ilike', reference)
        ]
        return self.search(domain)
    
    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
        Override to include reference information in portal URLs
        """
        url = super(AccountMove, self).get_portal_url(
            suffix=suffix, 
            report_type=report_type, 
            download=download, 
            query_string=query_string, 
            anchor=anchor
        )
        
        # Add reference information to URL if available
        if self.ref:
            separator = '&' if '?' in url else '?'
            url += f"{separator}customer_ref={self.ref}"
            
        return url
    
    @api.constrains('ref')
    def _check_reference_format(self):
        """
        Validate customer reference format if needed
        """
        for move in self:
            if move.ref and len(move.ref) > 100:
                raise ValidationError(_("Customer reference must not exceed 100 characters."))
    
    def _get_invoice_reference(self):
        """
        Helper method to get the best available reference
        """
        self.ensure_one()
        return self.ref or self.invoice_origin or self.name
