# ⚡ Quick Start Guide - 15-Minute Bill Automation Setup

Get your bill automation working in just 15 minutes with this streamlined approach!

**⏱️ Total Time**: 15 minutes  
**🎯 Result**: Working bill automation from Google Drive to Odoo  
**💡 Best for**: Testing, proof of concept, small to medium volumes

---

## 🚀 What You'll Accomplish

After 15 minutes, you'll have:
- ✅ Bills automatically uploaded from Google Drive
- ✅ AI OCR extraction with ChatGPT  
- ✅ Vendor bills created in Odoo automatically
- ✅ File attachments included
- ✅ Basic duplicate prevention

---

## 📋 Before You Start

### Requirements Checklist
- [ ] **Automation Platform**: 
  - **Option A**: Zapier account (Starter plan - $19.99/month)
  - **Option B**: n8n (Free, self-hosted) - See `n8n_automation_setup.md`
- [ ] **Google Drive** with a dedicated folder for bills
- [ ] **ChatGPT Plus** or **OpenAI API** access
- [ ] **Odoo 17/18/19** with admin access and HTTPS enabled
- [ ] **5-10 sample bills** (PDF/images) for testing

### Your Webhook URL
```
https://scholarix-global-consultant.odoo.com/web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2
```

---

## 🔧 Step 1: Set Up Odoo Webhook (5 minutes)

### 1.1 Create Webhook Code

Navigate to **Settings → Technical → Server Actions** in Odoo and create a new Server Action:

**Name**: `Bill Automation Webhook`  
**Model**: `ir.http`  
**Action Type**: `Python Code`

**Python Code**:
```python
import json
import logging
import base64
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)

def create_bill_from_webhook():
    # Get the request data
    request_data = request.httprequest.get_json()
    
    if not request_data:
        return {'error': 'No data received'}
    
    try:
        # Extract bill information
        vendor_name = request_data.get('vendor_name', 'Unknown Vendor')
        amount = float(request_data.get('amount', 0))
        invoice_date = request_data.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))
        description = request_data.get('description', 'Automated Bill')
        reference = request_data.get('reference', '')
        file_url = request_data.get('file_url', '')
        file_name = request_data.get('file_name', 'bill.pdf')
        
        # Find or create vendor
        partner = env['res.partner'].search([('name', 'ilike', vendor_name)], limit=1)
        if not partner:
            partner = env['res.partner'].create({
                'name': vendor_name,
                'is_company': True,
                'supplier_rank': 1
            })
            _logger.info(f"Created new vendor: {vendor_name}")
        
        # Check for duplicate bills
        existing_bill = env['account.move'].search([
            ('partner_id', '=', partner.id),
            ('amount_total', '=', amount),
            ('invoice_date', '=', invoice_date),
            ('move_type', '=', 'in_invoice')
        ], limit=1)
        
        if existing_bill:
            _logger.warning(f"Duplicate bill detected: {reference}")
            return {'error': 'Duplicate bill', 'existing_bill_id': existing_bill.id}
        
        # Get default accounts and journal
        journal = env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        if not journal:
            return {'error': 'No purchase journal found'}
        
        expense_account = env['account.account'].search([
            ('account_type', '=', 'expense')
        ], limit=1)
        if not expense_account:
            expense_account = env['account.account'].search([
                ('code', '=like', '6%')
            ], limit=1)
        
        # Create the vendor bill
        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner.id,
            'invoice_date': invoice_date,
            'ref': reference,
            'journal_id': journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': description,
                'quantity': 1,
                'price_unit': amount,
                'account_id': expense_account.id if expense_account else False,
            })]
        }
        
        bill = env['account.move'].create(bill_vals)
        
        # Download and attach file if URL provided
        if file_url:
            try:
                response = requests.get(file_url, timeout=30)
                if response.status_code == 200:
                    file_content = base64.b64encode(response.content)
                    attachment = env['ir.attachment'].create({
                        'name': file_name,
                        'datas': file_content,
                        'res_model': 'account.move',
                        'res_id': bill.id,
                        'mimetype': response.headers.get('content-type', 'application/pdf')
                    })
                    _logger.info(f"File attached: {file_name}")
            except Exception as e:
                _logger.warning(f"Failed to attach file: {str(e)}")
        
        _logger.info(f"Bill created successfully: {bill.name}")
        
        return {
            'success': True,
            'bill_id': bill.id,
            'bill_number': bill.name,
            'vendor': vendor_name,
            'amount': amount
        }
        
    except Exception as e:
        _logger.error(f"Error creating bill: {str(e)}")
        return {'error': str(e)}

# Execute the function
result = create_bill_from_webhook()

# Return JSON response
import werkzeug.wrappers
response = werkzeug.wrappers.Response(
    json.dumps(result),
    content_type='application/json',
    status=200 if result.get('success') else 400
)
```

