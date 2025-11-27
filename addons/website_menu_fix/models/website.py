# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'
    
    def get_safe_menu_data(self):
        """
        Get menu data safely for website templates.
        This replaces the problematic load_menus_root() call.
        """
        try:
            if not self.menu_id:
                return []
            
            menus = []
            for menu in self.menu_id.child_id:
                menu_data = {
                    'id': menu.id,
                    'name': menu.name,
                    'url': menu.url or '#',
                    'children': []
                }
                
                # Add children if they exist
                for child in menu.child_id:
                    child_data = {
                        'id': child.id,
                        'name': child.name,
                        'url': child.url or '#',
                    }
                    menu_data['children'].append(child_data)
                
                menus.append(menu_data)
            
            return menus
        except Exception as e:
            _logger.error(f"Error getting menu data: {e}")
            return []

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'
    
    @api.model
    def _render_template(self, template, values=None, engine='ir.qweb'):
        """Override template rendering to handle menu-related errors."""
        if values is None:
            values = {}
        
        try:
            # Add safe menu data to template context
            if 'website' in values and hasattr(values['website'], 'get_safe_menu_data'):
                values['safe_menu_data'] = values['website'].get_safe_menu_data()
            
            return super()._render_template(template, values, engine)
        except Exception as e:
            # If there's a menu-related error, log it and provide fallback
            if 'load_menus_root' in str(e) or "menu['action']" in str(e):
                _logger.error(f"Menu rendering error in template {template}: {e}")
                
                # Provide fallback values
                if 'website' in values:
                    values['safe_menu_data'] = values['website'].get_safe_menu_data()
                
                # Try rendering again with safe values
                return super()._render_template(template, values, engine)
            else:
                raise
