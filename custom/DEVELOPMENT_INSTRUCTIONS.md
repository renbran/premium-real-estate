# Odoo 18 Development Instructions & Guide

## Quick Start Instructions

### 1. Environment Setup

**Prerequisites Installation:**

```bash
# Install Python 3.8+
python --version  # Verify Python 3.8+

# Install PostgreSQL 12+
# Windows: Download from https://www.postgresql.org/download/windows/
# Create database user
psql -U postgres
CREATE USER odoo WITH CREATEDB NOCREATEROLE SUPERUSER;
\password odoo
```

**Odoo 18 Setup:**

```bash
# Clone Odoo 18
git clone https://github.com/odoo/odoo.git -b 18.0 --depth 1
cd odoo

# Install dependencies
pip install -r requirements.txt

# Create development structure
mkdir -p ~/odoo-dev/custom-addons
mkdir -p ~/odoo-dev/config
```

**Development Environment Structure:**

```text
~/odoo-dev/
├── odoo/                 # Odoo core source
├── enterprise/           # Enterprise modules (optional)
├── custom-addons/        # Your custom modules
├── data/                 # Database backups
└── config/
    └── odoo.conf        # Configuration file
```

### 2. VS Code & Copilot Configuration

**Install Essential Extensions:**
```bash
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension ms-python.black-formatter
```

**Create `.vscode/settings.json`:**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "github.copilot.enable": {
        "*": true,
        "python": true,
        "javascript": true,
        "xml": true
    },
    "files.associations": {
        "*.xml": "xml",
        "*.py": "python"
    }
}
```

## Development Workflow

### Phase 1: Module Creation

**1. Scaffold New Module:**
```bash
./odoo-bin scaffold my_custom_app ~/odoo-dev/custom-addons/
```

**2. Module Structure (Standard):**
```
my_custom_app/
├── __init__.py                 # Package initialization
├── __manifest__.py            # Module manifest
├── controllers/               # Web controllers
├── data/                      # Data files
├── demo/                      # Demo data
├── i18n/                      # Translations
├── models/                    # Python models
├── security/                  # Security rules
├── static/                    # Static assets
├── views/                     # XML views
├── wizard/                    # Transient models
└── tests/                     # Unit tests
```

### Phase 2: Model Development

**AI Prompt for Model Creation:**
```
Create an Odoo 18 model for [business domain] with:
- Models for [entity1], [entity2]
- Proper inheritance from mail.thread
- Fields: [list specific fields with types]
- Computed fields with dependencies
- Validation constraints
- Business methods for workflow
- Follow Odoo coding guidelines
```

**Model Template:**
```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, id desc'
    
    # Basic fields
    name = fields.Char('Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Html('Description')
    
    # Relational fields
    user_id = fields.Many2one('res.users', 'Responsible User', tracking=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    
    # Selection field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)
    
    # Computed fields
    total_amount = fields.Float('Total', compute='_compute_total', store=True)
    
    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if len(record.name) < 3:
                raise ValidationError("Name must be at least 3 characters long")
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_done(self):
        self.write({'state': 'done'})
```

### Phase 3: View Development

**Form View Template:**
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
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <div class="oe_title">
                    <h1>
                        <field name="name" placeholder="Enter name..."/>
                    </h1>
                </div>
                <group>
                    <group>
                        <field name="user_id" widget="many2one_avatar_user"/>
                        <field name="partner_id"/>
                    </group>
                    <group>
                        <field name="total_amount" widget="monetary"/>
                        <field name="active"/>
                    </group>
                </group>
                <notebook>
                    <page string="Description">
                        <field name="description" widget="html"/>
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

**Tree View Template:**
```xml
<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree>
            <field name="name"/>
            <field name="user_id" widget="many2one_avatar_user"/>
            <field name="partner_id"/>
            <field name="total_amount" widget="monetary"/>
            <field name="state" widget="badge" 
                   decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"
                   decoration-muted="state == 'draft'"/>
        </tree>
    </field>
</record>
```

### Phase 4: Security Implementation

**Access Rights (security/ir.model.access.csv):**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

**Record Rules (security/security.xml):**
```xml
<odoo>
    <data noupdate="1">
        <record id="rule_my_model_user" model="ir.rule">
            <field name="name">My Model: User Access</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        </record>
    </data>
</odoo>
```

## Essential Do's and Don'ts

### ✅ DO's

**Model Development:**
```python
# ✅ DO: Use proper model structure
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'Always provide description'
    _inherit = ['mail.thread']
    _order = 'name, id desc'

# ✅ DO: Use @api.depends for computed fields
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))

# ✅ DO: Use proper field attributes
name = fields.Char('Name', required=True, tracking=True, help="Enter name")

# ✅ DO: Use constraints for validation
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for record in self:
        if record.start_date and record.end_date and record.start_date > record.end_date:
            raise ValidationError("Start date must be before end date")
```

**View Development:**
```xml
<!-- ✅ DO: Use proper view structure -->
<record id="view_model_form" model="ir.ui.view">
    <field name="name">model.name.form</field>
    <field name="model">model.name</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <!-- Form content -->
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### ❌ DON'Ts

**Avoid Deprecated Syntax:**
```python
# ❌ DON'T: Use old API (deprecated)
def old_create(self, cr, uid, vals, context=None):
    return super().create(cr, uid, vals, context=context)

# ❌ DON'T: Use @api.one (deprecated)
@api.one
def my_method(self):
    return self.name

# ❌ DON'T: Use direct SQL without escaping
self.env.cr.execute("SELECT * FROM table WHERE id = %s" % record_id)

# ❌ DON'T: Ignore empty recordsets
def _compute_total(self):
    self.total = sum(self.line_ids.mapped('amount'))  # Fails on empty
```

