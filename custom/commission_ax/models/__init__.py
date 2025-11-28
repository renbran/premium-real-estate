# -*- coding: utf-8 -*-
"""
Commission Models Initialization with Robust Error Handling
==========================================================
"""

import logging
_logger = logging.getLogger(__name__)

# Core models (always load these first)
try:
    from . import commission_type
    _logger.info("✅ commission_type model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load commission_type: {str(e)}")

try:
    from . import commission_line
    _logger.info("✅ commission_line model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load commission_line: {str(e)}")

try:
    from . import commission_dashboard
    _logger.info("✅ commission_dashboard model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load commission_dashboard: {str(e)}")

try:
    from . import commission_report_generator
    _logger.info("✅ commission_report_generator model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load commission_report_generator: {str(e)}")

try:
    # Temporarily disabled due to missing database table
    # from . import commission_assignment
    _logger.info("⚠️  commission_assignment model temporarily disabled")
except Exception as e:
    _logger.error(f"❌ Failed to load commission_assignment: {str(e)}")

try:
    from . import sale_order
    _logger.info("✅ sale_order model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load sale_order: {str(e)}")

try:
    from . import purchase_order
    _logger.info("✅ purchase_order model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load purchase_order: {str(e)}")

try:
    from . import res_partner
    _logger.info("✅ res_partner model loaded")
except Exception as e:
    _logger.error(f"❌ Failed to load res_partner: {str(e)}")

# Advanced models (load with error handling)
try:
    from . import commission_ai_analytics
    _logger.info("✅ commission_ai_analytics model loaded")
except Exception as e:
    _logger.warning(f"⚠️  commission_ai_analytics not loaded: {str(e)}")

try:
    from . import commission_statement_line
    _logger.info("✅ commission_statement_line model loaded")
except Exception as e:
    _logger.warning(f"⚠️  commission_statement_line not loaded: {str(e)}")

_logger.info("🎯 Commission models initialization completed")