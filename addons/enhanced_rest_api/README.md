# Enhanced REST API for Odoo 17 Server-Wide Modules

## Overview

The Enhanced REST API module provides comprehensive REST API functionality for all major Odoo modules, designed to work as a server-wide module with advanced features and enterprise-grade security.

## Features

### 🚀 **Core Functionality**
- **Server-Wide Integration**: Works across all Odoo modules
- **Advanced Authentication**: API key, JWT, OAuth2 support
- **Rate Limiting**: Configurable request limits per endpoint
- **Comprehensive Logging**: Request/response tracking and analytics
- **Version Control**: API versioning support
- **Security Groups**: Fine-grained access control

### 📊 **Module-Specific APIs**
- **CRM API**: Leads management, dashboard data, pipeline analytics
- **Sales API**: Orders, products, customer data, sales analytics
- **Payment API**: Payment processing, QR code verification, voucher management
- **Payment Vouchers**: A4-optimized PDF/HTML voucher generation with OS PROPER branding
- **Generic Model API**: CRUD operations for any Odoo model

### 🧾 **Payment Voucher Features**
- **Professional Templates**: A4-optimized voucher templates with OS PROPER branding
- **Multiple Formats**: PDF download, HTML preview, and JSON data endpoints
- **QR Code Integration**: Auto-generated QR codes for payment verification
- **Workflow Tracking**: Multi-step approval process visualization
- **Responsive Design**: Mobile-friendly and print-optimized layouts
- **Dynamic Data**: Real-time integration with Odoo payment data

### 🔒 **Security Features**
- **API Key Management**: Generate, revoke, and manage API keys
- **User Authentication**: Multi-level authentication support
- **Access Control**: Group-based permissions
- **Request Validation**: Input sanitization and validation
- **Audit Trail**: Complete request logging

## Installation

### 1. Add to Server-Wide Modules

Edit your `odoo.conf` file to include the enhanced REST API as a server-wide module:

```ini
[options]
server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api
```

### 2. Install Dependencies

Ensure Python dependencies are installed:

```bash
pip install PyJWT requests
```

### 3. Restart Odoo Server

```bash
# Stop Odoo
sudo systemctl stop odoo

# Start Odoo
sudo systemctl start odoo
```

### 4. Install Module

1. Go to Apps menu in Odoo
2. Update Apps List
3. Search for "Enhanced REST API"
4. Install the module

## Configuration

### API Key Generation

1. **Via Web Interface**:
   - Go to Settings → Users & Companies → Users
   - Select a user
   - Click "Generate API Key" button

2. **Via API**:
   ```bash
   curl -X POST http://your-domain.com/api/v1/auth/generate-key \
        -H "Content-Type: application/json" \
        -u username:password
   ```

### Endpoint Configuration

Navigate to **Enhanced REST API → API Endpoints** to:
- Configure available endpoints
- Set rate limits
- Manage authentication requirements
- Control access permissions

## API Usage

### Authentication

Include your API key in requests:

```bash
# Using X-API-Key header (recommended)
curl -H "X-API-Key: your-api-key-here" \
     http://your-domain.com/api/v1/crm/leads

# Using api-key header (alternative)
curl -H "api-key: your-api-key-here" \
     http://your-domain.com/api/v1/sales/orders
```

### Standard Response Format

All API endpoints return standardized JSON responses:

```json
{
  "success": true,
  "timestamp": "2024-08-07T12:00:00Z",
  "data": {
    // Response data here
  },
  "error": null
}
```

### Error Responses

```json
{
  "success": false,
  "timestamp": "2024-08-07T12:00:00Z",
  "data": null,
  "error": {
    "code": 401,
    "message": "Invalid API key"
  }
}
```

## API Endpoints

### 🔐 **Authentication Endpoints**

#### Generate API Key
```bash
POST /api/v1/auth/generate-key
# Requires: User authentication
# Returns: API key and expiry information
```

#### Revoke API Key
```bash
POST /api/v1/auth/revoke-key
# Requires: API key authentication
# Returns: Success confirmation
```

#### User Profile
```bash
GET /api/v1/user/profile
# Requires: API key authentication
# Returns: Current user information and API usage stats
```

### 📈 **CRM Endpoints**

#### Get Leads
```bash
GET /api/v1/crm/leads?stage=new&limit=50&offset=0
# Parameters: stage, team_id, user_id, date_from, date_to, limit, offset
# Returns: Paginated list of CRM leads
```

#### Create Lead
```bash
POST /api/v1/crm/leads
Content-Type: application/json

{
  "name": "New Lead",
  "partner_name": "Customer Name",
  "email_from": "customer@example.com",
  "phone": "+1234567890"
}
```

#### CRM Dashboard
```bash
GET /api/v1/crm/dashboard?date_from=2024-01-01&date_to=2024-12-31
# Returns: CRM analytics and pipeline data
```

### 💰 **Sales Endpoints**

#### Get Sales Orders
```bash
GET /api/v1/sales/orders?state=sale&limit=100
# Parameters: state, partner_id, user_id, date_from, date_to, limit, offset
# Returns: Paginated list of sales orders
```

#### Create Sales Order
```bash
POST /api/v1/sales/orders
Content-Type: application/json

{
  "partner_id": 123,
  "order_line": [
    {
      "product_id": 456,
      "product_uom_qty": 2,
      "price_unit": 100.00
    }
  ]
}
```

#### Sales Dashboard
```bash
GET /api/v1/sales/dashboard?date_from=2024-01-01
# Returns: Sales analytics, revenue trends, top customers
```

