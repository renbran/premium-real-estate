# Partner Statement & Follow-up Module

## Overview

The Partner Statement & Follow-up module is a comprehensive solution for managing customer receivables, generating professional statements, and automating follow-up processes in Odoo 17.

## Key Features

### 📊 **Partner Statements**
- **One-screen view** with complete transaction history
- **Ageing analysis** with customizable buckets (Current, 1-30, 31-60, 61-90, 90+ days)
- **On-the-fly reconciliation** directly from statement view
- **Multiple export formats**: Screen view, PDF, Excel
- **Email delivery** with professional templates

### 📧 **Automated Follow-up System**
- **3-level escalating** follow-up process
- **Customizable email templates** for each level
- **Automatic scheduling** with configurable intervals
- **Batch processing** for multiple partners
- **Follow-up history tracking** with audit trail

### ⚙️ **Configuration & Customization**
- **Multi-company support** with separate configurations
- **Flexible ageing buckets** (30/60/90 days configurable)
- **Email template customization** with HTML support
- **Statement branding** with company logo and footer
- **Security groups** for user access control

### 🔧 **Advanced Features**
- **Partner blocking** option to prevent follow-ups
- **Payment reference tracking** for easy reconciliation
- **Overdue analysis** with days calculation
- **Cron job automation** for daily follow-up checks
- **Weekly ageing reports** for management

## Installation

1. Copy the module to your Odoo addons directory
2. Update the apps list
3. Install the "Partner Statement & Follow-up" module
4. Configure settings in Accounting > Follow-up & Statements > Configuration

## Configuration

### Initial Setup
1. Go to **Accounting > Follow-up & Statements > Configuration > Statement Settings**
2. Configure ageing buckets (default: 30, 60, 90 days)
3. Set up email templates and follow-up levels
4. Configure automatic follow-up settings

### Security Groups
- **Statement User**: Can view statements and send follow-ups
- **Statement Manager**: Full access including configuration

### Email Templates
Three pre-configured templates are included:
- **Level 1**: Friendly payment reminder
- **Level 2**: Urgent payment notice
- **Level 3**: Final notice before collection

## Usage

### Generating Partner Statements
1. Go to **Accounting > Follow-up & Statements > Partner Statement**
2. Select partner and date range
3. Choose output format (Screen/PDF/Excel)
4. View statement with ageing analysis

### Managing Follow-ups
1. **Individual Follow-up**: Partner form > Follow-up tab > Send Follow-up
2. **Batch Follow-up**: Accounting > Follow-up & Statements > Batch Follow-up
3. **Automated**: Configured via cron jobs (daily execution)

### Monitoring
- **Partners Follow-up**: View all partners due for follow-up
- **Follow-up History**: Complete audit trail of sent follow-ups
- **Ageing Analysis**: Pivot/graph views of outstanding balances

## Technical Details

### Models
- `res.partner` (extended): Follow-up fields and balance calculations
- `account.move.line` (extended): Ageing analysis and reconciliation
- `res.partner.statement.config`: Multi-company configuration
- `res.partner.followup.history`: Follow-up audit trail

### Security
- Multi-company record rules
- Group-based access control
- Email template security

### Automation
- Daily follow-up checks via cron job
- Weekly ageing reports to accounts team
- Automatic balance calculations

## Support

For issues, feature requests, or customizations, please contact the development team.

## Version History

- **v1.0**: Initial release with core functionality
- Comprehensive statement generation
- 3-level follow-up system
- Multi-company support
- Professional reporting

---

*This module replaces and extends the standard Odoo account_followup functionality with enhanced features and better user experience.*
