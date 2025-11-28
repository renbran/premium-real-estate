# 🚀 DEPLOYMENT GUIDE - Property Management Module v18.0.1.0.1

## ✅ MODULE IS PRODUCTION READY!

All critical issues have been fixed and the module is ready for production deployment.

---

## 📦 WHAT WAS FIXED

### Security & Access Control
- ✅ Added complete security rules for all models
- ✅ Proper user group assignments (base.group_user)
- ✅ All CRUD operations properly controlled

### Data Integrity
- ✅ SQL constraints prevent invalid data at database level
- ✅ Python constraints validate business logic
- ✅ Unique constraints on critical fields
- ✅ Positive value checks on amounts
- ✅ Percentage range validations (0-100%)

### Performance Optimization
- ✅ Database indexes on foreign keys
- ✅ Computed fields properly stored
- ✅ Efficient field ordering
- ✅ Image size limits

### Code Quality
- ✅ Proper error handling
- ✅ Comprehensive logging
- ✅ Translation support
- ✅ Audit trail (mail tracking)
- ✅ Proper field relations with cascade rules

---

## 🔧 DEPLOYMENT STEPS

### Step 1: Backup Current Database (CRITICAL!)

```bash
cd /var/odoo/scholarixstudy.cloudpepper.site

# Create backup
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf \
  -d sampledb \
  --stop-after-init \
  --db-filter=sampledb

# Or use pg_dump
sudo -u postgres pg_dump sampledb > /tmp/sampledb_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Pull Latest Code

```bash
cd /var/odoo/scholarixstudy.cloudpepper.site/extra-addons

# If property_management is in a Git repository:
cd property_management
git pull origin main

# Or if it's part of the main addons repo:
cd ..
git pull origin main
```

### Step 3: Stop Odoo (Optional but Recommended)

```bash
sudo systemctl stop scholarixstudy.cloudpepper.site
```

### Step 4: Upgrade Module

```bash
cd /var/odoo/scholarixstudy.cloudpepper.site

sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf \
  -u property_management \
  -d sampledb \
  --stop-after-init
```

**Expected Output:**
```
INFO ? odoo.modules.loading: loading 1 modules...
INFO ? odoo.modules.loading: 1 modules loaded in 0.01s, 0 queries
INFO ? odoo.modules.registry: module property_management: loading
INFO ? odoo.modules.registry: module property_management: upgrading tables
INFO ? odoo.modules.registry: module property_management: creating or updating database tables
INFO ? odoo.modules.registry: module property_management: 100% complete
```

### Step 5: Start Odoo

```bash
sudo systemctl start scholarixstudy.cloudpepper.site

# Monitor startup
tail -f /var/odoo/scholarixstudy.cloudpepper.site/logs/odoo.log
```

### Step 6: Verify Deployment

```bash
# Check if Odoo is running
sudo systemctl status scholarixstudy.cloudpepper.site

# Check for errors in logs
grep -i "error\|warning\|property_management" /var/odoo/scholarixstudy.cloudpepper.site/logs/odoo.log | tail -20
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### 1. Login and Check Module Status

1. Go to: https://sampledb.scholarixglobal.com
2. Login as Administrator
3. Go to Apps
4. Search for "Property Management"
5. Status should be: **Installed** (Green)

### 2. Test Core Functionality

#### Test Property Creation:
```
1. Go to: Property Management > Properties
2. Click "New"
3. Fill in:
   - Name: Test Property 001
   - Property Price: 1000000
   - Sale/Rent: For Sale
   - Revenue Account: Select any income account
   - Currency: AED
4. Click "Save"
5. Should save successfully without errors
```

#### Test Sale Creation:
```
1. Open any property
2. Click "Create Sale" button
3. Fill in:
   - Customer: Select a customer (REQUIRED - will show red if empty)
   - Start Date: Today's date
   - Down Payment %: 20
   - No. of Installments: 12
4. Click "Save"
5. Click "Confirm Sale" button
6. Check:
   - Property state changes to "Sold"
   - Payment schedule is generated
   - State changes to "Confirmed"
```

#### Test Invoice Generation:
```
1. Open a confirmed sale
2. Click "Generate All Invoices"
3. Should show success message
4. Click "View Invoices"
5. Invoices should be listed
```

#### Test Broker Commission:
```
1. Create a sale with Seller/Broker filled in
2. Set Broker Commission %: 5
3. Confirm the sale
4. Click "Generate Broker Commission"
5. Should create commission record
6. Open commission record
7. Click "Generate Invoice"
8. Should create invoice successfully
```

### 3. Check Computed Fields

1. Open any property with confirmed sale
2. Verify these fields update:
   - Payment Progress shows percentage
   - Total Invoiced shows amount
   - Total Paid shows amount
   - Remaining Amount calculated correctly
   - Active Sale shows the correct sale

### 4. Check Reports

1. Open a property
2. Click "Sales Offer" button
3. PDF should generate without errors
4. Images should display (if property_image is set)
5. No `to_text()` errors

---

## 🚨 TROUBLESHOOTING

### Issue: Module Won't Upgrade

**Error:** "Module not found" or "No module named property_management"