### 1.2 Create Webhook Endpoint

Go to **Settings → Technical → Website → Website Menus** and create:

**URL**: `/web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2`  
**Action**: Select your "Bill Automation Webhook" server action

---

## 🤖 Step 2: Set Up Automation Platform (8 minutes)

**Choose Your Automation Platform:**

### Option A: Zapier (Easiest)
- ✅ Quick setup (8 minutes)
- ❌ Costs $19.99/month
- ❌ 100 task limit on free plan

### Option B: n8n (Recommended)  
- ✅ **FREE** (self-hosted)
- ✅ Unlimited executions
- ✅ More powerful features
- ⏱️ Setup time: 15-30 minutes
- 📖 **See**: `n8n_automation_setup.md` for complete guide

---

## 🔗 Zapier Setup (Option A)

### 2.1 Create New Zap

1. **Go to** https://zapier.com/app/zaps
2. **Click** "Create Zap"
3. **Name it**: "Bill Automation - Drive to Odoo"

### 2.2 Trigger: Google Drive

1. **Choose App**: Google Drive
2. **Trigger Event**: New File in Folder
3. **Connect Account**: Your Google Drive
4. **Configure**:
   - **Folder**: Select your bills folder
   - **File Extensions**: `pdf,png,jpg,jpeg`
5. **Test**: Upload a sample bill and verify trigger works

### 2.3 Action 1: ChatGPT OCR

1. **Choose App**: ChatGPT  
2. **Action Event**: Conversation
3. **Configure**:

**User Message**:
```
Please analyze this bill/invoice image and extract the following information in JSON format:

{
  "vendor_name": "Company name from the bill",
  "amount": "Total amount as number (e.g., 150.75)",
  "invoice_date": "Date in YYYY-MM-DD format",
  "description": "Brief description of services/products",
  "reference": "Invoice number or reference",
  "currency": "Currency code (e.g., USD, EUR)"
}

Image: {{1.Download URL}}

Return ONLY the JSON object, no other text.
```

**Assistant Instructions**:
```
You are a professional OCR assistant. Extract bill/invoice data accurately and return only JSON format. If any field is unclear, use your best judgment or "Unknown" for text fields and 0 for amounts.
```

4. **Test**: Verify JSON output is properly formatted

### 2.4 Action 2: Send to Odoo Webhook

1. **Choose App**: Webhooks by Zapier
2. **Action Event**: POST
3. **Configure**:

**URL**: `https://scholarix-global-consultant.odoo.com/web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2`

**Payload Type**: JSON

**Data**:
```json
{
  "vendor_name": "{{ChatGPT Response}}",
  "amount": "{{ChatGPT Response}}",
  "invoice_date": "{{ChatGPT Response}}",
  "description": "{{ChatGPT Response}}",
  "reference": "{{ChatGPT Response}}",
  "file_url": "{{Google Drive File Download URL}}",
  "file_name": "{{Google Drive File Name}}"
}
```

**Headers**:
```
Content-Type: application/json
```

4. **Test**: Send sample data to webhook

### 2.5 Turn On Zap

1. **Review** all steps
2. **Turn On** the Zap
3. **Monitor** for any immediate errors

---

## 🧪 Step 3: Test Your Setup (2 minutes)

### 3.1 End-to-End Test

1. **Upload a test bill** to your Google Drive folder
2. **Wait 2-3 minutes** for processing
3. **Check Odoo** → Accounting → Vendor Bills
4. **Verify**:
   - Bill is created
   - Vendor exists (or was created)
   - Amount is correct
   - File is attached

### 3.2 Quick Validation Script

Create and run this test script:

