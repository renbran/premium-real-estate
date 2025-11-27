# DEVELOPER QUICK REFERENCE
**payment_account_enhanced Module - Odoo 17.0**

---

## QUICK START

### 1. Module Structure at a Glance
```
models/                    → Database models (14 files)
  └─ account_payment.py    → MAIN: Payment workflow engine
views/                     → UI templates (9 files)
controllers/               → HTTP API endpoints (2 files)
reports/                   → PDF vouchers (2 files)
data/                      → Sequences, cron, emails (3 files)
security/                  → User groups & permissions (2 files)
tests/                     → Test suite (2 files, 735 lines)
```

### 2. Key Workflows

#### Payment Approval Flow
```
Draft
  ↓ submit_for_review()
Under Review (Reviewer)
  ↓ review_payment()
For Approval (Approver)
  ├─ IF amount < 10k AED:
  │  ↓ approve_payment()
  │  APPROVED
  │  ↓ action_post()
  │  POSTED ✓
  │
  └─ IF amount ≥ 10k AED:
     ↓ approve_payment()
     For Authorization (Authorizer)
     ↓ authorize_payment()
     APPROVED
     ↓ action_post()
     POSTED ✓

Any Stage: reject_payment() → Draft
```

### 3. Critical Files to Know

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| account_payment.py | Core workflow engine | 1,816 | ⚠️ Has duplicate write() |
| payment_approval_history.py | Audit trail | 251 | ✅ Good |
| payment_qr_verification.py | QR analytics | 318 | ✅ Good |
| controllers/main.py | /payment/verify endpoint | 450 | ⚠️ No rate limit |
| mail_template_data.xml | Email templates | 388 | ✅ Fixed (line endings) |

---

## COMMON TASKS

### Add a New Workflow State
```python
# 1. In account_payment.py, update selection field:
approval_state = fields.Selection([
    ('draft', 'Draft'),
    ('under_review', 'Under Review'),
    ('for_approval', 'For Approval'),
    ('for_authorization', 'For Authorization'),
    ('approved', 'Approved'),
    ('posted', 'Posted'),
    ('cancelled', 'Cancelled'),
    ('new_state', 'New State'),  # ADD HERE
], default='draft')

# 2. Add constraint validation:
def _check_workflow_progression(self):
    # Add new_state transition logic

# 3. Create action method:
def new_state_action(self):
    # Perform action
    self.write({'approval_state': 'new_state'})
    # Send email notification
```

### Modify Email Template
```python
# File: mail_template_data.xml

<record id="mail_template_payment_custom" model="mail.template">
    <field name="name">Custom Email</field>
    <field name="model_id" ref="account.model_account_payment"/>
    <field name="subject">Payment <t t-out="object.voucher_number"/></field>
    <field name="body_html" type="html">
        <div>
            <p>Dear <t t-out="object.partner_id.name"/>,</p>
            <!-- Your HTML here -->
        </div>
    </field>
</record>

# Then in payment.py, trigger it:
self.env['mail.template'].browse(template_id).send_mail(self.id)
```

### Add New Permission Group
```python
# File: security/payment_security.xml

<record id="group_payment_custom" model="res.groups">
    <field name="name">Payment: Custom Role</field>
    <field name="category_id" ref="base.module_category_accounting"/>
    <field name="implied_ids" eval="[(4, ref('group_payment_user'))]"/>
    <!-- Inherits USER permissions -->
</record>

# Then add record rules:
<record id="rule_payment_custom" model="ir.rule">
    <field name="name">Custom Rule</field>
    <field name="model_id" ref="model_account_payment"/>
    <field name="groups" eval="[(4, ref('group_payment_custom'))]"/>
    <field name="domain_force">[('approval_state', 'in', ['draft', 'under_review'])]</field>
</record>
```

