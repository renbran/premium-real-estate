# Frontend Enhancement Module for Odoo 17

## Overview

The **Frontend Enhancement** module is a comprehensive custom module for Odoo 17 that significantly enhances the frontend user experience by providing advanced order reference management and sophisticated file upload functionality. This module is specifically designed for **OSUS Properties** branding and maintains professional formatting while seamlessly integrating with existing Odoo setups.

## 🚀 Key Features

### 📋 Order Reference Enhancement
- **Client Order Reference Display**: Enhanced visualization of client order references in sales orders
- **Customer Reference Management**: Professional customer reference handling in invoices
- **Reference Priority System**: Urgency levels (Low, Normal, High, Urgent) with visual indicators
- **Reference Validation**: Built-in validation system for customer references with approval workflow
- **Portal Integration**: Customer-facing portal displays with reference information
- **Search & Filter**: Advanced search capabilities by reference fields

### 📁 File Upload Functionality
- **Drag & Drop Interface**: Modern, intuitive file upload with drag-and-drop support
- **Multiple File Formats**: Support for PDF, DOC, DOCX, XLS, XLSX, TXT, images, archives
- **File Size Management**: Configurable file size limits per user (default 50MB)
- **Access Control**: Public, Internal, and Restricted access levels
- **Automatic Logging**: Files automatically logged in record chatter/notes
- **Download Tracking**: Download count and usage analytics
- **File Management**: Archive, restore, and permanent deletion capabilities
- **Portal File Access**: Customer portal integration for file management

### 🎨 UI/UX Enhancements
- **Professional Design**: OSUS Properties branded interface
- **Mobile Responsive**: Optimized for all device sizes
- **Modern Styling**: Professional color scheme and typography
- **Enhanced Views**: Improved Kanban, List, and Form views
- **Visual Indicators**: Priority badges, validation status, file type icons
- **Smooth Animations**: Subtle transitions and hover effects

## 📦 Installation

### Prerequisites
- Odoo 17.0 or later
- Python 3.8+
- Required Odoo modules: `base`, `sale`, `account`, `mail`, `portal`, `web`, `website`

### Installation Steps

1. **Copy Module to Addons Directory**
   ```bash
   cp -r frontend_enhancement /path/to/odoo/addons/
   ```

2. **Update Apps List**
   - Go to Apps → Update Apps List
   - Search for "Frontend Enhancement"

3. **Install Module**
   - Click "Install" on the Frontend Enhancement module
   - The module will automatically install all dependencies

4. **Verify Installation**
   - Check that new menu items appear in Sales and Accounting
   - Verify file upload functionality in user settings

## 🔧 Configuration

### File Upload Settings
Configure file upload parameters in **Settings → Technical → Parameters → System Parameters**:

- `frontend_enhancement.max_file_size_mb`: Maximum file size in MB (default: 50)
- `frontend_enhancement.allowed_file_types`: Comma-separated list of allowed extensions

### User Configuration
Each user can configure their file upload preferences:
- **Max Upload Size**: Individual limits per user
- **Allowed File Types**: Custom file type restrictions
- **Upload Notifications**: Email notifications for uploads

### Reference Validation
Configure reference validation in **Settings → Accounting**:
- Enable automatic reference validation
- Set validation requirements
- Configure approval workflows

## 📚 Usage Guide

### Sales Order References

1. **Creating Orders with References**
   - Navigate to Sales → Orders → Sales Orders (Enhanced)
   - Fill in the "Client Order Reference" field
   - Set priority level and add reference notes
   - Reference automatically transfers to invoices

2. **Searching by Reference**
   - Use the enhanced search filters
   - Filter by reference priority
   - Group by reference validation status

### Invoice Customer References

1. **Managing Customer References**
   - Open any customer invoice
   - Enter customer reference in enhanced field
   - Validate reference using validation buttons
   - View reference source and validation status

2. **Reference Dashboard**
   - Navigate to Accounting → Reporting → Reference Dashboard
   - View all references and validation status
   - Export reference reports

### File Upload Management

1. **Uploading Files**
   - Go to Settings → Users → [Select User] → File Attachments
   - Click "Upload File" or drag files to upload area
   - Fill in file details and set access level
   - Files automatically appear in user's file list

