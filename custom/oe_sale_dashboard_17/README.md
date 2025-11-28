# OSUS Executive Sales Dashboard

## Version 17.0.0.3.0

A beautiful, modern executive dashboard for Odoo 17 with advanced visualizations and business intelligence capabilities.

This module is under copyright of 'OdooElevate'

## ✨ Key Features

### 🎨 Modern Visual Design
- **Executive-Grade Interface**: Professional gradient backgrounds and modern card layouts
- **Interactive Charts**: Custom chart implementation with doughnut and line charts
- **Animated Components**: Smooth transitions and loading animations
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### 📊 Advanced Analytics
- **KPI Cards**: Key performance indicators with trend indicators
  - Total Pipeline Value
  - Revenue Realized
  - Conversion Rate
  - Average Deal Size

### 1. Date Range Filtering
- **Start Date & End Date**: Select custom date ranges for filtering sales data
- **Booking Date Reference**: All filtering is now based on `booking_date` instead of `order_date`

### 2. Amount Field Selection
- **Total Amount**: Uses the standard `amount_total` field from sale orders
- **Sale Value**: Uses a custom `sale_value` field that can be customized based on business logic

### 3. Enhanced Sale Order Model
- **booking_date**: New datetime field to track when sales were booked
- **sale_value**: New monetary field for alternative amount calculations
- **Automatic Migration**: Existing orders will have their booking_date initialized from date_order

## Changes Made

### Backend Changes
1. **New Model Fields**:
   - `booking_date`: Datetime field in sale.order model
   - `sale_value`: Monetary field in sale.order model

2. **Data Migration**:
   - Automatic initialization of booking_date for existing records
   - Default booking_date set to current date/time for new records

### Frontend Changes
1. **Date Range Selector**: Replaced single date picker with start/end date inputs
2. **Amount Field Dropdown**: Added dropdown to choose between Total Amount and Sale Value
3. **Simplified Table Layout**: Removed time period columns, showing only Company and Amount
4. **Real-time Updates**: Dashboard updates automatically when filters change

### UI/UX Improvements
1. **Responsive Design**: Better layout for different screen sizes
2. **Modern Styling**: Clean, professional appearance with proper spacing
3. **Loading Indicators**: Clear feedback during data loading
4. **User-friendly Labels**: Clear field names and descriptions

## Installation Notes

1. **Module Dependencies**: Requires `sale_management` module
2. **Field Migration**: The module will automatically migrate existing data on installation
3. **Database Changes**: New fields will be added to the sale_order table

## Usage

1. **Access**: Navigate to Sales → Sales Report from the main menu
2. **Date Range**: Set start and end dates to filter the reporting period
3. **Amount Field**: Choose between "Total Amount" or "Sale Value" for calculations
4. **Real-time Data**: Dashboard updates automatically when filters change

## Customization

The `sale_value` field computation can be customized in the `sale_order.py` model based on specific business requirements. Currently, it mirrors the `amount_total` field but can be modified to implement custom calculation logic.

## Technical Details

- **Module Version**: 17.0.0.1.1
- **Odoo Version**: 17.0
- **Framework**: OWL Components
- **Database**: PostgreSQL compatible
- **License**: AGPL-3

## Recent Updates & Bug Fixes

### v17.0.0.3.0
- Added dynamic field validation and fallbacks for optional dependencies
- Enhanced Chart.js loading with improved availability checks
- Added safe DOM element access utilities to prevent null reference errors
- Added comprehensive deployment and update scripts
- Added detailed documentation for deployment and troubleshooting

### v17.0.0.2.0
- Fixed JavaScript syntax error "Missing catch or finally after try"
- Added automatic try/catch wrapper for all dashboard methods
- Added enhanced error handling throughout the codebase
- Fixed potential memory leaks from unhandled exceptions
- Improved module stability and error resilience

### v17.0.0.1.9
- Added CDN fallback mechanism for Chart.js loading
- Added compatibility layer to handle method name discrepancies
- Fixed potential issues with chart creation methods
- Added improved error handling and logging

### v17.0.0.1.8
- Fixed missing catch block for trend analysis chart creation
- Added null checks for data access throughout the codebase
- Added proper chart cleanup before creating new ones
- Fixed safe array access with null checks
- Added safety checks before accessing object properties

### v17.0.0.1.7
- Initial implementation of the trend data generation method
- Fixed Chart.js loading and initialization
- Updated chart documentation

## Deployment Instructions

For detailed deployment instructions, see the [Deployment Guide](./docs/DEPLOYMENT_GUIDE.md).

### Quick Start

1. **Verify Dependencies**
   - The module works best with `osus_invoice_report` and `le_sale_type` but will adapt if they're not available

2. **Installation**
   - Copy the module to your Odoo addons directory
   - Run deployment script: `./deploy.sh` (Linux/Mac) or `.\deploy.ps1` (Windows)
   - Update the module in Odoo: `-u oe_sale_dashboard_17`

3. **Troubleshooting**
   - For common issues and solutions, see the [Issues Resolution Plan](./docs/ISSUES_RESOLUTION_PLAN.md)
   - Check browser console for JavaScript errors
   - Review server logs for Python errors

## Support

For technical support and customizations, contact OdooElevate at https://odooelevate.odoo.com/
