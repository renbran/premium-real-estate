# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """Configuration settings for AI Tech White-Label theme."""
    
    _inherit = 'res.config.settings'

    # AI Tech Theme Colors
    ai_theme_primary_color = fields.Char(
        string='Primary Theme Color',
        related='company_id.ai_theme_primary_color',
        readonly=False,
        help='Main brand color for headers, buttons, and primary elements'
    )
    
    ai_theme_secondary_color = fields.Char(
        string='Secondary Theme Color',
        related='company_id.ai_theme_secondary_color',
        readonly=False,
        help='Secondary accent color for highlights and effects'
    )
    
    ai_theme_accent_color = fields.Char(
        string='Accent Color',
        related='company_id.ai_theme_accent_color',
        readonly=False,
        help='Accent color for interactive elements and notifications'
    )
    
    ai_theme_dark_bg = fields.Char(
        string='Dark Background Color',
        related='company_id.ai_theme_dark_bg',
        readonly=False,
        help='Main background color for dark mode'
    )
    
    ai_theme_sidebar_bg = fields.Char(
        string='Sidebar Background',
        related='company_id.ai_theme_sidebar_bg',
        readonly=False,
        help='Background color for sidebar and navigation'
    )
    
    # Typography
    ai_theme_font_family = fields.Selection(
        related='company_id.ai_theme_font_family',
        readonly=False,
        string='Font Family',
        help='Main font family for the interface'
    )
    
    # Branding
    ai_theme_app_name = fields.Char(
        string='Application Name',
        related='company_id.ai_theme_app_name',
        readonly=False,
        help='Custom application name displayed in login and header'
    )
    
    ai_theme_tagline = fields.Char(
        string='Tagline',
        related='company_id.ai_theme_tagline',
        readonly=False,
        help='Tagline displayed on login page'
    )
    
    ai_theme_login_bg_image = fields.Binary(
        string='Login Background Image',
        related='company_id.ai_theme_login_bg_image',
        readonly=False,
        help='Custom background image for login page'
    )
    
    ai_theme_favicon = fields.Binary(
        string='Favicon',
        related='company_id.ai_theme_favicon',
        readonly=False,
        help='Custom favicon (ICO file)'
    )
    
    # Effects
    ai_theme_enable_glassmorphism = fields.Boolean(
        string='Enable Glassmorphism',
        related='company_id.ai_theme_enable_glassmorphism',
        readonly=False,
        help='Enable glass-like transparency effects'
    )
    
    ai_theme_enable_animations = fields.Boolean(
        string='Enable Animations',
        related='company_id.ai_theme_enable_animations',
        readonly=False,
        help='Enable smooth transitions and animations'
    )
    
    ai_theme_enable_gradients = fields.Boolean(
        string='Enable Gradients',
        related='company_id.ai_theme_enable_gradients',
        readonly=False,
        help='Enable gradient backgrounds and effects'
    )
    
    ai_theme_enable_particles = fields.Boolean(
        string='Enable Particle Effects',
        related='company_id.ai_theme_enable_particles',
        readonly=False,
        help='Enable animated particle effects on login page'
    )
