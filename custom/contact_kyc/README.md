# Contact KYC Module

## Overview

The Contact KYC module adds Know-Your-Customer (KYC) functionality to Odoo 17 contacts, enabling comprehensive customer due diligence and compliance management.

## Features

### KYC Information Management
- **Personal Information**: Date of birth, place of birth, gender, aliases
- **Passport Information**: Number, country of issue, dates
- **UAE Residency**: Visa number, Emirates ID, expiry dates
- **Employment Details**: Years in role, employer information
- **Financial Information**: Source of funds/wealth, income, payment methods
- **PEP Status**: Politically Exposed Person screening

### KYC Form Report
- Professional PDF KYC form generation
- Complete customer information compilation
- Ready for regulatory compliance
- Print-ready format with signature fields

### Configuration Management
- Configurable source of funds options
- Configurable source of wealth options
- Administrative menu structure
- Security groups and access controls

## Installation

1. Copy the module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Contact KYC" module from the Apps menu

## Usage

### Adding KYC Information
1. Navigate to Contacts > Contacts
2. Open any contact record
3. Go to the "KYC Information" tab
4. Fill in the required KYC details
5. Save the record

### Generating KYC Report
1. Open a contact with KYC information
2. Click "Print" → "KYC Form"
3. The PDF report will be generated

### Managing KYC Options
1. Go to Settings > KYC > KYC Configuration
2. Manage "Source of Funds" and "Source of Wealth" options
3. Add/edit/deactivate options as needed

## Security

### Access Groups
- **KYC Manager**: Full access to KYC configuration
- **KYC User**: Access to KYC information on contacts

### Permissions
- KYC fields are visible to internal users
- Portal and public users have limited access
- Proper access controls on KYC configuration models

## Technical Details

### Models
- `res.partner`: Extended with KYC fields
- `kyc.source.funds`: Configurable funding sources
- `kyc.source.wealth`: Configurable wealth sources

### Views
- Enhanced partner form with KYC tab
- Tree/form views for KYC configuration
- Menu structure for easy access

### Reports
- QWeb PDF report for KYC forms
- Professional styling and layout
- Complete information compilation

## Compliance

This module helps organizations meet regulatory requirements for:
- Customer identification procedures
- Enhanced due diligence
- PEP screening
- Source of funds verification
- Record keeping requirements

## Support

For technical support or customization requests, please contact your system administrator or Odoo partner.

## License

LGPL-3 - See LICENSE file for details.
