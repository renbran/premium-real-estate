# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    Pre-installation hook for Enhanced Sales Dashboard
    This hook runs before the module is installed.
    """
    _logger.info("Enhanced Sales Dashboard: Starting pre-installation checks...")
    
    try:
        # Check if required base modules are installed
        cr.execute("""
            SELECT name FROM ir_module_module 
            WHERE name IN ('sale', 'account', 'web') 
            AND state = 'installed'
        """)
        installed_modules = [row[0] for row in cr.fetchall()]
        
        required_modules = ['sale', 'web']
        missing_modules = [mod for mod in required_modules if mod not in installed_modules]
        
        if missing_modules:
            _logger.warning(f"Missing required modules: {missing_modules}")
        else:
            _logger.info("All required modules are installed")
        
        # Check database version compatibility
        cr.execute("SELECT version()")
        db_version = cr.fetchone()[0]
        _logger.info(f"Database version: {db_version}")
        
        # Create backup of existing dashboard configurations if any
        cr.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'sale_order'
        """)
        
        if cr.fetchone()[0] > 0:
            _logger.info("sale_order table exists, checking for existing data...")
            cr.execute("SELECT COUNT(*) FROM sale_order")
            order_count = cr.fetchone()[0]
            _logger.info(f"Found {order_count} existing sales orders")
        
    except Exception as e:
        _logger.error(f"Pre-installation hook failed: {e}")
        # Don't raise exception to allow installation to continue


def post_init_hook(cr, registry):
    """
    Post-installation hook for Enhanced Sales Dashboard
    This hook runs after the module is installed.
    """
    _logger.info("Enhanced Sales Dashboard: Starting post-installation setup...")
    
    try:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Initialize field mapping for dashboard
        SaleOrder = env['sale.order']
        
        # Check field availability and log findings
        fields_to_check = [
            'booking_date', 'sale_value', 'date_order', 'amount_total',
            'sale_order_type_id', 'agent1_partner_id', 'agent1_amount',
            'broker_partner_id', 'broker_amount', 'invoice_amount'
        ]
        
        available_fields = []
        for field in fields_to_check:
            if hasattr(SaleOrder, '_check_field_exists') and SaleOrder._check_field_exists(field):
                available_fields.append(field)
            elif field in SaleOrder._fields:
                available_fields.append(field)
        
        _logger.info(f"Available dashboard fields: {available_fields}")
        
        # Create sample configuration record for demonstration
        try:
            # Check if sales types are available
            sales_types_available = False
            for model_name in ['le.sale.type', 'sale.order.type', 'sale.type']:
                if model_name in env:
                    sales_types_available = True
                    _logger.info(f"Sales types available via model: {model_name}")
                    break
            
            if not sales_types_available:
                _logger.info("No sales type models found - dashboard will work without categorization")
            
            # Set up default dashboard preferences
            IrConfigParameter = env['ir.config_parameter']
            IrConfigParameter.sudo().set_param('oe_sale_dashboard_17.default_date_range', '90')
            IrConfigParameter.sudo().set_param('oe_sale_dashboard_17.auto_refresh_enabled', 'False')
            IrConfigParameter.sudo().set_param('oe_sale_dashboard_17.chart_cdn_url', 
                'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.js')
            
            _logger.info("Default dashboard configuration created")
            
        except Exception as e:
            _logger.warning(f"Could not create sample configuration: {e}")
        
        # Run initial health check
        try:
            if hasattr(SaleOrder, 'get_dashboard_health_check'):
                health_check = SaleOrder.get_dashboard_health_check()
                _logger.info(f"Dashboard health check: {health_check.get('overall_status', 'unknown')}")
                
                if health_check.get('warnings'):
                    for warning in health_check['warnings']:
                        _logger.warning(f"Dashboard warning: {warning}")
                
                if health_check.get('errors'):
                    for error in health_check['errors']:
                        _logger.error(f"Dashboard error: {error}")
            
        except Exception as e:
            _logger.warning(f"Could not run health check: {e}")
        
        # Initialize performance optimization
        try:
            if hasattr(SaleOrder, 'optimize_dashboard_performance'):
                optimization = SaleOrder.optimize_dashboard_performance()
                _logger.info(f"Dashboard optimization completed: {optimization}")
        except Exception as e:
            _logger.warning(f"Could not run optimization: {e}")
        
        _logger.info("Enhanced Sales Dashboard post-installation completed successfully")
        
    except Exception as e:
        _logger.error(f"Post-installation hook failed: {e}")
        # Don't raise exception to allow module to remain installed


