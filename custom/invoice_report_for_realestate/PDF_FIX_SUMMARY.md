# OSUS Invoice Report - PDF Empty File Fix

## Problem Analysis
The error "PyPDF2.errors.EmptyFileError: Cannot read an empty file" indicates that the QWeb report is generating an empty PDF file, which happens when the template has runtime errors during rendering.

## Root Causes Fixed

### 1. ✅ QR Code Binary Field Issue
**Problem**: Template was trying to decode already-encoded binary data
**Fixed**: Removed `.decode('utf-8')` from QR image references

**Files Changed**:
- `report/invoice_report.xml`
- `report/bulk_report.xml`

**Before**:
```xml
<img t-att-src="'data:image/png;base64,' + o.qr_image.decode('utf-8')"/>
```

**After**:
```xml
<img t-att-src="'data:image/png;base64,' + o.qr_image"/>
```

### 2. ✅ DateTime Reference Issue
**Problem**: `datetime.datetime.now()` is not available in QWeb templates
**Fixed**: Replaced with `time.strftime()` which is available

**Files Changed**:
- `report/bulk_report.xml` (3 occurrences)

**Before**:
```xml
<t t-esc="datetime.datetime.now().strftime('%d/%m/%Y %H:%M')"/>
```

**After**:
```xml
<t t-esc="time.strftime('%d/%m/%Y %H:%M')"/>
```

### 3. ✅ Missing Template Variables
**Problem**: `doc_index` variable not passed to called template
**Fixed**: Added proper variable passing in template call

**Files Changed**:
- `report/bulk_report.xml`

**Before**:
```xml
<t t-call="osus_invoice_report.report_osus_single_invoice_content"/>
```

**After**:
```xml
<t t-call="osus_invoice_report.report_osus_single_invoice_content">
    <t t-set="doc_index" t-value="doc_index"/>
</t>
```

### 4. ✅ Field Name Compatibility
**Problem**: `invoice_date_due` field might not exist in all contexts
**Fixed**: Added fallback to `date` field

**Files Changed**:
- `report/invoice_report.xml`
- `report/bulk_report.xml`

**Before**:
```xml
<span t-esc="format_uk_date(o.invoice_date_due)"/>
```

**After**:
```xml
<span t-esc="format_uk_date(o.invoice_date_due or o.date)"/>
```

### 5. ✅ Amount By Group Issue (Previously Fixed)
**Problem**: `amount_by_group` field not available on account.move
**Fixed**: Simplified tax display to use `amount_tax` field directly

## Testing Strategy

### Phase 1: Simple Test
1. Use the new simple test report: `action_report_osus_invoice_simple`
2. Test with a basic invoice first
3. If successful, move to complex templates

### Phase 2: Component Testing
1. Test individual templates one by one
2. Test QR code generation separately
3. Test bulk printing functionality

### Phase 3: Full Integration
1. Test all bulk printing features
2. Test with real data
3. Verify PDF generation

## Files Modified
1. `models/custom_invoice.py` - Fixed amount_by_group issue
2. `report/invoice_report.xml` - Fixed QR code and field references
3. `report/bulk_report.xml` - Fixed multiple template issues
4. `report/simple_test_report.xml` - Added simple fallback template
5. `__manifest__.py` - Added simple test report

## Verification Scripts Created
1. `verify_bulk_print.py` - Checks module configuration
2. `validate_templates.py` - Validates XML structure

## Recommended Testing Order
1. **Test Simple Template First**:
   ```
   Use "OSUS Invoice (Simple)" report on a single invoice
   ```

2. **Test Standard Template**:
   ```
   Use "OSUS Invoice" report on a single invoice
   ```

3. **Test Bulk Functionality**:
   ```
   Select multiple invoices and use bulk print actions
   ```

## If Issues Persist
1. Check Odoo logs for specific error messages
2. Test with minimal data (new invoice with one line)
3. Disable QR code generation temporarily by setting `qr_in_report = False`
4. Check field permissions and access rights

## Manual Debugging Steps
1. Create a test invoice with minimal data
2. Try printing using standard Odoo invoice report first
3. Try the simple test report
4. Gradually enable more complex features

The empty PDF error should now be resolved with these fixes.
