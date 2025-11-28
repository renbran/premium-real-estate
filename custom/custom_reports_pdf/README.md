# SCHOLARIX Custom PDF Reports

## 📋 Overview

This Odoo module provides professionally designed PDF reports for invoices and sales orders with SCHOLARIX Global Consultants branding. The module includes custom QWeb templates, CSS styling, and enhanced PDF generation capabilities.

## ✨ Features

### 🎨 **Professional Design**
- Custom SCHOLARIX branding with circuit-style logo
- Modern gradient color scheme (#0080FF, #00FFFF, #1B365D)
- Professional typography using Inter font family
- Print-optimized A4 layout with proper margins

### 📄 **Invoice Reports**
- Enhanced invoice layout with company branding
- Detailed client information section
- Payment details and terms
- Itemized table with discount information
- Tax calculations and totals
- Terms & conditions section
- Professional footer with contact information

### 🛒 **Sales Order Reports**
- Professional quotation/sales order layout
- Customer information block
- Order details with salesperson info
- Product/service itemization
- Status indicators (Draft, Sent, Confirmed, etc.)
- Terms and conditions

### 🔧 **Technical Features**
- QWeb template inheritance
- Custom CSS styling
- PDF optimization for printing
- Responsive design elements
- Web controllers for enhanced PDF generation
- Security access controls

## 📁 Module Structure

```
custom_reports_pdf/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── models/
│   ├── __init__.py
│   ├── account_move.py
│   ├── sale_order.py
│   └── report_models.py
├── reports/
│   ├── report_actions.xml
│   ├── report_invoice_templates.xml
│   ├── report_sale_templates.xml
│   └── report_styles.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       └── css/
│           └── report_styles.css
└── views/
    ├── account_move_views.xml
    └── sale_order_views.xml
```

## 🚀 Installation

### Prerequisites
- Odoo 18.0
- Base, Account, and Sale modules installed

### Installation Steps

1. **Copy Module**: Copy the `custom_reports_pdf` folder to your Odoo addons directory:
   ```bash
   cp -r custom_reports_pdf /path/to/odoo/addons/
   ```

2. **Update Apps List**: In Odoo, go to Apps → Update Apps List

3. **Install Module**: Search for "SCHOLARIX Custom PDF Reports" and click Install

4. **Restart Odoo** (recommended): Restart your Odoo server for best results

## 💼 Usage

### 📄 Invoice Reports

1. **From Invoice Form**:
   - Open any customer invoice
   - Click the "📄 SCHOLARIX Invoice" button in the header
   - PDF will be generated and downloaded

2. **From Invoice List**:
   - Select one or more invoices
   - Go to Action → Print SCHOLARIX Invoice

3. **From Menu**:
   - Navigate to Accounting → Reporting → 📊 SCHOLARIX Reports → Invoice Reports

### 🛒 Sales Order Reports

1. **From Sales Order Form**:
   - Open any sales order/quotation
   - Click the "📄 SCHOLARIX Quotation" button in the header
   - PDF will be generated and downloaded

2. **From Sales Order List**:
   - Select one or more sales orders
   - Go to Action → Print SCHOLARIX Quotation

3. **From Menu**:
   - Navigate to Sales → 📊 SCHOLARIX Reports → Quotation Reports

## 🎨 Customization

### Company Information
The reports automatically pull company information from your Odoo company settings, but also include SCHOLARIX-specific branding:

- **Company Name**: SCHOLARIX Global Consultants
- **Tagline**: AI-Powered Business Transformation
- **Address**: Al Quijada, Abu Saif Business Center 201, Metro Station - Hor Al Anz, Dubai, UAE
- **Contact**: info@scholarixglobal.com, +971 058 624 1100

### Styling Customization
To customize the appearance:

1. Edit `/static/src/css/report_styles.css`
2. Modify colors, fonts, or layout as needed
3. Update Odoo to reload assets

### Template Customization
To modify report content:

1. Edit QWeb templates in `/reports/` directory
2. Update module to reload templates

## 🔧 Technical Details

### Dependencies
- `base`: Core Odoo functionality
- `account`: Invoice management
- `sale`: Sales order management
- `web`: Web interface and reporting

### Models Extended
- `account.move`: Invoice functionality
- `sale.order`: Sales order functionality
- Custom report models for data processing

### Reports Generated
- `custom_reports_pdf.report_scholarix_invoice_document`
- `custom_reports_pdf.report_scholarix_saleorder_document`

### Controllers
- PDF generation endpoints
- HTML preview endpoints
- Enhanced error handling

## 🛡️ Security

- Access rights configured for user groups
- Report access limited to authorized users
- Secure PDF generation endpoints

## 🐛 Troubleshooting

### Common Issues

1. **CSS Not Loading**:
   - Clear browser cache
   - Restart Odoo server
   - Update module

2. **PDF Generation Errors**:
   - Check server logs
   - Verify wkhtmltopdf installation
   - Check template syntax

3. **Missing Buttons**:
   - Verify module installation
   - Check user permissions
   - Clear browser cache

### Support

For technical support or customization requests:
- **Email**: info@scholarixglobal.com
- **Website**: https://scholarixglobal.com

## 📄 License

This module is licensed under LGPL-3.

## 👥 Credits

**Developed by**: SCHOLARIX Global Consultants  
**Website**: https://scholarixglobal.com  
**Version**: 18.0.1.0.0

---

© 2025 SCHOLARIX Global Consultants. All rights reserved.