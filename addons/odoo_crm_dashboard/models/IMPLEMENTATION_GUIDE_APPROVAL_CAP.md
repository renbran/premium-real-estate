# 🚀 Quick Implementation Guide: AED 15,000 Approval Cap

**Target:** Implement transaction approval cap functionality  
**Timeline:** 3 days (~22 hours)  
**Priority:** HIGH

---

## 📋 Implementation Checklist

### Phase 1: Backend Logic (4 hours)

#### Step 1.1: Add Computed Fields to Model

**File:** `payment_account_enhanced/models/account_payment.py`

**Location:** After existing fields (around line 135)

```python
# ============================================================================
# APPROVAL CAP FIELDS
# ============================================================================

requires_full_approval = fields.Boolean(
    string='Requires Full Approval Chain',
    compute='_compute_requires_full_approval',
    store=True,
    help="True if amount exceeds AED 15,000 cap"
)

approval_cap_amount = fields.Monetary(
    string='Approval Cap Amount',
    default=15000.0,
    currency_field='currency_id',
    help="Amount threshold for full approval requirement"
)

@api.depends('amount', 'currency_id', 'company_id', 'date')
def _compute_requires_full_approval(self):
    """Check if payment exceeds approval cap"""
    for payment in self:
        # Get AED currency for conversion
        aed_currency = self.env['res.currency'].search([('name', '=', 'AED')], limit=1)
        
        if not aed_currency:
            _logger.warning("AED currency not found, using payment currency for cap check")
            amount_in_aed = payment.amount
        elif payment.currency_id and payment.currency_id != aed_currency:
            # Convert amount to AED for comparison
            amount_in_aed = payment.currency_id._convert(
                payment.amount,
                aed_currency,
                payment.company_id or self.env.company,
                payment.date or fields.Date.today()
            )
        else:
            amount_in_aed = payment.amount
        
        # Get configurable cap (default 15,000 AED)
        cap_param = self.env['ir.config_parameter'].sudo().get_param(
            'payment_account_enhanced.approval_cap_aed', 
            '15000.00'
        )
        approval_cap = float(cap_param)
        
        payment.requires_full_approval = amount_in_aed > approval_cap
        
        _logger.info("Payment %s: Amount in AED: %.2f, Cap: %.2f, Requires full approval: %s",
                    payment.voucher_number or payment.id,
                    amount_in_aed,
                    approval_cap,
                    payment.requires_full_approval)
```

#### Step 1.2: Add Posting Validation

**File:** `payment_account_enhanced/models/account_payment.py`

**Location:** Find the `action_post` method or create one

```python
def action_post(self):
    """Enhanced posting with approval cap validation"""
    for payment in self:
        # Get current user's groups
        user = self.env.user
        is_reviewer = user.has_group('payment_account_enhanced.group_payment_reviewer')
        is_poster = user.has_group('payment_account_enhanced.group_payment_poster')
        is_manager = user.has_group('payment_account_enhanced.group_payment_manager')
        
        _logger.info("Posting validation for %s by user %s (Reviewer: %s, Poster: %s, Manager: %s)",
                    payment.voucher_number or payment.id,
                    user.name,
                    is_reviewer, is_poster, is_manager)
        
        # Check if payment requires full approval (> AED 15,000)
        if payment.requires_full_approval:
            _logger.info("Payment %s requires full approval (amount exceeds cap)", 
                        payment.voucher_number)
            
            # Must be in approved state
            if payment.approval_state != 'approved':
                raise ValidationError(_(
                    '🚫 High-Value Payment Approval Required\n\n'
                    'Payment: %s\n'
                    'Amount: %.2f %s (exceeds AED 15,000)\n'
                    'Current Status: %s\n'
                    'Required Status: Approved\n\n'
                    'This payment requires full approval chain:\n'
                    '1️⃣ Reviewer → 2️⃣ Approver → 3️⃣ Authorizer → ✅ Approved\n\n'
                    'Please complete the approval workflow before posting.'
                ) % (
                    payment.voucher_number or payment.name,
                    payment.amount,
                    payment.currency_id.name,
                    dict(payment._fields['approval_state'].selection).get(payment.approval_state)
                ))
            
            # Only Poster or Manager can post high-value
            if not (is_poster or is_manager):
                raise ValidationError(_(
                    '🚫 Insufficient Permissions\n\n'
                    'Payment: %s\n'
                    'Amount: %.2f %s (exceeds AED 15,000)\n\n'
                    'High-value payments can only be posted by users with "Payment Poster" role.\n\n'
                    'Your current role: %s\n'
                    'Required role: Payment Poster or Payment Manager\n\n'
                    'Please contact your payment manager for assistance.'
                ) % (
                    payment.voucher_number or payment.name,
                    payment.amount,
                    payment.currency_id.name,
                    ', '.join(user.groups_id.mapped('name'))
                ))
            
            _logger.info("✓ High-value payment posting authorized by %s", user.name)
        
        else:
            # Low-value payment (≤ AED 15,000)
            _logger.info("Payment %s is low-value (fast-track eligible)", 
                        payment.voucher_number)
            
            # Reviewer, Poster, or Manager can post
            if not (is_reviewer or is_poster or is_manager):
                raise ValidationError(_(
                    '🚫 Posting Permission Required\n\n'
                    'You do not have permission to post payments.\n\n'
                    'Required role: Payment Reviewer or higher\n\n'
                    'Please request access from your system administrator.'
                ))
            
            # Must be at least reviewed (not draft)
            if payment.approval_state == 'draft':
                raise ValidationError(_(
                    '🚫 Review Required\n\n'
                    'Payment: %s\n'
                    'Amount: %.2f %s\n\n'
                    'Payment must be reviewed before posting.\n\n'
                    'Actions available:\n'
                    '• Click "Submit for Review" button\n'
                    '• Complete the review process\n'
                    '• Then try posting again'
                ) % (
                    payment.voucher_number or payment.name,
                    payment.amount,
                    payment.currency_id.name
                ))
            
            _logger.info("✓ Low-value payment posting authorized by %s (fast-track)", user.name)
    
    # Call parent method to perform actual posting
    result = super(AccountPayment, self).action_post()
    
    return result
```

