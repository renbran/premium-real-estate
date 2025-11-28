# Odoo 18 Development Cheat Sheet

## 🏗️ Module Structure

```text
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── views.xml
├── security/
│   └── ir.model.access.csv
├── data/
├── demo/
├── static/
└── tests/
```

## 📋 Essential Files

### `__manifest__.py`

```python
{
    'name': 'Module Name',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
```

### `models/__init__.py`

```python
from . import my_model
```

### `__init__.py`

```python
from . import models
```

## 🗃️ Model Patterns

### Basic Model

```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread']
    _order = 'name'
    
    name = fields.Char('Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True)
```

### Field Types Reference

```python
# Basic fields
name = fields.Char('Name', size=100, required=True)
description = fields.Text('Description')
content = fields.Html('Content')
count = fields.Integer('Count', default=0)
amount = fields.Float('Amount', digits=(16, 2))
is_active = fields.Boolean('Active', default=True)

# Date fields
date_field = fields.Date('Date', default=fields.Date.today)
datetime_field = fields.Datetime('DateTime', default=fields.Datetime.now)

# Selection field
state = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
], default='draft')

# Relational fields
partner_id = fields.Many2one('res.partner', 'Partner')
line_ids = fields.One2many('my.model.line', 'parent_id', 'Lines')
tag_ids = fields.Many2many('my.model.tag', string='Tags')

# Computed field
total = fields.Float('Total', compute='_compute_total', store=True)
```

### Computed Fields

```python
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

### Constraints

```python
@api.constrains('amount')
def _check_amount(self):
    for record in self:
        if record.amount < 0:
            raise ValidationError("Amount must be positive")
```

### Onchange Methods

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    if self.partner_id:
        self.email = self.partner_id.email
```

## 🖼️ View Templates

### Form View

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_confirm" string="Confirm" 
                        type="object" class="btn-primary"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="partner_id"/>
                    <field name="amount" widget="monetary"/>
                </group>
            </sheet>
            <div class="oe_chatter">
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### Tree View

```xml
<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree decoration-success="state == 'done'">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="amount"/>
            <field name="state" widget="badge"/>
        </tree>
    </field>
</record>
```

### Search View

```xml
<record id="view_my_model_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search>
            <field name="name"/>
            <filter name="active" string="Active" 
                    domain="[('active', '=', True)]"/>
            <group string="Group By">
                <filter name="group_state" string="State" 
                        context="{'group_by': 'state'}"/>
            </group>
        </search>
    </field>
</record>
```

## 🔒 Security Templates

### Access Rights (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

### Record Rules

```xml
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: User Access</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## 🧪 Testing Template

```python
from odoo.tests.common import TransactionCase

class TestMyModel(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Model = self.env['my.model']
    
    def test_create(self):
        record = self.Model.create({'name': 'Test'})
        self.assertEqual(record.name, 'Test')
```

## 🎨 Widget Reference

### Form Widgets

```xml
<field name="amount" widget="monetary"/>
<field name="date" widget="date"/>
<field name="datetime" widget="datetime"/>
<field name="priority" widget="priority"/>
<field name="user_id" widget="many2one_avatar_user"/>
<field name="state" widget="statusbar"/>
<field name="tags" widget="many2many_tags"/>
<field name="description" widget="html"/>
<field name="image" widget="image"/>
```

### Tree Decorations

```xml
<tree decoration-success="state == 'done'"
      decoration-info="state == 'draft'"
      decoration-danger="amount < 0"
      decoration-muted="active == False">
```

## 🤖 AI Prompting Templates

### Model Generation

```text
Create an Odoo 18 model for [domain] with:
- Inherit from mail.thread
- Fields: [field1: type, field2: type]
- Computed field [name] based on [fields]
- Constraint to validate [condition]
- Business methods for [actions]
```

### View Generation

```text
Generate Odoo 18 views for [model] with:
- Form view with header/sheet structure
- Tree view with decorations
- Search with filters for [criteria]
- Use appropriate widgets
```

## ⚡ Common Commands

```bash
# Development server
python odoo-bin --dev=all -d mydb --addons-path=addons,custom-addons

# Install module
python odoo-bin -d mydb -i my_module

# Update module
python odoo-bin -d mydb -u my_module

# Run tests
python odoo-bin -d test_db -i my_module --test-enable --stop-after-init
```

## 🔧 Debugging

### Add Debug Logging

```python
import logging
_logger = logging.getLogger(__name__)

def my_method(self):
    _logger.info('Debug message: %s', self.name)
```

### Common Issues

#### Module not loading

1. Check `__manifest__.py` syntax
2. Verify `__init__.py` files exist
3. Restart Odoo server
4. Check logs for errors

#### Field not showing

1. Update module after changes
2. Check field definition syntax
3. Clear browser cache

## 📊 Performance Tips

### Efficient Queries

```python
# ❌ Inefficient
for record in records:
    partner = record.partner_id  # N+1 queries

# ✅ Efficient  
records.mapped('partner_id')  # Prefetch
for record in records:
    partner = record.partner_id  # Cached
```

### Batch Operations

```python
# ❌ Slow
for record in records:
    record.write({'processed': True})

# ✅ Fast
records.write({'processed': True})
```

## 🔄 Migration Helpers

### Old to New API

```python
# ❌ Old API (deprecated)
def old_method(self, cr, uid, ids, context=None):
    pass

# ✅ New API
@api.model
def new_method(self):
    pass
```

## 📚 Quick Reference

### Domain Operators

```python
# Comparison
('field', '=', 'value')
('amount', '>', 100)
('name', 'like', 'pattern%')
('id', 'in', [1, 2, 3])

# Logical
('field1', '=', 'a'), ('field2', '=', 'b')  # AND
[('field1', '=', 'a'), '|', ('field2', '=', 'b')]  # OR
('field', '!=', 'value')  # NOT EQUAL
```

### Context Keys

```python
# Common context keys
'active_id': current_record_id,
'active_ids': [record_ids],
'active_model': 'model.name',
'default_field': 'value',  # Default value
'search_default_filter': True,  # Activate filter
```

## 🎯 Best Practices Checklist

- ✅ Always provide `_description` for models
- ✅ Use `tracking=True` for important fields
- ✅ Add proper constraints and validations
- ✅ Write unit tests for business logic
- ✅ Follow Odoo naming conventions
- ✅ Use proper field types and widgets
- ✅ Implement proper security rules
- ✅ Add help text for user fields

## 🚀 Module Development Flow

1. **Plan**: Define requirements and models
2. **Scaffold**: Create module structure  
3. **Models**: Define data models
4. **Views**: Create user interface
5. **Security**: Implement access controls
6. **Test**: Write and run tests
7. **Deploy**: Install and validate

---

**💡 Pro Tip**: Use GitHub Copilot with specific context about Odoo 18 patterns for better code suggestions!
