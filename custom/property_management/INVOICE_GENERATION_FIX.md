# Invoice Generation Fix - Property Management

## 🐛 Issue Description

**Problem**: When clicking "Generate All Invoices" button, only 3 invoices were created (down payment, DLD fee, admin fee) instead of all installments.

**Root Cause**: The `action_generate_all_invoices()` method had a date filter that only generated invoices for installments with due dates <= today:

```python
unpaid_lines = self.property_sale_line_ids.filtered(
    lambda l: l.collection_status == 'unpaid' and 
    l.collection_date <= fields.Date.today()  # ❌ This was the problem
)
```

This prevented future monthly installments from being invoiced.

---

## ✅ Solution Implemented

### 1. **Removed Date Filter**
Changed the filter to generate invoices for ALL unpaid installments that don't have an invoice yet:

```python
unpaid_lines = self.property_sale_line_ids.filtered(
    lambda l: l.collection_status == 'unpaid' and not l.invoice_id
)
```

### 2. **Fixed Invoice Date Logic**
- **Past/Current Due Dates**: Uses the collection date as invoice date
- **Future Due Dates**: Uses today's date but sets proper due date

```python
invoice_date = line.collection_date if line.collection_date <= fields.Date.today() else fields.Date.today()
invoice_vals = {
    'invoice_date': invoice_date,
    'invoice_date_due': line.collection_date,  # Always set proper due date
    ...
}
```

### 3. **Removed Automatic Payment Status**
**Before**: Invoices were immediately marked as 'paid' upon creation ❌

```python
line.write({
    'invoice_id': invoice.id,
    'collection_status': 'paid'  # ❌ Wrong - invoice not paid yet!
})
```

**After**: Invoices are created in draft/open state ✅

```python
line.write({
    'invoice_id': invoice.id,
    # collection_status now updates automatically via computed field
})
```

### 4. **Added Automatic Payment Tracking**
Created a computed field that automatically updates `collection_status` when invoice is paid:

```python
@api.depends('invoice_id', 'invoice_id.payment_state')
def _compute_collection_status(self):
    """Automatically update collection status based on invoice payment state"""
    for record in self:
        if record.invoice_id and record.invoice_id.payment_state == 'paid':
            record.collection_status = 'paid'
        else:
            record.collection_status = 'unpaid'
```

### 5. **Enhanced Invoice Descriptions**
Added better descriptions for each invoice type:

```python
if line.line_type == 'downpayment':
    payment_description = _("Down Payment")
elif line.line_type == 'dld_fee':
    payment_description = _("DLD Registration Fee")
elif line.line_type == 'admin_fee':
    payment_description = _("Administrative Fee")
else:
    payment_description = _("Installment #%s") % (line.serial_number - 3)
```

### 6. **Improved Logging and Messages**
- Better error messages with installment numbers
- Detailed success message with count and total amount
- Logger info for each invoice created

---

## 🔄 Workflow Changes

### Before:
1. Click "Generate All Invoices"
2. Only 3 invoices created (immediate payments only)
3. Future installments ignored
4. Invoices immediately marked as "paid" ❌

### After:
1. Click "Generate All Invoices"
2. ALL unpaid installments get invoices created ✅
3. Invoices created with proper due dates
4. Collection status automatically updates when invoice paid ✅
5. Detailed success message shows count and total amount

---

## 📊 Technical Changes Summary

| Component | Change | Impact |
|-----------|--------|--------|
| **Filter Logic** | Removed date restriction | All unpaid lines now included |
| **Invoice Date** | Smart date logic | Past=collection date, Future=today |
| **Due Date** | Always set properly | Correct payment tracking |
| **Payment Status** | Computed field | Automatic status updates |
| **Descriptions** | Enhanced text | Better invoice clarity |
| **Logging** | Improved messages | Better debugging |

---

## 🧪 Testing Checklist

- [ ] **Create Property Sale** with full payment schedule (e.g., 12 installments)
- [ ] **Confirm Sale** - Verify payment schedule generated correctly
- [ ] **Click "Generate All Invoices"** - Should create invoices for all unpaid lines
- [ ] **Verify Invoice Count** - Should match number of unpaid installments
- [ ] **Check Invoice Details**:
  - [ ] Proper descriptions (Down Payment, DLD Fee, Installment #1, etc.)
  - [ ] Correct amounts from capital_repayment
  - [ ] Invoice dates set correctly
  - [ ] Due dates match collection dates
  - [ ] State is 'draft' (not 'posted' or 'paid')
- [ ] **Payment Recording**:
  - [ ] Register payment on one invoice
  - [ ] Verify installment line collection_status automatically becomes 'paid'
  - [ ] Check property sale payment_progress updates
- [ ] **Duplicate Prevention**:
  - [ ] Click "Generate All Invoices" again
  - [ ] Should show error: "No unpaid installments found"
  - [ ] No duplicate invoices created
- [ ] **Partial Invoicing**:
  - [ ] Create new sale, generate some invoices
  - [ ] Click button again - should only create invoices for remaining lines

---

## 🚀 Deployment Steps

### For Existing Sales:
If you have existing property sales with only 3 invoices created:

1. **Option 1: Regenerate Missing Invoices**
   ```python
   # Run in Odoo shell
   sales = env['property.sale'].search([('state', '=', 'invoiced')])
   for sale in sales:
       uninvoiced_lines = sale.property_sale_line_ids.filtered(
           lambda l: l.collection_status == 'unpaid' and not l.invoice_id
       )
       if uninvoiced_lines:
           print(f"Sale {sale.name}: {len(uninvoiced_lines)} missing invoices")
           # Optionally call action_generate_all_invoices() to create them
   ```

2. **Option 2: Manual Invoice Creation**
   - Go to each property sale
   - Click "Generate All Invoices" button
   - Missing invoices will be created automatically

### For New Sales:
- No action needed - button now works correctly

---

## 📝 Related Files Modified

- **property_sale.py**: 
  - Fixed `action_generate_all_invoices()` method
  - Added `_compute_collection_status()` method to PropertySaleLine
  - Added `invoice_payment_state` field to PropertySaleLine

---

## 💡 Benefits

1. **Complete Invoice Generation**: All installments get invoices, not just immediate ones
2. **Automatic Status Tracking**: No manual status updates needed
3. **Better Descriptions**: Clear invoice names for accounting
4. **Proper Due Dates**: Payment tracking aligned with schedule
5. **Duplicate Prevention**: Can't create duplicate invoices
6. **Better Logging**: Easier debugging and monitoring

---

## ⚠️ Breaking Changes

**None** - This is a bug fix that corrects incorrect behavior. The changes are backward compatible.

---

## 📧 Support

If you encounter any issues:
1. Check Odoo logs for detailed error messages
2. Verify property sale is in 'confirmed' state
3. Ensure installment lines exist with unpaid status
4. Check that revenue account is configured on property

---

**Fixed Date**: 2025-01-19
**Developer**: GitHub Copilot (renbran/Odoo18_Development)
**Module**: property_management
**Version**: 18.0.1.0
