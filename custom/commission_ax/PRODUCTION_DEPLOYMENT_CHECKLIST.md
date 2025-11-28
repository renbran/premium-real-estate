# Commission AX - Production Deployment Checklist
## Odoo 18 Migration (v18.0.1.0.0)

**Date**: ________________  
**Deployed By**: ________________  
**Server**: scholarixstudy.cloudpepper.site  

---

## ✅ PRE-DEPLOYMENT (Before Starting)

### Environment Verification
- [ ] Odoo 18 installed and running
- [ ] Python 3.10+ available
- [ ] PostgreSQL accessible
- [ ] Disk space > 2GB free
- [ ] Server backup configured
- [ ] Git repository accessible

### Backup Creation
- [ ] Database backup completed
- [ ] Filestore backup completed
- [ ] Backup files verified (not corrupted)
- [ ] Backup location documented: `/var/backups/`
- [ ] Backup file names recorded:
  ```
  Database: __________________________.sql
  Filestore: _________________________.tar.gz
  ```

### Documentation
- [ ] Current commission_line record count: __________
- [ ] Current module version documented: 17.0.3.2.1
- [ ] Migration guide reviewed
- [ ] Rollback procedure understood
- [ ] Emergency contacts available

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Code Update
- [ ] SSH into production server
- [ ] Navigate to `/var/odoo/scholarixstudy.cloudpepper.site/extra-addons/`
- [ ] Run `git fetch origin`
- [ ] Run `git pull origin main`
- [ ] Verify `__manifest__.py` shows version `18.0.1.0.0`
- [ ] Check file permissions (should be odoo:odoo)

### Step 2: Odoo Service Stop
- [ ] Run `sudo systemctl stop odoo18`
- [ ] Verify service stopped: `sudo systemctl status odoo18`
- [ ] Wait 10 seconds for clean shutdown
- [ ] Check no Odoo processes running: `ps aux | grep odoo`

### Step 3: Module Upgrade
- [ ] Start upgrade command (see migration guide)
- [ ] Upgrade process completed without errors
- [ ] Log file saved: `/tmp/commission_ax_upgrade.log`
- [ ] No "ERROR" or "EXCEPTION" in logs
- [ ] Migration scripts executed successfully
  - [ ] Pre-migration script ran
  - [ ] Post-migration script ran

### Step 4: Database Verification
- [ ] Module version in DB is `18.0.1.0.0`
- [ ] Module state is `installed`
- [ ] Commission line count matches pre-deployment: __________
- [ ] No orphaned records found
- [ ] No NULL required fields
- [ ] All states are valid (draft/calculated/confirmed/processed/paid/cancelled)
- [ ] Company_id populated on all records
- [ ] Currency consistency verified

### Step 5: Service Restart
- [ ] Run `sudo systemctl start odoo18`
- [ ] Service status is "active (running)"
- [ ] Check logs: `sudo tail -f /var/log/odoo18/odoo.log`
- [ ] "Modules loaded" message appears
- [ ] No errors in startup logs
- [ ] Web interface accessible

---

## ✅ POST-DEPLOYMENT TESTING

### UI Testing (30 minutes)

#### Test 1: Commission Line List
- [ ] Navigate to Sales → Commission Management → Commission Lines
- [ ] List view loads without errors
- [ ] All records visible (count: __________)
- [ ] Filters work correctly
- [ ] Search functions properly
- [ ] Form view opens correctly

#### Test 2: Commission Creation
- [ ] Open a sale order
- [ ] Navigate to Commission Management tab
- [ ] Add new commission line
- [ ] Fill in partner, type, role, rate
- [ ] Click "Calculate Commission"
- [ ] Amount calculates correctly
- [ ] State changes to "Calculated"
- [ ] Save successful

#### Test 3: Commission Processing
- [ ] Open calculated commission line
- [ ] Click "Confirm" button
- [ ] State changes to "Confirmed"
- [ ] Click "Process" button
- [ ] State changes to "Processed"
- [ ] For external commission:
  - [ ] Purchase order created
  - [ ] PO linked correctly
  - [ ] PO amount matches commission

#### Test 4: Commission Reports
- [ ] Select multiple commission lines
- [ ] Print → Commission Report
- [ ] PDF generates successfully
- [ ] Report data is accurate
- [ ] Company information displays correctly

#### Test 5: Smart Buttons
- [ ] Open sale order with commissions
- [ ] Commission Lines smart button shows count
- [ ] Click smart button → opens filtered view
- [ ] Purchase Orders smart button works
- [ ] Statement smart button functions

### Integration Testing (20 minutes)

#### Test 6: New Sale Order Workflow
- [ ] Create new quotation
- [ ] Add products (total > $1000)
- [ ] Add commission line (external broker, 2%)
- [ ] Calculate commission
- [ ] Confirm quotation
- [ ] Process commission
- [ ] Verify purchase order created
- [ ] Check accounting entries

