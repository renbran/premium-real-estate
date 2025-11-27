from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrderEnhanced(models.Model):
    _inherit = 'sale.order'

    # Add tracking fields for monitoring
    commission_last_modified = fields.Datetime(string="Commission Last Modified", readonly=True)
    commission_modified_by = fields.Many2one('res.users', string="Commission Modified By", readonly=True)
    
    # Enhanced constraints and validations
    @api.constrains('consultant_comm_percentage', 'manager_comm_percentage', 
                    'second_agent_comm_percentage', 'director_comm_percentage',
                    'broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate',
                    'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _check_commission_rates_enhanced(self):
        """Enhanced validation for commission rates"""
        for order in self:
            # Check for negative rates
            rate_fields = [
                'consultant_comm_percentage', 'manager_comm_percentage',
                'second_agent_comm_percentage', 'director_comm_percentage',
                'broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate',
                'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate'
            ]
            
            for field in rate_fields:
                if getattr(order, field, 0) < 0:
                    raise ValidationError(f"Commission rate for {field} cannot be negative")
            
            # Check total commission doesn't exceed sale amount
            if order.total_commission_amount > order.amount_total:
                raise ValidationError(
                    f"Total commission amount ({order.total_commission_amount}) "
                    f"cannot exceed sale amount ({order.amount_total})"
                )

    @api.constrains('state', 'commission_processed')
    def _check_commission_processing_constraints(self):
        """Ensure commissions can only be processed under correct conditions"""
        for order in self:
            if order.commission_processed and order.state not in ['sale', 'done']:
                raise ValidationError(
                    "Commissions can only be processed for confirmed sale orders"
                )
    
    @api.constrains('invoice_status', 'commission_status')
    def _check_invoice_commission_consistency(self):
        """Ensure commission status aligns with invoice status"""
        for order in self:
            if order.commission_status == 'confirmed' and order.invoice_status != 'invoiced':
                raise ValidationError(
                    "Cannot confirm commissions without posting invoices"
                )

    # Field monitoring with @api.onchange
    @api.onchange('consultant_id', 'manager_id', 'second_agent_id', 'director_id',
                  'broker_partner_id', 'referrer_partner_id', 'cashback_partner_id',
                  'other_external_partner_id', 'agent1_partner_id', 'agent2_partner_id',
                  'manager_partner_id', 'director_partner_id')
    def _onchange_commission_partners(self):
        """Monitor partner changes and reset commission status if needed"""
        if self.commission_processed:
            return {
                'warning': {
                    'title': 'Commission Partner Changed',
                    'message': 'Changing commission partners will reset the commission status to draft. '
                              'You will need to recalculate commissions.',
                }
            }

    @api.onchange('consultant_comm_percentage', 'manager_comm_percentage',
                  'second_agent_comm_percentage', 'director_comm_percentage',
                  'broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate',
                  'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _onchange_commission_rates(self):
        """Monitor rate changes and provide warnings"""
        # Calculate total percentage for legacy fields
        total_legacy_percentage = (
            (self.consultant_comm_percentage or 0) +
            (self.manager_comm_percentage or 0) +
            (self.second_agent_comm_percentage or 0) +
            (self.director_comm_percentage or 0)
        )
        
        if total_legacy_percentage > 100:
            return {
                'warning': {
                    'title': 'High Commission Percentage',
                    'message': f'Total legacy commission percentage is {total_legacy_percentage}%, '
                              'which exceeds 100%. Please review.',
                }
            }
        
        # Check if total commission would exceed sale amount
        if hasattr(self, 'amount_total') and self.amount_total > 0:
            estimated_total = self._estimate_total_commissions()
            if estimated_total > self.amount_total:
                return {
                    'warning': {
                        'title': 'High Commission Amount',
                        'message': f'Estimated total commission ({estimated_total}) '
                                  f'exceeds sale amount ({self.amount_total}). Please review.',
                    }
                }

    @api.onchange('broker_commission_type', 'referrer_commission_type',
                  'cashback_commission_type', 'other_external_commission_type',
                  'agent1_commission_type', 'agent2_commission_type',
                  'manager_commission_type', 'director_commission_type')
    def _onchange_commission_types(self):
        """Monitor commission type changes and provide guidance"""
        if self.commission_processed:
            return {
                'warning': {
                    'title': 'Commission Type Changed',
                    'message': 'Changing commission calculation types will affect commission amounts. '
                              'Consider recalculating commissions.',
                }
            }

    def _estimate_total_commissions(self):
        """Estimate total commission amount based on current settings"""
        total = 0
        
        # Legacy commissions
        if self.amount_total:
            total += (self.consultant_comm_percentage / 100) * self.amount_total
            total += (self.manager_comm_percentage / 100) * self.amount_total
            total += (self.second_agent_comm_percentage / 100) * self.amount_total
            total += (self.director_comm_percentage / 100) * self.amount_total
        
        # Modern commissions (simplified estimation)
        commission_fields = [
            ('broker_rate', 'broker_commission_type'),
            ('referrer_rate', 'referrer_commission_type'),
            ('cashback_rate', 'cashback_commission_type'),
            ('other_external_rate', 'other_external_commission_type'),
            ('agent1_rate', 'agent1_commission_type'),
            ('agent2_rate', 'agent2_commission_type'),
            ('manager_rate', 'manager_commission_type'),
            ('director_rate', 'director_commission_type'),
        ]
        
        for rate_field, type_field in commission_fields:
            rate = getattr(self, rate_field, 0)
            commission_type = getattr(self, type_field, 'percent_untaxed_total')
            
            if rate > 0:
                total += self._calculate_commission_amount(rate, commission_type, self)
        
        return total

    # Enhanced write method with detailed tracking
    def write(self, vals):
        """Enhanced write method with detailed change tracking"""
        commission_fields = [
            'consultant_id', 'consultant_comm_percentage',
            'manager_id', 'manager_comm_percentage',
            'second_agent_id', 'second_agent_comm_percentage',
            'director_id', 'director_comm_percentage',
            'broker_partner_id', 'broker_rate', 'broker_commission_type',
            'referrer_partner_id', 'referrer_rate', 'referrer_commission_type',
            'cashback_partner_id', 'cashback_rate', 'cashback_commission_type',
            'other_external_partner_id', 'other_external_rate', 'other_external_commission_type',
            'agent1_partner_id', 'agent1_rate', 'agent1_commission_type',
            'agent2_partner_id', 'agent2_rate', 'agent2_commission_type',
            'manager_partner_id', 'manager_rate', 'manager_commission_type',
            'director_partner_id', 'director_rate', 'director_commission_type'
        ]
        
        commission_changed = any(field in vals for field in commission_fields)
        
        # Track commission modifications
        if commission_changed:
            vals.update({
                'commission_last_modified': fields.Datetime.now(),
                'commission_modified_by': self.env.user.id
            })
            
            # Log detailed changes for audit trail
            for order in self:
                if order.commission_processed:
                    changes = []
                    for field in commission_fields:
                        if field in vals:
                            old_value = getattr(order, field, None)
                            new_value = vals[field]
                            if old_value != new_value:
                                changes.append(f"{field}: {old_value} → {new_value}")
                    
                    if changes:
                        order.message_post(
                            body=f"Commission settings modified by {self.env.user.name}:\n" +
                                 "\n".join(changes),
                            subject="Commission Settings Changed"
                        )
        
        result = super(SaleOrderEnhanced, self).write(vals)
        
        # Reset commission processing if relevant fields changed
        if commission_changed:
            for order in self:
                if order.commission_processed and order.commission_status != 'draft':
                    # Check if any commission POs are already confirmed
                    confirmed_pos = order.purchase_order_ids.filtered(
                        lambda po: po.state not in ['draft', 'cancel']
                    )
                    if confirmed_pos:
                        raise UserError(
                            f"Cannot modify commission settings because commission purchase orders "
                            f"are already confirmed: {', '.join(confirmed_pos.mapped('name'))}"
                        )
                    
                    # Reset to draft if changes are allowed
                    order.write({
                        'commission_processed': False,
                        'commission_status': 'draft'
                    })
        
        return result

    # Enhanced action methods with better validation
    def action_process_commissions(self):
        """Enhanced commission processing with better validation"""
        for order in self:
            # Pre-processing validations
            if order.state not in ['sale', 'done']:
                raise UserError("Can only process commissions for confirmed sale orders")
            
            if order.invoice_status not in ['invoiced', 'to invoice']:
                auto_process_invoices = self.env['ir.config_parameter'].sudo().get_param(
                    'commission_ax.require_invoices_for_commissions', default='true'
                )
                if auto_process_invoices.lower() == 'true':
                    raise UserError("Please create and post invoices before processing commissions")
            
            if order.amount_total <= 0:
                raise UserError("Cannot process commissions for orders with zero or negative amounts")
            
            # Check for duplicate partners
            all_partners = []
            commission_entries = order._get_commission_entries()
            for entry in commission_entries:
                if entry['partner'].id in [p.id for p in all_partners]:
                    raise UserError(
                        f"Duplicate commission partner detected: {entry['partner'].name}. "
                        "Please ensure each partner appears only once in commission settings."
                    )
                all_partners.append(entry['partner'])
        
        return super(SaleOrderEnhanced, self).action_process_commissions()

    @api.model
    def _cron_validate_commission_consistency(self):
        """Scheduled action to validate commission data consistency"""
        _logger.info("Starting commission consistency validation")
        
        # Find orders with inconsistent states
        inconsistent_orders = self.search([
            ('commission_processed', '=', True),
            ('commission_status', '=', 'draft')
        ])
        
        for order in inconsistent_orders:
            order.message_post(
                body="Warning: Commission processed but status is still draft. Please review.",
                subject="Commission Status Inconsistency Detected"
            )
        
        # Check for orphaned purchase orders
        orphaned_pos = self.env['purchase.order'].search([
            ('origin_so_id', '!=', False),
            ('origin_so_id.commission_processed', '=', False)
        ])
        
        for po in orphaned_pos:
            po.message_post(
                body="Warning: Commission PO exists but source SO shows commissions not processed.",
                subject="Orphaned Commission PO Detected"
            )
        
        _logger.info(f"Commission consistency validation completed. "
                    f"Found {len(inconsistent_orders)} inconsistent orders and "
                    f"{len(orphaned_pos)} orphaned POs")

    def action_validate_commission_setup(self):
        """Manual action to validate commission setup before processing"""
        for order in self:
            warnings = []
            errors = []
            
            # Check for missing partners
            if order.total_commission_amount > 0:
                commission_entries = order._get_commission_entries()
                if not commission_entries:
                    errors.append("Commission amounts calculated but no commission partners assigned")
            
            # Check for unrealistic commission percentages
            if order.total_commission_amount > order.amount_total * 0.5:  # 50% threshold
                warnings.append("Total commission exceeds 50% of sale amount")
            
            # Check for inactive partners
            all_partners = []
            for entry in order._get_commission_entries():
                if not entry['partner'].active:
                    errors.append(f"Inactive partner assigned: {entry['partner'].name}")
                all_partners.append(entry['partner'])
            
            # Compile results
            message_parts = []
            if errors:
                message_parts.append("❌ ERRORS:\n" + "\n".join(f"• {error}" for error in errors))
            if warnings:
                message_parts.append("⚠️ WARNINGS:\n" + "\n".join(f"• {warning}" for warning in warnings))
            
            if not errors and not warnings:
                message_parts.append("✅ All commission validations passed")
            
            if errors:
                raise UserError("\n\n".join(message_parts))
            elif warnings:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Commission Validation',
                        'message': "\n\n".join(message_parts),
                        'type': 'warning',
                        'sticky': True,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Commission Validation',
                        'message': "✅ All commission validations passed",
                        'type': 'success',
                    }
                }