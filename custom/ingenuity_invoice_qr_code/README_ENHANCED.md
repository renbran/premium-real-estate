# QR Code for Invoice and Payment - Enhanced

## Overview
This module provides comprehensive QR code functionality for both **Invoices** and **Payments** in Odoo 17. The QR codes contain relevant document information and can be displayed on forms and printed on reports.

## Features

### Invoice QR Codes
- **Portal URL QR**: Contains secure portal link for invoice access
- **Form Display**: QR code visible on invoice form view
- **Report Integration**: QR code included in invoice PDF reports
- **Toggle Control**: Enable/disable QR code per invoice

### Payment QR Codes (NEW)
- **Payment Information QR**: Contains payment details (reference, amount, partner, date)
- **Form Display**: QR code visible on payment form view
- **Report Integration**: New payment voucher report with QR code
- **Receipt/Payment Types**: Supports both customer receipts and vendor payments
- **Toggle Control**: Enable/disable QR code per payment

## Installation
1. Install the module from Apps menu
2. QR codes will be automatically available on invoices and payments
3. Use the "Display QR Code in Report" checkbox to control visibility

## Configuration

### For Invoices
- Go to any invoice
- Check "Display QRCode in Report" field
- QR code appears automatically with portal URL

### For Payments
- Go to any payment record
- Check "Display QR Code in Report" field  
- QR code appears with payment information

## QR Code Content

### Invoice QR Contains:
- Secure portal URL for customer access
- Invoice details and payment information

### Payment QR Contains:
- Payment reference number
- Payment type (Receipt/Payment)
- Partner name
- Amount and currency
- Payment date
- Company information

## Reports
- **Invoice Report**: Enhanced with QR code display
- **Payment Voucher Report**: New report template with QR code support

## Technical Details
- **Models Extended**: `account.move`, `account.payment`
- **QR Library**: Uses `qrcode` Python library
- **Image Format**: PNG images encoded as base64
- **Field Names**: 
  - Invoice: `qr_image`, `qr_in_report`
  - Payment: `qr_code`, `qr_in_report`

## Compatibility
- **Odoo Version**: 17.0
- **Dependencies**: `web`, `account`
- **Module Conflicts**: Compatible with existing QR modules (uses different field names)

## Author
Ingenuity Info - Enhanced for comprehensive Invoice and Payment QR support

## Version
17.0.1.0.0 - Extended to support both Invoice and Payment QR codes