```python
# test_quick_setup.py
import requests
import json

webhook_url = "https://scholarix-global-consultant.odoo.com/web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2"

test_data = {
    "vendor_name": "Test Vendor Ltd",
    "amount": 125.50,
    "invoice_date": "2024-10-28",
    "description": "Test bill for setup validation",
    "reference": "TEST-001",
    "file_name": "test_bill.pdf"
}

response = requests.post(webhook_url, json=test_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

Run with: `python test_quick_setup.py`

---

## ✅ Success Checklist

Your setup is working when:

- [ ] **Zapier triggers** on file upload (check Task History)
- [ ] **ChatGPT extracts** bill data accurately (>90%)
- [ ] **Webhook receives** data (check Odoo logs)
- [ ] **Bills are created** in Odoo automatically
- [ ] **Vendors are found** or auto-created
- [ ] **Files are attached** to bills
- [ ] **No duplicate bills** are created on re-upload
- [ ] **Processing time** is under 3 minutes

---

## 🔧 Quick Troubleshooting

### Zapier Not Triggering
```
❌ Check: Google Drive folder permissions
❌ Check: File format supported (PDF, PNG, JPG, JPEG)  
❌ Check: Zapier account has remaining tasks
✅ Fix: Verify folder path and test with manual trigger
```

### ChatGPT OCR Inaccurate
```
❌ Check: Image quality (minimum 200 DPI recommended)
❌ Check: Bill format is standard invoice layout
❌ Check: ChatGPT prompt is complete
✅ Fix: Improve image quality or adjust prompt
```

### Bills Not Created in Odoo
```
❌ Check: Webhook URL is correct and accessible
❌ Check: HTTPS is enabled on Odoo
❌ Check: Purchase journal exists
✅ Fix: Check Odoo server logs for specific errors
```

### File Not Attached
```
❌ Check: File URL is publicly accessible
❌ Check: File size is reasonable (<10MB)
❌ Check: Network connectivity from Odoo server
✅ Fix: Verify download URL in webhook logs
```

---

## 📈 Next Steps After Quick Setup

### Immediate (Today)
1. **Test with 5-10 real bills** to validate accuracy
2. **Train your team** on the upload process
3. **Monitor** first few processing cycles
4. **Document** any specific issues or customizations needed

### This Week
1. **Review OCR accuracy** and improve ChatGPT prompt if needed
2. **Set up error notifications** (Zapier can email on failures)
3. **Create user documentation** for bill upload process
4. **Consider upgrading** to the full module for better logging

### Production Considerations
- **Volume**: Quick setup handles 50-100 bills/month well
- **Monitoring**: Consider upgrading to full module for logging UI
- **Security**: Add API key authentication for production use
- **Backup**: Document all configurations for disaster recovery

---

## 🚀 Upgrade to Production Module

When you're ready for more features:

1. **Read**: `odoo_module/README.md`  
2. **Install**: Copy module to Odoo addons directory
3. **Configure**: Update Zapier webhook URL to `/api/v1/bills/create`
4. **Benefits**: 
   - Logging dashboard
   - Better error handling  
   - Security features
   - Maintenance tools

---

## 📞 Support Resources

### If Something Goes Wrong

1. **Zapier Issues**: Check Task History in Zapier dashboard
2. **Odoo Issues**: Check server logs in Settings → Technical → Logging
3. **OCR Issues**: Review ChatGPT responses in Zapier history
4. **Webhook Issues**: Use test script to isolate problems

### Getting Help

- **Zapier Support**: help@zapier.com
- **OpenAI Support**: help.openai.com  
- **Odoo Community**: odoo.com/forum
- **This Project**: Review other documentation files

---

## 🎉 Congratulations!

You now have a working bill automation system! 

**What you've accomplished**:
- ⚡ 15-minute setup completed
- 🤖 AI-powered OCR processing
- 📄 Automatic bill creation
- 📁 File attachment functionality
- 🔄 Basic duplicate prevention

**Expected time savings**: 80-85% reduction in manual bill entry time

**Next recommended reading**: `COMPLETE_CHECKLIST.md` to track your ongoing optimization

---

*Setup completed on: ___________*  
*Team members trained: ___________*  
*First production bill processed: ___________*