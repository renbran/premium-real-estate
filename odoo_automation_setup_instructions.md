# 🔧 Odoo Automation Setup Instructions - Complete Technical Guide

This comprehensive guide covers all aspects of setting up the bill automation system in Odoo, including both quick setup and production module installation.

**📋 What This Guide Covers:**
- Quick setup using Server Actions (15 minutes)
- Production module installation (45 minutes)  
- Security configuration and best practices
- Troubleshooting and maintenance
- Performance optimization

---

## 🎯 Choose Your Setup Path

### Path 1: Quick Setup ⚡ (15 minutes)
**Best for**: Testing, proof of concept, small volumes (<100 bills/month)

**Pros**:
- Fast implementation
- No file copying required  
- Easy to modify and test
- Works immediately

**Cons**:
- Limited logging capabilities
- Basic error handling
- No management interface
- Harder to maintain long-term

### Path 2: Production Module 🏭 (45 minutes)  
**Best for**: Production use, high volumes (>100 bills/month), enterprise needs

**Pros**:
- Professional logging dashboard
- Advanced error handling
- Security features
- Easy maintenance and monitoring
- Scalable architecture

**Cons**:
- Longer setup time
- Requires file management
- Module updates needed

---

## 🚀 Path 1: Quick Setup Instructions

### Prerequisites
- [ ] Odoo 17, 18, or 19 running with HTTPS
- [ ] Admin access to Odoo
- [ ] Purchase module installed
- [ ] At least one Purchase Journal configured
- [ ] At least one Expense Account available

### Step 1: Create Server Action (10 minutes)

#### 1.1 Navigate to Server Actions
1. **Go to**: Settings → Technical → Actions → Server Actions
2. **Click**: Create
3. **Fill basic information**:
   - **Name**: `Bill Automation Webhook`
   - **Model**: `ir.http`  
   - **Action Type**: `Python Code`

#### 1.2 Copy Python Code
**Copy the entire code from `odoo_automation_code.py` into the Python Code field**

*Note: The code is approximately 400 lines and includes all necessary functions for bill processing.*

#### 1.3 Save Server Action
- **Click Save** to create the server action

### Step 2: Create Webhook Route (3 minutes)

#### 2.1 Create Controller File
**Option A: Add to existing controller**
If you have custom modules, add to existing controller:

```python
@http.route('/web/hook/<string:hook_id>', type='json', auth='none', 
            methods=['POST'], csrf=False, cors="*")
def handle_bill_webhook(self, hook_id=None, **kwargs):
    # Verify hook ID  
    if hook_id != "b43b901e-1346-4c99-afab-1ea8b6946ba2":
        return {'error': 'Invalid webhook ID'}
    
    # Execute server action
    server_action = request.env['ir.actions.server'].sudo().search([
        ('name', '=', 'Bill Automation Webhook')
    ], limit=1)
    
    if server_action:
        return server_action.run()
    else:
        return {'error': 'Server action not found'}
```

**Option B: Use Website Menu (Simpler)**
1. **Go to**: Settings → Technical → User Interface → Website Menus
2. **Create new menu**:
   - **URL**: `/web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2`
   - **Action**: Select "Bill Automation Webhook" server action
   - **Save**

### Step 3: Test Quick Setup (2 minutes)

#### 3.1 Run Test Script
```bash
python3 test_webhook.py --url https://your-odoo.com --health-only
```

#### 3.2 Create Test Bill
```bash  
python3 test_webhook.py --url https://your-odoo.com --vendor "Test Corp" --amount 123.45
```

#### 3.3 Verify in Odoo
- **Check**: Accounting → Vendor Bills
- **Verify**: New bill created with correct data
- **Test**: File attachment (if file URL provided)

### Step 4: Configure Zapier
Update your Zapier webhook URL to:
```
https://your-odoo.com/web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2
```

---

## 🏭 Path 2: Production Module Installation

### Step 1: Prepare Module Files (5 minutes)

