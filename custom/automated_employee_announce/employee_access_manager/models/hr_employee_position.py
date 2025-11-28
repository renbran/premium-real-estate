from odoo import models, fields

class HREmployeePosition(models.Model):
    _name = 'hr.employee.position'
    _description = 'Employee Position'

    name = fields.Char(string='Position Name', required=True)
    access_rights = fields.Many2many('ir.model.access', string='Access Rights')