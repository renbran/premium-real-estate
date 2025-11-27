# -*- coding: utf-8 -*-
"""
Pre-migration script for payment approval state sync
"""

import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Pre-migration: Log current state"""
    _logger.info("Starting payment approval state migration from version %s", version)
    
    # Count payments that need migration
    cr.execute("""
        SELECT 
            state,
            approval_state,
            COUNT(*) as count
        FROM account_payment 
        WHERE (state = 'posted' AND approval_state != 'posted')
           OR (state = 'cancel' AND approval_state != 'cancelled')
           OR (state = 'draft' AND approval_state NOT IN ('draft', 'under_review'))
        GROUP BY state, approval_state
    """)
    
    results = cr.fetchall()
    _logger.info("Payments requiring migration: %s", results)
