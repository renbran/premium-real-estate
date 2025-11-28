# OSUS Invoice Report - Bulk Printing Installation Guide

## Quick Installation Steps

1. **Restart Odoo** to load the enhanced module:
   ```bash
   docker-compose restart odoo
   ```

2. **Update the Module**:
   - Go to Apps menu
   - Remove "Apps" filter 
   - Search for "OSUS Invoice Report"
   - Click "Upgrade" button

3. **Access Bulk Printing**:
   - Navigate to **Accounting > OSUS Bulk Print**
   - Or use Actions menu in any invoice/bill list view

## Verification Steps

1. Go to **Accounting > Customer Invoices**
2. Select multiple invoices
3. Click **Actions** → Should see new bulk print options
4. Check **Accounting** menu → Should see "OSUS Bulk Print" submenu

## Troubleshooting

If bulk print options don't appear:
1. Clear browser cache
2. Restart Odoo: `docker-compose restart odoo`
3. Update module list and upgrade

For errors during printing:
- Check that qrcode and num2words libraries are installed
- Verify selected documents are in 'posted' state
- Check Odoo logs for detailed error messages

## Features Available

✅ **Single Document Printing** (existing)
- Print individual invoices, bills, receipts

✅ **Bulk Document Printing** (new)
- Bulk print customer invoices
- Bulk print vendor bills  
- Bulk print mixed documents

✅ **Professional Output** (new)
- Cover pages with summaries
- Document counts and totals
- Proper page breaks

✅ **Enhanced UI** (new)
- Dedicated bulk print menus
- List view actions
- Error handling and validation

Ready to use! 🎉
