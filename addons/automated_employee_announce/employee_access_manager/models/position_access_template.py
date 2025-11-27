from odoo import models, fields

class PositionAccessTemplate(models.Model):
    _name = 'position.access.template'
    _description = 'Access Template for Employee Positions'

    name = fields.Char(string='Template Name', required=True)
    position_ids = fields.Many2many('hr.employee.position', string='Associated Positions')
    access_rights = fields.Text(string='Access Rights', help='Define the access rights associated with this template.')

    def apply_template(self, employee):
        """Apply the access rights defined in this template to the given employee."""
        if employee.position_id in self.position_ids:
            # Logic to apply access rights to the employee
            pass