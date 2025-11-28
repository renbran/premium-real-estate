# -*- coding: utf-8 -*-
"""
Post-migration script for sales order status sync
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration: Sync order_status with sale state"""
    _logger.info("Running sales order status sync migration")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    updated_count = 0
    
    # 1. Fix confirmed/done orders
    confirmed_orders = env['sale.order'].search([
        ('state', 'in', ['sale', 'done']),
        ('order_status', 'not in', ['post', 'approved'])
    ])
    
    if confirmed_orders:
        _logger.info("Updating %d confirmed/done orders to order_status=post", len(confirmed_orders))
        for order in confirmed_orders:
            order.write({'order_status': 'post'})
            
            # Set workflow users if missing
            if not order.documentation_user_id and order.create_uid:
                order.documentation_user_id = order.create_uid
            
            if not order.commission_user_id and order.write_uid:
                order.commission_user_id = order.write_uid
            
            if not order.allocation_user_id and order.write_uid:
                order.allocation_user_id = order.write_uid
            
            if not order.final_review_user_id and order.write_uid:
                order.final_review_user_id = order.write_uid
            
            if not order.approval_user_id and order.write_uid:
                order.approval_user_id = order.write_uid
            
            if not order.posting_user_id and order.write_uid:
                order.posting_user_id = order.write_uid
                
        updated_count += len(confirmed_orders)
    
    # 2. Fix draft orders with advanced statuses
    draft_orders = env['sale.order'].search([
        ('state', '=', 'draft'),
        ('order_status', 'not in', ['draft', 'document_review'])
    ])
    
    if draft_orders:
        _logger.info("Updating %d draft orders to order_status=draft", len(draft_orders))
        draft_orders.write({'order_status': 'draft'})
        updated_count += len(draft_orders)
    
    _logger.info("Sales order status migration completed. Updated %d orders.", updated_count)
