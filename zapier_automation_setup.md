# 🎯 Zapier Automation Setup - Complete Guide

This guide provides detailed instructions for setting up the Zapier automation that triggers bill processing from Google Drive to Odoo.

**⏱️ Setup Time**: 20-30 minutes  
**💰 Cost**: $19.99/month (Zapier Starter) + ChatGPT API usage  
**🎯 Result**: Fully automated bill processing pipeline

---

## 📋 Prerequisites

### Accounts & Subscriptions
- [ ] **Zapier account** with Starter plan or higher
- [ ] **Google Drive** with dedicated folder for bills
- [ ] **ChatGPT Plus** subscription OR **OpenAI API** account
- [ ] **Odoo instance** with webhook endpoint configured

### Preparation
- [ ] **Test bills** ready (5-10 PDF/image files)
- [ ] **Webhook URL** from Odoo setup
- [ ] **API key** (if using enhanced security)
- [ ] **File permissions** verified on Google Drive

---

## 🚀 Step-by-Step Setup

### Step 1: Create New Zap (5 minutes)

1. **Login to Zapier** → https://zapier.com/app/zaps
2. **Click "Create Zap"**
3. **Name your Zap**: "Bill Automation - Drive to Odoo"
4. **Choose starting point**: "When this happens..."

### Step 2: Configure Google Drive Trigger (5 minutes)

#### 2.1 Select App and Event
- **Choose App**: Google Drive
- **Choose Event**: "New File in Folder"
- **Click Continue**

#### 2.2 Connect Google Drive Account
- **Sign in** to your Google Drive account
- **Allow access** to Zapier
- **Test connection** to ensure it works

#### 2.3 Configure Trigger Settings
```
Folder: [Select your bills folder]
File Extensions: pdf,png,jpg,jpeg
Include Subfolders: No (unless you want subfolders)
```

#### 2.4 Test the Trigger
- **Upload a test file** to your designated folder
- **Click "Test trigger"**
- **Verify** Zapier can see the uploaded file
- **Continue** to next step

### Step 3: Set Up ChatGPT OCR Processing (10 minutes)

#### 3.1 Add ChatGPT Action
- **Choose App**: ChatGPT
- **Choose Event**: "Conversation"
- **Connect** your ChatGPT account (Plus subscription required)

#### 3.2 Configure ChatGPT Prompt

**User Message**:
```
Please analyze this bill/invoice image and extract the following information in JSON format. Be as accurate as possible and ensure all amounts are numeric values without currency symbols.

Required JSON format:
{
  "vendor_name": "Full company name from the bill (no abbreviations)",
  "amount": "Total amount as number only (e.g., 150.75, not $150.75)",
  "invoice_date": "Date in YYYY-MM-DD format (e.g., 2024-10-28)",
  "description": "Brief description of services/products (max 100 chars)",
  "reference": "Invoice number, reference, or bill number",
  "currency": "Currency code (USD, EUR, GBP, etc.)",
  "tax_amount": "Tax amount as number only (0 if no tax visible)"
}

Important rules:
- Return ONLY the JSON object, no other text
- If any field is unclear, use your best judgment
- For amounts, use numbers only (no currency symbols or commas)
- For vendor_name, use the full legal name if available
- For dates, convert any format to YYYY-MM-DD
- If no reference number, use "AUTO-" + random 4 digits

Image to analyze: {{1.Download URL}}
```

**Assistant Instructions**:
```
You are a professional OCR assistant specializing in invoice and bill processing. Your task is to extract structured data from bill images with high accuracy. Always return only valid JSON format. If any information is unclear or missing, make reasonable assumptions but prioritize accuracy. For amounts, never include currency symbols or text - only numbers with decimals where appropriate.
```

#### 3.3 Test ChatGPT Processing
- **Use the test file** from Google Drive trigger
- **Run the test** and verify JSON output is properly formatted
- **Check accuracy** of extracted data
- **Refine prompt** if needed for better accuracy

### Step 4: Optional - Log to Google Sheets (5 minutes)

*This step is optional but recommended for tracking and debugging*

#### 4.1 Create Logging Spreadsheet
- **Create new Google Sheet** named "Bill Automation Log"
- **Add headers**: Date, Vendor, Amount, Status, Bill ID, Errors
- **Share with Zapier** or ensure it's accessible

#### 4.2 Add Google Sheets Action
- **Choose App**: Google Sheets
- **Choose Event**: "Create Spreadsheet Row"
- **Select your logging spreadsheet**

