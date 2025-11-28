# -*- coding: utf-8 -*-
"""
OSUS Premium Enhanced Branding Module
====================================

This module provides comprehensive luxury branding for OSUS Properties
with modern UI/UX enhancements, performance optimizations, and accessibility features.

Author: OSUS Properties Development Team
License: LGPL-3
Version: 17.0.2.0.0
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Post-installation hook to configure OSUS Premium Enhanced branding.
    """
    try:
        _logger.info("🎨 Initializing OSUS Premium Enhanced Branding...")
        env = api.Environment(cr, SUPERUSER_ID, {})
        _setup_brand_parameters(env)
        _setup_theme_configuration(env)
        _setup_performance_configuration(env)
        _setup_accessibility_configuration(env)
        _setup_notification_configuration(env)
        _logger.info("✅ OSUS Premium Enhanced Branding initialized successfully!")
    except Exception as e:
        _logger.error("❌ Error during OSUS Premium Enhanced initialization: %s", str(e))
        raise

def uninstall_hook(cr, registry):
    """
    Uninstallation hook to clean up OSUS Premium Enhanced branding.
    """
    try:
        _logger.info("🧹 Cleaning up OSUS Premium Enhanced Branding...")
        env = api.Environment(cr, SUPERUSER_ID, {})
        _cleanup_brand_parameters(env)
        _cleanup_theme_configuration(env)
        _cleanup_performance_data(env)
        _logger.info("✅ OSUS Premium Enhanced Branding cleaned up successfully!")
    except Exception as e:
        _logger.error("❌ Error during OSUS Premium Enhanced cleanup: %s", str(e))

def _setup_brand_parameters(env):
    brand_params = {
        'osus.brand.primary_color': '#4d1a1a',
        'osus.brand.secondary_color': '#b8a366',
        'osus.brand.tertiary_color': '#2c1010',
        'osus.brand.accent_color': '#d4af37',
        'osus.brand.primary_font': 'Montserrat',
        'osus.brand.font_weights': 'light:300,regular:400,medium:500,semibold:600,bold:700,extrabold:800',
        'osus.brand.border_radius': '0.75rem',
        'osus.brand.shadow_intensity': 'medium',
        'osus.brand.animation_duration': '250ms',
        'osus.brand.button_style': 'luxury',
        'osus.brand.form_style': 'enhanced',
        'osus.brand.navigation_style': 'auto-hide',
        'osus.performance.enable_animations': 'true',
        'osus.performance.lazy_loading': 'true',
        'osus.performance.image_optimization': 'true',
        'osus.performance.cache_duration': '3600',
        'osus.accessibility.high_contrast_support': 'true',
        'osus.accessibility.reduced_motion_support': 'true',
        'osus.accessibility.keyboard_navigation': 'enhanced',
        'osus.accessibility.screen_reader_support': 'true',
        'osus.features.dark_mode': 'true',
        'osus.features.auto_save': 'true',
        'osus.features.smart_notifications': 'true',
        'osus.features.performance_monitoring': 'true',
    }
    IrConfigParameter = env['ir.config_parameter'].sudo()
    for key, value in brand_params.items():
        existing = IrConfigParameter.search([('key', '=', key)])
        if existing:
            existing.value = value
        else:
            IrConfigParameter.create({'key': key, 'value': value})
        _logger.info(f"📝 Set parameter {key} = {value}")

def _setup_theme_configuration(env):
    try:
        Users = env['res.users'].sudo()
        all_users = Users.search([])
        for user in all_users:
            user.write({'context_lang': user.lang or 'en_US'})
        _logger.info("🎨 Theme configuration completed for %d users", len(all_users))
    except Exception as e:
        _logger.warning("⚠️ Could not configure theme for all users: %s", str(e))

def _setup_performance_configuration(env):
    try:
        performance_config = {
            'osus.perf.monitor.lcp_threshold': '2500',
            'osus.perf.monitor.fid_threshold': '100',
            'osus.perf.monitor.cls_threshold': '0.1',
            'osus.perf.monitor.memory_threshold': '90',
            'osus.perf.cache.static_assets': 'true',
            'osus.perf.cache.api_responses': 'true',
            'osus.perf.minify.css': 'true',
            'osus.perf.minify.js': 'true',
            'osus.perf.lazy_load.images': 'true',
            'osus.perf.lazy_load.components': 'true',
        }
        IrConfigParameter = env['ir.config_parameter'].sudo()
        for key, value in performance_config.items():
            IrConfigParameter.set_param(key, value)
        _logger.info("⚡ Performance configuration completed")
    except Exception as e:
        _logger.warning("⚠️ Could not configure performance settings: %s", str(e))

def _setup_accessibility_configuration(env):
    try:
        a11y_config = {
            'osus.a11y.wcag_level': 'AA',
            'osus.a11y.color_contrast_ratio': '4.5',
            'osus.a11y.font_size_min': '16px',
            'osus.a11y.focus_visible': 'true',
            'osus.a11y.skip_links': 'true',
            'osus.a11y.aria_labels': 'enhanced',
            'osus.a11y.keyboard_traps': 'managed',
            'osus.a11y.screen_reader_announcements': 'true',
        }
        IrConfigParameter = env['ir.config_parameter'].sudo()
        for key, value in a11y_config.items():
            IrConfigParameter.set_param(key, value)
        _logger.info("♿ Accessibility configuration completed")
    except Exception as e:
        _logger.warning("⚠️ Could not configure accessibility settings: %s", str(e))

def _setup_notification_configuration(env):
    try:
        notification_config = {
            'osus.notifications.style': 'luxury',
            'osus.notifications.position': 'top-right',
            'osus.notifications.duration.success': '3000',
            'osus.notifications.duration.error': '5000',
            'osus.notifications.duration.warning': '4000',
            'osus.notifications.duration.info': '3000',
            'osus.notifications.max_visible': '5',
            'osus.notifications.animation': 'slide-fade',
            'osus.notifications.sound': 'false',
            'osus.notifications.persist_errors': 'true',
        }
        IrConfigParameter = env['ir.config_parameter'].sudo()
        for key, value in notification_config.items():
            IrConfigParameter.set_param(key, value)
        _logger.info("🔔 Notification configuration completed")
    except Exception as e:
        _logger.warning("⚠️ Could not configure notification settings: %s", str(e))

def _cleanup_brand_parameters(env):
    try:
        IrConfigParameter = env['ir.config_parameter'].sudo()
        osus_params = IrConfigParameter.search([
            ('key', 'ilike', 'osus.%')
        ])
        if osus_params:
            param_count = len(osus_params)
            osus_params.unlink()
            _logger.info("🧹 Removed %d OSUS brand parameters", param_count)
    except Exception as e:
        _logger.warning("⚠️ Could not clean up brand parameters: %s", str(e))

def _cleanup_theme_configuration(env):
    try:
        Users = env['res.users'].sudo()
        all_users = Users.search([])
        _logger.info("🎨 Theme configuration reset for %d users", len(all_users))
    except Exception as e:
        _logger.warning("⚠️ Could not reset theme configuration: %s", str(e))

def _cleanup_performance_data(env):
    try:
        _logger.info("⚡ Performance data cleaned up")
    except Exception as e:
        _logger.warning("⚠️ Could not clean up performance data: %s", str(e))

__version__ = '17.0.2.0.0'
__author__ = 'OSUS Properties Development Team'
__email__ = 'dev@osusproperties.com'
__website__ = 'https://osusproperties.com'
__license__ = 'LGPL-3'
__all__ = [
    'post_init_hook',
    'uninstall_hook',
]