#### Test 7: Multi-Currency
- [ ] Create sale order in EUR
- [ ] Add commission line
- [ ] Calculate commission
- [ ] Amount converted correctly
- [ ] Currency matches sale order

#### Test 8: Multi-Company
- [ ] Switch company (if multi-company setup)
- [ ] Access commission lines
- [ ] Only current company records visible
- [ ] Create commission in Company A
- [ ] Switch to Company B
- [ ] Company A commission not visible

### Performance Testing (10 minutes)

#### Test 9: Large Dataset
- [ ] Filter commission lines: last 30 days
- [ ] List loads in < 3 seconds
- [ ] Search by partner: < 1 second
- [ ] Filter by state: < 1 second
- [ ] Export to Excel: < 5 seconds

#### Test 10: Concurrent Users
- [ ] 2-3 users access commissions simultaneously
- [ ] No locking errors
- [ ] No performance degradation
- [ ] All operations complete successfully

---

## 🔍 DATA VALIDATION

### SQL Validation Queries

Run these and document results:

```sql
-- 1. Record count
SELECT COUNT(*) FROM commission_line;
-- Expected: Same as pre-deployment
-- Actual: __________

-- 2. State distribution
SELECT state, COUNT(*) FROM commission_line GROUP BY state;
-- Expected: Valid states only (draft/calculated/confirmed/processed/paid/cancelled)
-- Actual:

-- 3. Orphaned records
SELECT COUNT(*) FROM commission_line cl 
LEFT JOIN sale_order so ON cl.sale_order_id = so.id 
WHERE so.id IS NULL;
-- Expected: 0
-- Actual: __________

-- 4. Missing company
SELECT COUNT(*) FROM commission_line WHERE company_id IS NULL;
-- Expected: 0
-- Actual: __________

-- 5. Currency mismatch
SELECT COUNT(*) FROM commission_line cl 
JOIN sale_order so ON cl.sale_order_id = so.id 
WHERE cl.currency_id != so.currency_id;
-- Expected: 0
-- Actual: __________
```

---

## 📊 MONITORING (First 24 Hours)

### Hour 1
- [ ] Check error log: `/var/log/odoo18/odoo.log`
- [ ] No errors related to commission_ax
- [ ] Active users: __________
- [ ] Commission operations: __________

### Hour 4
- [ ] Review error log
- [ ] System performance normal
- [ ] Users report no issues
- [ ] Database size: __________

### Hour 8
- [ ] End of business day check
- [ ] All commission processing completed
- [ ] No outstanding errors
- [ ] User feedback collected

### Day 1 Complete
- [ ] 24-hour monitoring complete
- [ ] No critical issues
- [ ] Performance acceptable
- [ ] Users satisfied

---

## ⚠️ ISSUES ENCOUNTERED

### Issue Log

| Time | Issue | Severity | Action Taken | Status |
|------|-------|----------|--------------|--------|
|      |       |          |              |        |
|      |       |          |              |        |
|      |       |          |              |        |

---

## 🔄 ROLLBACK REQUIRED?

**If critical issues found:**

### Rollback Decision
- [ ] Critical bug prevents operations
- [ ] Data integrity compromised
- [ ] Rollback approved by: ________________

### Rollback Steps
- [ ] Stop Odoo service
- [ ] Restore database backup
- [ ] Restore code to previous version
- [ ] Restart Odoo service
- [ ] Verify rollback successful
- [ ] Document rollback reason

### Rollback Time
- Start: __________
- Complete: __________
- Downtime: __________ minutes

---

## ✅ DEPLOYMENT SIGN-OFF

### Success Criteria
- [ ] Module upgraded to 18.0.1.0.0
- [ ] All tests passed
- [ ] Data integrity verified
- [ ] No critical errors
- [ ] Performance acceptable
- [ ] Users trained/notified
- [ ] Documentation updated

### Approvals

**Technical Lead**: ________________  
**Date**: ________________  
**Signature**: ________________  

**Operations Manager**: ________________  
**Date**: ________________  
**Signature**: ________________  

**Database Admin**: ________________  
**Date**: ________________  
**Signature**: ________________  

---

## 📝 POST-DEPLOYMENT NOTES

### What Went Well:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

### What Could Be Improved:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

### Lessons Learned:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

### Follow-Up Actions:
- [ ] Schedule 1-week review meeting
- [ ] Update runbook with new procedures
- [ ] Document any workarounds
- [ ] Plan next module upgrade

---

## 📞 CONTACTS

**Technical Support**: ________________  
**On-Call Engineer**: ________________  
**Escalation Contact**: ________________  

---

**Deployment Status**: ⬜ Success  ⬜ Success with Issues  ⬜ Rolled Back  

**Completion Date**: ________________  
**Total Downtime**: ________________  
**Next Review Date**: ________________  

---

**Document Version**: 1.0  
**Last Updated**: November 7, 2025  
**Module Version**: 18.0.1.0.0