#### 4.3 Configure Logging Data
```
Date: {{Zap run timestamp}}
Vendor: {{ChatGPT response vendor_name}}
Amount: {{ChatGPT response amount}}
File Name: {{Google Drive file name}}
Status: Processing
Bill ID: [Will be filled later]
Errors: [Will be filled if errors occur]
```

### Step 5: Configure Webhook to Odoo (5 minutes)

#### 5.1 Add Webhook Action
- **Choose App**: Webhooks by Zapier
- **Choose Event**: "POST"

#### 5.2 Configure Webhook Settings

**URL**: 
```
https://your-odoo-domain.com/api/v1/bills/create
```

**Method**: `POST`

**Data Pass-Through**: `No`

**Payload Type**: `JSON`

#### 5.3 Set Request Headers
```json
{
  "Content-Type": "application/json"
}
```

#### 5.4 Configure Request Body

**Using Individual Fields Method**:
```json
{
  "vendor_name": "{{2.vendor_name}}",
  "amount": "{{2.amount}}",
  "invoice_date": "{{2.invoice_date}}",
  "description": "{{2.description}}",
  "reference": "{{2.reference}}",
  "currency": "{{2.currency}}",
  "tax_amount": "{{2.tax_amount}}",
  "file_url": "{{1.Download URL}}",
  "file_name": "{{1.Name}}"
}
```

**Using Full JSON Method** (if ChatGPT returns complete JSON):
```json
{
  "vendor_name": "{{2.Parse JSON vendor_name}}",
  "amount": "{{2.Parse JSON amount}}",
  "invoice_date": "{{2.Parse JSON invoice_date}}",
  "description": "{{2.Parse JSON description}}",
  "reference": "{{2.Parse JSON reference}}",
  "currency": "{{2.Parse JSON currency}}",
  "tax_amount": "{{2.Parse JSON tax_amount}}",
  "file_url": "{{1.Download URL}}",
  "file_name": "{{1.Name}}"
}
```

#### 5.5 Add Security (If Required)
If your Odoo setup requires API key authentication:
```json
{
  "vendor_name": "{{2.vendor_name}}",
  "amount": "{{2.amount}}",
  "invoice_date": "{{2.invoice_date}}",
  "description": "{{2.description}}",
  "reference": "{{2.reference}}",
  "api_key": "your-api-key-here",
  "file_url": "{{1.Download URL}}",
  "file_name": "{{1.Name}}"
}
```

#### 5.6 Test Webhook
- **Click "Test step"**
- **Verify** response from Odoo (should be 200 OK)
- **Check** if bill was created in Odoo
- **Review** webhook logs in Odoo (if module installed)

### Step 6: Add Error Handling (Optional but Recommended)

#### 6.1 Add Filter (Optional)
- **Insert Filter** after ChatGPT step
- **Condition**: `vendor_name` exists and is not empty
- **This prevents** processing when OCR fails completely

#### 6.2 Add Error Notification
If webhook fails:
- **Add Email action** after webhook
- **Trigger only on** webhook failure
- **Send notification** to admin with error details

#### 6.3 Add Success Confirmation
If webhook succeeds:
- **Add Email action** (optional)
- **Trigger only on** webhook success  
- **Send confirmation** with bill details

---

## ⚙️ Advanced Configuration

### Improving OCR Accuracy

#### Enhanced ChatGPT Prompt
```
You are an expert OCR system for processing invoices and bills. Analyze the uploaded document image with extreme attention to detail.

Extract the following information and return ONLY a valid JSON object:

{
  "vendor_name": "Complete legal business name (look for 'Bill From:', header, letterhead)",
  "amount": "Total amount due as number (check 'Total:', 'Amount Due:', bottom right)",
  "invoice_date": "Invoice/bill date in YYYY-MM-DD format (not due date)",
  "description": "Main service/product description (first line item if multiple)",
  "reference": "Invoice number, bill number, or reference (look for INV, #, REF)",
  "currency": "Currency code (USD, EUR, GBP - if not visible, assume USD)",
  "tax_amount": "Tax amount as number (look for 'Tax:', 'VAT:', 'Sales Tax:')"
}

OCR Guidelines:
- Read text carefully, including small print
- For vendor_name: Use full legal name, not abbreviations
- For amount: Find the final total, not subtotals
- For dates: Convert any format (MM/DD/YY, DD-MM-YYYY) to YYYY-MM-DD
- For currency: Look for symbols ($, €, £) or text
- If field is unclear: make best educated guess
- Never include currency symbols in amount fields

Document to process: {{1.Download URL}}
```

