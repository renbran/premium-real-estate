from odoo import models, fields

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    employee_position_id = fields.Many2one(
        'hr.employee.position',
        string='Employee Position',
        help='Position of the employee for access rights management'
    )

    access_template_id = fields.Many2one(
        'position.access.template',
        string='Access Template',
        help='Access rights template associated with the employee position'
    )