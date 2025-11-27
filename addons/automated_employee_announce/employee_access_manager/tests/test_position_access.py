from odoo.tests import TransactionCase
from odoo.exceptions import AccessError

class TestPositionAccess(TransactionCase):

    def setUp(self):
        super(TestPositionAccess, self).setUp()
        # Create test positions
        self.sales_admin_position = self.env['hr.employee.position'].create({
            'name': 'Sales Admin',
            'access_rights': ['read', 'write', 'create']
        })
        self.accountant_position = self.env['hr.employee.position'].create({
            'name': 'Accountant',
            'access_rights': ['read', 'write']
        })
        self.cfo_position = self.env['hr.employee.position'].create({
            'name': 'CFO',
            'access_rights': ['read', 'write', 'create', 'delete']
        })
        self.ceo_position = self.env['hr.employee.position'].create({
            'name': 'CEO',
            'access_rights': ['read', 'write', 'create', 'delete']
        })

        # Create test users
        self.sales_admin_user = self.env['res.users'].create({
            'name': 'Sales Admin User',
            'login': 'sales_admin',
            'employee_id': self.sales_admin_position.id,
        })
        self.accountant_user = self.env['res.users'].create({
            'name': 'Accountant User',
            'login': 'accountant',
            'employee_id': self.accountant_position.id,
        })

    def test_sales_admin_access(self):
        self.assertTrue(self.sales_admin_user.has_group('employee_access_manager.group_sales_admin'))
        # Test access rights for Sales Admin
        with self.assertRaises(AccessError):
            self.env['some.model'].create({'field': 'value'}, user=self.accountant_user.id)

    def test_accountant_access(self):
        self.assertTrue(self.accountant_user.has_group('employee_access_manager.group_accountant'))
        # Test access rights for Accountant
        self.env['some.model'].create({'field': 'value'}, user=self.accountant_user.id)

    def test_cfo_access(self):
        self.assertTrue(self.cfo_position.access_rights, 'CFO should have full access rights')

    def test_ceo_access(self):
        self.assertTrue(self.ceo_position.access_rights, 'CEO should have full access rights')