#### Multiple OCR Attempts
For better accuracy, you can:
1. **Duplicate ChatGPT step** with different prompts
2. **Compare results** using Formatter
3. **Use highest confidence** result

### File Handling Optimization

#### File Size Optimization
- **Add Filter** to check file size
- **Skip processing** if file > 10MB
- **Send notification** for oversized files

#### File Type Validation
- **Add Filter** after Google Drive trigger
- **Check file extension** is in allowed list
- **Skip non-image/PDF files**

### Batch Processing

#### Multiple Files at Once
- **Use "New Files in Folder"** trigger (plural)
- **Add Iterator** to process each file
- **Loop through** ChatGPT and webhook steps

### Duplicate Prevention

#### Before Processing
- **Add Google Sheets lookup** to check if file already processed
- **Skip if** filename exists in log
- **Continue if** new file

#### After Processing  
- **Update tracking sheet** with file name and bill ID
- **Mark as processed** with timestamp

---

## 🧪 Testing & Validation

### Pre-Launch Testing

#### Test Scenarios
1. **Perfect Bill** - High quality PDF with all fields clear
2. **Poor Quality** - Blurry or low-resolution image
3. **Foreign Language** - Non-English bill (if applicable)
4. **Complex Layout** - Multi-page or complex formatting
5. **Partial Data** - Missing some required fields
6. **Duplicate Test** - Same bill uploaded twice

#### Validation Checklist
- [ ] OCR accuracy >90% for good quality bills
- [ ] All required fields extracted correctly
- [ ] Amounts parsed as numbers (no currency symbols)
- [ ] Dates formatted correctly (YYYY-MM-DD)
- [ ] Vendor names complete and accurate
- [ ] File attachments working in Odoo
- [ ] Error handling working for bad data
- [ ] Duplicate prevention working
- [ ] Processing time <2 minutes per bill

### Performance Testing

#### Load Testing
- **Upload 10 bills** simultaneously
- **Monitor processing** time and success rate
- **Check Zapier** task usage limits
- **Verify Odoo** performance not impacted

#### Monthly Usage Estimation
```
Bills per month: _____ 
× 2 Zapier tasks per bill (trigger + webhook) = _____ tasks
× ChatGPT API calls = $____ estimated cost
× Zapier plan cost = $19.99
Total monthly cost = $____
```

---

## 🔍 Monitoring & Maintenance

### Zapier Task History

#### Daily Monitoring
- **Check Task History** in Zapier dashboard
- **Review failed tasks** and error messages
- **Retry failed tasks** after fixing issues
- **Monitor usage** against plan limits

#### Weekly Review
- **Analyze success rate** trends
- **Identify common** failure patterns
- **Update prompts** if OCR accuracy decreases
- **Check file** processing volumes

### Error Patterns & Solutions

#### Common Zapier Errors

**"ChatGPT returned invalid JSON"**
- **Solution**: Update ChatGPT prompt for better JSON formatting
- **Prevention**: Add JSON validation step

**"Webhook timeout"**
- **Solution**: Increase Zapier timeout setting
- **Prevention**: Optimize Odoo server performance

**"File not accessible"**
- **Solution**: Check Google Drive permissions
- **Prevention**: Use service account for consistent access

**"Rate limit exceeded"**
- **Solution**: Add delays between requests
- **Prevention**: Upgrade Zapier plan or optimize workflow

### OCR Quality Monitoring

#### Accuracy Tracking
- **Manual spot checks** on 5-10% of processed bills
- **Compare extracted** vs actual values
- **Track accuracy** metrics over time
- **Update prompts** when accuracy drops below 90%

#### Common OCR Issues

**Vendor Name Extraction**
- **Problem**: Abbreviated or partial names
- **Solution**: Update prompt to look for full legal names
- **Enhancement**: Add vendor name mapping in Odoo

**Amount Parsing**
- **Problem**: Currency symbols included in amount
- **Solution**: Emphasize number-only requirement in prompt
- **Validation**: Add regex check in webhook

**Date Format Issues**
- **Problem**: Wrong date format or wrong date field
- **Solution**: Specify exact date format requirement
- **Enhancement**: Add date validation in Odoo webhook

---

## 📈 Optimization Tips

### Performance Optimization

#### Zapier Efficiency
- **Combine steps** where possible
- **Use filters** to skip unnecessary processing
- **Minimize external** API calls
- **Cache frequently** used data

