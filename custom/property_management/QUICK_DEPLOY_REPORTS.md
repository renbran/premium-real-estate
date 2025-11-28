# Quick Deployment Guide - Report PDF Fixes

## ⚡ Fast Track Deployment

### Step 1: Backup (2 minutes)
```bash
sudo -u postgres pg_dump sampledb > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Pull Latest Code (1 minute)
```bash
cd /path/to/odoo/custom/addons/property_management
git pull origin main
```

### Step 3: Upgrade Module (3 minutes)
```bash
cd /path/to/odoo
sudo -u odoo python3 odoo-bin -u property_management -d sampledb --stop-after-init
```

### Step 4: Restart Odoo (1 minute)
```bash
sudo systemctl restart scholarixstudy.cloudpepper.site
# OR
sudo systemctl restart odoo.service
```

### Step 5: Test (5 minutes)
1. Login to Odoo
2. Go to Property Management
3. Open any Property Sale record
4. Click Print → Sales Offer Report
5. Verify PDF generates successfully
6. Click "Send Sales Offer Email"
7. Check customer receives email with PDF

---

## 🧪 Quick Test Checklist

**Reports to Test:**
- [ ] Property Sales Offer (from property.property)
- [ ] Sales Offer Report (from property.sale)
- [ ] Property Sale Report (from property.sale)
- [ ] Email with PDF attachment

**Expected Results:**
- ✅ All PDFs generate without errors
- ✅ All fields populate correctly
- ✅ Images display properly
- ✅ Currency formatting works (e.g., $1,234.56)
- ✅ Dates format correctly (e.g., 04 November 2025)
- ✅ Status badges show colors
- ✅ Email sends successfully

---

## 🔴 If Something Goes Wrong

### Rollback Procedure:
```bash
# 1. Stop Odoo
sudo systemctl stop scholarixstudy.cloudpeeper.site

# 2. Restore database
sudo -u postgres psql sampledb < /tmp/backup_TIMESTAMP.sql

# 3. Revert code
cd /path/to/odoo/custom/addons/property_management
git checkout HEAD~1 reports/

# 4. Restart Odoo
sudo systemctl start scholarixstudy.cloudpepper.site
```

### Check Logs:
```bash
tail -f /var/log/odoo/odoo-server.log | grep -i "error\|report\|pdf"
```

---

## 📝 What Was Fixed

**Files Changed:**
- `reports/property_sale_management.xml` - Complete rewrite with QWeb
- `reports/sales_offer_report_template.xml` - CSS and datetime fixes
- `reports/property_sales_offer_template.xml` - Datetime fix

**Commit Hash:** b605965

**Main Changes:**
1. Converted `data` dictionary to proper QWeb `t-foreach="docs" t-as="o"` syntax
2. Fixed all datetime references
3. Added professional CSS styling
4. Fixed binary image handling with `.decode()`
5. Added status color badges

---

## ⏱️ Total Estimated Time: 15-20 minutes

**No downtime required** - Module can be upgraded while system is running, just restart Odoo service at the end.

---

## 📞 Support

If you encounter any issues:
1. Check the logs: `tail -f /var/log/odoo/odoo-server.log`
2. Verify module state: Apps → Property Sale Management → Check "Installed"
3. Clear browser cache and retry
4. Refer to full REPORT_FIX_SUMMARY.md for detailed troubleshooting

**Status:** ✅ All fixes tested and ready for production
