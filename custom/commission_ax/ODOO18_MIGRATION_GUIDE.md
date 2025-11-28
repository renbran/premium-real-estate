# Commission AX - Production Migration Guide to Odoo 18
## Version 17.0.3.2.1 → 18.0.1.0.0

---

## ⚠️ CRITICAL ODOO 18 BREAKING CHANGES

### View Type Changes (FIXED)
**Odoo 18 requires `<list>` instead of `<tree>` in XML views**

```xml
<!-- ❌ OLD (Odoo 17) - WILL FAIL -->
<field name="arch" type="xml">
    <tree>
        <field name="name"/>
    </tree>
</field>

<!-- ✅ NEW (Odoo 18) - CORRECT -->
<field name="arch" type="xml">
    <list>
        <field name="name"/>
    </list>
</field>
```

**Important Notes:**
- ✅ XML tag: `<tree>` → `<list>` (CHANGED)
- ✅ view_mode: Still uses `tree` (NOT CHANGED)
- ✅ **All views fixed in commit ff86f96**

**Error if not fixed:**
```
ParseError: Invalid view type: 'tree'.
Allowed types are: list, form, graph, pivot, calendar, kanban, search, qweb, hierarchy, activity
```

---

## 📋 PRE-MIGRATION CHECKLIST

### 1. **CRITICAL: Database Backup**
```bash
# Stop Odoo service
sudo systemctl stop odoo18

# Backup database
sudo -u postgres pg_dump scholarixstudy_db > /var/backups/scholarixstudy_db_$(date +%Y%m%d_%H%M%S).sql

# Backup filestore
sudo tar -czf /var/backups/filestore_$(date +%Y%m%d_%H%M%S).tar.gz /var/odoo/.local/share/Odoo/filestore/

# Verify backup size
ls -lh /var/backups/*.sql
ls -lh /var/backups/*.tar.gz
```

### 2. **Document Current State**
```bash
# Save current module version
echo "commission_ax current version:" > /tmp/pre_migration_info.txt
grep "'version':" /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/commission_ax/__manifest__.py >> /tmp/pre_migration_info.txt

# Count existing records
psql -U odoo -d scholarixstudy_db -c "SELECT COUNT(*) FROM commission_line;" >> /tmp/pre_migration_info.txt
psql -U odoo -d scholarixstudy_db -c "SELECT state, COUNT(*) FROM commission_line GROUP BY state;" >> /tmp/pre_migration_info.txt
```

### 3. **Environment Check**
```bash
# Verify Odoo version
/usr/bin/odoo-bin --version

# Check Python version (should be 3.10+)
python3 --version

# Verify PostgreSQL
sudo -u postgres psql --version

# Check disk space (need at least 2GB free)
df -h /var/odoo
```

---

## 🚀 MIGRATION PROCEDURE

### Step 1: Pull Latest Code (Development)
```bash
cd /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/
git fetch origin
git pull origin main

# Verify version in manifest
grep "'version':" commission_ax/__manifest__.py
# Should show: 'version': '18.0.1.0.0',
```

### Step 2: Test in Staging (RECOMMENDED)
```bash
# If you have a staging environment, test there first:
# 1. Restore production backup to staging
# 2. Run upgrade on staging
# 3. Test all commission workflows
# 4. Only proceed to production if staging succeeds
```

### Step 3: Upgrade Module
```bash
# Navigate to Odoo installation
cd /usr/lib/python3/dist-packages/odoo

# Run upgrade with module name
sudo -u odoo /usr/bin/odoo-bin \
    -c /etc/odoo18/odoo.conf \
    -d scholarixstudy_db \
    -u commission_ax \
    --stop-after-init \
    --log-level=info \
    2>&1 | tee /tmp/commission_ax_upgrade.log

# Check for errors
grep -i "error\|traceback\|exception" /tmp/commission_ax_upgrade.log
```

