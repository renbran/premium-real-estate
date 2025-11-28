# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class OrderStatusChangeWizard(models.TransientModel):
    _name = 'order.status.change.wizard'
    _description = 'Change Order Status Wizard'
    
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    current_status_id = fields.Many2one('order.status', string='Current Status', readonly=True)
    new_status_id = fields.Many2one('order.status', string='New Status', required=True)
    notes = fields.Text(string='Notes')
    
    # Helper fields for UI logic
    requires_documentation_user = fields.Boolean(
        compute='_compute_required_assignments',
        string="Requires Documentation User",
        store=False
    )
    requires_commission_user = fields.Boolean(
        compute='_compute_required_assignments',
        string="Requires Commission User",
        store=False
    )
    requires_review_user = fields.Boolean(
        compute='_compute_required_assignments',
        string="Requires Review User",
        store=False
    )
    
    # Assignment fields (shown conditionally)
    documentation_user_id = fields.Many2one(
        'res.users',
        string='Documentation User',
        domain=[('active', '=', True)]
    )
    commission_user_id = fields.Many2one(
        'res.users',
        string='Commission User',
        domain=[('active', '=', True)]
    )
    final_review_user_id = fields.Many2one(
        'res.users',
        string='Final Review User',
        domain=[('active', '=', True)]
    )
    
    # Additional wizard fields
    force_assign = fields.Boolean(
        string='Force Assignment',
        help="Force assignment even if user is not in required group"
    )
    send_notification = fields.Boolean(
        string='Send Notification',
        default=True,
        help="Send notification to assigned users"
    )
    
    @api.model
    def default_get(self, fields_list):
        """Set default values when opening the wizard"""
        res = super().default_get(fields_list)
        
        # Get order from context
        order_id = self.env.context.get('default_order_id')
        if order_id:
            order = self.env['sale.order'].browse(order_id)
            if order.exists():
                # Get current status from order
                current_status = self._get_current_order_status(order)
                if current_status:
                    res['current_status_id'] = current_status.id
                
                # Set current user assignments
                res.update({
                    'documentation_user_id': getattr(order, 'documentation_user_id', False) and order.documentation_user_id.id or False,
                    'commission_user_id': getattr(order, 'commission_user_id', False) and order.commission_user_id.id or False,
                    'final_review_user_id': getattr(order, 'final_review_user_id', False) and order.final_review_user_id.id or False,
                })
        
        return res
    
    def _get_current_order_status(self, order):
        """Get current status of the order"""
        # First check if order has a custom status field
        if hasattr(order, 'order_status_id') and order.order_status_id:
            return order.order_status_id
        
        # Map Odoo standard states to custom statuses
        status_mapping = {
            'draft': 'draft',
            'sent': 'documentation_progress',
            'sale': 'approved',
            'done': 'approved',
            'cancel': 'draft'
        }
        
        status_code = status_mapping.get(order.state, 'draft')
        return self.env['order.status'].search([('code', '=', status_code)], limit=1)
    
    @api.depends('new_status_id')
    def _compute_required_assignments(self):
        """Compute which user assignments are required for the new status"""
        for wizard in self:
            if wizard.new_status_id:
                wizard.requires_documentation_user = (
                    wizard.new_status_id.responsible_type == 'documentation'
                )
                wizard.requires_commission_user = (
                    wizard.new_status_id.responsible_type == 'commission'
                )
                wizard.requires_review_user = (
                    wizard.new_status_id.responsible_type == 'final_review'
                )
            else:
                wizard.requires_documentation_user = False
                wizard.requires_commission_user = False
                wizard.requires_review_user = False
    
    @api.onchange('current_status_id')
    def _onchange_current_status(self):
        """Limit available statuses based on current status"""
        domain = [('active', '=', True)]
        
        if self.current_status_id:
            # If next statuses are defined, use them; otherwise allow all non-current
            if self.current_status_id.next_status_ids:
                domain.append(('id', 'in', self.current_status_id.next_status_ids.ids))
            else:
                domain.append(('id', '!=', self.current_status_id.id))
        
        return {'domain': {'new_status_id': domain}}
    
    @api.onchange('new_status_id')
    def _onchange_new_status(self):
        """Auto-suggest notes based on status transition"""
        if self.new_status_id and self.current_status_id:
            suggestions = {
                'documentation_progress': _("Documentation process initiated. Please prepare all required documents."),
                'commission_progress': _("Commission calculation in progress. Please verify commission rates and calculations."),
                'final_review': _("Order submitted for final review. Please review all documentation and calculations."),
                'approved': _("Order approved for processing. Ready for confirmation."),
                'draft': _("Order returned to draft status for revision.")
            }
            
            if self.new_status_id.code in suggestions:
                self.notes = suggestions[self.new_status_id.code]
    
    @api.onchange('order_id')
    def _onchange_order_id(self):
        """Update current status when order changes"""
        if self.order_id:
            current_status = self._get_current_order_status(self.order_id)
            self.current_status_id = current_status.id if current_status else False
            
            # Load current assignments
            if hasattr(self.order_id, 'documentation_user_id'):
                self.documentation_user_id = self.order_id.documentation_user_id
            if hasattr(self.order_id, 'commission_user_id'):
                self.commission_user_id = self.order_id.commission_user_id
            if hasattr(self.order_id, 'final_review_user_id'):
                self.final_review_user_id = self.order_id.final_review_user_id
    
    def change_status(self):
        """Apply status change with validation"""
        self.ensure_one()
        
        try:
            # Validate transition is allowed
            self._validate_status_transition()
            
            # Validate required assignments
            self._validate_assignments()
            
            # Update assignments on the sale order
            self._update_assignments()
            
            # Apply the new status
            self._apply_status_change()
            
            # Create status history record
            self._create_status_history()
            
            # Send notifications if requested
            if self.send_notification:
                self._send_notifications()
            
            # Show success message
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Status Changed'),
                    'message': _('Order status changed to %s successfully.') % self.new_status_id.name,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error("Error changing order status: %s", str(e))
            raise UserError(_("Failed to change status: %s") % str(e))
    
    def _validate_status_transition(self):
        """Validate that the status transition is allowed"""
        if not self.current_status_id or not self.new_status_id:
            raise UserError(_("Both current and new status must be specified."))
        
        if self.current_status_id.id == self.new_status_id.id:
            raise UserError(_("Current and new status cannot be the same."))
        
        # Check if transition is explicitly allowed
        if (self.current_status_id.next_status_ids and 
            self.new_status_id.id not in self.current_status_id.next_status_ids.ids):
            allowed_statuses = ', '.join(self.current_status_id.next_status_ids.mapped('name'))
            raise UserError(
                _("The selected status transition is not allowed. "
                  "Allowed transitions from '%s' are: %s") % 
                (self.current_status_id.name, allowed_statuses)
            )
    
    def _apply_status_change(self):
        """Apply the new status to the order"""
        # Use the custom _change_status method if it exists, otherwise update directly
        if hasattr(self.order_id, '_change_status'):
            self.order_id._change_status(self.new_status_id.id, self.notes)
        else:
            # Fallback: update order status directly and handle state mapping
            self._update_order_status_and_state()
    
    def _update_order_status_and_state(self):
        """Update order status and corresponding Odoo state"""
        vals = {}
        
        # Update custom status if field exists
        if hasattr(self.order_id, 'order_status_id'):
            vals['order_status_id'] = self.new_status_id.id
        
        # Map custom status to Odoo standard states
        state_mapping = {
            'draft': 'draft',
            'documentation_progress': 'sent',
            'commission_progress': 'sale',
            'final_review': 'sale',
            'approved': 'sale',
        }
        
        if self.new_status_id.code in state_mapping:
            new_state = state_mapping[self.new_status_id.code]
            
            # Handle state transitions properly
            if new_state == 'sale' and self.order_id.state in ['draft', 'sent']:
                self.order_id.action_confirm()
            elif new_state == 'sent' and self.order_id.state == 'draft':
                vals['state'] = 'sent'
            elif new_state != self.order_id.state:
                vals['state'] = new_state
        
        if vals:
            self.order_id.write(vals)
    
    def _create_status_history(self):
        """Create a status history record"""
        self.env['order.status.history'].create({
            'order_id': self.order_id.id,
            'status_id': self.new_status_id.id,
            'previous_status_id': self.current_status_id.id,
            'user_id': self.env.user.id,
            'notes': self.notes or '',
        })
    
    def _send_notifications(self):
        """Send notifications to relevant users"""
        try:
            # Collect users to notify
            users_to_notify = []
            
            if self.requires_documentation_user and self.documentation_user_id:
                users_to_notify.append(self.documentation_user_id)
            if self.requires_commission_user and self.commission_user_id:
                users_to_notify.append(self.commission_user_id)
            if self.requires_review_user and self.final_review_user_id:
                users_to_notify.append(self.final_review_user_id)
            
            # Send notifications
            for user in users_to_notify:
                self._send_user_notification(user)
                
        except Exception as e:
            _logger.warning("Failed to send notifications: %s", str(e))
    
    def _send_user_notification(self, user):
        """Send notification to a specific user"""
        message = _("Order %s status changed to %s. You have been assigned as %s.") % (
            self.order_id.name,
            self.new_status_id.name,
            self.new_status_id.responsible_type.replace('_', ' ').title()
        )
        
        # Create activity
        self.env['mail.activity'].create({
            'res_id': self.order_id.id,
            'res_model': 'sale.order',
            'user_id': user.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': _('Order Status Change Assignment'),
            'note': message,
        })
    
    def _validate_assignments(self):
        """Validate required user assignments are present"""
        errors = []
        
        if self.requires_documentation_user and not self.documentation_user_id:
            errors.append(_("Documentation user must be assigned for this status."))
        
        if self.requires_commission_user and not self.commission_user_id:
            errors.append(_("Commission user must be assigned for this status."))
        
        if self.requires_review_user and not self.final_review_user_id:
            errors.append(_("Final review user must be assigned for this status."))
        
        # Validate user permissions (if not forcing assignment)
        if not self.force_assign:
            if self.documentation_user_id:
                self._validate_user_permissions(self.documentation_user_id, 'documentation')
            if self.commission_user_id:
                self._validate_user_permissions(self.commission_user_id, 'commission')
            if self.final_review_user_id:
                self._validate_user_permissions(self.final_review_user_id, 'final_review')
        
        if errors:
            raise UserError('\n'.join(errors))
    
    def _validate_user_permissions(self, user, role_type):
        """Validate that user has required permissions for the role"""
        # Define required groups for each role
        group_mapping = {
            'documentation': 'group_order_documentation_reviewer',
            'commission': 'group_order_commission_calculator', 
            'final_review': 'group_order_approval_manager'
        }
        
        required_group = group_mapping.get(role_type)
        if required_group:
            group_ref = f'order_status_override.{required_group}'
            try:
                group = self.env.ref(group_ref)
                if group not in user.groups_id:
                    raise UserError(
                        _("User %s does not have the required permissions for %s role. "
                          "Please assign them to the %s group or enable 'Force Assignment'.") %
                        (user.name, role_type.replace('_', ' ').title(), group.name)
                    )
            except ValueError:
                # Group doesn't exist, skip validation
                pass
    
    def _update_assignments(self):
        """Update user assignments on the sale order"""
        vals = {}
        
        # Check if fields exist before updating
        order_fields = self.order_id._fields
        
        if self.requires_documentation_user and self.documentation_user_id:
            if 'documentation_user_id' in order_fields:
                vals['documentation_user_id'] = self.documentation_user_id.id
            
        if self.requires_commission_user and self.commission_user_id:
            if 'commission_user_id' in order_fields:
                vals['commission_user_id'] = self.commission_user_id.id
            
        if self.requires_review_user and self.final_review_user_id:
            if 'final_review_user_id' in order_fields:
                vals['final_review_user_id'] = self.final_review_user_id.id
        
        if vals:
            self.order_id.write(vals)
            _logger.info("Updated user assignments on order %s: %s", self.order_id.name, vals)
    
    def action_cancel(self):
        """Cancel the wizard without making changes"""
        return {'type': 'ir.actions.act_window_close'}
    
    def action_force_change(self):
        """Force status change bypassing some validations"""
        self.force_assign = True
        return self.change_status()