# Computed Field Fix - Property Management Module

## Issue Fixed
**Warning:** Field `active_sale_id` is computed without being stored and may cause performance issues.

## Changes Made

### 1. **models/property_property.py**

#### Updated `active_sale_id` field definition:
```python
active_sale_id = fields.Many2one(
    'property.sale', 
    string="Active Sale", 
    compute="_compute_active_sale", 
    store=True,  # ✅ ADDED - Makes field searchable and prevents dependency warnings
    readonly=True, 
    help="The currently active sale for this property"
)
```

#### Updated `_compute_active_sale` method:
```python
@api.depends('property_sale_ids', 'property_sale_ids.state')  # ✅ ADDED .state dependency
def _compute_active_sale(self):
    """Compute the active sale for this property."""
    for record in self:
        # Find sales with 'confirmed' or 'invoiced' state, sorted by most recent
        active_sales = record.property_sale_ids.filtered(
            lambda s: s.state in ['confirmed', 'invoiced']
        ).sorted('create_date', reverse=True)
        
        # Set the most recent active sale
        record.active_sale_id = active_sales[:1] if active_sales else False
```

## Why These Changes Matter

### **Before (Without `store=True`):**
- ❌ Field computed on-the-fly every time it's accessed
- ❌ Cannot be searched/filtered in list views
- ❌ Dependency tracking warnings in logs
- ❌ Performance issues with large datasets
- ❌ Other computed fields depending on it may not trigger updates

### **After (With `store=True`):**
- ✅ Field value stored in database
- ✅ Searchable and filterable in views
- ✅ No dependency warnings
- ✅ Better performance
- ✅ Proper cascade updates when dependencies change
- ✅ Other computed fields (`payment_progress`, `remaining_amount`, etc.) work correctly

## How to Deploy

### On Your Odoo Server:

1. **Pull the latest code:**
   ```bash
   cd /var/odoo/scholarixstudy.cloudpepper.site/extra-addons/property_management
   git pull origin main
   ```

2. **Upgrade the module:**
   ```bash
   cd /var/odoo/scholarixstudy.cloudpepper.site
   sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf \
     -u property_management \
     -d your_database_name \
     --stop-after-init
   ```

3. **Restart Odoo:**
   ```bash
   sudo systemctl restart scholarixstudy.cloudpepper.site
   ```

4. **Verify the fix:**
   ```bash
   tail -f /var/odoo/scholarixstudy.cloudpepper.site/logs/odoo.log
   ```
   
   You should no longer see warnings about `active_sale_id`.

## Related Computed Fields (Already Properly Configured)

These fields were already using `store=True` and work correctly:
- ✅ `payment_progress`
- ✅ `total_invoiced`
- ✅ `total_paid`
- ✅ `remaining_amount`

All of these depend on `active_sale_id`, so fixing the storage of `active_sale_id` ensures they update correctly.

## Testing Checklist

After deployment, verify:
- [ ] No warnings in Odoo logs
- [ ] Property list view loads quickly
- [ ] Can filter/search by active sale
- [ ] Payment progress shows correctly
- [ ] Remaining amount calculates properly
- [ ] Creating/confirming sales updates property correctly

## Commit Details

- **Commit:** b7ef69e
- **Message:** "Fix active_sale_id computed field - add store=True to make it searchable and prevent dependency warnings"
- **Date:** 2025-11-03