---

### Phase 2: UI Enhancements (2 hours)

#### Step 2.1: Add Alert Banners

**File:** `payment_account_enhanced/views/account_payment_views.xml`

**Location:** Inside the form view, before `<sheet>` tag

```xml
<xpath expr="//form/sheet" position="before">
    <!-- High-Value Payment Warning -->
    <div class="alert alert-warning" role="alert" 
         attrs="{'invisible': [('requires_full_approval', '=', False)]}">
        <div class="row">
            <div class="col-1 text-center">
                <i class="fa fa-exclamation-triangle fa-3x"/>
            </div>
            <div class="col-11">
                <h4 class="alert-heading">
                    <strong>⚠️ High-Value Payment Alert</strong>
                </h4>
                <p class="mb-1">
                    This payment exceeds <strong>AED 15,000</strong> and requires the complete approval chain.
                </p>
                <hr/>
                <p class="mb-0">
                    <strong>Required Steps:</strong>
                    1️⃣ Reviewer → 2️⃣ Approver → 3️⃣ Authorizer → ✅ Post (by Poster only)
                </p>
            </div>
        </div>
    </div>
    
    <!-- Fast-Track Eligible Info -->
    <div class="alert alert-info" role="alert" 
         attrs="{'invisible': [('requires_full_approval', '=', True)]}">
        <div class="row">
            <div class="col-1 text-center">
                <i class="fa fa-info-circle fa-3x"/>
            </div>
            <div class="col-11">
                <h4 class="alert-heading">
                    <strong>ℹ️ Fast-Track Eligible</strong>
                </h4>
                <p class="mb-0">
                    This payment is <strong>≤ AED 15,000</strong> and can be posted directly by a Reviewer after review.
                </p>
            </div>
        </div>
    </div>
</xpath>
```

#### Step 2.2: Add Cap Indicator Fields

**File:** `payment_account_enhanced/views/account_payment_views.xml`

**Location:** In the form view, add invisible fields for attrs conditions

```xml
<xpath expr="//field[@name='amount']" position="after">
    <field name="requires_full_approval" invisible="1"/>
    <field name="approval_cap_amount" invisible="1"/>
</xpath>
```

#### Step 2.3: Add Cap Information in Header

**File:** `payment_account_enhanced/views/account_payment_views.xml`

**Location:** In the form header area

```xml
<xpath expr="//header" position="inside">
    <!-- Cap Status Badge -->
    <button name="dummy" type="object" class="oe_stat_button" icon="fa-shield"
            attrs="{'invisible': [('requires_full_approval', '=', False)]}">
        <div class="o_field_widget o_stat_info">
            <span class="o_stat_value text-danger">Full Approval</span>
            <span class="o_stat_text">Required</span>
        </div>
    </button>
    
    <button name="dummy" type="object" class="oe_stat_button" icon="fa-bolt"
            attrs="{'invisible': [('requires_full_approval', '=', True)]}">
        <div class="o_field_widget o_stat_info">
            <span class="o_stat_value text-success">Fast-Track</span>
            <span class="o_stat_text">Eligible</span>
        </div>
    </button>
</xpath>
```