**Solution:**
```bash
# Check if module is in addons path
ls -la /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/property_management

# Check odoo.conf for correct addons_path
cat /var/odoo/scholarixstudy.cloudpepper.site/odoo.conf | grep addons_path

# Restart Odoo to reload addons
sudo systemctl restart scholarixstudy.cloudpepper.site
```

### Issue: Security Errors

**Error:** "You don't have access to this document"

**Solution:**
```bash
# Update security groups
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf \
  -u property_management \
  -d sampledb \
  --stop-after-init

# Or from Odoo UI:
# Settings > Technical > Security > Access Rights
# Check if all models have rules
```

### Issue: SQL Constraint Violations

**Error:** "violates check constraint" or "duplicate key value"

**Solution:**
```sql
-- Connect to database
sudo -u postgres psql sampledb

-- Check for duplicate sale references
SELECT name, COUNT(*) FROM property_sale GROUP BY name HAVING COUNT(*) > 1;

-- Fix duplicates by updating names
UPDATE property_sale SET name = name || '-' || id WHERE id IN (
  SELECT id FROM (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY name ORDER BY id) as rn
    FROM property_sale
  ) t WHERE t.rn > 1
);

-- Exit
\q
```

### Issue: Computed Field Not Updating

**Error:** Payment progress shows 0% even though payments exist

**Solution:**
```python
# From Odoo shell
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d sampledb

# In Python shell:
env = self.env
properties = env['property.property'].search([])
properties._compute_active_sale()
properties._compute_payment_progress()
properties._compute_payment_details()
env.cr.commit()
exit()
```

### Issue: Invoice Creation Fails

**Error:** "Revenue account not found"

**Solution:**
1. Go to property record
2. Ensure "Revenue Account" field is filled
3. If empty, select an account with type "Income"
4. Try invoice generation again

---

## 📊 MONITORING COMMANDS

### Check Odoo Status
```bash
sudo systemctl status scholarixstudy.cloudpepper.site
```

### View Live Logs
```bash
tail -f /var/odoo/scholarixstudy.cloudpepper.site/logs/odoo.log
```

### Check for Errors
```bash
grep -i "error" /var/odoo/scholarixstudy.cloudpepper.site/logs/odoo.log | tail -50
```

### Check Property Management Operations
```bash
grep -i "property\|sale\|commission" /var/odoo/scholarixstudy.cloudpepper.site/logs/odoo.log | tail -50
```

### Database Connection Check
```bash
sudo -u postgres psql sampledb -c "SELECT COUNT(*) FROM property_sale;"
sudo -u postgres psql sampledb -c "SELECT COUNT(*) FROM property_property;"
```

---

## 🔄 ROLLBACK PROCEDURE

If something goes wrong:

### 1. Stop Odoo
```bash
sudo systemctl stop scholarixstudy.cloudpepper.site
```

### 2. Restore Database Backup
```bash
# If using pg_dump backup
sudo -u postgres psql -c "DROP DATABASE sampledb;"
sudo -u postgres psql -c "CREATE DATABASE sampledb OWNER odoo;"
sudo -u postgres psql sampledb < /tmp/sampledb_backup_YYYYMMDD_HHMMSS.sql
```

### 3. Revert Code (if needed)
```bash
cd /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/property_management
git log --oneline -5  # Find commit to revert to
git reset --hard <commit_hash>
```

### 4. Start Odoo
```bash
sudo systemctl start scholarixstudy.cloudpepper.site
```

---

## 📞 SUPPORT

If you encounter issues during deployment:

1. **Check Logs First:**
   ```bash
   tail -100 /var/odoo/scholarixstudy.cloudpepper.site/logs/odoo.log
   ```

2. **Verify Module Files:**
   ```bash
   ls -la /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/property_management/
   ```

3. **Test Database Connection:**
   ```bash
   sudo -u postgres psql sampledb -c "\dt property_*"
   ```

4. **Restart Odoo Service:**
   ```bash
   sudo systemctl restart scholarixstudy.cloudpepper.site
   ```

---

## ✅ SUCCESS CRITERIA

Deployment is successful when:

- ✅ Module shows "Installed" in Apps
- ✅ No errors in Odoo logs
- ✅ Can create properties
- ✅ Can create sales with customer selection
- ✅ Can confirm sales
- ✅ Payment schedule generates
- ✅ Can generate invoices
- ✅ Can create broker commissions
- ✅ Reports generate without errors
- ✅ All computed fields update correctly
- ✅ No SQL constraint violations

---

## 📅 DEPLOYMENT SCHEDULE

**Recommended Deployment Window:**
- Low traffic period (e.g., late evening or weekend)
- Have technical support available
- Plan for 30-60 minutes deployment time
- Monitor for 2-4 hours post-deployment

**Steps Duration:**
- Backup: 5-10 minutes
- Code pull: 1 minute
- Module upgrade: 2-5 minutes
- Testing: 15-30 minutes
- Monitoring: 2-4 hours

---

**Deployment Version:** 18.0.1.0.1  
**Last Updated:** 2025-11-03  
**Status:** ✅ READY FOR PRODUCTION  
**Commit:** 7767b54

**⚠️ IMPORTANT:** Always backup before deploying!
