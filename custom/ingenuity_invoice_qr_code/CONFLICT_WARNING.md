# UPDATED: ingenuity_invoice_qr_code now supports both Invoice and Payment QR codes

## Changes Made:
- Extended QR functionality to account.payment model with `qr_code` field
- Added payment-specific QR generation with payment details
- Created payment report templates with QR code support
- Added payment views with QR code controls

## Field Mapping:
- **account.move**: `qr_image` and `qr_in_report` (for invoices)
- **account.payment**: `qr_code` and `qr_in_report` (for payments)

## Note:
- The `invoice_report_for_realestate` module uses `qr_code_urls` for payments
- This module uses `qr_code` for payments
- Both can coexist as they use different field names
- Users can choose which QR implementation to use per module

## RECOMMENDATION: 
This module now provides comprehensive QR support for both invoices and payments.
If you only need one QR system, you can disable the other module's QR features.