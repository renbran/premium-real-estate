# Payment Voucher Report Enhancement

## Overview
Enhanced the OSUS payment voucher report with intelligent document detection and dynamic labeling based on the type of related documents.

## New Features

### 🎯 **Intelligent Document Detection**
- **Automatic Detection**: Detects whether payment is related to customer invoices, vendor bills, or credit notes
- **Dynamic Labels**: Changes label from "Related invoice" to "Related bill" based on actual document type
- **Mixed Document Support**: Handles payments related to multiple document types

### 📋 **Enhanced Document Information**
- **Document Summary Table**: Shows detailed information when multiple documents are involved
- **Payment Summary**: Displays payment status (full/partial) and remaining balances
- **Comprehensive References**: Lists all related document numbers with proper formatting

## How It Works

### 1. **Document Type Detection Logic**

```python
def get_document_type_label(self):
    """Smart labeling based on actual related documents"""
    related_docs = self.get_related_documents()
    
    # Check document types
    has_bills = any(doc.move_type == 'in_invoice' for doc in related_docs)
    has_invoices = any(doc.move_type == 'out_invoice' for doc in related_docs)
    has_credits = any(doc.move_type in ['out_refund', 'in_refund'] for doc in related_docs)
    
    # Return appropriate label
    if has_bills and not has_invoices:
        return "Related bill"
    elif has_invoices and not has_bills:
        return "Related invoice"
    # ... etc
```

### 2. **Enhanced Document Discovery**

The system now looks for related documents in multiple ways:
- **Direct Reconciliation**: Uses `reconciled_invoice_ids` if available
- **Move Line Analysis**: Analyzes reconciled move lines to find related documents
- **Reconciliation Groups**: Traces through full reconciliation records

### 3. **Payment Summary Calculation**

```python
def get_payment_summary(self):
    """Calculate payment completeness and remaining balances"""
    total_invoice_amount = sum(related_docs.mapped('amount_total'))
    payment_amount = self.amount
    remaining_balance = total_invoice_amount - payment_amount
    is_full_payment = abs(remaining_balance) < 0.01
```

## Report Enhancements

### **Before** (Static Labels):
```xml
<div class="field-label">Related invoice</div>
```

### **After** (Dynamic Labels):
```xml
<t t-set="doc_info" t-value="o.get_related_document_info()"/>
<div class="field-label">
    <span t-esc="doc_info['label']"/>  <!-- "Related bill" or "Related invoice" -->
</div>
```

## Visual Improvements

### 1. **Document Details Table** (for multiple documents)
```
┌─────────────────────────────────────────────────────────────┐
│ Document Details (3 documents)                             │
├──────────────┬─────────────────┬──────────┬────────────────┤
│ Document #   │ Type            │ Date     │ Amount         │
├──────────────┼─────────────────┼──────────┼────────────────┤
│ BILL/2024/001│ Vendor Bill     │ 15/01/24 │ 1,500.00 AED   │
│ BILL/2024/002│ Vendor Bill     │ 16/01/24 │ 2,300.00 AED   │
│ BILL/2024/003│ Vendor Bill     │ 17/01/24 │   800.00 AED   │
└──────────────┴─────────────────┴──────────┴────────────────┘
```

### 2. **Payment Summary** (when documents are related)
```
┌─────────────────────────────────────────────────────────────┐
│ Payment Summary                                             │
├─────────────────────────────────────────────────────────────┤
│ Description: Payment for 3 documents                       │
│ Total Document Amount: 4,600.00 AED                        │
│ Payment Status: ⚠ Partial Payment                          │
│                 (Remaining: 1,100.00 AED)                  │
└─────────────────────────────────────────────────────────────┘
```

## Use Cases

### ✅ **Customer Invoice Payment**
- Label: "Related invoice" 
- Shows invoice number: INV/2024/001
- Status: Full/Partial payment indication

### ✅ **Vendor Bill Payment**
- Label: "Related bill"
- Shows bill number: BILL/2024/001
- Status: Full/Partial payment indication

### ✅ **Mixed Document Payment**
- Label: "Related documents"
- Shows all document numbers with types
- Detailed table with individual amounts

### ✅ **Credit Note Application**
- Label: "Related credit note"
- Shows credit note reference
- Appropriate status indication

## Technical Implementation

### **New Methods Added:**
1. `get_related_documents()` - Find all related documents
2. `get_document_type_label()` - Generate appropriate label
3. `get_related_document_references()` - Format document references
4. `get_related_document_info()` - Complete document information
5. `get_payment_summary()` - Payment analysis
6. `get_voucher_description()` - Descriptive text generation

### **Report Template Changes:**
- Dynamic label generation
- Conditional document details table
- Payment summary section
- Enhanced visual formatting

## Benefits

1. **Accuracy**: Always shows correct document type labels
2. **Clarity**: Clear indication of what documents the payment relates to
3. **Completeness**: Shows payment status and remaining balances
4. **Professional**: Enhanced visual presentation
5. **Flexibility**: Handles various payment scenarios automatically

## Installation

The enhancement is part of the OSUS Invoice Report module. After updating:

1. Restart Odoo
2. Update the module
3. Payment vouchers will automatically use the new logic

## Testing Scenarios

1. **Create vendor bill** → Make payment → Print voucher → Should show "Related bill"
2. **Create customer invoice** → Receive payment → Print voucher → Should show "Related invoice"
3. **Pay multiple bills** → Print voucher → Should show document details table
4. **Partial payment** → Print voucher → Should show remaining balance

The system automatically detects the scenario and adjusts the report accordingly! 🎉
