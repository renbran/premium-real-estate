# -*- coding: utf-8 -*-
"""
Pre-migration script for commission_ax module upgrade to Odoo 18.0.1.0.0

This script runs BEFORE the module is loaded by Odoo during upgrade.
It performs data validation and prepares the database for the upgrade.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Pre-migration tasks for commission_ax to Odoo 18
    
    Args:
        cr: Database cursor
        version: Current installed version (e.g., '17.0.3.2.1')
    """
    _logger.info("=" * 80)
    _logger.info("Starting pre-migration for commission_ax from %s to 18.0.1.0.0", version)
    _logger.info("=" * 80)
    
    # Check if commission.line table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'commission_line'
        );
    """)
    table_exists = cr.fetchone()[0]
    
    if not table_exists:
        _logger.info("✅ Clean installation - no existing data to migrate")
        return
    
    _logger.info("📊 Existing commission_line table found - validating data...")
    
    # 1. Count existing records
    cr.execute("SELECT COUNT(*) FROM commission_line;")
    total_records = cr.fetchone()[0]
    _logger.info("   Found %d commission line records", total_records)
    
    # 2. Check for orphaned records (sale orders that don't exist)
    cr.execute("""
        SELECT COUNT(*) 
        FROM commission_line cl
        LEFT JOIN sale_order so ON cl.sale_order_id = so.id
        WHERE so.id IS NULL;
    """)
    orphaned_records = cr.fetchone()[0]
    
    if orphaned_records > 0:
        _logger.warning("   ⚠️  Found %d orphaned commission lines (sale order deleted)", orphaned_records)
        _logger.info("   Cleaning up orphaned records...")
        cr.execute("""
            DELETE FROM commission_line
            WHERE sale_order_id NOT IN (SELECT id FROM sale_order);
        """)
        _logger.info("   ✅ Cleaned up %d orphaned records", orphaned_records)
    
    # 3. Validate state values
    cr.execute("""
        SELECT DISTINCT state 
        FROM commission_line 
        WHERE state IS NOT NULL
        ORDER BY state;
    """)
    states = [row[0] for row in cr.fetchall()]
    _logger.info("   Current states in use: %s", states)
    
    valid_states = ['draft', 'calculated', 'confirmed', 'processed', 'paid', 'cancelled']
    invalid_states = [s for s in states if s not in valid_states]
    
    if invalid_states:
        _logger.warning("   ⚠️  Found invalid states: %s", invalid_states)
        _logger.info("   Converting invalid states to 'draft'...")
        cr.execute("""
            UPDATE commission_line
            SET state = 'draft'
            WHERE state NOT IN %s;
        """, (tuple(valid_states),))
        _logger.info("   ✅ Fixed invalid state values")
    
    # 4. Ensure company_id exists on all records
    cr.execute("""
        SELECT COUNT(*) 
        FROM commission_line 
        WHERE company_id IS NULL;
    """)
    null_company = cr.fetchone()[0]
    
    if null_company > 0:
        _logger.info("   Found %d records without company_id, setting default...", null_company)
        cr.execute("""
            UPDATE commission_line cl
            SET company_id = so.company_id
            FROM sale_order so
            WHERE cl.sale_order_id = so.id
            AND cl.company_id IS NULL;
        """)
        _logger.info("   ✅ Updated company_id for %d records", null_company)
    
    # 5. Check currency consistency
    cr.execute("""
        SELECT COUNT(*) 
        FROM commission_line cl
        JOIN sale_order so ON cl.sale_order_id = so.id
        WHERE cl.currency_id != so.currency_id;
    """)
    currency_mismatch = cr.fetchone()[0]
    
    if currency_mismatch > 0:
        _logger.warning("   ⚠️  Found %d records with currency mismatch", currency_mismatch)
        _logger.info("   Synchronizing currency with sale order...")
        cr.execute("""
            UPDATE commission_line cl
            SET currency_id = so.currency_id
            FROM sale_order so
            WHERE cl.sale_order_id = so.id
            AND cl.currency_id != so.currency_id;
        """)
        _logger.info("   ✅ Fixed currency mismatch for %d records", currency_mismatch)
    
    # 6. Summary
    cr.execute("SELECT COUNT(*) FROM commission_line;")
    final_count = cr.fetchone()[0]
    
    _logger.info("=" * 80)
    _logger.info("✅ Pre-migration completed successfully!")
    _logger.info("   Total records: %d", final_count)
    _logger.info("   Ready for Odoo 18 upgrade")
    _logger.info("=" * 80)
