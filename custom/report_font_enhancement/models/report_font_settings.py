# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ReportFontSettings(models.Model):
    _name = 'report.font.settings'
    _description = 'Report Font Enhancement Settings'
    _order = 'create_date desc'
    
    name = fields.Char(
        string='Setting Name',
        required=True,
        help="Descriptive name for this font setting"
    )
    
    report_type = fields.Selection([
        ('invoice', 'Invoice Reports'),
        ('financial', 'Financial Reports'),
        ('sale', 'Sales Reports'),
        ('purchase', 'Purchase Reports'),
        ('inventory', 'Inventory Reports'),
        ('hr', 'HR Reports'),
        ('all', 'All Reports'),
    ], string='Report Type', default='all', required=True)
    
    font_family = fields.Selection([
        ('system', 'System Default'),
        ('arial', 'Arial'),
        ('helvetica', 'Helvetica'),
        ('georgia', 'Georgia'),
        ('times', 'Times New Roman'),
        ('roboto', 'Roboto'),
        ('opensans', 'Open Sans'),
    ], string='Font Family', default='system', required=True)
    
    base_font_size = fields.Integer(
        string='Base Font Size (px)',
        default=12,
        help="Base font size in pixels"
    )
    
    header_font_size = fields.Integer(
        string='Header Font Size (px)',
        default=16,
        help="Header font size in pixels"
    )
    
    title_font_size = fields.Integer(
        string='Title Font Size (px)',
        default=20,
        help="Title font size in pixels"
    )
    
    font_weight = fields.Selection([
        ('normal', 'Normal'),
        ('bold', 'Bold'),
        ('lighter', 'Lighter'),
        ('bolder', 'Bolder'),
        ('600', '600'),
        ('700', '700'),
    ], string='Font Weight', default='normal')
    
    text_color = fields.Char(
        string='Text Color',
        default='#212529',
        help="Default text color in hex format"
    )
    
    background_color = fields.Char(
        string='Background Color',
        default='#ffffff',
        help="Default background color in hex format"
    )
    
    high_contrast_mode = fields.Boolean(
        string='High Contrast Mode',
        default=True,
        help="Enable high contrast mode for better visibility"
    )
    
    adaptive_transparency = fields.Boolean(
        string='Adaptive Transparency',
        default=True,
        help="Automatically adjust transparency based on background"
    )
    
    transparency_level = fields.Float(
        string='Transparency Level',
        default=0.9,
        help="Background transparency level (0.1 to 1.0)"
    )
    
    line_height = fields.Float(
        string='Line Height',
        default=1.4,
        help="Line height multiplier for better readability"
    )
    
    letter_spacing = fields.Float(
        string='Letter Spacing (px)',
        default=0.0,
        help="Letter spacing in pixels"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    apply_to_existing_reports = fields.Boolean(
        string='Apply to Existing Reports',
        default=True,
        help="Apply settings to existing reports"
    )
    
    css_custom = fields.Text(
        string='Custom CSS',
        help="Additional custom CSS rules"
    )
    
    @api.constrains('base_font_size', 'header_font_size', 'title_font_size')
    def _check_font_sizes(self):
        for record in self:
            if record.base_font_size < 8 or record.base_font_size > 24:
                raise ValidationError("Base font size must be between 8 and 24 pixels")
            if record.header_font_size < 10 or record.header_font_size > 32:
                raise ValidationError("Header font size must be between 10 and 32 pixels")
            if record.title_font_size < 12 or record.title_font_size > 48:
                raise ValidationError("Title font size must be between 12 and 48 pixels")
    
    @api.constrains('transparency_level')
    def _check_transparency_level(self):
        for record in self:
            if record.transparency_level < 0.1 or record.transparency_level > 1.0:
                raise ValidationError("Transparency level must be between 0.1 and 1.0")
    
    @api.constrains('text_color', 'background_color')
    def _check_color_format(self):
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
        for record in self:
            if not hex_pattern.match(record.text_color):
                raise ValidationError("Text color must be in hex format (#000000)")
            if not hex_pattern.match(record.background_color):
                raise ValidationError("Background color must be in hex format (#ffffff)")
    
    def get_css_rules(self):
        """Generate CSS rules based on current settings"""
        self.ensure_one()
        
        font_family_map = {
            'system': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'arial': 'Arial, sans-serif',
            'helvetica': 'Helvetica, Arial, sans-serif',
            'georgia': 'Georgia, serif',
            'times': '"Times New Roman", Times, serif',
            'roboto': 'Roboto, sans-serif',
            'opensans': '"Open Sans", sans-serif',
        }
        
        css_rules = f"""
        /* Report Font Enhancement - {self.name} */
        .report-font-enhanced,
        .o_report_layout_standard,
        .o_report_layout_boxed,
        .o_report_layout_clean,
        .report_content,
        .invoice-report,
        .financial-report {{
            font-family: {font_family_map.get(self.font_family, font_family_map['system'])} !important;
            font-size: {self.base_font_size}px !important;
            font-weight: {self.font_weight} !important;
            line-height: {self.line_height} !important;
            letter-spacing: {self.letter_spacing}px !important;
            color: {self.text_color} !important;
            background-color: rgba({self._hex_to_rgb(self.background_color)}, {self.transparency_level}) !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
            text-rendering: optimizeLegibility !important;
        }}
        
        .report-font-enhanced h1,
        .o_report_layout_standard h1,
        .o_report_layout_boxed h1,
        .o_report_layout_clean h1 {{
            font-size: {self.title_font_size}px !important;
            font-weight: bold !important;
            color: {self.text_color} !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
        }}
        
        .report-font-enhanced h2,
        .report-font-enhanced h3,
        .report-font-enhanced h4,
        .report-font-enhanced th,
        .o_report_layout_standard th,
        .o_report_layout_boxed th,
        .o_report_layout_clean th {{
            font-size: {self.header_font_size}px !important;
            font-weight: bold !important;
            color: {self.text_color} !important;
        }}
        
        .report-font-enhanced table,
        .o_report_layout_standard table,
        .o_report_layout_boxed table,
        .o_report_layout_clean table {{
            border-collapse: collapse !important;
            width: 100% !important;
        }}
        
        .report-font-enhanced td,
        .report-font-enhanced th,
        .o_report_layout_standard td,
        .o_report_layout_standard th,
        .o_report_layout_boxed td,
        .o_report_layout_boxed th,
        .o_report_layout_clean td,
        .o_report_layout_clean th {{
            padding: 8px 12px !important;
            border: 1px solid rgba({self._hex_to_rgb(self.text_color)}, 0.2) !important;
            vertical-align: top !important;
        }}
        
        .report-font-enhanced th,
        .o_report_layout_standard th,
        .o_report_layout_boxed th,
        .o_report_layout_clean th {{
            background-color: rgba({self._hex_to_rgb(self.text_color)}, 0.1) !important;
            font-weight: bold !important;
        }}
        
        .report-font-enhanced .amount,
        .report-font-enhanced .monetary,
        .o_report_layout_standard .amount,
        .o_report_layout_standard .monetary {{
            text-align: right !important;
            font-weight: {self.font_weight} !important;
        }}
        """
        
        if self.high_contrast_mode:
            css_rules += f"""
            .report-font-enhanced,
            .o_report_layout_standard,
            .o_report_layout_boxed,
            .o_report_layout_clean {{
                color: {self.text_color} !important;
                text-shadow: 0 0 1px rgba({self._hex_to_rgb(self._get_contrast_color())}, 0.5) !important;
            }}
            
            .report-font-enhanced th,
            .o_report_layout_standard th,
            .o_report_layout_boxed th,
            .o_report_layout_clean th {{
                background-color: {self.text_color} !important;
                color: {self.background_color} !important;
            }}
            """
        
        if self.css_custom:
            css_rules += f"\n/* Custom CSS */\n{self.css_custom}"
        
        return css_rules
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))
    
    def _get_contrast_color(self):
        """Get contrasting color for text shadow"""
        # Simple contrast calculation
        bg_rgb = [int(self.background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
        luminance = (0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]) / 255
        return '#000000' if luminance > 0.5 else '#ffffff'
    
    @api.model
    def get_active_settings(self, report_type='all'):
        """Get active font settings for a specific report type"""
        domain = [('active', '=', True)]
        if report_type != 'all':
            domain.extend(['|', ('report_type', '=', report_type), ('report_type', '=', 'all')])
        
        return self.search(domain, limit=1)
    
    def apply_settings(self):
        """Apply current settings to reports"""
        self.ensure_one()
        _logger.info(f"Applying font enhancement settings: {self.name}")
        return True
