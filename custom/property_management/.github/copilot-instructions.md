# Property Management Module - AI Coding Instructions

This is an Odoo 17 Real Estate Property Management module that handles property sales, broker commissions, and installment payment tracking.

## Core Architecture

### Domain Models
- **Property (`property.property`)**: Real estate inventory with pricing, location, status tracking
- **Property Sale (`property.sale`)**: Sales transactions with installment payment plans, DLD fees, broker commissions
- **Broker Commission (`broker.commission.invoice`)**: Commission tracking and invoice generation for brokers/sellers
- **Account Move Extension**: Links invoices to property sales and commissions

### Key Relationships
```
Property (1) → (N) Property Sales → (N) Installment Lines
Property Sale (1) → (N) Broker Commissions → (N) Invoices
```

## Business Logic Patterns

### State Management
- **Property**: `available` → `reserved` → `booked` → `sold` (auto-updated on sale confirmation)
- **Property Sale**: `draft` → `confirmed` → `invoiced` → `cancelled`
- **Broker Commission**: `draft` → `confirmed` → `invoiced` → `cancelled`

### Financial Calculations (Auto-computed)
```python
# Property Sale financial flow
property_value = property_id.property_price
dld_fee = property_value * 0.04  # 4% Dubai Land Department fee
total_selling_price = property_value + dld_fee + admin_fee
down_payment = (down_payment_percentage / 100) * property_value
remaining_balance = total_selling_price - down_payment - dld_fee - admin_fee
amount_per_installment = remaining_balance / no_of_installments

# Broker commission
commission_amount = (commission_percentage / 100) * property_value
```

### Payment Schedule Generation
When a sale is confirmed (`action_confirm`), the system auto-generates installment lines:
1. Down payment (due on start_date)
2. DLD fee (due on start_date) 
3. Admin fee (due on start_date)
4. Monthly EMI installments (calculated using `relativedelta`)

## Development Conventions

### Field Naming
- Use `_id` suffix for Many2one relationships (`property_id`, `seller_id`)
- Monetary fields use `currency_field='currency_id'` parameter
- Computed fields follow pattern `_compute_{field_name}`
- State constants: `STATE_DRAFT = 'draft'` etc.

### View Structure
- Form views use header with statusbar and action buttons
- Tree views include monetary widgets with currency options
- Search views provide state-based filters and grouping
- Action buttons use `invisible` attributes with state-based domains

### Security & Access
- Models use `ir.model.access.csv` for basic CRUD permissions
- Group-based access via `property_user_group.xml` (Agent/Manager roles)
- Multi-company rules in `real_estate_security.xml`

## Critical Workflows

### Property Sale Confirmation
```python
# In property_sale.py action_confirm()
record._create_emi_lines()  # Generate payment schedule
record.property_id.write({'state': 'sold', 'partner_id': record.partner_id.id})
record.state = 'confirmed'
```

### Invoice Generation
- `action_generate_all_invoices()`: Creates invoices for due installments
- Links invoices via `property_order_id` field on `account.move`
- Updates installment `collection_status` to 'paid'

### Broker Commission Flow
1. Generate commission record from property sale
2. Confirm commission (`action_confirm`)
3. Generate customer invoice (`action_generate_customer_invoice`)
4. Track payment progress via related invoice states

## File Organization
```
models/
├── property_property.py      # Property inventory management
├── property_sale.py         # Sales & installment logic
├── broker_commission.py     # Commission tracking
└── account_move.py          # Invoice extensions

views/
├── property_property_views.xml
├── property_sale_views.xml
├── broker_commission.xml
└── account_move_views.xml

reports/
├── property_sale_management.py      # Report controller
├── property_sale_report_template.xml
└── sales_offer_report_template.xml  # Comprehensive PDF report
```

## Testing & Debugging
- Use `_logger.info()` for transaction logging
- State validation via `@api.constrains` decorators
- Error handling with `UserError` for business rule violations
- Enable developer mode for field debugging and model inspection

## Integration Points
- **Accounting**: Extends `account.move` with property sale tracking
- **Mail**: Uses `mail.thread` for chatter and activity tracking  
- **Currency**: Multi-currency support via `res.currency` relationships
- **Partners**: Broker/seller management via `res.partner` with company domain filters