## AI Prompting Strategies

### Effective Prompts

**For Model Generation:**
```
Create an Odoo 18 model for [domain] with:
- Proper inheritance from mail.thread
- Fields: [list specific fields with types]
- Computed fields with dependencies
- Validation constraints
- Business methods for workflow
- Follow Odoo coding guidelines
```

**For View Generation:**
```
Generate Odoo 18 XML views for model [model_name]:
- List view with filters and search
- Form view with proper layout and widgets
- Kanban view with drag-drop functionality
- Include proper field widgets and options
```

**For Debugging:**
```
Debug this Odoo error:
[paste error traceback]

Context: 
- Odoo 18.0
- Custom module: [module_name]
- Trying to: [describe what you were doing]
```

### Context-Aware Development
Always provide context to Copilot:

```python
# Context comment for AI
# This is an Odoo 18 model for inventory management
# Inherits from stock.picking for warehouse operations
# Needs integration with accounting module
# Must follow Odoo security patterns
```

## Testing & Quality Assurance

### Unit Test Template
```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestMyModel(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Model = self.env['my.model']
        
    def test_model_creation(self):
        """Test basic model creation"""
        record = self.Model.create({
            'name': 'Test Record',
        })
        self.assertEqual(record.name, 'Test Record')
        self.assertEqual(record.state, 'draft')
    
    def test_constraints(self):
        """Test validation constraints"""
        with self.assertRaises(ValidationError):
            self.Model.create({
                'name': 'AB',  # Too short, should fail
            })
```

### Running Tests
```bash
# Run specific test
python odoo-bin -d test_db -i my_module --test-enable --stop-after-init

# Run all tests for module
python odoo-bin -d test_db -u my_module --test-enable --stop-after-init
```

## Deployment Instructions

### Git Workflow

**Branch Naming Convention:**
```bash
# Feature branch
git checkout -b 18.0-add-inventory-module

# Bug fix branch  
git checkout -b 18.0-fix-calculation-error
```

**Commit Message Format:**
```bash
git commit -m "[TAG] module: description

- Added feature X
- Fixed issue Y
- Updated documentation"

# TAG examples: [ADD], [IMP], [FIX], [REM], [REF]
```

### Pre-deployment Checklist

1. **Code Quality:**
   - [ ] All tests passing
   - [ ] No linting errors
   - [ ] Proper documentation
   - [ ] Security rules implemented

2. **Module Validation:**
   - [ ] XML syntax valid
   - [ ] Python syntax valid
   - [ ] Dependencies correctly declared
   - [ ] Access rights configured

3. **Performance:**
   - [ ] No heavy computations in loops
   - [ ] Proper database indexes
   - [ ] Efficient queries

### Production Configuration
```python
# odoo.conf for production
[options]
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom-addons
data_dir = /opt/odoo/.local/share/Odoo
admin_passwd = [secure_password]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = [secure_password]
logfile = /var/log/odoo/odoo.log
log_level = info
workers = 4
max_cron_threads = 2
```

## Common Patterns & Examples

### State Machine Pattern
```python
class DocumentWorkflow(models.Model):
    _name = 'document.workflow'
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)
    
    def action_submit(self):
        self.write({'state': 'submitted'})
    
    def action_approve(self):
        self.write({'state': 'approved'})
    
    def action_reject(self):
        self.write({'state': 'rejected'})
```

### Mixin Pattern
```python
class TimestampMixin(models.AbstractModel):
    _name = 'timestamp.mixin'
    _description = 'Timestamp Mixin'
    
    created_date = fields.Datetime('Created Date', default=fields.Datetime.now)
    modified_date = fields.Datetime('Modified Date')
    
    @api.model
    def create(self, vals):
        vals['created_date'] = fields.Datetime.now()
        return super().create(vals)
    
    def write(self, vals):
        vals['modified_date'] = fields.Datetime.now()
        return super().write(vals)
```

### RESTful API Controller
```python
from odoo import http
from odoo.http import request
import json

class APIController(http.Controller):
    
    @http.route('/api/v1/records', auth='user', methods=['GET'], csrf=False)
    def get_records(self, **kwargs):
        records = request.env['my.model'].search([])
        return request.make_response(
            json.dumps([{
                'id': record.id,
                'name': record.name,
                'state': record.state,
            } for record in records]),
            headers={'Content-Type': 'application/json'}
        )
```

## Troubleshooting

### Common Issues

1. **Module not loading:**
   - Check `__manifest__.py` syntax
   - Verify dependencies are installed
   - Check file permissions

2. **Import errors:**
   - Verify `__init__.py` files exist
   - Check import statements
   - Ensure proper module structure

3. **Database errors:**
   - Check field definitions
   - Verify constraint syntax
   - Review access rights

### Debugging Commands
```bash
# Start Odoo in development mode
python odoo-bin --dev=all -d mydb -i my_module

# Update module
python odoo-bin -d mydb -u my_module

# Install module
python odoo-bin -d mydb -i my_module
```

## Next Steps

1. **Setup Development Environment**
2. **Practice with Small Modules**
3. **Learn Advanced Patterns**
4. **Explore Integration Options**
5. **Contribute to Community**

## Additional Resources

- [Odoo 18 Official Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo Community Forums](https://www.odoo.com/forum/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [VS Code Python Development](https://code.visualstudio.com/docs/python/python-tutorial)

Remember: AI is a powerful assistant, but understanding Odoo's architecture and business logic remains crucial for successful development. Always validate AI-generated code and test thoroughly.