---

### Phase 3: Security Rules (2 hours)

#### Step 3.1: Update Security Rules

**File:** `payment_account_enhanced/security/payment_security.xml`

**Location:** Add after existing record rules

```xml
<!-- Low-Value Payment Posting Rule -->
<record id="payment_reviewer_post_low_value_rule" model="ir.rule">
    <field name="name">Reviewer: Post Low-Value Payments (≤ AED 15K)</field>
    <field name="model_id" ref="account.model_account_payment"/>
    <field name="domain_force">[
        ('requires_full_approval', '=', False),
        ('approval_state', 'in', ['under_review', 'for_approval', 'for_authorization', 'approved'])
    ]</field>
    <field name="groups" eval="[(4, ref('payment_account_enhanced.group_payment_reviewer'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>

<!-- High-Value Payment Posting Rule -->
<record id="payment_poster_high_value_rule" model="ir.rule">
    <field name="name">Poster: Post High-Value Payments (> AED 15K)</field>
    <field name="model_id" ref="account.model_account_payment"/>
    <field name="domain_force">[
        ('requires_full_approval', '=', True),
        ('approval_state', '=', 'approved')
    ]</field>
    <field name="groups" eval="[(4, ref('payment_account_enhanced.group_payment_poster'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

#### Step 3.2: Add Configuration Parameter

**File:** `payment_account_enhanced/data/config_data.xml` (CREATE NEW FILE)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <!-- Approval Cap Configuration -->
        <record id="config_approval_cap_aed" model="ir.config_parameter">
            <field name="key">payment_account_enhanced.approval_cap_aed</field>
            <field name="value">15000.00</field>
        </record>
        
        <!-- Auto QR Generation -->
        <record id="config_auto_qr_generation" model="ir.config_parameter">
            <field name="key">payment_account_enhanced.auto_qr_generation</field>
            <field name="value">True</field>
        </record>
        
    </data>
</odoo>
```

#### Step 3.3: Update Manifest

**File:** `payment_account_enhanced/__manifest__.py`

**Location:** Add to `data` list

```python
'data': [
    # ... existing data files ...
    'data/config_data.xml',  # ADD THIS LINE
    # ... rest of data files ...
],
```

---

### Phase 4: Testing (4 hours)

#### Step 4.1: Create Test File

**File:** `payment_account_enhanced/tests/test_approval_cap.py` (CREATE NEW FILE)

```python
# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestApprovalCap(TransactionCase):
    
    def setUp(self):
        super(TestApprovalCap, self).setUp()
        
        # Create test users
        self.user_reviewer = self.env['res.users'].create({
            'name': 'Test Reviewer',
            'login': 'reviewer',
            'groups_id': [(4, self.env.ref('payment_account_enhanced.group_payment_reviewer').id)]
        })
        
        self.user_poster = self.env['res.users'].create({
            'name': 'Test Poster',
            'login': 'poster',
            'groups_id': [(4, self.env.ref('payment_account_enhanced.group_payment_poster').id)]
        })
        
        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Vendor'
        })
        
        # Get AED currency
        self.aed = self.env['res.currency'].search([('name', '=', 'AED')], limit=1)
    
    def _create_payment(self, amount, user=None):
        """Helper to create payment"""
        vals = {
            'payment_type': 'outbound',
            'partner_id': self.partner.id,
            'amount': amount,
            'currency_id': self.aed.id,
        }
        
        if user:
            return self.env['account.payment'].with_user(user).create(vals)
        return self.env['account.payment'].create(vals)
    
    def test_low_value_requires_full_approval_false(self):
        """Payments ≤ AED 15,000 should not require full approval"""
        payment = self._create_payment(10000.00)
        self.assertFalse(payment.requires_full_approval)
    
    def test_high_value_requires_full_approval_true(self):
        """Payments > AED 15,000 should require full approval"""
        payment = self._create_payment(20000.00)
        self.assertTrue(payment.requires_full_approval)
    
    def test_exact_cap_requires_full_approval_false(self):
        """Payment exactly at AED 15,000 should not require full approval"""
        payment = self._create_payment(15000.00)
        self.assertFalse(payment.requires_full_approval)
    
    def test_reviewer_can_post_low_value(self):
        """Reviewer should be able to post payments ≤ AED 15,000"""
        payment = self._create_payment(10000.00)
        payment.approval_state = 'under_review'
        
        # Should not raise exception
        payment.with_user(self.user_reviewer).action_post()
        self.assertEqual(payment.state, 'posted')
    
    def test_reviewer_cannot_post_high_value(self):
        """Reviewer should NOT be able to post payments > AED 15,000"""
        payment = self._create_payment(20000.00)
        payment.approval_state = 'approved'  # Even if approved
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            payment.with_user(self.user_reviewer).action_post()
        
        self.assertIn('Insufficient Permissions', str(cm.exception))
    
    def test_poster_can_post_high_value_when_approved(self):
        """Poster should be able to post high-value payments when approved"""
        payment = self._create_payment(25000.00)
        payment.approval_state = 'approved'
        
        # Should succeed
        payment.with_user(self.user_poster).action_post()
        self.assertEqual(payment.state, 'posted')
    
    def test_poster_cannot_post_high_value_when_not_approved(self):
        """Poster cannot post high-value payments if not approved"""
        payment = self._create_payment(25000.00)
        payment.approval_state = 'for_approval'  # Not fully approved
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError) as cm:
            payment.with_user(self.user_poster).action_post()
        
        self.assertIn('Approval Required', str(cm.exception))
```