### Step 4: Verify Migration
```bash
# Check module version in database
psql -U odoo -d scholarixstudy_db -c \
    "SELECT name, latest_version, state FROM ir_module_module WHERE name = 'commission_ax';"

# Should show: commission_ax | 18.0.1.0.0 | installed

# Verify data integrity
psql -U odoo -d scholarixstudy_db << EOF
    -- Check commission line counts
    SELECT 'Total Records:' as check, COUNT(*) FROM commission_line;
    
    -- Check by state
    SELECT 'By State:' as check, state, COUNT(*) FROM commission_line GROUP BY state;
    
    -- Check for orphaned records
    SELECT 'Orphaned Records:' as check, COUNT(*) 
    FROM commission_line cl 
    LEFT JOIN sale_order so ON cl.sale_order_id = so.id 
    WHERE so.id IS NULL;
    
    -- Check currency consistency
    SELECT 'Currency Issues:' as check, COUNT(*) 
    FROM commission_line cl 
    JOIN sale_order so ON cl.sale_order_id = so.id 
    WHERE cl.currency_id != so.currency_id;
EOF
```

### Step 5: Restart Odoo
```bash
# Start Odoo service
sudo systemctl start odoo18

# Check service status
sudo systemctl status odoo18

# Monitor logs for errors
sudo tail -f /var/log/odoo18/odoo.log

# Look for successful startup message
# Should see: "Modules loaded." and no errors related to commission_ax
```

---

## ✅ POST-MIGRATION VALIDATION

### 1. **UI Testing** (Login to Odoo Web Interface)

#### Test Commission Line Access
1. Navigate to: **Sales → Commission Management → Commission Lines**
2. Verify:
   - ✅ List view loads without errors
   - ✅ All records visible
   - ✅ Filters work correctly
   - ✅ Search works

#### Test Commission Creation
1. Open any **Sale Order**
2. Go to **Commission Management** tab
3. Click **Add a line**
4. Fill in commission details
5. Click **Calculate Commission**
6. Verify:
   - ✅ Commission calculates correctly
   - ✅ State changes to "Calculated"
   - ✅ Amount is accurate

#### Test Commission Processing
1. Open a calculated commission line
2. Click **Confirm**
3. Click **Process**
4. Verify:
   - ✅ State changes to "Processed"
   - ✅ Purchase order created (for external commissions)
   - ✅ No errors in the log

### 2. **Report Testing**
```bash
# Generate a commission report
1. Go to Commission Lines
2. Select multiple lines
3. Print → Commission Report
4. Verify PDF generates without errors
```

### 3. **Integration Testing**
```bash
# Test sale order integration
1. Create a new quotation
2. Add products
3. Add commission lines
4. Confirm the sale order
5. Process commissions
6. Verify purchase orders created
```

### 4. **Data Validation SQL**
```sql
-- Run these queries to validate data integrity:

-- 1. Check for NULL required fields
SELECT COUNT(*) as null_partner FROM commission_line WHERE partner_id IS NULL;
SELECT COUNT(*) as null_sale_order FROM commission_line WHERE sale_order_id IS NULL;
SELECT COUNT(*) as null_state FROM commission_line WHERE state IS NULL;

-- 2. Verify all states are valid
SELECT DISTINCT state FROM commission_line ORDER BY state;
-- Should only show: calculated, cancelled, confirmed, draft, paid, processed

-- 3. Check company_id consistency
SELECT COUNT(*) as missing_company FROM commission_line WHERE company_id IS NULL;

-- 4. Verify currency alignment
SELECT COUNT(*) as currency_mismatch 
FROM commission_line cl 
JOIN sale_order so ON cl.sale_order_id = so.id 
WHERE cl.currency_id != so.currency_id;

-- All above counts should be 0
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: Module Won't Upgrade
```bash
# Error: "Module commission_ax not found"
# Solution: Verify module path
ls -la /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/commission_ax/__manifest__.py

# Error: "Dependency not found"
# Solution: Install missing dependencies
sudo -u odoo /usr/bin/odoo-bin -c /etc/odoo18/odoo.conf -d scholarixstudy_db -i base,sale,purchase,account --stop-after-init
```

### Issue 2: View Errors After Upgrade
```bash
# Error: "View not found" or "Invalid view"
# Solution: Update module to reload views
sudo -u odoo /usr/bin/odoo-bin -c /etc/odoo18/odoo.conf -d scholarixstudy_db -u commission_ax --stop-after-init
```

### Issue 3: Data Migration Errors
```bash
# Check migration logs
grep "commission_ax" /tmp/commission_ax_upgrade.log | grep -i error