2. **Portal File Access**
   - Customers can access files via portal
   - Navigate to "My Files" in portal menu
   - Upload, download, and manage files
   - View upload statistics

3. **File Management**
   - Archive files instead of permanent deletion
   - Track download counts and usage
   - Restore archived files when needed
   - Bulk operations for file management

## 🔍 Technical Details

### Module Structure
```
frontend_enhancement/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   ├── portal_controller.py
│   └── file_upload_controller.py
├── models/
│   ├── __init__.py
│   ├── sale_order.py
│   ├── account_move.py
│   ├── file_attachment.py
│   └── res_users.py
├── views/
│   ├── sale_order_views.xml
│   ├── account_move_views.xml
│   ├── res_users_views.xml
│   └── frontend_templates.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── css/
│       └── js/
└── data/
    └── file_upload_data.xml
```

### Key Models

#### `file.attachment.enhancement`
- Enhanced file attachment model with advanced features
- Inherits mail.thread for automatic logging
- Supports access control and download tracking

#### Extended Models
- `sale.order`: Enhanced with client reference management
- `account.move`: Enhanced with customer reference validation
- `res.users`: Extended with file upload capabilities

### Security
- Role-based access control
- File type validation
- Size restrictions
- Portal access controls
- Audit logging

## 🔧 API Documentation

### File Upload Controller Endpoints

#### `/web/file_upload/validate`
Validates file before upload
```json
{
    "file_name": "document.pdf",
    "file_size": 1024000,
    "file_type": "application/pdf"
}
```

#### `/web/file_upload/create`
Creates new file attachment
```json
{
    "file_data": "base64_encoded_data",
    "name": "document.pdf",
    "description": "Important document",
    "access_level": "internal"
}
```

#### Portal Endpoints
- `/my/files`: List user's files
- `/my/files/upload`: File upload page
- `/my/files/download/<id>`: Download file
- `/my/files/delete/<id>`: Delete file

## 🎯 Examples

### Example 1: Creating Enhanced Sale Order
```python
# Create sale order with enhanced references
order = env['sale.order'].create({
    'partner_id': partner.id,
    'client_order_ref': 'CLIENT-2024-001',
    'reference_priority': 'high',
    'order_reference_notes': 'Urgent delivery required for Q1',
})
```

### Example 2: File Upload via API
```python
# Upload file for user
attachment = env['file.attachment.enhancement'].create({
    'name': 'contract.pdf',
    'description': 'Signed contract document',
    'file_data': base64_encoded_content,
    'user_id': user.id,
    'access_level': 'internal',
})
```

### Example 3: Reference Validation
```python
# Validate invoice reference
invoice = env['account.move'].browse(invoice_id)
if invoice.ref:
    invoice.action_validate_reference()
```

## 📈 Performance Considerations

- **File Storage**: Uses Odoo's attachment system with efficient storage
- **Database Optimization**: Indexed fields for fast reference searches
- **Caching**: Computed fields cached for better performance
- **Pagination**: Large file lists automatically paginated
- **Lazy Loading**: Files loaded on demand in portal

## 🛠️ Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size limits
   - Verify file type permissions
   - Ensure sufficient disk space
   - Check user permissions

2. **References Not Displaying**
   - Clear browser cache
   - Update module
   - Check view inheritance
   - Verify field permissions

3. **Portal Access Issues**
   - Check portal user permissions
   - Verify website settings
   - Ensure portal templates active
   - Check access rights

### Debug Mode
Enable debug mode to access technical features:
- Go to Settings → Activate Developer Mode
- Access technical menus and debugging tools

## 🔄 Updates and Maintenance

### Regular Maintenance
- Monitor file storage usage
- Clean up inactive files (automated via cron)
- Review download statistics
- Update file type restrictions as needed

### Backup Considerations
- Include file attachments in backups
- Test restore procedures
- Monitor backup size growth
- Consider external file storage for large deployments

## 📞 Support

For technical support or feature requests:
- **Email**: support@osusproperties.com
- **Documentation**: Internal wiki
- **Training**: Contact IT department

## 📄 License

This module is licensed under LGPL-3. See the LICENSE file for details.

## 🏷️ Version History

### Version 17.0.1.0.0
- Initial release for Odoo 17
- Enhanced order reference management
- File upload functionality
- Portal integration
- OSUS Properties branding

---

**© 2024 OSUS Properties - All rights reserved**