#### Step 4.2: Manual Testing Checklist

```
Manual Test Scenarios:

✅ Test 1: Low-Value Fast-Track
1. Login as Payment Reviewer
2. Create payment: AED 10,000
3. Verify banner shows "Fast-Track Eligible"
4. Submit for Review
5. Try to Post → Should succeed
6. Verify state = Posted
7. Verify QR code generated
8. Verify reference number visible

✅ Test 2: High-Value Full Approval
1. Login as Payment Reviewer
2. Create payment: AED 25,000
3. Verify banner shows "High-Value Payment Alert"
4. Submit for Review
5. Try to Post → Should fail with permission error
6. Forward to Approver
7. Login as Approver, approve
8. Forward to Authorizer
9. Login as Authorizer, authorize
10. Login as Poster
11. Post payment → Should succeed
12. Verify all workflow history recorded

✅ Test 3: Currency Conversion
1. Create payment: USD 5,000 (converts to AED 18,350)
2. Verify requires_full_approval = True
3. Verify banner shows high-value alert

✅ Test 4: Exact Cap Amount
1. Create payment: AED 15,000.00
2. Verify requires_full_approval = False
3. Verify fast-track eligible

✅ Test 5: Configuration Change
1. Go to Settings > Technical > Parameters
2. Change payment_account_enhanced.approval_cap_aed to 10000
3. Create payment: AED 12,000
4. Verify requires_full_approval = True (new cap)
```

---

## 🚀 Deployment Steps

### Step 1: Backup Database
```bash
docker-compose exec db pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql
```

### Step 2: Apply Changes
```bash
# Stop Odoo
docker-compose stop odoo

# Update module
docker-compose exec odoo odoo --update=payment_account_enhanced --stop-after-init -d odoo

# Restart Odoo
docker-compose start odoo
```

### Step 3: Verify Deployment
```bash
# Check logs for errors
docker-compose logs -f odoo | grep -i "payment\|error\|warning"

# Test in UI
# 1. Create test payment with AED 10,000
# 2. Create test payment with AED 20,000
# 3. Verify banners appear correctly
# 4. Test posting permissions
```

### Step 4: User Training
```
Training Points:
1. Explain AED 15,000 cap threshold
2. Show fast-track vs. full approval workflows
3. Demonstrate UI indicators (banners, badges)
4. Review permission changes
5. Practice test scenarios
```

---

## 📊 Success Metrics

After implementation, verify:

- ✅ Computed field `requires_full_approval` calculates correctly
- ✅ Low-value payments can be posted by Reviewers
- ✅ High-value payments require Poster role
- ✅ UI banners display appropriately
- ✅ All validation errors are user-friendly
- ✅ Audit trail captures all actions
- ✅ Currency conversion works correctly
- ✅ Configuration parameter is respected
- ✅ All tests pass
- ✅ No performance degradation

---

## 🆘 Rollback Plan

If issues occur:

```bash
# 1. Stop Odoo
docker-compose stop odoo

# 2. Restore database backup
docker-compose exec db psql -U odoo odoo < backup_YYYYMMDD.sql

# 3. Revert code changes
git revert HEAD

# 4. Restart Odoo
docker-compose start odoo
```

---

**Ready to implement? Start with Phase 1!** 🚀