#### Confirm Order
```bash
POST /api/v1/sales/orders/123/confirm
# Confirms and processes the sales order
```

### 💳 **Payment Endpoints**

#### Get Payments
```bash
GET /api/v1/payments?state=posted&payment_type=inbound
# Parameters: state, partner_id, payment_type, date_from, date_to, limit, offset
# Returns: Paginated list of payments
```

#### Create Payment
```bash
POST /api/v1/payments
Content-Type: application/json

{
  "amount": 1000.00,
  "partner_id": 123,
  "payment_type": "inbound",
  "payment_method_id": 1
}
# Returns: Payment with QR code and voucher number
```

#### Verify Payment (QR Code)
```bash
GET /api/v1/payments/123/verify
# No authentication required
# Returns: Payment verification details
```

#### Payment Dashboard
```bash
GET /api/v1/payments/dashboard
# Returns: Payment analytics and statistics
```

### 🧾 **Payment Voucher Endpoints**

#### Generate Payment Voucher PDF
```bash
GET /api/v1/payments/voucher/{payment_id}
# Headers: X-API-Key: your_api_key
# Returns: Professional A4 PDF voucher download
# Example: curl -H "X-API-Key: your_key" -o voucher.pdf "/api/v1/payments/voucher/123"
```

#### Get Payment Voucher HTML Preview
```bash
GET /api/v1/payments/voucher/html/{payment_id}
# Headers: X-API-Key: your_api_key
# Returns: HTML preview of payment voucher
# Features: Responsive design, print-optimized, OS PROPER branding
```

#### Get Payment Voucher Data
```bash
GET /api/v1/payments/voucher/data/{payment_id}
# Headers: X-API-Key: your_api_key
# Returns: Complete voucher data as JSON including:
# - Payment details, company info, partner data
# - QR code data for verification
# - Workflow status and approval tracking
# - Download URLs for PDF and HTML versions
```

**Voucher Features:**
- **A4 Optimized**: Perfect for printing (210mm x 297mm)
- **OS PROPER Branding**: Company colors, professional typography
- **QR Code Integration**: Auto-generated verification codes
- **Workflow Tracking**: Visual approval process status
- **Responsive Design**: Mobile-friendly and print-ready
- **Multi-format**: PDF, HTML, and JSON data endpoints

### 🔍 **Generic Model Endpoints**

#### Search Any Model
```bash
GET /api/v1/models/res.partner/search?domain=[["is_company","=",true]]&fields=name,email&limit=50
# Parameters: domain (JSON), fields (comma-separated), limit, offset, order
# Returns: Records from specified model
```

## Rate Limiting

- Default rate limits are configured per endpoint
- Limits are enforced per user per minute
- Rate limit information is included in response headers
- Configurable through the API Endpoints interface

## Monitoring & Analytics

### Request Logs
- **Location**: Enhanced REST API → API Logs
- **Features**: Real-time request monitoring, error tracking, performance metrics

### Usage Statistics
- **Location**: Enhanced REST API → Usage Statistics
- **Features**: Daily/monthly usage trends, success rates, response times

### Dashboard Metrics
- Total API requests
- Success/failure rates
- Most used endpoints
- User activity patterns

## Security Best Practices

1. **API Key Management**:
   - Generate unique keys per application
   - Rotate keys regularly
   - Revoke unused keys immediately

2. **Network Security**:
   - Use HTTPS in production
   - Implement firewall rules
   - Monitor for suspicious activity

3. **Access Control**:
   - Assign minimal required permissions
   - Use security groups effectively
   - Regular access reviews

## Troubleshooting

### Common Issues

1. **"API key required" Error**:
   - Ensure X-API-Key header is included
   - Verify API key is active and not expired
   - Check user has API access permissions

2. **"Access denied" Error**:
   - Verify user has access to the requested model
   - Check security group assignments
   - Ensure endpoint is configured and active

3. **Rate limit exceeded**:
   - Check current rate limits in endpoint configuration
   - Implement request throttling in client
   - Consider upgrading rate limits if needed

### Debug Mode

Enable debug logging in `odoo.conf`:

```ini
[options]
log_level = debug
log_handler = :INFO,odoo.addons.enhanced_rest_api:DEBUG
```

## Integration Examples

### Python Client
```python
import requests

class OdooAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}
    
    def get_leads(self, **params):
        response = requests.get(
            f"{self.base_url}/api/v1/crm/leads",
            headers=self.headers,
            params=params
        )
        return response.json()

# Usage
client = OdooAPIClient('https://your-odoo.com', 'your-api-key')
leads = client.get_leads(stage='new', limit=10)
```

### JavaScript Client
```javascript
class OdooAPI {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {'X-API-Key': apiKey};
    }
    
    async getSalesOrders(params = {}) {
        const url = new URL('/api/v1/sales/orders', this.baseUrl);
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });
        
        const response = await fetch(url, {
            headers: this.headers
        });
        return response.json();
    }
}

// Usage
const api = new OdooAPI('https://your-odoo.com', 'your-api-key');
const orders = await api.getSalesOrders({state: 'sale', limit: 20});
```

## Support

For support and documentation:
- **Module Documentation**: Enhanced REST API → Help
- **API Testing**: Use included Postman collections
- **Error Logs**: Enhanced REST API → API Logs
- **Community**: Odoo Community Forums

## License

This module is licensed under LGPL-3.

---

**OSUS Technology Solutions** - Enterprise Odoo Solutions
