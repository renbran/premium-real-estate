# Odoo 18 Development Instructions & Quick Reference Guide

## Table of Contents

1. [Quick Start Setup](#quick-start-setup)
2. [Development Workflow](#development-workflow)
3. [Module Structure](#module-structure)
4. [Model Development](#model-development)
5. [View Development](#view-development)
6. [Security Implementation](#security-implementation)
7. [Best Practices](#best-practices)
8. [AI Prompting Strategies](#ai-prompting-strategies)
9. [Testing Guide](#testing-guide)
10. [Deployment](#deployment)

## Quick Start Setup

### Prerequisites Installation

Install the following prerequisites:

```bash
# Verify Python 3.8+ installation
python --version

# Install PostgreSQL 12+ (Windows)
# Download from https://www.postgresql.org/download/windows/

# Create PostgreSQL user
psql -U postgres
CREATE USER odoo WITH CREATEDB NOCREATEROLE SUPERUSER;
\password odoo
```

### Odoo 18 Installation

Clone and setup Odoo 18:

```bash
# Clone Odoo 18 source
git clone https://github.com/odoo/odoo.git -b 18.0 --depth 1
cd odoo

# Install Python dependencies
pip install -r requirements.txt

# Create development directory structure
mkdir -p ~/odoo-dev/custom-addons
mkdir -p ~/odoo-dev/config
mkdir -p ~/odoo-dev/data
```

### VS Code Configuration

Install essential extensions:

```bash
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension ms-python.black-formatter
```

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "github.copilot.enable": {
        "*": true,
        "python": true,
        "javascript": true,
        "xml": true,
        "css": true
    },
    "files.associations": {
        "*.xml": "xml",
        "*.py": "python"
    },
    "emmet.includeLanguages": {
        "xml": "html"
    }
}
```

## Development Workflow

### Phase 1: Create New Module

Generate module scaffold:

```bash
./odoo-bin scaffold my_custom_app ~/odoo-dev/custom-addons/
```

### Phase 2: Module Structure

Standard Odoo 18 module structure:

```text
my_custom_app/
├── __init__.py                 # Package initialization
├── __manifest__.py             # Module manifest/metadata
├── controllers/                # Web controllers
│   ├── __init__.py
│   └── main.py
├── data/                       # Data files
│   └── ir.model.access.csv
├── demo/                       # Demo data
│   └── demo.xml
├── i18n/                       # Translations
├── models/                     # Python models
│   ├── __init__.py
│   └── my_model.py
├── security/                   # Security rules
│   ├── ir.model.access.csv
│   └── security.xml
├── static/                     # Static assets
│   ├── description/
│   ├── src/
│   └── lib/
├── views/                      # XML views
│   ├── views.xml
│   └── templates.xml
├── wizard/                     # Transient models
└── tests/                      # Unit tests
```

### Phase 3: Manifest Configuration

Create `__manifest__.py`:

```python
{
    'name': 'My Custom App',
    'version': '18.0.1.0.0',
    'summary': 'Custom application for specific business needs',
    'description': """
        Detailed description of module functionality.
        Multiple lines supported for comprehensive information.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Custom',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_custom_app/static/src/js/**/*',
            'my_custom_app/static/src/css/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

## Model Development

### Standard Model Template

Create models following Odoo 18 best practices:

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, id desc'
    
    # Basic fields (required first)
    name = fields.Char('Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Html('Description')
    
    # Selection fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], default='1', string='Priority')
    
    # Date fields
    date_start = fields.Date('Start Date', default=fields.Date.today)
    date_end = fields.Date('End Date')
    date_deadline = fields.Date('Deadline')
    
    # Numeric fields
    amount = fields.Float('Amount', digits=(16, 2))
    quantity = fields.Integer('Quantity', default=1)
    
    # Relational fields
    user_id = fields.Many2one(
        'res.users', 
        string='Responsible User', 
        default=lambda self: self.env.user,
        tracking=True
    )
    partner_id = fields.Many2one('res.partner', 'Partner')
    line_ids = fields.One2many('my.model.line', 'model_id', 'Lines')
    tag_ids = fields.Many2many('my.model.tag', string='Tags')
    
    # Computed fields
    total_amount = fields.Float(
        'Total Amount', 
        compute='_compute_total_amount', 
        store=True
    )
    is_overdue = fields.Boolean(
        'Is Overdue', 
        compute='_compute_is_overdue'
    )
    
    # Computed field methods
    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))
    
    @api.depends('date_deadline', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.date_deadline and 
                record.date_deadline < today and 
                record.state not in ['done', 'cancelled']
            )
    
    # Constraints
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if (record.date_start and record.date_end and 
                record.date_start > record.date_end):
                raise ValidationError(
                    "Start date cannot be after end date."
                )
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError("Amount cannot be negative.")
    
    # Onchange methods
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # Auto-fill related fields
            return {
                'domain': {
                    'user_id': [('company_id', '=', self.partner_id.company_id.id)]
                }
            }
    
    # Business logic methods
    def action_confirm(self):
        """Confirm the record"""
        self.write({'state': 'confirmed'})
        return True
    
    def action_done(self):
        """Mark record as done"""
        self.write({'state': 'done'})
        return True
    
    def action_cancel(self):
        """Cancel the record"""
        self.write({'state': 'cancelled'})
        return True
    
    # Override ORM methods
    @api.model
    def create(self, vals):
        # Custom logic before creation
        record = super().create(vals)
        # Custom logic after creation
        return record
    
    def write(self, vals):
        # Custom logic before update
        result = super().write(vals)
        # Custom logic after update
        return result
```

## View Development

### Form View Template

Create comprehensive form views:

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_confirm" string="Confirm" 
                        type="object" class="btn-primary"
                        states="draft"/>
                <button name="action_done" string="Mark Done" 
                        type="object" class="btn-success"
                        states="confirmed"/>
                <button name="action_cancel" string="Cancel" 
                        type="object" 
                        states="draft,confirmed"/>
                <field name="state" widget="statusbar" 
                       statusbar_visible="draft,confirmed,done"/>
            </header>
            
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <!-- Smart buttons go here -->
                </div>
                
                <div class="oe_title">
                    <h1>
                        <field name="name" placeholder="Enter name..."/>
                    </h1>
                </div>
                
                <group>
                    <group name="left_group">
                        <field name="user_id" widget="many2one_avatar_user"/>
                        <field name="partner_id"/>
                        <field name="priority" widget="priority"/>
                    </group>
                    <group name="right_group">
                        <field name="date_start"/>
                        <field name="date_end"/>
                        <field name="date_deadline"/>
                        <field name="total_amount" widget="monetary"/>
                    </group>
                </group>
                
                <notebook>
                    <page string="Description" name="description">
                        <field name="description" widget="html"/>
                    </page>
                    
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <tree editable="bottom">
                                <field name="name"/>
                                <field name="quantity"/>
                                <field name="amount" widget="monetary"/>
                            </tree>
                        </field>
                    </page>
                    
                    <page string="Tags" name="tags">
                        <field name="tag_ids" widget="many2many_tags"/>
                    </page>
                </notebook>
            </sheet>
            
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### Tree View Template

Create efficient list views:

```xml
<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree decoration-success="state == 'done'"
              decoration-info="state == 'confirmed'"
              decoration-muted="state == 'cancelled'"
              decoration-danger="is_overdue == True">
            
            <field name="name"/>
            <field name="user_id" widget="many2one_avatar_user"/>
            <field name="partner_id"/>
            <field name="date_start"/>
            <field name="date_deadline"/>
            <field name="total_amount" widget="monetary"/>
            <field name="priority" widget="priority"/>
            <field name="state" widget="badge" 
                   decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"
                   decoration-muted="state == 'draft'"/>
            <field name="is_overdue" invisible="1"/>
        </tree>
    </field>
</record>
```

### Search View Template

Add comprehensive search and filter options:

```xml
<record id="view_my_model_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search>
            <field name="name" string="Name"/>
            <field name="user_id"/>
            <field name="partner_id"/>
            <field name="state"/>
            
            <filter name="my_records" string="My Records"
                    domain="[('user_id', '=', uid)]"/>
            <filter name="active" string="Active"
                    domain="[('active', '=', True)]"/>
            <filter name="overdue" string="Overdue"
                    domain="[('is_overdue', '=', True)]"/>
            
            <separator/>
            <filter name="draft" string="Draft"
                    domain="[('state', '=', 'draft')]"/>
            <filter name="confirmed" string="Confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <filter name="done" string="Done"
                    domain="[('state', '=', 'done')]"/>
            
            <group expand="0" string="Group By">
                <filter name="group_user" string="Responsible User"
                        context="{'group_by': 'user_id'}"/>
                <filter name="group_state" string="Status"
                        context="{'group_by': 'state'}"/>
                <filter name="group_date" string="Start Date"
                        context="{'group_by': 'date_start'}"/>
            </group>
        </search>
    </field>
</record>
```

## Security Implementation

### Access Rights Configuration

Create `security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
access_my_model_line_user,my.model.line.user,model_my_model_line,base.group_user,1,1,1,0
```

### Record Rules Implementation

Create `security/security.xml`:

```xml
<odoo>
    <data noupdate="1">
        <!-- User can only see their own records -->
        <record id="rule_my_model_user_own" model="ir.rule">
            <field name="name">My Model: User Own Records</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
            <field name="perm_read" eval="1"/>
            <field name="perm_write" eval="1"/>
            <field name="perm_create" eval="1"/>
            <field name="perm_unlink" eval="0"/>
        </record>
        
        <!-- Manager can see all records -->
        <record id="rule_my_model_manager_all" model="ir.rule">
            <field name="name">My Model: Manager All Records</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('base.group_system'))]"/>
        </record>
    </data>
</odoo>
```

## Best Practices

### ✅ DO's - Follow These Practices

**Model Development Best Practices:**

```python
# ✅ DO: Use proper model structure and ordering
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'Always provide model description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, id desc'

# ✅ DO: Use @api.depends for computed fields
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))

# ✅ DO: Use proper field attributes with help text
name = fields.Char(
    'Name', 
    required=True, 
    tracking=True, 
    help="Enter the name of the record"
)

# ✅ DO: Use constraints for validation
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for record in self:
        if (record.start_date and record.end_date and 
            record.start_date > record.end_date):
            raise ValidationError("Start date must be before end date")

# ✅ DO: Handle empty recordsets properly
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount')) if record.line_ids else 0.0
```

**View Development Best Practices:**

```xml
<!-- ✅ DO: Use proper view structure with semantic elements -->
<record id="view_model_form" model="ir.ui.view">
    <field name="name">model.name.form</field>
    <field name="model">model.name</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <!-- Form content with proper grouping -->
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>

<!-- ✅ DO: Use appropriate widgets for field types -->
<field name="date" widget="date"/>
<field name="amount" widget="monetary"/>
<field name="user_id" widget="many2one_avatar_user"/>
<field name="priority" widget="priority"/>
<field name="state" widget="badge"/>
```

### ❌ DON'Ts - Avoid These Mistakes

**Avoid Deprecated Syntax:**

```python
# ❌ DON'T: Use old API (completely deprecated)
def old_create(self, cr, uid, vals, context=None):
    return super().create(cr, uid, vals, context=context)

# ❌ DON'T: Use @api.one (deprecated since Odoo 8)
@api.one
def my_method(self):
    return self.name

# ❌ DON'T: Use direct SQL without proper escaping
self.env.cr.execute("SELECT * FROM table WHERE id = %s" % record_id)

# ❌ DON'T: Access self without iteration in computed methods
def _compute_total(self):
    self.total = sum(self.line_ids.mapped('amount'))  # Wrong!

# ❌ DON'T: Use mutable default arguments
def my_method(self, default_list=[]):  # Wrong!
    default_list.append('item')
    return default_list
```

## AI Prompting Strategies

### Effective Prompts for Different Tasks

**Model Generation Prompts:**

```text
Create an Odoo 18 model for [business domain] with:
- Proper inheritance from mail.thread
- Fields: [list specific fields with types]
- Computed fields with @api.depends
- Validation constraints using @api.constrains
- Business methods for workflow state changes
- Follow Odoo 18 coding guidelines and best practices
```

**View Generation Prompts:**

```text
Generate Odoo 18 XML views for model [model_name]:
- Form view with proper header, sheet, and chatter structure
- Tree view with appropriate decorations and widgets
- Search view with filters and group_by options
- Use modern widgets and proper field attributes
- Include responsive design considerations
```

**Debugging Assistance Prompts:**

```text
Debug this Odoo 18 error:
[paste complete error traceback]

Context Information:
- Odoo version: 18.0
- Custom module: [module_name]
- What I was trying to do: [describe action]
- Recent changes: [describe what was changed]

Please provide step-by-step debugging approach.
```

### Context-Aware Development

Always provide context to improve AI suggestions:

```python
# Context comment for AI assistance
# This is an Odoo 18 model for project task management
# Inherits from mail.thread for activity tracking
# Integrates with hr.employee for resource management
# Must maintain compatibility with project.project model
# Security: users can only see their assigned tasks

class ProjectTaskCustom(models.Model):
    # AI will generate more contextually appropriate code
    pass
```

## Testing Guide

### Unit Test Structure

Create comprehensive test cases:

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class TestMyModel(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Model = self.env['my.model']
        self.test_user = self.env.ref('base.user_demo')
        self.test_partner = self.env.ref('base.res_partner_1')
        
    def test_model_creation_basic(self):
        """Test basic model creation with required fields"""
        record = self.Model.create({
            'name': 'Test Record',
            'user_id': self.test_user.id,
        })
        
        # Assertions
        self.assertEqual(record.name, 'Test Record')
        self.assertEqual(record.user_id, self.test_user)
        self.assertEqual(record.state, 'draft')
        self.assertTrue(record.active)
    
    def test_computed_fields(self):
        """Test computed field calculations"""
        record = self.Model.create({
            'name': 'Test Record',
            'user_id': self.test_user.id,
        })
        
        # Add lines to test computation
        line1 = self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line 1',
            'amount': 100.0,
        })
        line2 = self.env['my.model.line'].create({
            'model_id': record.id,
            'name': 'Line 2', 
            'amount': 200.0,
        })
        
        # Test computed total
        self.assertEqual(record.total_amount, 300.0)
    
    def test_constraints_date_validation(self):
        """Test date constraint validation"""
        with self.assertRaises(ValidationError):
            self.Model.create({
                'name': 'Invalid Record',
                'user_id': self.test_user.id,
                'date_start': date.today() + timedelta(days=5),
                'date_end': date.today(),  # End before start - should fail
            })
    
    def test_workflow_state_changes(self):
        """Test business logic and state transitions"""
        record = self.Model.create({
            'name': 'Workflow Test',
            'user_id': self.test_user.id,
        })
        
        # Test initial state
        self.assertEqual(record.state, 'draft')
        
        # Test confirmation
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
        
        # Test completion
        record.action_done()
        self.assertEqual(record.state, 'done')
    
    def test_onchange_methods(self):
        """Test onchange method behavior"""
        record = self.Model.new({
            'name': 'Onchange Test',
            'partner_id': self.test_partner.id,
        })
        
        # Trigger onchange
        record._onchange_partner_id()
        
        # Verify results (depends on your onchange logic)
        # self.assertEqual(record.some_field, expected_value)
```

### Running Tests

Execute tests with proper commands:

```bash
# Run all tests for a specific module
python odoo-bin -d test_db -i my_module --test-enable --stop-after-init

# Run specific test class
python odoo-bin -d test_db -i my_module --test-enable --stop-after-init \
    --test-tags /my_module

# Run tests in development mode for better debugging
python odoo-bin --dev=all -d test_db -i my_module --test-enable --stop-after-init
```

## Deployment

### Git Workflow Best Practices

**Branch Naming Convention:**

```bash
# Feature branches (prefix with version)
git checkout -b 18.0-add-inventory-management
git checkout -b 18.0-improve-user-interface

# Bug fix branches
git checkout -b 18.0-fix-calculation-error
git checkout -b 18.0-fix-security-issue

# Hotfix branches
git checkout -b 18.0-hotfix-critical-bug
```

**Commit Message Format:**

```bash
# Standard Odoo commit message format
git commit -m "[TAG] module_name: brief description

Detailed description of changes:
- Added feature X with proper validation
- Fixed issue Y in calculation method
- Updated security rules for new functionality
- Added unit tests for edge cases

Closes: #123"

# TAG examples:
# [ADD] - New features
# [IMP] - Improvements
# [FIX] - Bug fixes
# [REM] - Removals
# [REF] - Refactoring
```

### Pre-deployment Validation

Create validation script:

```bash
#!/bin/bash
echo "=== Odoo 18 Module Validation ==="

# Check Python syntax
echo "Checking Python syntax..."
find . -name "*.py" -exec python -m py_compile {} \;

# Check XML syntax
echo "Checking XML syntax..."
find . -name "*.xml" -exec xmllint --noout {} \;

# Run module tests
echo "Running module tests..."
python odoo-bin -d test_db -i my_module --test-enable --stop-after-init

# Check for common issues
echo "Checking for common issues..."
grep -r "print(" . --include="*.py" && echo "WARNING: Print statements found"
grep -r "TODO\|FIXME" . --include="*.py" && echo "WARNING: TODO/FIXME comments found"

echo "Validation completed!"
```

### Production Configuration

Create production-ready `odoo.conf`:

```ini
[options]
# Basic configuration
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom-addons
data_dir = /opt/odoo/.local/share/Odoo
admin_passwd = your_secure_admin_password

# Database configuration
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_secure_db_password
db_maxconn = 64

# Security
list_db = False
proxy_mode = True

# Performance
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

# Logging
logfile = /var/log/odoo/odoo.log
log_level = info
log_db = False
log_db_level = warning
```

## Common Patterns & Examples

### State Machine Implementation

```python
class DocumentWorkflow(models.Model):
    _name = 'document.workflow'
    _description = 'Document with Workflow'
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True, required=True)
    
    def action_submit(self):
        """Submit document for review"""
        if self.state != 'draft':
            raise ValidationError("Only draft documents can be submitted")
        self.write({'state': 'submitted'})
        self._send_notification('submitted')
    
    def action_start_review(self):
        """Start review process"""
        self.write({'state': 'under_review'})
        self._send_notification('under_review')
    
    def action_approve(self):
        """Approve document"""
        self.write({'state': 'approved'})
        self._send_notification('approved')
    
    def action_reject(self, reason=None):
        """Reject document with reason"""
        self.write({'state': 'rejected'})
        if reason:
            self.message_post(body=f"Rejection reason: {reason}")
        self._send_notification('rejected')
    
    def _send_notification(self, transition):
        """Send notification based on state transition"""
        # Implementation depends on requirements
        pass
```

### Abstract Mixin Pattern

```python
class AuditMixin(models.AbstractModel):
    """Mixin to add audit fields to any model"""
    _name = 'audit.mixin'
    _description = 'Audit Trail Mixin'
    
    # Audit fields
    created_by = fields.Many2one(
        'res.users', 
        'Created by', 
        default=lambda self: self.env.user,
        readonly=True
    )
    created_on = fields.Datetime(
        'Created on', 
        default=fields.Datetime.now,
        readonly=True
    )
    modified_by = fields.Many2one(
        'res.users', 
        'Last Modified by',
        readonly=True
    )
    modified_on = fields.Datetime(
        'Last Modified on',
        readonly=True
    )
    
    @api.model
    def create(self, vals):
        vals.update({
            'created_by': self.env.user.id,
            'created_on': fields.Datetime.now(),
        })
        return super().create(vals)
    
    def write(self, vals):
        vals.update({
            'modified_by': self.env.user.id,
            'modified_on': fields.Datetime.now(),
        })
        return super().write(vals)
```

### RESTful API Controller

```python
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class APIController(http.Controller):
    
    @http.route('/api/v1/my-model', auth='user', methods=['GET'], csrf=False)
    def get_records(self, **kwargs):
        """Get records with pagination and filtering"""
        try:
            domain = []
            
            # Parse query parameters
            limit = int(kwargs.get('limit', 20))
            offset = int(kwargs.get('offset', 0))
            
            if kwargs.get('state'):
                domain.append(('state', '=', kwargs.get('state')))
            
            # Search records
            records = request.env['my.model'].search(
                domain, 
                limit=limit, 
                offset=offset,
                order='id desc'
            )
            
            # Format response
            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'name': record.name,
                    'state': record.state,
                    'total_amount': record.total_amount,
                    'user_id': record.user_id.id if record.user_id else None,
                })
            
            response = {
                'status': 'success',
                'data': data,
                'total': len(data),
                'limit': limit,
                'offset': offset,
            }
            
            return request.make_response(
                json.dumps(response),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            _logger.error(f"API Error: {str(e)}")
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
    
    @http.route('/api/v1/my-model', auth='user', methods=['POST'], csrf=False)
    def create_record(self, **kwargs):
        """Create new record via API"""
        try:
            data = json.loads(request.httprequest.data)
            
            # Validate required fields
            if not data.get('name'):
                raise ValueError("Name is required")
            
            # Create record
            record = request.env['my.model'].create(data)
            
            response = {
                'status': 'success',
                'data': {
                    'id': record.id,
                    'name': record.name,
                    'state': record.state,
                }
            }
            
            return request.make_response(
                json.dumps(response),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            _logger.error(f"API Creation Error: {str(e)}")
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': str(e)
                }),
                status=400,
                headers={'Content-Type': 'application/json'}
            )
```

## Troubleshooting Common Issues

### Module Loading Problems

**Issue: Module not appearing in Apps list**

Solution checklist:

1. Verify `__manifest__.py` syntax
2. Check module path in `addons_path`
3. Restart Odoo server
4. Update Apps list
5. Check server logs for errors

```bash
# Debug module loading
python odoo-bin --dev=all -d mydb --log-level=debug
```

**Issue: Import errors in Python**

Common causes and solutions:

```python
# ❌ Wrong: Missing __init__.py files
# Ensure all directories have __init__.py

# ❌ Wrong: Circular imports
# Restructure imports to avoid circular dependencies

# ✅ Correct: Proper import structure in __init__.py
from . import models
from . import controllers
from . import wizard
```

### Database and ORM Issues

**Issue: Field not appearing in database**

Solutions:

1. Update module after field addition
2. Check field definition syntax
3. Verify module dependencies

```bash
# Update module after changes
python odoo-bin -d mydb -u my_module
```

**Issue: Constraint validation errors**

Debug constraint issues:

```python
# Add debugging to constraint methods
@api.constrains('field_name')
def _check_field(self):
    for record in self:
        _logger.info(f"Checking record {record.id}: {record.field_name}")
        if not self._validate_field(record.field_name):
            raise ValidationError("Validation failed")
```

### Performance Optimization

**Identify Performance Issues:**

```python
# Add performance monitoring
import time
import logging

_logger = logging.getLogger(__name__)

@api.depends('line_ids.amount')
def _compute_total(self):
    start_time = time.time()
    
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
    
    elapsed = time.time() - start_time
    if elapsed > 1.0:  # Log slow computations
        _logger.warning(f"Slow computation in _compute_total: {elapsed:.2f}s")
```

**Optimize Database Queries:**

```python
# ❌ Inefficient: Multiple database queries
def bad_method(self):
    for record in self:
        partner = record.partner_id
        orders = partner.order_ids  # N+1 query problem

# ✅ Efficient: Prefetch related data
def good_method(self):
    # Prefetch related data
    self.mapped('partner_id.order_ids')
    
    for record in self:
        partner = record.partner_id
        orders = partner.order_ids  # Data already cached
```

## Additional Resources and Learning Path

### Recommended Learning Sequence

1. **Start with Basics**
   - Complete Odoo development tutorial
   - Create simple models and views
   - Practice with AI assistance

2. **Intermediate Development**
   - Complex business logic
   - Custom workflows
   - API development

3. **Advanced Topics**
   - Performance optimization
   - Custom widgets
   - Module migrations

### Essential Documentation Links

- [Odoo 18 Developer Documentation](https://www.odoo.com/documentation/18.0/developer/)
- [Odoo Community Guidelines](https://www.odoo.com/forum/)
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot)
- [Python Development in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)

### Community Resources

- **Odoo Community Association (OCA)**: Best practices and modules
- **Odoo Forums**: Community support and discussions
- **GitHub Repositories**: Open source modules for reference
- **YouTube Channels**: Video tutorials and webinars

### Development Tools Integration

**Recommended VS Code Extensions:**

- GitHub Copilot & Copilot Chat
- Python (Microsoft)
- Pylint
- Black Formatter  
- XML Tools
- GitLens
- Odoo Snippets

**External Tools:**

- **pgAdmin**: PostgreSQL database management
- **Postman**: API testing
- **Docker**: Containerized development
- **Nginx**: Reverse proxy for production

## Conclusion

This guide provides a comprehensive foundation for AI-assisted Odoo 18 development. Key takeaways:

### Remember These Principles

1. **AI as Assistant**: Use AI to accelerate learning and development, but always validate generated code
2. **Follow Standards**: Adhere to Odoo coding guidelines and best practices
3. **Test Thoroughly**: Write comprehensive tests for all functionality
4. **Security First**: Implement proper access controls and data validation
5. **Performance Matters**: Optimize queries and avoid heavy computations
6. **Documentation**: Document your code and business logic clearly

### Next Steps for Success

1. **Setup Development Environment** following this guide
2. **Start Small** with simple modules using AI assistance
3. **Practice Regularly** to build familiarity with patterns
4. **Join Community** to learn from experienced developers
5. **Contribute Back** by sharing knowledge and improvements

### Final Reminder

AI tools like GitHub Copilot are powerful assistants that can significantly accelerate Odoo development. However, understanding Odoo's architecture, business logic, and best practices remains essential for building robust, maintainable applications. Always review AI-generated code, test thoroughly, and follow established guidelines.

Happy coding with Odoo 18 and AI assistance! 🚀
