# OSUS Invoice Report - Bulk Printing Enhancement

## Overview
Enhanced OSUS Invoice Report module with comprehensive bulk printing functionality for efficient document management.

## New Features

### 🖨️ Bulk Printing Capabilities
- **Bulk Print Customer Invoices**: Print multiple customer invoices in a single PDF
- **Bulk Print Vendor Bills**: Print multiple vendor bills in a single PDF  
- **Bulk Print Mixed Documents**: Print any combination of invoices, bills, and credit notes in one PDF

### 📋 Features Include:
- **Cover Page**: Automatically generated summary page with document overview
- **Document Summary Table**: Lists all included documents with key details
- **Page Breaks**: Proper separation between individual documents
- **Professional Layout**: Maintains OSUS branding and formatting standards
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## How to Use

### Method 1: From List View Actions
1. Navigate to **Accounting > Customer Invoices** (or Bills)
2. Select multiple documents using checkboxes
3. Click **Actions** dropdown
4. Choose:
   - "Bulk Print Customer Invoices" (for invoices only)
   - "Bulk Print Vendor Bills" (for bills only)  
   - "Bulk Print All Documents" (for mixed document types)

### Method 2: From Dedicated Menu
1. Navigate to **Accounting > OSUS Bulk Print**
2. Choose from:
   - **Bulk Print Invoices**: Pre-filtered view of customer invoices
   - **Bulk Print Bills**: Pre-filtered view of vendor bills
   - **Bulk Print All Documents**: All posted accounting documents

### Method 3: From Form View
- Individual documents still have their single print buttons
- Use bulk printing for multiple documents only

## Technical Implementation

### New Models & Methods
```python
# In account.move model
def action_bulk_print_invoices()    # Bulk print customer invoices
def action_bulk_print_bills()       # Bulk print vendor bills  
def action_bulk_print_mixed()       # Bulk print mixed documents
```

### New Report Templates
- `report_osus_invoice_bulk_document`: Bulk invoice printing with cover page
- `report_osus_bill_bulk_document`: Bulk bill printing with cover page
- `report_osus_mixed_bulk_document`: Mixed document bulk printing
- `report_osus_single_invoice_content`: Reusable single invoice template

### New Report Actions
- `action_report_osus_invoice_bulk`: Bulk invoice report action
- `action_report_osus_bill_bulk`: Bulk bill report action
- `action_report_osus_mixed_bulk`: Mixed document report action

### Menu Structure
```
Accounting
└── OSUS Bulk Print
    ├── Bulk Print Invoices
    ├── Bulk Print Bills
    └── Bulk Print All Documents
```

## Cover Page Information
Each bulk print includes a professional cover page with:
- Document type and count
- Print date and user information
- Summary table with:
  - Document numbers
  - Customer/Vendor names
  - Amounts and currencies
  - Document dates
  - Total amount summary

## Error Handling
- Validates that at least one document is selected
- Filters documents by appropriate type for each action
- Provides clear error messages for invalid selections
- Falls back to standard Odoo reports if custom templates fail

## File Structure
```
osus_invoice_report/
├── models/
│   └── custom_invoice.py          # Enhanced with bulk print methods
├── views/
│   ├── account_move_views.xml     # Enhanced with bulk actions
│   └── bulk_print_menus.xml       # New menu structure
├── report/
│   ├── report_action.xml          # Enhanced with bulk actions
│   └── bulk_report.xml            # New bulk report templates
├── static/src/
│   └── js/
│       └── bulk_print_controller.js # Frontend enhancements
└── __manifest__.py                # Updated dependencies
```

## Benefits
- **Time Saving**: Print multiple documents at once
- **Professional Output**: Consistent formatting with cover pages
- **Document Management**: Easy tracking with summary tables
- **User Friendly**: Multiple access methods for different workflows
- **Flexible**: Supports mixed document types in single print job

## Requirements
- Odoo 17.0
- account module
- qrcode Python library
- num2words Python library

## Installation
1. Copy module to addons directory
2. Update apps list
3. Install "OSUS Invoice Report" module
4. New bulk print options will be available immediately

## Usage Tips
- Select documents of the same type for best results
- Use "Mixed Documents" option for combining different document types
- Cover page provides quick overview of all included documents
- Large bulk prints are automatically paginated for readability

## Support
For technical support or feature requests, contact OSUS Real Estate development team.

---
**Version**: 17.0.1.0.0
**Author**: OSUS Real Estate
**License**: LGPL-3
