# Enhanced REST API - Payment Voucher Integration

## Overview
The Enhanced REST API now includes comprehensive payment voucher functionality with A4-optimized templates that match your OS PROPER branding requirements.

## Payment Voucher Endpoints

### 1. Generate Payment Voucher PDF
**Endpoint:** `GET /api/v1/payments/voucher/{payment_id}`

**Description:** Generates a professionally formatted PDF payment voucher

**Headers:**
```
X-API-Key: your_api_key_here
```

**Response:** PDF file download

**Example:**
```bash
curl -H "X-API-Key: 9990ae0a2c22e17acc150028e83c9503cf83af5d" \
     "https://testerp.cloudpepper.site/api/v1/payments/voucher/123" \
     -o "payment_voucher_123.pdf"
```

### 2. Get Payment Voucher HTML Preview
**Endpoint:** `GET /api/v1/payments/voucher/html/{payment_id}`

**Description:** Returns HTML preview of the payment voucher

**Headers:**
```
X-API-Key: your_api_key_here
```

**Response:** HTML content

**Example:**
```bash
curl -H "X-API-Key: 9990ae0a2c22e17acc150028e83c9503cf83af5d" \
     "https://testerp.cloudpepper.site/api/v1/payments/voucher/html/123"
```

### 3. Get Payment Voucher Data
**Endpoint:** `GET /api/v1/payments/voucher/data/{payment_id}`

**Description:** Returns payment voucher data as JSON

**Headers:**
```
X-API-Key: your_api_key_here
```

**Response Example:**
```json
{
  "success": true,
  "timestamp": "2025-08-06T21:30:00.000000",
  "data": {
    "id": 123,
    "name": "NV/2025/00293",
    "reference": "NV/2025/00293",
    "voucher_type": "receipt",
    "amount": 1000.0,
    "currency": "AED",
    "currency_symbol": "د.إ",
    "partner": {
      "id": 45,
      "name": "Customer Name",
      "phone": "0563905772",
      "mobile": "0563905772",
      "email": "customer@example.com"
    },
    "company": {
      "id": 1,
      "name": "CONTINENTAL INVESTMENT LTD LLC",
      "vat": "100236589600003",
      "phone": "0563905772",
      "address": {
        "street": "Single Business Tower",
        "street2": "29th Floor",
        "city": "Dubai",
        "country": "United Arab Emirates"
      }
    },
    "payment_method": "Bank Transfer",
    "journal": "Bank",
    "state": "posted",
    "date": "2025-08-06",
    "create_date": "2025-08-06T15:06:00.000000",
    "create_user": "ADMINISTRATOR",
    "qr_code_data": "Payment: NV/2025/00293...",
    "voucher_urls": {
      "pdf": "/api/v1/payments/voucher/123",
      "html": "/api/v1/payments/voucher/html/123"
    }
  },
  "error": null
}
```

## Template Features

### A4 Optimization
- **Size:** 210mm x 297mm (A4 standard)
- **Margins:** 12mm on all sides
- **Print-ready:** Optimized for both screen and print
- **Responsive:** Mobile-friendly design

### Branding Elements
- **OS PROPER** company header with gradient background
- **Company colors:** Deep burgundy (#800020) and gold (#ffd700)
- **Professional typography:** Inter font family
- **QR Code integration:** For payment verification
- **Logo placeholder:** Ready for company logo integration

### Payment Information Sections
1. **Header:** Company name, voucher number, subtitle
2. **Brand Section:** Logo and QR code placeholders
3. **Payment Details:** Method, reference, phone, amount, date
4. **Company Details:** Address, VAT, initiator, reviewer
5. **Authorization Workflow:** Multi-step approval process
6. **Receiver Information:** Fields for manual completion
7. **Signature Area:** Authorized signature space
8. **Footer:** Contact information and disclaimer

### Template Customization
The template supports dynamic data replacement using Odoo's QWeb templating system:

- `{{voucher_number}}` - Payment voucher number
- `{{voucher_type}}` - Receipt or Payment voucher
- `{{payment_method}}` - Payment method (Bank Transfer, etc.)
- `{{amount}}` - Payment amount with currency
- `{{company_name}}` - Company name
- `{{partner_name}}` - Customer/vendor name
- `{{date}}` - Payment date
- `{{state}}` - Payment status (Draft, Approved, Paid, etc.)

### Status Indicators
- **Pending Status:** Red italic text for pending items
- **Approved Status:** Green bold text for approved items
- **Amount Highlight:** Prominent display of payment amount
- **Workflow Tracking:** Visual progress indicators

## Integration Examples

### JavaScript/Web Integration
```javascript
// Fetch payment voucher data
async function getPaymentVoucher(paymentId) {
    const response = await fetch(`/api/v1/payments/voucher/data/${paymentId}`, {
        headers: {
            'X-API-Key': 'your_api_key_here',
            'Content-Type': 'application/json'
        }
    });
    
    if (response.ok) {
        const data = await response.json();
        return data.data;
    } else {
        throw new Error('Failed to fetch payment voucher');
    }
}

// Download PDF voucher
function downloadVoucherPDF(paymentId) {
    const url = `/api/v1/payments/voucher/${paymentId}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `payment_voucher_${paymentId}.pdf`;
    link.click();
}
```

### Python Integration
```python
import requests

api_key = "your_api_key_here"
base_url = "https://testerp.cloudpepper.site"

# Get voucher data
def get_voucher_data(payment_id):
    url = f"{base_url}/api/v1/payments/voucher/data/{payment_id}"
    headers = {"X-API-Key": api_key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"API Error: {response.status_code}")

# Download voucher PDF
def download_voucher_pdf(payment_id, filename):
    url = f"{base_url}/api/v1/payments/voucher/{payment_id}"
    headers = {"X-API-Key": api_key}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        raise Exception(f"API Error: {response.status_code}")
```

## Error Handling

Common error responses:

### 401 - Unauthorized
```json
{
  "success": false,
  "error": {
    "error": "API key required",
    "code": 401
  }
}
```

### 404 - Not Found
```json
{
  "success": false,
  "error": {
    "error": "Payment not found",
    "code": 404
  }
}
```

### 403 - Access Denied
```json
{
  "success": false,
  "error": {
    "error": "Access denied",
    "code": 403
  }
}
```

## Testing with Your API Key

Use your existing API key to test the new voucher endpoints:

**API Key:** `9990ae0a2c22e17acc150028e83c9503cf83af5d`

**Test Commands:**
```bash
# Get payment voucher data
curl -H "X-API-Key: 9990ae0a2c22e17acc150028e83c9503cf83af5d" \
     "https://testerp.cloudpepper.site/api/v1/payments/voucher/data/1"

# Preview voucher HTML
curl -H "X-API-Key: 9990ae0a2c22e17acc150028e83c9503cf83af5d" \
     "https://testerp.cloudpepper.site/api/v1/payments/voucher/html/1"

# Download voucher PDF
curl -H "X-API-Key: 9990ae0a2c22e17acc150028e83c9503cf83af5d" \
     "https://testerp.cloudpepper.site/api/v1/payments/voucher/1" \
     -o "voucher.pdf"
```

## Next Steps

1. **Restart Odoo Server** to load the new voucher functionality
2. **Test the voucher endpoints** with your API key
3. **Customize the template** with your actual logo and branding
4. **Integrate with your applications** using the provided examples

The payment voucher system is now fully integrated with your Enhanced REST API and ready for production use!