# If pre-migration script failed:
# Manually run data cleanup:
psql -U odoo -d scholarixstudy_db << EOF
    -- Remove orphaned records
    DELETE FROM commission_line 
    WHERE sale_order_id NOT IN (SELECT id FROM sale_order);
    
    -- Fix NULL states
    UPDATE commission_line SET state = 'draft' WHERE state IS NULL;
    
    -- Fix NULL company
    UPDATE commission_line cl 
    SET company_id = so.company_id 
    FROM sale_order so 
    WHERE cl.sale_order_id = so.id AND cl.company_id IS NULL;
EOF

# Then retry upgrade
```

### Issue 4: Performance Issues
```bash
# Reindex database
psql -U odoo -d scholarixstudy_db -c "REINDEX TABLE commission_line;"

# Analyze tables
psql -U odoo -d scholarixstudy_db -c "ANALYZE commission_line;"

# Vacuum database
psql -U odoo -d scholarixstudy_db -c "VACUUM ANALYZE;"
```

---

## 🔄 ROLLBACK PROCEDURE (If Migration Fails)

### Step 1: Stop Odoo
```bash
sudo systemctl stop odoo18
```

### Step 2: Restore Database
```bash
# Find your backup
ls -lh /var/backups/*.sql

# Restore database
sudo -u postgres psql << EOF
    DROP DATABASE scholarixstudy_db;
    CREATE DATABASE scholarixstudy_db OWNER odoo;
EOF

sudo -u postgres psql scholarixstudy_db < /var/backups/scholarixstudy_db_YYYYMMDD_HHMMSS.sql
```

### Step 3: Restore Code
```bash
cd /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/
git checkout HEAD~1 commission_ax/
# Or restore from backup
```

### Step 4: Restart Odoo
```bash
sudo systemctl start odoo18
sudo systemctl status odoo18
```

---

## 📊 MIGRATION SUMMARY

### What Changed in 18.0.1.0.0:
1. ✅ **Version Updated**: 17.0.3.2.1 → 18.0.1.0.0
2. ✅ **Odoo 18 Compatibility**: All APIs updated
3. ✅ **Migration Scripts**: Pre and post-migration automation
4. ✅ **Data Validation**: Automatic cleanup of inconsistent data
5. ✅ **No Breaking Changes**: All existing features maintained

### Migration Scripts:
- **`migrations/18.0.1.0.0/pre-migration.py`**:
  - Validates existing data
  - Cleans up orphaned records
  - Fixes invalid states
  - Ensures company_id consistency
  - Synchronizes currencies

- **`migrations/18.0.1.0.0/post-migration.py`**:
  - Recomputes stored fields
  - Validates views and actions
  - Generates migration statistics
  - Performs final validation

### Zero Downtime Features:
- ✅ All data structures remain compatible
- ✅ No field deletions or renames
- ✅ Backward-compatible state values
- ✅ Automatic data migration

---

## 📞 SUPPORT & CONTACTS

### If Issues Occur:
1. **Check logs**: `/var/log/odoo18/odoo.log`
2. **Migration log**: `/tmp/commission_ax_upgrade.log`
3. **Save error screenshots**
4. **Document exact error messages**

### Emergency Contacts:
- **Technical Team**: [Your Email]
- **Database Admin**: [DBA Email]
- **Odoo Support**: support@odoo.com

---

## 📝 MAINTENANCE NOTES

### Post-Migration Tasks:
- [ ] Monitor system performance for 24-48 hours
- [ ] Check error logs daily for first week
- [ ] Validate commission calculations with finance team
- [ ] Update user documentation if needed
- [ ] Schedule follow-up review meeting

### Regular Maintenance:
```bash
# Weekly: Check commission processing
psql -U odoo -d scholarixstudy_db -c \
    "SELECT state, COUNT(*) FROM commission_line 
     WHERE create_date > NOW() - INTERVAL '7 days' 
     GROUP BY state;"

# Monthly: Database optimization
psql -U odoo -d scholarixstudy_db -c "VACUUM ANALYZE commission_line;"
```

---

## ✅ MIGRATION COMPLETE

**Date**: _______________  
**Performed By**: _______________  
**Duration**: _______________  
**Status**: _______________  

**Post-Migration Checklist**:
- [ ] Module upgraded successfully
- [ ] All tests passed
- [ ] Data integrity verified
- [ ] Performance acceptable
- [ ] Users notified
- [ ] Documentation updated

---

**Version**: 18.0.1.0.0  
**Last Updated**: November 7, 2025  
**Status**: Production Ready ✅
