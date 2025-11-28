# QR Code on Invoice and Payment with Validation System

## Overview

This enhanced module generates QR codes for invoices and payments with a secure validation system that allows customers and vendors to verify payment authenticity through secure web pages.

## Features

### Core QR Code Generation
- **Invoice QR Codes**: Generate QR codes for invoices with customizable content
- **Payment QR Codes**: Generate QR codes for payments that link to validation pages
- **Report Integration**: QR codes can be displayed on printed reports
- **Form Integration**: QR codes visible on invoice and payment forms

### Payment Validation System
- **Secure Validation**: Cryptographic token-based validation system
- **Validation URLs**: QR codes redirect to secure validation web pages
- **Token Management**: Automatic token generation with expiry dates
- **Access Tracking**: Monitor validation page access and usage
- **Professional UI**: Bootstrap-styled validation pages with payment details

## Installation

1. Copy the module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the module from Apps menu
4. The module depends on `web` and `account` modules

## Configuration

### Invoice QR Codes
1. Go to Accounting > Customers > Invoices
2. Open any invoice
3. Enable "Display QR Code in Report" checkbox
4. QR code will be generated automatically

### Payment QR Codes with Validation
1. Go to Accounting > Customers > Payments
2. Open any confirmed payment
3. Enable "Display QR Code in Report" checkbox
4. QR code with validation URL will be generated automatically

## Validation System Workflow

### For Customers/Vendors:
1. Scan the QR code from payment receipt/document
2. Redirected to secure validation page
3. View payment details and verification status
4. Confirm payment authenticity

### For Administrators:
1. Access "Validation & QR Code" tab in payment form
2. View validation token and access statistics
3. Regenerate tokens if needed
4. Monitor validation access logs

## Technical Details

### Security Features
- **SHA-256 Encryption**: Validation tokens use cryptographic hashing
- **Token Expiry**: Configurable token expiration (default: 1 year)
- **Access Tracking**: Log validation attempts and timestamps
- **Tamper Prevention**: Secure token generation prevents manipulation

### Validation Endpoints
- **Public Validation**: `/payment/validate/<token>` - Web page validation
- **API Validation**: `/payment/validate/api/<token>` - JSON API response
- **Error Handling**: Comprehensive error pages for invalid/expired tokens

### Database Fields Added

#### account.payment
- `validation_token`: Secure validation token
- `validation_token_expiry`: Token expiration date
- `validation_url`: Computed validation URL
- `validation_access_count`: Number of validation accesses
- `last_validation_access`: Last validation timestamp

## Usage Examples

### Generate Payment QR Code
```python
# In payment record
payment = self.env['account.payment'].browse(payment_id)
payment.qr_in_report = True  # Enable QR code
# QR code with validation URL generated automatically
```

### Manual Token Regeneration
```python
# Regenerate validation token
payment.regenerate_validation_token()
```

### Access Validation Page Programmatically
```python
# Get validation URL
validation_url = payment.validation_url
# Open in new window
payment.action_open_validation_page()
```

## API Endpoints

### Web Validation
- **URL**: `/payment/validate/<token>`
- **Method**: GET
- **Response**: HTML validation page
- **Features**: Professional UI with payment details

### JSON API Validation
- **URL**: `/payment/validate/api/<token>`
- **Method**: GET
- **Response**: JSON with validation status
- **Format**:
```json
{
    "valid": true,
    "payment": {
        "name": "PAY/001",
        "amount": 1000.00,
        "currency": "USD",
        "partner": "Customer Name",
        "date": "2024-01-15"
    },
    "access_count": 5,
    "message": "Payment validated successfully"
}
```

## Validation Page Features

### Success Page
- ✅ Payment verification status
- 📄 Complete payment details
- 🔒 Security confirmation
- 📊 Access statistics
- 🎨 Professional Bootstrap styling

### Error Handling
- ❌ Invalid token messages
- ⏰ Expired token notifications
- 🔍 Token not found errors
- 🏠 Navigation back to home

### Information Page
- ℹ️ System information
- 📋 How validation works
- 🔐 Security features
- 📞 Contact information

## Customization

### Token Expiry Period
Modify token expiry in `_generate_validation_token()`:
```python
expiry = datetime.now() + timedelta(days=365)  # Change days as needed
```

### Validation Page Styling
Customize templates in `templates/payment_validation_templates.xml`:
- Update Bootstrap classes
- Modify layout structure
- Add custom CSS
- Change color schemes

### QR Code Content
Modify QR code generation in `_generate_payment_qr_code()`:
```python
# Change QR code content
validation_url = f"{base_url}/payment/validate/{payment.validation_token}"
# Add custom parameters or modify URL structure
```

## Security Considerations

1. **Token Security**: Tokens use SHA-256 encryption with random secrets
2. **Public Access**: Validation endpoints are publicly accessible by design
3. **No Sensitive Data**: Validation pages show only basic payment information
4. **Expiry Management**: Tokens expire automatically to prevent long-term exposure
5. **Access Logging**: All validation attempts are logged for audit trails

## Troubleshooting

### QR Code Not Generating
- Check if "Display QR Code in Report" is enabled
- Ensure payment is in 'posted' state
- Verify base URL is configured correctly

### Validation Page Not Loading
- Check if validation token exists
- Verify token hasn't expired
- Ensure web server is accessible
- Check controller routing configuration

### Token Regeneration Issues
- Ensure user has proper permissions
- Check if payment is in correct state
- Verify token generation logic

## Support

For technical support or customizations:
- **Website**: https://ingenuityinfo.in
- **Email**: Contact through website
- **Documentation**: Check module comments and docstrings

## Version History

- **17.0.1.0**: Added payment validation system with secure web pages
- **17.0.0.0**: Initial QR code generation for invoices and payments

## License

AGPL-3 License - See LICENSE file for details