#### 1.1 Copy Module Directory
```bash
# Copy the entire odoo_module directory to your addons folder
cp -r /path/to/project/odoo_module /path/to/odoo/addons/bill_automation_webhook

# Set proper permissions
chmod -R 755 /path/to/odoo/addons/bill_automation_webhook
chown -R odoo:odoo /path/to/odoo/addons/bill_automation_webhook
```

#### 1.2 Verify File Structure
```
/path/to/odoo/addons/bill_automation_webhook/
├── __init__.py
├── __manifest__.py  
├── README.md
├── controllers/
│   ├── __init__.py
│   └── webhook_controller.py
├── models/
│   ├── __init__.py
│   ├── webhook_log.py
│   ├── bill_automation_config.py
│   └── account_move.py
├── views/
│   └── webhook_log_views.xml
└── security/
    └── ir.model.access.csv
```

### Step 2: Restart Odoo Service (2 minutes)

```bash
# Stop Odoo service
sudo systemctl stop odoo

# Or using service command
sudo service odoo stop

# Start Odoo service  
sudo systemctl start odoo

# Or using service command
sudo service odoo start

# Check status
sudo systemctl status odoo
```

### Step 3: Install Module (5 minutes)

#### 3.1 Update App List
1. **Go to**: Apps in Odoo
2. **Click**: Update Apps List (may require developer mode)
3. **Wait**: For update to complete

#### 3.2 Install Module
1. **Remove**: "Apps" filter to show all modules
2. **Search**: "Bill Automation Webhook"
3. **Click**: Install on the module
4. **Wait**: For installation to complete

#### 3.3 Verify Installation
- **Check**: Accounting menu for "Bill Automation" section
- **Verify**: Configuration menu is accessible
- **Test**: Webhook logs view loads

### Step 4: Configure Module (15 minutes)

#### 4.1 Basic Configuration
1. **Navigate to**: Accounting → Bill Automation → Configuration  
2. **Create/Edit** configuration with these settings:

**Basic Settings**:
```
✅ Active: True
✅ Webhook Enabled: True  
📝 Configuration Name: "Production Bill Automation"
```

**Processing Settings**:
```
✅ Auto-create Vendors: True
✅ Duplicate Detection: True
✅ File Attachment: True
```

**Default Accounts**:
```
📂 Default Journal: [Select your Purchase Journal]
💰 Default Expense Account: [Select expense account]
💱 Default Currency: [Your company currency]
```

#### 4.2 Security Configuration (Optional)

**For Enhanced Security**:
```
✅ Require API Key: True  
🔑 API Key: [Auto-generated - copy this for Zapier]
📍 Allowed IPs: 192.168.1.0/24,10.0.0.0/8 (adjust as needed)
```

**For Basic Security** (recommended for most users):
```
❌ Require API Key: False
📍 Allowed IPs: [Leave empty to allow all]
```

#### 4.3 Advanced Settings
```
📁 Max File Size: 10 MB
⏱️ Request Timeout: 30 seconds  
📧 Error Notifications: True
📮 Notification Email: admin@yourcompany.com
```

#### 4.4 Test Configuration
- **Click**: "Test Configuration" button
- **Verify**: All checks pass (green checkmarks)
- **Fix**: Any issues identified

### Step 5: Update Zapier Configuration (3 minutes)

Update your Zapier webhook URL to:
```
https://your-odoo.com/api/v1/bills/create
```

If using API key authentication, add to Zapier payload:
```json
{
  "vendor_name": "{{ChatGPT.vendor_name}}",
  "amount": "{{ChatGPT.amount}}", 
  "api_key": "your-generated-api-key",
  "..."
}
```

### Step 6: Comprehensive Testing (15 minutes)

#### 6.1 API Endpoint Tests
```bash
# Health check
python3 test_webhook.py --url https://your-odoo.com --health-only

# Service status  
curl -X GET https://your-odoo.com/api/v1/bills/status

# Create test bill
python3 test_webhook.py --url https://your-odoo.com --test-all
```

