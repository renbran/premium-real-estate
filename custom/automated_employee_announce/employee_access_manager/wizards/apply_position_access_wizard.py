from odoo import models, fields, api
from odoo.exceptions import UserError

class ApplyPositionAccessWizard(models.TransientModel):
    _name = 'apply.position.access.wizard'
    _description = 'Wizard to apply access rights based on employee positions'

    position_id = fields.Many2one('hr.employee.position', string='Position', required=True)
    user_ids = fields.Many2many('res.users', string='Users', required=True)

    def apply_access(self):
        if not self.user_ids:
            raise UserError("Please select at least one user to apply access rights.")

        for user in self.user_ids:
            # Logic to apply access rights based on the selected position
            access_template = self.position_id.access_template_id
            if access_template:
                user.groups_id = [(4, group.id) for group in access_template.group_ids]
        
        return {'type': 'ir.actions.act_window_close'}