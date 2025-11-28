# Webhook CRM Module

## Overview
This module provides comprehensive webhook functionality for creating CRM leads from external sources with advanced field mapping capabilities.

## Features
- **Webhook Endpoints**: Handle external webhooks for CRM lead creation
- **Flexible Field Mapping**: Configure how webhook data maps to CRM lead fields
- **Data Transformation**: Transform and validate incoming webhook data
- **Multiple Sources**: Support for multiple webhook sources with different configurations
- **Error Handling**: Comprehensive error handling and logging
- **Admin Interface**: Easy-to-use configuration interface

## Endpoints

### 1. Generic Webhook Endpoint
```
POST /webhook/crm/lead
Content-Type: application/json
```

### 2. Source-Specific Webhook Endpoint
```
POST /webhook/crm/lead/<source_name>
Content-Type: application/json
```

### 3. Test Endpoint
```
GET /webhook/test
```

## Configuration

### Webhook Mapping Setup
1. Go to **CRM > Webhooks > Webhook Mappings**
2. Create a new mapping configuration
3. Set the source name (identifier for webhook source)
4. Configure field mappings between webhook data and CRM lead fields
5. Add default values (JSON format)
6. Define transformation rules (Python code)

### Field Mapping Options
- **Source Field Path**: Use dot notation for nested fields (e.g., `contact.email`)
- **Target Field**: Select the CRM lead field to map to
- **Transformation Type**: Choose how to transform the data
- **Transformation Parameters**: Additional parameters for transformations

### Transformation Types
- **None**: No transformation
- **Uppercase/Lowercase/Capitalize**: Text case transformations
- **Strip**: Remove whitespace
- **Replace**: Replace text patterns
- **Mapping**: Value mapping using JSON
- **Format**: String formatting
- **Boolean/Float/Int**: Type conversions

## Example Webhook Data

```json
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "company": "Example Corp",
    "message": "Interested in your services",
    "source": "website"
}
```

## Default Mapping
The module includes a default mapping configuration that handles common webhook fields:
- `name` → Lead Name
- `email` → Email
- `phone` → Phone
- `company` → Company Name
- `message` → Description

## Installation
1. Copy the module to your Odoo addons directory
2. Update the app list
3. Install the "Webhook CRM Lead Handler" module
4. Configure webhook mappings as needed

## Security
- Webhook endpoints use `auth='none'` for external access
- Internal operations use `sudo()` for proper permissions
- CSRF protection is disabled for webhook endpoints

## Logging
All webhook activities are logged with appropriate levels:
- INFO: Successful operations
- WARNING: Data transformation issues
- ERROR: Processing failures

## Dependencies
- base
- crm
- website

## BOM Character Resolution
This module has been completely recreated to eliminate any BOM (Byte Order Mark) characters that could cause parsing errors. All files are saved with UTF-8 encoding without BOM.