### Test Workflow Transition
```python
# File: tests/test_vendor_payment_workflow.py

def test_new_workflow_step(self):
    """Test transition from state A to state B"""
    # 1. Create test payment
    payment = self.env['account.payment'].create({
        'partner_id': self.partner.id,
        'amount': 5000,
        'journal_id': self.journal.id,
    })

    # 2. Verify initial state
    self.assertEqual(payment.approval_state, 'draft')

    # 3. Perform action
    payment.submit_for_review()

    # 4. Verify final state
    self.assertEqual(payment.approval_state, 'under_review')

    # 5. Check side effects
    self.assertIsNotNone(payment.reviewer_id)
    self.assertTrue(payment.approval_history_ids)
```

---

## KEY CLASSES & METHODS

### AccountPayment Main Methods
```python
class AccountPayment(models.Model):
    # WORKFLOW
    def submit_for_review(self)
    def review_payment(self)
    def approve_payment(self)
    def authorize_payment(self)
    def reject_payment(reason=None)
    def action_post(self)

    # QR CODE
    def generate_qr_code(self)
    def action_regenerate_qr_code(self)

    # VALIDATION
    def _check_workflow_progression(self)
    def _check_unique_approvers(self)
    def _validate_workflow_transition(self)

    # NOTIFICATIONS
    def send_workflow_email(template_id)

    # UTILITIES
    def get_approval_state_display(self)
    def get_pending_days(self)
```

### PaymentApprovalHistory Methods
```python
class PaymentApprovalHistory(models.Model):
    @staticmethod
    def log_approval_action(payment, action, user, notes='')
```

### PaymentQRVerification Methods
```python
class PaymentQRVerification(models.Model):
    def get_verification_count(payment_id)
    def get_unique_verifiers(payment_id)
    def get_verification_by_date(payment_id)
```

---

## API ENDPOINTS

### Public QR Verification
```
GET /payment/verify/<access_token>

Parameters:
  access_token (string, required): 32-char token

Response (on success):
  {
    "payment": {
      "voucher_number": "PV-00123",
      "partner_id": "Vendor Name",
      "amount": 5500.00,
      "approval_state": "posted",
      "qr_code": "<base64 PNG>",
      "approval_chain": [...]
    }
  }

Status Codes:
  200 - Success
  404 - Token not found
  400 - Invalid token format
```

### Public Fallback (Simple HTML)
```
GET /payment/verify/simple/<access_token>

Same as above but returns simple HTML instead of JSON
Used when template rendering fails
```

---

## CONFIGURATION

### Company Settings
```python
# In res_company.py:
payment_verification_enabled      # Boolean
qr_code_enabled                   # Boolean
four_stage_workflow_enabled       # Boolean
authorization_threshold           # Float (default 5000 AED)
max_approval_amount              # Float (default 10000 AED)
auto_post_approved_payments      # Boolean
send_notifications_enabled       # Boolean
voucher_footer_text             # Text
```

### System Settings
```python
# In res_config_settings.py:
pdf_generation_mode  # standard / ssl_safe / fallback
```

### Hardcoded Values (Should be Constants)
```python
# From account_payment.py:
if amount >= 10000:  # <-- APPEARS IN 7 PLACES
    requires_authorization = True

# Should be:
AUTHORIZATION_THRESHOLD = 10000

# Line endings issue (FIXED):
# All XML files must use LF (\n), not CRLF (\r\n)
# Use: dos2unix <filename>
```

---

## SECURITY CHECKLIST

### Before Deploying
- [ ] HTTPS configured (payment tokens in URL)
- [ ] Rate limiting added to /payment/verify
- [ ] Duplicate write() method fixed
- [ ] Database backed up
- [ ] Test users created with proper groups
- [ ] Email configuration tested
- [ ] Firewall rules allow only HTTPS

### Role Separation
- [ ] Creator ≠ Reviewer
- [ ] Reviewer ≠ Approver
- [ ] Approver ≠ Authorizer (for high-value)
- [ ] Authorizer ≠ Poster

---

## TROUBLESHOOTING

### Problem: "Element odoo has extra content: data, line 3"
**Cause:** CRLF line endings in XML file
**Fix:** `dos2unix data/mail_template_data.xml`

