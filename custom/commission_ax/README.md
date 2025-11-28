# Enhanced Commission Management System

## Overview

This module extends Odoo's commission management system with advanced features including automatic vendor reference population from customer references in sales orders.

## Key Features

### 1. Vendor Reference Auto-Population
- **Feature**: Automatically populates the vendor reference field in commission purchase orders with the customer reference from the originating sale order
- **Benefit**: Maintains reference consistency across the sales-to-purchase workflow
- **Implementation**: When commission purchase orders are created, the `partner_ref` field is automatically set to the `client_order_ref` from the sale order

### 2. Enhanced Commission Structure
- **Dual Commission Groups**: External (Broker, Referrer, Cashback, Others) and Internal (Agent 1, Agent 2, Manager, Director)
- **Multiple Calculation Methods**: 
  - Fixed Amount
  - Percentage of Unit Price
  - Percentage of Untaxed Total
- **Legacy Support**: Maintains backward compatibility with existing commission structures

### 3. Purchase Order Integration
- **Commission Purchase Orders**: Automatically creates purchase orders for commission payments
- **Smart Buttons**: Easy navigation between sale orders and their commission purchase orders
- **Commission Tracking**: Track commission status (Draft, Calculated, Confirmed)

## Installation

1. Copy the module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Enhanced Commission Management System" module

## Usage

### Setting Up Customer References

1. Create or edit a Sale Order
2. In the "Other Information" tab, set the "Customer Reference" field
3. This reference will automatically be used as the vendor reference in commission purchase orders

### Configuring Commissions

1. Open a Sale Order
2. Go to the "Commissions" tab
3. Configure External and/or Internal commissions:
   - **External Commissions**: Broker, Referrer, Cashback, Other External
   - **Internal Commissions**: Agent 1, Agent 2, Manager, Director
4. For each commission type:
   - Select the partner
   - Choose calculation method (Fixed, % of Unit Price, % of Untaxed Total)
   - Set the rate/amount

### Processing Commissions

1. Click "Calculate Commissions" to create commission purchase orders
2. Review the generated purchase orders (accessible via the smart button)
3. Verify that the vendor reference matches the customer reference
4. Click "Confirm Commissions" to finalize the process

## Technical Implementation

### Vendor Reference Population

The vendor reference is populated through the following workflow:

1. **Sale Order Setup**: User sets `client_order_ref` on the sale order
2. **Commission Calculation**: When commissions are processed, the system calls `_prepare_purchase_order_vals()`
3. **Reference Transfer**: The method automatically adds `partner_ref: sale_order.client_order_ref` to the purchase order values
4. **Purchase Order Creation**: The purchase order is created with the vendor reference populated

### Key Methods

#### SaleOrder Model
```python
def _prepare_purchase_order_vals(self, partner, product, amount, description):
    """Enhanced to include vendor reference from customer reference"""
    vals = {
        # ... other fields
        'partner_ref': self.client_order_ref,  # Auto-populated
        # ... more fields
    }
```

#### PurchaseOrder Model
```python
@api.model_create_multi
def create(self, vals_list):
    """Override to ensure vendor reference is set for commission POs"""
    for vals in vals_list:
        if vals.get('origin_so_id'):
            sale_order = self.env['sale.order'].browse(vals['origin_so_id'])
            if sale_order.client_order_ref:
                vals['partner_ref'] = sale_order.client_order_ref
```

### Database Fields

#### New Sale Order Fields
- `commission_status`: Track commission processing status
- `commission_processed`: Boolean flag for commission completion
- Various commission partner and calculation fields

#### New Purchase Order Fields
- `origin_so_id`: Link to originating sale order
- `commission_posted`: Track commission posting status
- `is_commission_po`: Computed field to identify commission purchase orders

## Views and Navigation

### Sale Order Enhancements
- **Commission Tab**: Organized commission configuration with External and Internal sections
- **Smart Button**: "Commission POs" button showing count and providing quick access
- **Status Bar**: Commission status tracking in the header

### Purchase Order Enhancements
- **Commission Fields**: Display of origin sale order and commission status
- **Smart Button**: "Origin Sale Order" button for reverse navigation
- **Filters**: Special filters for commission vs. regular purchase orders

## Demo Data

The module includes demo data with:
- Sample commission partners (Broker, Referrer, Agent, Manager)
- Demo customer with reference
- Pre-configured commission service product

## Security

Access rights are configured for:
- Sale Order commission fields (base.group_user)
- Purchase Order commission fields (base.group_user)

## Benefits

1. **Consistency**: Ensures reference numbers flow seamlessly from sales to purchasing
2. **Traceability**: Easy tracking of commission payments back to original sales
3. **Automation**: Reduces manual data entry and potential errors
4. **Integration**: Seamless integration with existing Odoo workflows
5. **Reporting**: Better reporting capabilities with linked references

## Example Workflow

1. **Sales Team** creates a Sale Order with Customer Reference "CUST-REF-12345"
2. **Commission Setup**: Configure broker commission at 2.5% of total
3. **Process Commissions**: System creates Purchase Order for broker
4. **Automatic Reference**: Purchase Order automatically gets Vendor Reference "CUST-REF-12345"
5. **Payment Processing**: Accounts payable can easily trace commission back to original sale

## Troubleshooting

### Common Issues

1. **Vendor Reference Not Populated**
   - Ensure Customer Reference is set on the Sale Order
   - Verify the purchase order was created through commission processing

2. **Commission Partners Not Available**
   - Check that partners have `supplier_rank` > 0
   - Verify partners are active

3. **Smart Buttons Not Showing**
   - Ensure commission purchase orders exist
   - Check user permissions

## Support and Customization

This module is designed to be extensible. Common customizations include:
- Additional commission calculation methods
- Custom reference format transformations
- Integration with external accounting systems
- Enhanced reporting and analytics

## Version History

- **17.0.2.0.0**: Enhanced vendor reference auto-population feature
- **17.0.1.0.0**: Initial commission management system

## Dependencies

- `sale`: Sales Management
- `purchase`: Purchase Management  
- `account`: Accounting

## License

LGPL-3