#### ChatGPT Optimization
- **Optimize prompt** length for cost efficiency
- **Use precise** instructions to reduce retries
- **Consider GPT-4** for better accuracy vs GPT-3.5 for speed
- **Batch similar** requests if possible

### Cost Optimization

#### Zapier Plan Management
- **Monitor task usage** monthly
- **Optimize workflow** to reduce task count
- **Consider higher plans** for bulk discounts
- **Use built-in apps** instead of webhooks where possible

#### ChatGPT API Costs
- **Monitor token** usage
- **Optimize prompt** to reduce tokens
- **Use appropriate model** (GPT-3.5 vs GPT-4)
- **Implement caching** for repeated requests

---

## 🚨 Troubleshooting Guide

### Setup Issues

#### Zapier Connection Problems
1. **Check account** permissions and subscriptions
2. **Verify app connections** are active
3. **Re-authenticate** if connections expired
4. **Test individual steps** in isolation

#### Google Drive Access Issues
1. **Check folder** permissions
2. **Verify Zapier** has access to correct folder
3. **Test file upload** and trigger manually
4. **Check file format** support

#### ChatGPT Integration Issues
1. **Verify subscription** status (Plus required)
2. **Check API** rate limits and usage
3. **Test prompt** with sample images
4. **Validate JSON** output format

### Runtime Issues

#### Processing Failures
1. **Check Zapier** task history for error details
2. **Review webhook** response codes and messages
3. **Verify file** accessibility and format
4. **Test with** smaller/simpler files

#### Data Quality Issues
1. **Review OCR** accuracy on failed bills
2. **Update prompts** for better extraction
3. **Check for** special characters or formatting
4. **Validate data** types and formats

### Recovery Procedures

#### Reprocessing Failed Bills
1. **Identify failed** tasks in Zapier history
2. **Fix underlying** issue (prompt, webhook, etc.)
3. **Manually replay** failed tasks
4. **Verify results** in Odoo

#### Bulk Reprocessing
1. **Export failed** task list from Zapier
2. **Re-upload files** to trigger folder
3. **Monitor processing** closely
4. **Update tracking** systems

---

## 📋 Launch Checklist

### Pre-Launch Validation
- [ ] All test scenarios passed
- [ ] OCR accuracy >90% achieved
- [ ] Error handling tested and working
- [ ] Duplicate prevention verified
- [ ] File attachment functionality confirmed
- [ ] Security settings configured
- [ ] Monitoring systems in place

### Go-Live Preparation
- [ ] Team trained on new process
- [ ] Old manual process documented as backup
- [ ] Communication sent to all users
- [ ] Support contacts identified
- [ ] Rollback plan prepared

### Post-Launch Monitoring
- [ ] Daily monitoring for first week
- [ ] Success rate tracking implemented
- [ ] Error notification system active
- [ ] User feedback collection planned
- [ ] Performance metrics baseline established

---

## 📞 Support Resources

### Zapier Support
- **Help Center**: https://zapier.com/help
- **Community**: https://community.zapier.com
- **Status Page**: https://status.zapier.com
- **Contact**: help@zapier.com

### ChatGPT/OpenAI Support  
- **Documentation**: https://platform.openai.com/docs
- **Help Center**: https://help.openai.com
- **API Status**: https://status.openai.com
- **Community**: https://community.openai.com

### Integration Issues
- **Webhook Testing**: Use test_webhook.py script
- **Odoo Logs**: Check webhook module logs
- **Network Issues**: Verify connectivity and firewalls
- **Performance**: Monitor server resources

---

## 🎯 Success Metrics

### Key Performance Indicators
- **Success Rate**: >95% for good quality bills
- **Processing Time**: <2 minutes from upload to Odoo bill
- **OCR Accuracy**: >90% for all extracted fields
- **Error Rate**: <5% overall failure rate
- **User Adoption**: >80% of bills processed automatically

### Monthly Review Metrics
- **Bills Processed**: Track volume trends
- **Cost per Bill**: Monitor automation costs
- **Time Savings**: Calculate vs manual processing
- **Error Patterns**: Identify improvement opportunities
- **User Satisfaction**: Survey team regularly

---

**Setup Complete!** 🎉

Your Zapier automation is now ready to process bills automatically. Monitor the first few bills closely and adjust prompts as needed for optimal accuracy.

**Next Steps:**
1. Upload 5-10 test bills to validate end-to-end processing
2. Train your team on the new upload process
3. Set up regular monitoring and maintenance schedules
4. Document any customizations for your specific use case