#### 6.2 Zapier End-to-End Test
1. **Upload test bill** to Google Drive folder
2. **Monitor Zapier** task history
3. **Check webhook logs** in Odoo: Accounting → Bill Automation → Webhook Logs
4. **Verify bill creation** in Accounting → Vendor Bills
5. **Check file attachment** on created bill

#### 6.3 Error Handling Test
1. **Upload invalid file** (unsupported format)
2. **Send invalid JSON** to webhook
3. **Test duplicate prevention** (upload same bill twice)
4. **Verify error logging** in webhook logs

---

## 🛡️ Security Configuration

### HTTPS Requirements
**⚠️ Critical**: Always use HTTPS for webhook endpoints in production

#### Enable HTTPS in Odoo
```bash
# Add to odoo.conf
[options]
proxy_mode = True
xmlrpc_interface = 127.0.0.1
netrpc = False
```

#### Nginx Configuration (Recommended)
```nginx
server {
    listen 443 ssl;
    server_name your-odoo.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

### API Key Authentication

#### Generate Strong API Keys
```python
# In Odoo shell or Python
import secrets
import string

def generate_api_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

print(generate_api_key())
```

#### Store API Keys Securely
- **Never commit** API keys to version control
- **Use environment variables** for sensitive data
- **Rotate keys** regularly (monthly or quarterly)
- **Log API key usage** for auditing

### IP Address Restrictions

#### Common IP Ranges to Allow
```
# Zapier IP ranges (update regularly from Zapier docs)
54.85.0.0/16
52.0.0.0/8  
34.0.0.0/8

# Your office network
192.168.1.0/24

# Cloud providers (if applicable)
10.0.0.0/8
```

#### Firewall Configuration
```bash
# Allow only specific IPs to webhook endpoint
iptables -A INPUT -p tcp --dport 443 -s 54.85.0.0/16 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -s 52.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j DROP
```

---

## 📊 Monitoring & Logging

### Odoo Server Logs

#### Enable Detailed Logging
```bash
# Add to odoo.conf for webhook debugging
[options]  
log_level = debug
logfile = /var/log/odoo/odoo.log
log_handler = :INFO,werkzeug:WARNING,odoo.service:INFO
```

#### Monitor Log Files
```bash
# Real-time monitoring
tail -f /var/log/odoo/odoo.log | grep -E "(webhook|bill)"

# Search for errors
grep -E "ERROR.*webhook" /var/log/odoo/odoo.log

# Check specific time range
grep "2024-10-28 10:" /var/log/odoo/odoo.log | grep webhook
```

### Webhook Log Analysis

#### Access Webhook Logs
1. **Go to**: Accounting → Bill Automation → Webhook Logs
2. **Filter by**: Status, date range, vendor, etc.
3. **Export data**: For external analysis if needed

#### Key Metrics to Track
- **Success Rate**: Target >95%
- **Processing Time**: Target <30 seconds
- **Error Patterns**: Identify common issues
- **Volume Trends**: Plan for capacity

#### Automated Alerts
```python
# Add to scheduled action (daily)
def check_webhook_health():
    yesterday = fields.Date.today() - timedelta(days=1)
    logs = env['webhook.log'].search([
        ('create_date', '>=', yesterday)
    ])
    
    if logs:
        success_rate = len(logs.filtered('status', '=', 'success')) / len(logs) * 100
        if success_rate < 90:
            # Send alert email
            pass
```

### Performance Monitoring

#### Database Query Analysis
```sql
-- Check webhook processing performance
SELECT 
    DATE(create_date) as date,
    COUNT(*) as total_requests,
    AVG(processing_time) as avg_processing_time,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful
FROM webhook_log 
WHERE create_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(create_date)
ORDER BY date;
```

#### Server Resource Monitoring
```bash
# CPU and memory usage
htop

# Disk space
df -h

# Network connections
netstat -tulpn | grep :8069