### Problem: Duplicate write() method errors
**Cause:** Lines 600 & 679 in account_payment.py
**Fix:** Consolidate into single method
**Status:** KNOWN ISSUE - needs fixing

### Problem: No emails sent
**Cause:** Email configuration missing
**Fix:**
```
Settings → Technical → Parameters → email.server.address
Settings → Email → Email Templates (test)
```

### Problem: QR code not showing
**Cause:**
- Python qrcode package not installed
- Pillow not installed
**Fix:** `pip install qrcode[pil] Pillow`

### Problem: /payment/verify returns 404
**Cause:** Invalid access token or payment doesn't exist
**Fix:**
- Verify token format (should be 32 chars)
- Check payment exists and is posted
- Check payment QR generated

---

## PERFORMANCE TIPS

### Database Queries
```python
# ❌ SLOW - N+1 problem
for payment in payments:
    print(payment.partner_id.name)  # Extra query per payment

# ✅ FAST - Prefetch related
payments = payments.with_context(prefetch_fields=False)
payments = payments.mapped('partner_id')  # Single query
```

### QR Generation
```python
# Current: Synchronous (blocks user)
# Consider: Async job via cron
# File: models/payment_reminder.py (similar pattern)

def generate_qr_background(self):
    # Queue job
    self.env['queue.job'].create({
        'model_name': 'account.payment',
        'method_name': 'generate_qr_code',
        'records': self.ids,
    })
```

---

## TESTING COMMANDS

```bash
# Run all tests
./odoo-bin -d test_db -i payment_account_enhanced --test-enable

# Run specific test file
./odoo-bin -d test_db --test-file=test_vendor_payment_workflow.py

# Run specific test class
./odoo-bin -d test_db --test-file=test_vendor_payment_workflow.py::TestPaymentWorkflow

# With coverage
./odoo-bin -d test_db --test-enable --coverage --coverage-report=html
```

---

## USEFUL SQL QUERIES

```sql
-- Find pending approvals
SELECT id, voucher_number, partner_id, amount, approval_state
FROM account_payment
WHERE approval_state = 'under_review'
  AND reviewer_id = 123
ORDER BY create_date DESC;

-- Count by approval stage
SELECT approval_state, COUNT(*) as count, SUM(amount) as total
FROM account_payment
WHERE date >= NOW() - INTERVAL '30 days'
GROUP BY approval_state;

-- Find payments without QR code
SELECT id, voucher_number
FROM account_payment
WHERE qr_code IS NULL
  AND approval_state IN ('approved', 'posted');

-- Audit trail for specific payment
SELECT user_id, action, create_date, notes
FROM payment_approval_history
WHERE payment_id = 123
ORDER BY create_date;
```

---

## RESOURCES

### Documentation Files in Module
- `COMPREHENSIVE_REVIEW.md` - Full code review
- `EXECUTIVE_SUMMARY.md` - High-level overview
- `IMPLEMENTATION_GUIDE_APPROVAL_CAP.md` - Implementation details
- `WORKFLOW_VISUAL_GUIDE.md` - Visual diagrams
- `QUICK_REFERENCE.md` - Quick lookup

### External Resources
- [Odoo 17 Documentation](https://www.odoo.com/documentation/17.0/)
- [QRCode Library](https://github.com/lincolnloop/python-qrcode)
- [Pillow Image Library](https://pillow.readthedocs.io/)

---

## COMMON BUGS & FIXES

| Bug | Location | Fix |
|-----|----------|-----|
| Duplicate write() | account_payment.py:600,679 | Consolidate methods |
| No rate limiting | controllers/main.py | Add @rate_limit decorator |
| Hardcoded threshold | account_payment.py (7 places) | Define constant |
| CRLF line endings | data/mail_template_data.xml | Run dos2unix |
| Complex validation | account_payment.py:48 lines | Break into helpers |

---

## CONTACT & SUPPORT

- **Code Owner:** OSUS Properties
- **Module Maintainer:** [Your Name]
- **Bug Reports:** GitHub Issues
- **Questions:** Code comments + docstrings

---

**Last Updated:** November 3, 2025
**Document Version:** 1.0
