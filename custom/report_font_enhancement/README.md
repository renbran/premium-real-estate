# Report Font Enhancement Module

## Overview
The Report Font Enhancement module provides advanced font styling and readability improvements for all Odoo reports. It features high contrast text, adaptive transparency, and dynamic font adjustments based on background colors.

## Features

### ✨ **High Contrast Font Styling**
- Automatically adjusts text color based on background luminance
- Enhanced text shadows for better readability
- Support for light and dark themes

### 🎨 **Adaptive Transparency**
- Smart background transparency that adjusts based on content
- Better readability over background images
- Smooth transitions between different transparency levels

### 📊 **Enhanced Table Styling**
- Professional table headers with gradients
- Zebra striping for better row distinction
- Hover effects for interactive tables
- Special styling for totals and subtotals

### 🌐 **Universal Compatibility**
- Works with all Odoo report layouts (Standard, Boxed, Clean)
- Compatible with custom report modules
- Supports RTL languages
- Print-friendly optimizations

### ⚙️ **Configurable Settings**
- Multiple font families (System, Arial, Helvetica, Georgia, Roboto, Open Sans)
- Adjustable font sizes for different elements
- Color customization with hex color picker
- Custom CSS support for advanced users

## Installation

1. Copy the module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Report Font Enhancement" module
4. The module will automatically apply enhancements to all reports

## Configuration

Navigate to **Settings > Report Enhancement > Font Settings** to configure:

- **Report Type**: Choose which reports to enhance (All, Invoice, Financial, etc.)
- **Font Family**: Select from predefined font families
- **Font Sizes**: Configure base, header, and title font sizes
- **Colors**: Set text and background colors
- **High Contrast Mode**: Enable for maximum readability
- **Adaptive Transparency**: Automatic transparency adjustments
- **Custom CSS**: Add your own styling rules

## Technical Features

### CSS Variables
The module uses CSS custom properties for consistent theming:
```css
--report-font-family
--report-font-size-base
--report-text-color
--report-background-color
--report-line-height
```

### JavaScript Enhancement
- Dynamic contrast calculation based on background luminance
- Mutation observer for dynamically loaded content
- System preference detection (dark mode, high contrast)
- Print mode optimizations

### Accessibility
- Support for `prefers-color-scheme: dark`
- Support for `prefers-contrast: high`
- Reduced motion support
- WCAG 2.1 AA compliant contrast ratios

## Browser Support
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## Print Optimization
- Automatic high contrast for PDF generation
- Optimized font sizes for print
- Proper page break handling
- Ink-saving color schemes

## Performance
- Lightweight CSS-only enhancements
- Minimal JavaScript overhead
- Non-blocking initialization
- Cached style calculations

## Customization

### Adding Custom Styles
1. Go to Font Settings
2. Open the "Custom CSS" tab
3. Add your CSS rules:

```css
/* Example: Custom invoice styling */
.invoice-report .amount {
    color: #2e7d32 !important;
    font-weight: 700 !important;
}
```

### Creating New Settings
You can create multiple font settings for different report types or user preferences.

## Troubleshooting

### Reports Not Enhanced
- Check if the module is installed and active
- Verify that font settings are applied and active
- Clear browser cache and refresh

### Print Issues
- Ensure print color adjustment is enabled in browser
- Check PDF generation settings
- Verify wkhtmltopdf configuration

### Custom Report Integration
For custom report modules, add the enhancement class:
```xml
<div class="report-enhanced">
    <!-- Your report content -->
</div>
```

## Support

For support and feature requests, please contact your system administrator or module developer.

## License
This module is licensed under LGPL-3.

## Changelog

### Version 1.0.0
- Initial release
- High contrast font styling
- Adaptive transparency
- Configurable settings
- Universal report compatibility
- Print optimizations