# Odoo processes
ps aux | grep odoo
```

---

## 🔧 Troubleshooting Guide

### Common Installation Issues

#### Module Not Appearing in Apps List
**Causes & Solutions**:
1. **File permissions**: `chmod -R 755 /path/to/module`
2. **Wrong location**: Module must be in addons path
3. **Syntax errors**: Check `__manifest__.py` for errors
4. **Missing dependencies**: Install required modules first
5. **Cache issues**: Restart Odoo service

#### Installation Fails with Errors
**Check These**:
```bash
# Odoo server logs during installation
tail -f /var/log/odoo/odoo.log

# File syntax
python3 -m py_compile /path/to/module/__manifest__.py

# Dependencies 
pip3 install requests (if missing)

# Database permissions
sudo -u postgres psql -c "ALTER USER odoo CREATEDB;"
```

### Runtime Issues

#### Webhook Returns 404 Not Found
**Diagnostic Steps**:
1. **Verify module** is installed and activated
2. **Check URL** format: `/api/v1/bills/create`
3. **Test health** endpoint: `/api/v1/bills/health`
4. **Review Odoo** server logs for routing errors
5. **Restart Odoo** service if needed

#### Bills Not Created Despite Success Response
**Check These**:
1. **Webhook logs** for detailed error messages
2. **Journal configuration**: Must have purchase journal
3. **Account configuration**: Must have expense accounts
4. **Vendor data**: Check if vendor name is valid
5. **Amount parsing**: Verify amounts are numeric

#### File Attachment Failures
**Troubleshooting**:
1. **URL accessibility**: Test download URL manually
2. **File size**: Check against max size limit (10MB default)
3. **Network connectivity**: Odoo server can reach file URL
4. **Permissions**: Odoo user can write to attachment directory
5. **File format**: Supported formats (PDF, PNG, JPG, JPEG)

### Performance Issues

#### Slow Webhook Response Times
**Optimization Steps**:
1. **Database indexing**: Ensure proper indexes exist
2. **Server resources**: Check CPU, memory, disk usage
3. **File download**: Optimize file attachment process
4. **Query optimization**: Review database queries
5. **Caching**: Enable Odoo caching where appropriate

#### High Memory Usage
**Solutions**:
1. **Log cleanup**: Remove old webhook logs regularly
2. **Attachment management**: Compress or archive old files
3. **Database maintenance**: Regular vacuum and reindex
4. **Worker processes**: Optimize Odoo worker configuration

---

## 🔄 Maintenance Procedures

### Daily Maintenance (5 minutes)

#### Health Check Routine
```bash
# Check service status
systemctl status odoo

# Test webhook endpoint  
curl -X GET https://your-odoo.com/api/v1/bills/health

# Review recent errors
tail -100 /var/log/odoo/odoo.log | grep ERROR
```

#### Monitor Key Metrics
- **Webhook success rate** (last 24 hours)
- **Processing times** (average and max)
- **Error patterns** (frequent issues)
- **System resources** (CPU, memory, disk)

### Weekly Maintenance (15 minutes)

#### Log Analysis
1. **Export webhook logs** for the past week
2. **Analyze success rates** and trends
3. **Identify error patterns** and root causes
4. **Review vendor auto-creation** accuracy
5. **Check file attachment** success rates

#### Performance Review
```sql
-- Weekly performance query
SELECT 
    status,
    COUNT(*) as count,
    AVG(processing_time) as avg_time,
    MAX(processing_time) as max_time
FROM webhook_log 
WHERE create_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY status;
```

### Monthly Maintenance (30 minutes)

#### System Optimization
1. **Clean up old logs** (30+ days)
2. **Optimize database** (vacuum, reindex)
3. **Review security** settings and access logs
4. **Update API keys** if using rotation policy
5. **Test backup/restore** procedures

#### Documentation Updates
- **Update configuration** documentation
- **Record any customizations** made
- **Update team training** materials
- **Review troubleshooting** procedures

---

## 📈 Performance Optimization

### Database Optimization

#### Essential Indexes
```sql
-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_webhook_log_status 
    ON webhook_log(status);
    
CREATE INDEX IF NOT EXISTS idx_webhook_log_create_date 
    ON webhook_log(create_date);
    
CREATE INDEX IF NOT EXISTS idx_webhook_log_vendor 
    ON webhook_log(vendor_name);
    
