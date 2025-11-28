# -*- coding: utf-8 -*-
"""
Pre-migration script for sales order status sync
"""

import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Pre-migration: Log current state"""
    _logger.info("Starting sales order status migration from version %s", version)
    
    # Count orders that need migration
    cr.execute("""
        SELECT 
            state,
            order_status,
            COUNT(*) as count
        FROM sale_order 
        WHERE (state IN ('sale', 'done') AND order_status NOT IN ('post', 'approved'))
           OR (state = 'draft' AND order_status NOT IN ('draft', 'document_review'))
        GROUP BY state, order_status
    """)
    
    results = cr.fetchall()
    _logger.info("Sales orders requiring migration: %s", results)
