# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    # AI Tech Theme Colors
    ai_theme_primary_color = fields.Char(
        string='Primary Theme Color',
        default='#0ea5e9',  # Cyan
        help='Main brand color for headers, buttons, and primary elements'
    )
    
    ai_theme_secondary_color = fields.Char(
        string='Secondary Theme Color',
        default='#8b5cf6',  # Purple
        help='Secondary accent color for highlights and effects'
    )
    
    ai_theme_accent_color = fields.Char(
        string='Accent Color',
        default='#06b6d4',  # Bright Cyan
        help='Accent color for interactive elements and notifications'
    )
    
    ai_theme_dark_bg = fields.Char(
        string='Dark Background Color',
        default='#0f172a',  # Dark Blue-Gray
        help='Main background color for dark mode'
    )
    
    ai_theme_sidebar_bg = fields.Char(
        string='Sidebar Background',
        default='#1e293b',  # Lighter Dark Blue-Gray
        help='Background color for sidebar and navigation'
    )
    
    # Typography
    ai_theme_font_family = fields.Selection([
        ('Inter', 'Inter (Modern Sans)'),
        ('Roboto', 'Roboto'),
        ('Poppins', 'Poppins'),
        ('Montserrat', 'Montserrat'),
        ('IBM Plex Sans', 'IBM Plex Sans (Tech)'),
    ], string='Font Family', default='Inter',
        help='Main font family for the interface')
    
    # Branding
    ai_theme_app_name = fields.Char(
        string='Application Name',
        default='OSUS ERP',
        help='Custom application name displayed in login and header'
    )
    
    ai_theme_tagline = fields.Char(
        string='Tagline',
        default='Powered by AI Technology',
        help='Tagline displayed on login page'
    )
    
    ai_theme_login_bg_image = fields.Binary(
        string='Login Background Image',
        help='Custom background image for login page'
    )
    
    ai_theme_favicon = fields.Binary(
        string='Favicon',
        help='Custom favicon (ICO file)'
    )
    
    # Effects
    ai_theme_enable_glassmorphism = fields.Boolean(
        string='Enable Glassmorphism',
        default=True,
        help='Enable glass-like transparency effects'
    )
    
    ai_theme_enable_animations = fields.Boolean(
        string='Enable Animations',
        default=True,
        help='Enable smooth transitions and animations'
    )
    
    ai_theme_enable_gradients = fields.Boolean(
        string='Enable Gradients',
        default=True,
        help='Enable gradient backgrounds and effects'
    )
    
    ai_theme_enable_particles = fields.Boolean(
        string='Enable Particle Effects',
        default=False,
        help='Enable animated particle effects on login page'
    )
