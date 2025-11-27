from odoo import models, fields, api
from odoo.exceptions import UserError

class BulkAssignPositionWizard(models.TransientModel):
    _name = 'bulk.assign.position.wizard'
    _description = 'Bulk Assign Position Wizard'

    position_id = fields.Many2one('hr.employee.position', string='Position', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)

    def action_assign_access(self):
        if not self.employee_ids:
            raise UserError("Please select at least one employee.")
        
        for employee in self.employee_ids:
            employee.position_id = self.position_id
            # Here you can add logic to assign access rights based on the position
            # For example, you might call a method to apply access rights template

        return {'type': 'ir.actions.act_window_close'}