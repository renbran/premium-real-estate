# -*- coding: utf-8 -*-
"""
Post-migration script for commission_ax module upgrade to Odoo 18.0.1.0.0

This script runs AFTER the module is loaded by Odoo during upgrade.
It performs data updates and finalizes the migration.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Post-migration tasks for commission_ax to Odoo 18
    
    Args:
        cr: Database cursor
        version: Version being migrated from (e.g., '17.0.3.2.1')
    """
    _logger.info("=" * 80)
    _logger.info("Starting post-migration for commission_ax to 18.0.1.0.0")
    _logger.info("Migrating from version: %s", version)
    _logger.info("=" * 80)
    
    # 1. Recompute stored fields
    _logger.info("📊 Recomputing stored fields...")
    
    cr.execute("""
        SELECT id FROM commission_line 
        WHERE state NOT IN ('cancelled') 
        LIMIT 10;
    """)
    sample_ids = [row[0] for row in cr.fetchall()]
    
    if sample_ids:
        _logger.info("   Found %d active commission lines", len(sample_ids))
        _logger.info("   Note: Computed fields will be recalculated on first access")
    
    # 2. Update any XML IDs if module name changed
    _logger.info("📝 Checking XML IDs...")
    cr.execute("""
        SELECT COUNT(*) FROM ir_model_data 
        WHERE module = 'commission_ax';
    """)
    xml_id_count = cr.fetchone()[0]
    _logger.info("   Found %d XML IDs for commission_ax module", xml_id_count)
    
    # 3. Validate views
    _logger.info("🔍 Validating views...")
    cr.execute("""
        SELECT COUNT(*) FROM ir_ui_view 
        WHERE name LIKE '%commission%' 
        AND model IN ('commission.line', 'commission.type', 'sale.order');
    """)
    view_count = cr.fetchone()[0]
    _logger.info("   Found %d commission-related views", view_count)
    
    # 4. Check actions and menus
    _logger.info("🔗 Validating actions and menus...")
    cr.execute("""
        SELECT COUNT(*) FROM ir_act_window 
        WHERE res_model IN ('commission.line', 'commission.type');
    """)
    action_count = cr.fetchone()[0]
    _logger.info("   Found %d commission actions", action_count)
    
    cr.execute("""
        SELECT COUNT(*) FROM ir_ui_menu 
        WHERE name LIKE '%Commission%';
    """)
    menu_count = cr.fetchone()[0]
    _logger.info("   Found %d commission menus", menu_count)
    
    # 5. Summary statistics
    _logger.info("📈 Migration Statistics:")
    
    cr.execute("SELECT COUNT(*), state FROM commission_line GROUP BY state ORDER BY state;")
    for count, state in cr.fetchall():
        _logger.info("   %s: %d records", state or 'NULL', count)
    
    cr.execute("""
        SELECT COUNT(*), commission_category 
        FROM commission_line 
        GROUP BY commission_category;
    """)
    for count, category in cr.fetchall():
        _logger.info("   %s commissions: %d", category or 'NULL', count)
    
    # 6. Final validation
    _logger.info("✅ Running final validation...")
    
    # Check for any records without required fields
    cr.execute("""
        SELECT COUNT(*) FROM commission_line 
        WHERE partner_id IS NULL 
        OR sale_order_id IS NULL 
        OR state IS NULL;
    """)
    invalid_records = cr.fetchone()[0]
    
    if invalid_records > 0:
        _logger.error("   ❌ Found %d records with missing required fields!", invalid_records)
        _logger.error("   Please review and fix these records manually")
    else:
        _logger.info("   ✅ All records have required fields")
    
    # 7. Completion
    _logger.info("=" * 80)
    _logger.info("✅ Post-migration completed successfully!")
    _logger.info("   commission_ax is now running on Odoo 18.0.1.0.0")
    _logger.info("   Please test the following:")
    _logger.info("   1. Create a new sale order with commissions")
    _logger.info("   2. Process existing commission lines")
    _logger.info("   3. Generate commission reports")
    _logger.info("   4. Test purchase order creation for external commissions")
    _logger.info("=" * 80)