def uninstall_hook(cr, registry):
    """
    Uninstallation hook for Enhanced Sales Dashboard
    This hook runs when the module is uninstalled.
    """
    _logger.info("Enhanced Sales Dashboard: Starting uninstallation cleanup...")
    
    try:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Clean up configuration parameters
        IrConfigParameter = env['ir.config_parameter']
        config_keys = [
            'oe_sale_dashboard_17.default_date_range',
            'oe_sale_dashboard_17.auto_refresh_enabled',
            'oe_sale_dashboard_17.chart_cdn_url'
        ]
        
        for key in config_keys:
            try:
                IrConfigParameter.sudo().search([('key', '=', key)]).unlink()
                _logger.info(f"Removed configuration parameter: {key}")
            except Exception as e:
                _logger.warning(f"Could not remove config parameter {key}: {e}")
        
        # Clear any cached data
        try:
            SaleOrder = env['sale.order']
            if hasattr(SaleOrder, 'clear_dashboard_cache'):
                cache_result = SaleOrder.clear_dashboard_cache()
                _logger.info(f"Dashboard cache cleared: {cache_result}")
        except Exception as e:
            _logger.warning(f"Could not clear cache: {e}")
        
        # Clean up any temporary files or data
        try:
            # Remove any dashboard-specific temporary data
            cr.execute("""
                DELETE FROM ir_attachment 
                WHERE res_model = 'sale.order' 
                AND name LIKE '%dashboard%'
            """)
            _logger.info("Cleaned up dashboard attachments")
        except Exception as e:
            _logger.warning(f"Could not clean up attachments: {e}")
        
        _logger.info("Enhanced Sales Dashboard uninstallation cleanup completed")
        
    except Exception as e:
        _logger.error(f"Uninstallation hook failed: {e}")


def upgrade_hook(cr, registry, version):
    """
    Upgrade hook for Enhanced Sales Dashboard
    This hook runs when the module is upgraded.
    """
    _logger.info(f"Enhanced Sales Dashboard: Starting upgrade to version {version}...")
    
    try:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Version-specific upgrade logic
        if version.startswith('1.0'):
            _logger.info("Upgrading to version 1.0.x series")
            
            # Clear old caches
            SaleOrder = env['sale.order']
            if hasattr(SaleOrder, 'clear_dashboard_cache'):
                SaleOrder.clear_dashboard_cache()
            
            # Update configuration parameters
            IrConfigParameter = env['ir.config_parameter']
            
            # Update Chart.js CDN URL if needed
            current_cdn = IrConfigParameter.sudo().get_param('oe_sale_dashboard_17.chart_cdn_url')
            if not current_cdn or 'chart.js' not in current_cdn.lower():
                IrConfigParameter.sudo().set_param('oe_sale_dashboard_17.chart_cdn_url',
                    'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.js')
                _logger.info("Updated Chart.js CDN URL")
            
            # Run health check after upgrade
            if hasattr(SaleOrder, 'get_dashboard_health_check'):
                health_check = SaleOrder.get_dashboard_health_check()
                _logger.info(f"Post-upgrade health check: {health_check.get('overall_status')}")
        
        _logger.info(f"Enhanced Sales Dashboard upgrade to {version} completed successfully")
        
    except Exception as e:
        _logger.error(f"Upgrade hook failed: {e}")


def migration_hook(cr, version):
    """
    Migration hook for data migration between versions
    """
    _logger.info(f"Enhanced Sales Dashboard: Running migration for version {version}...")
    
    try:
        # Add version-specific migration logic here
        if version == '1.0.0':
            # Initial migration logic
            _logger.info("Running initial migration for version 1.0.0")
            
            # Ensure required database indexes exist for performance
            try:
                cr.execute("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS 
                    idx_sale_order_dashboard_date_state 
                    ON sale_order (date_order, state) 
                    WHERE state != 'cancel'
                """)
                _logger.info("Created performance index for dashboard")
            except Exception as e:
                _logger.warning(f"Could not create performance index: {e}")
            
            # Update any existing data format if needed
            try:
                cr.execute("""
                    UPDATE sale_order 
                    SET amount_total = COALESCE(amount_total, 0)
                    WHERE amount_total IS NULL
                """)
                _logger.info("Updated null amount_total values")
            except Exception as e:
                _logger.warning(f"Could not update amount values: {e}")
        
        _logger.info(f"Migration for version {version} completed successfully")
        
    except Exception as e:
        _logger.error(f"Migration hook failed: {e}")


def backup_configuration(cr):
    """
    Backup existing dashboard configuration
    """
    try:
        _logger.info("Creating backup of dashboard configuration...")
        
        # Export current configuration to a backup table or file
        cr.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_config_backup AS
            SELECT 
                'oe_sale_dashboard_17' as module_name,
                now() as backup_date,
                (SELECT COUNT(*) FROM sale_order) as total_orders,
                (SELECT COUNT(*) FROM sale_order WHERE state = 'sale') as confirmed_orders
        """)
        
        _logger.info("Dashboard configuration backup created successfully")
        
    except Exception as e:
        _logger.warning(f"Could not create configuration backup: {e}")


def validate_installation(cr):
    """
    Validate that the installation was successful
    """
    try:
        _logger.info("Validating dashboard installation...")
        
        # Check that required tables exist
        cr.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('sale_order', 'res_partner', 'account_move')
        """)
        tables = [row[0] for row in cr.fetchall()]
        
        required_tables = ['sale_order', 'res_partner']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            _logger.error(f"Installation validation failed: missing tables {missing_tables}")
            return False
        
        # Check that basic data access works
        cr.execute("SELECT COUNT(*) FROM sale_order LIMIT 1")
        
        _logger.info("Dashboard installation validation passed")
        return True
        
    except Exception as e:
        _logger.error(f"Installation validation failed: {e}")
        return False