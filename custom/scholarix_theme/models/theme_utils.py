# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ScholarixThemeUtils(models.AbstractModel):
    """
    Theme utilities for Scholarix AI Theme
    Provides helper methods for theme customization and AI-themed elements
    """
    _name = 'scholarix.theme.utils'
    _description = 'Scholarix Theme Utilities'
    
    @api.model
    def get_theme_colors(self):
        """Return the primary color palette for the theme"""
        return {
            'primary': '#00E5FF',
            'secondary': '#0D47A1',
            'accent': '#7C4DFF',
            'success': '#00E676',
            'warning': '#FFD600',
            'danger': '#FF5722',
            'dark': '#1A1A1A',
            'light': '#FFFFFF',
            'teal': '#00BCD4',
            'neon_blue': '#40C4FF',
            'orange': '#FF6D00',
            'purple': '#7C4DFF',
            'silver': '#E0E0E0'
        }
    
    @api.model
    def get_ai_icons(self):
        """Return AI-themed icon classes"""
        return {
            'brain': 'fas fa-brain',
            'robot': 'fas fa-robot',
            'microchip': 'fas fa-microchip',
            'network': 'fas fa-network-wired',
            'code': 'fas fa-code',
            'chart': 'fas fa-chart-line',
            'cogs': 'fas fa-cogs',
            'lightning': 'fas fa-bolt',
            'shield': 'fas fa-shield-alt',
            'rocket': 'fas fa-rocket'
        }
    
    @api.model
    def get_gradient_classes(self):
        """Return available gradient CSS classes"""
        return [
            'scholarix-gradient-primary',
            'scholarix-gradient-secondary',
            'scholarix-gradient-accent',
            'scholarix-gradient-holographic',
            'scholarix-gradient-tech',
            'scholarix-gradient-neon'
        ]
    
    @api.model
    def get_animation_classes(self):
        """Return available animation CSS classes"""
        return [
            'scholarix-glow',
            'scholarix-pulse',
            'scholarix-float',
            'scholarix-fade-in',
            'scholarix-slide-up',
            'scholarix-tech-scan',
            'scholarix-holographic'
        ]
