# Odoo 18 Development - Quick Setup Guide

This is a streamlined guide for setting up Odoo 18 development with AI assistance using VS Code Copilot.

## 🚀 Quick Setup (30 minutes)

### Step 1: Prerequisites Installation

```bash
# Verify Python 3.8+
python --version

# Install PostgreSQL and create user
# Windows: Download from https://www.postgresql.org/download/windows/
psql -U postgres
CREATE USER odoo WITH CREATEDB NOCREATEROLE SUPERUSER;
\password odoo
\q
```

### Step 2: Odoo 18 Installation

```bash
# Clone Odoo 18
git clone https://github.com/odoo/odoo.git -b 18.0 --depth 1
cd odoo
pip install -r requirements.txt

# Create development structure
mkdir -p ~/odoo-dev/custom-addons ~/odoo-dev/config
```

### Step 3: VS Code Setup

Install extensions:

```bash
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
code --install-extension ms-python.python
```

Create `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "github.copilot.enable": {
        "*": true,
        "python": true,
        "xml": true
    },
    "files.associations": {
        "*.xml": "xml",
        "*.py": "python"
    }
}
```

### Step 4: Test Installation

```bash
# Start Odoo
python odoo-bin --addons-path=addons,~/odoo-dev/custom-addons -d mydb --dev=all

# Access: http://localhost:8069
```

## 📋 Essential Templates

### Module Manifest (`__manifest__.py`)

```python
{
    'name': 'My Module',
    'version': '18.0.1.0.0',
    'summary': 'Brief description',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
```

### Basic Model Template

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread']
    
    name = fields.Char('Name', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft', tracking=True)
    
    amount = fields.Float('Amount')
    total = fields.Float('Total', compute='_compute_total', store=True)
    
    @api.depends('amount')
    def _compute_total(self):
        for record in self:
            record.total = record.amount * 1.2
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError("Amount must be positive")
    
    def action_done(self):
        self.state = 'done'
```

### Basic Form View

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_done" string="Mark Done" 
                        type="object" states="draft"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="amount"/>
                    <field name="total"/>
                </group>
            </sheet>
            <div class="oe_chatter">
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### Security Template (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
```

## 🤖 AI Prompting Guide

### Effective AI Prompts

**For Model Creation:**
```text
Create an Odoo 18 model for [domain] with:
- Fields: [list fields with types]
- Inherit from mail.thread
- Add computed fields with @api.depends
- Include validation with @api.constrains
- Follow Odoo best practices
```

**For View Creation:**
```text
Create Odoo 18 views for model [model_name]:
- Form view with header/sheet/chatter structure
- Tree view with proper widgets
- Search view with filters
```

**For Debugging:**
```text
Debug this Odoo error: [paste error]
Context: Odoo 18, module [name], trying to [action]
```

## ✅ DO's and ❌ DON'Ts

### ✅ Modern Practices (Odoo 18)

```python
# ✅ Use new API
@api.depends('field')
def _compute_something(self):
    for record in self:
        record.computed_field = record.field * 2

# ✅ Proper model structure
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'Description'
    _inherit = ['mail.thread']
```

### ❌ Deprecated Practices (Avoid)

```python
# ❌ Old API (deprecated)
def old_method(self, cr, uid, context=None):
    pass

# ❌ @api.one (deprecated)
@api.one
def bad_method(self):
    pass
```

## 🧪 Testing Template

```python
from odoo.tests.common import TransactionCase

class TestMyModel(TransactionCase):
    
    def test_basic_creation(self):
        record = self.env['my.model'].create({
            'name': 'Test',
            'amount': 100,
        })
        self.assertEqual(record.total, 120)
        self.assertEqual(record.state, 'draft')
```

## 🚀 Common Commands

```bash
# Start development server
python odoo-bin --dev=all -d mydb

# Install module
python odoo-bin -d mydb -i my_module

# Update module
python odoo-bin -d mydb -u my_module

# Run tests
python odoo-bin -d test_db -i my_module --test-enable --stop-after-init
```

## 📚 Quick Reference

### Field Types
- `Char('Name')` - Text field
- `Text('Description')` - Large text
- `Html('Content')` - HTML content
- `Integer('Count')` - Number
- `Float('Amount', digits=(16,2))` - Decimal
- `Boolean('Active', default=True)` - Checkbox
- `Date('Date')` - Date picker
- `Datetime('Timestamp')` - Date/time
- `Selection([('a','A'), ('b','B')])` - Dropdown
- `Many2one('res.partner')` - Link to record
- `One2many('model', 'field')` - Child records
- `Many2many('model')` - Multiple links

### Common Widgets
- `widget="date"` - Date picker
- `widget="monetary"` - Currency format
- `widget="priority"` - Star rating
- `widget="statusbar"` - Status bar
- `widget="many2one_avatar_user"` - User with avatar
- `widget="badge"` - Colored badge

### Decorations (Tree View)
- `decoration-success="state=='done'"` - Green
- `decoration-info="state=='draft'"` - Blue
- `decoration-danger="amount < 0"` - Red
- `decoration-muted="active==False"` - Gray

## 🔧 Troubleshooting

### Module not loading?
1. Check `__manifest__.py` syntax
2. Restart Odoo server
3. Check server logs
4. Update Apps list

### Field not showing?
1. Update module after changes
2. Check field definition
3. Verify view XML syntax

### Permission errors?
1. Check `ir.model.access.csv`
2. Verify user groups
3. Add record rules if needed

## 🎯 Next Steps

1. **Practice**: Create simple module with AI help
2. **Learn**: Study existing modules
3. **Test**: Write unit tests
4. **Deploy**: Setup production environment
5. **Contribute**: Share with community

## 📖 Resources

- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [Odoo Community](https://www.odoo.com/forum/)

---

**💡 Pro Tip**: Always use AI assistance with proper context and validate generated code against Odoo guidelines!