CREATE INDEX IF NOT EXISTS idx_account_move_webhook 
    ON account_move(created_by_webhook);
```

#### Regular Maintenance
```sql  
-- Weekly database maintenance
VACUUM ANALYZE webhook_log;
VACUUM ANALYZE account_move;
REINDEX TABLE webhook_log;
```

### Server Configuration

#### Odoo Configuration Optimization
```bash
# Add to odoo.conf for better performance
[options]
workers = 4
max_cron_threads = 1
db_maxconn = 64
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
```

#### Nginx Optimization
```nginx
# Add to nginx config for webhook performance
location /api/v1/bills/ {
    proxy_pass http://127.0.0.1:8069;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    
    # Increase buffer sizes for large files
    proxy_buffer_size 16k;
    proxy_buffers 32 16k;
    proxy_busy_buffers_size 64k;
}
```

### Application Optimization

#### File Processing Optimization
```python
# Optimize file download and processing
def optimized_file_download(file_url, max_size_mb=10):
    try:
        # Stream download for large files
        with requests.get(file_url, stream=True, timeout=30) as response:
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > max_size_mb * 1024 * 1024:
                raise ValueError(f"File too large: {content_length} bytes")
            
            # Download in chunks
            chunks = []
            total_size = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    total_size += len(chunk)
                    if total_size > max_size_mb * 1024 * 1024:
                        raise ValueError(f"File too large: {total_size} bytes")
                    chunks.append(chunk)
            
            return b''.join(chunks)
            
    except Exception as e:
        raise Exception(f"File download failed: {str(e)}")
```

---

## 🎯 Success Metrics & KPIs

### Technical Metrics

#### System Performance
- **Webhook Response Time**: <2 seconds (95th percentile)
- **Success Rate**: >95% overall
- **Error Rate**: <5% of all requests
- **Uptime**: >99.5% availability
- **File Attachment Success**: >90% when URL provided

#### Processing Metrics
- **OCR Accuracy**: >90% field extraction accuracy
- **Vendor Auto-creation**: <10% false positives
- **Duplicate Prevention**: 100% effectiveness
- **Processing Throughput**: 100+ bills/hour capacity

### Business Metrics

#### Efficiency Gains
- **Time Savings**: 80-85% reduction in manual entry time
- **Error Reduction**: 70%+ reduction in data entry errors
- **Processing Speed**: <2 minutes from upload to Odoo bill
- **User Adoption**: >90% of bills processed via automation

#### Cost Effectiveness
- **ROI**: >500% within first year
- **Cost per Bill**: <$0.50 automation cost
- **Manual Labor Savings**: 15-20 hours/week for 100 bills/week
- **Error Correction Savings**: 5-10 hours/week reduced

---

## 📞 Support & Help Resources

### Internal Documentation
- **Configuration Guide**: This document
- **User Training**: Upload process documentation  
- **Troubleshooting**: Error resolution procedures
- **API Documentation**: Webhook endpoint specifications

### External Resources
- **Odoo Documentation**: https://www.odoo.com/documentation/
- **Python Requests**: https://docs.python-requests.org/
- **Zapier Help**: https://zapier.com/help
- **OpenAI API**: https://platform.openai.com/docs

### Emergency Contacts
- **System Administrator**: ________________
- **Odoo Developer**: ________________  
- **Accounting Manager**: ________________
- **IT Support**: ________________

### Escalation Procedures
1. **Level 1**: Check webhook logs and common solutions
2. **Level 2**: Review server logs and system status
3. **Level 3**: Contact system administrator
4. **Level 4**: Engage external Odoo support or developer

---

**Setup Complete!** 🎉

Your Odoo bill automation system is now configured and ready for production use. Remember to monitor the system regularly and maintain proper backup procedures.

**Next Recommended Actions**:
1. **Train your team** on the new automated process
2. **Set up monitoring** dashboards and alerts  
3. **Schedule regular maintenance** windows
4. **Document any customizations** for future reference
5. **Plan for scaling** as volume increases