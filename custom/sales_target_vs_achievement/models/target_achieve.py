from odoo import api, fields, models, _


class TargetAchieve(models.Model):
    """Target Achieve class to set the target and compute its achievement
    based on the span given for the CRM Team member, consultant, and manager"""
    _name = 'target.achieve'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Target Achieve'

    name = fields.Char(string='Name', compute='_compute_name', store=True,
                       help="Auto created name which is a combination"
                            " of Consultant, Manager, timespan, and team name.")
    consultant_id = fields.Many2one('res.partner', 
                                    string="Consultant", 
                                    tracking=True, 
                                    help="Consultant to whom the target is set.")
    manager_id = fields.Many2one('res.partner', 
                                 string="Manager", 
                                 tracking=True, 
                                 help="Manager to whom the target is set.")
    user_target = fields.Float('Target', required=True,
                               tracking=True,
                               help="Value for the personal target to reach.",
                               copy=False)
    time_span = fields.Selection(
        [('daily', 'Daily'),
         ('monthly', 'Monthly'),
         ('yearly', 'Yearly')], string='Time Span', default='monthly',
        required=True, tracking=True,
        help="The target can be set Daily/Monthly/Yearly with this field.")
    team_id = fields.Many2one('crm.team',
                              related='consultant_id.x_crm_team_id',  # Related to consultant's team
                              string="Sales Team",
                              help="Sales Team in which the consultant is a member.",
                              store=True)
    team_target = fields.Float(string="Team Target",
                               compute='_compute_team_target',
                               help="Auto calculated value of Sales team.")
    person_achieved_amt = fields.Float(string='Achieved Amount',
                                       store=True,
                                       compute_sudo=True,
                                       help="Calculated value from sale orders for each individual.",
                                       compute='_compute_achieved_amt')
    team_achieved_amt = fields.Float(string='Team Achieved Amount',
                                     store=True,
                                     compute_sudo=True,
                                     help="Calculated value from sale orders for the sales team.",
                                     compute='_compute_achieved_amt')
    currency_id = fields.Many2one('res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  help="Company currency to show the monetary field.")

    _sql_constraints = [
        ('unique_combination', 'unique (name)',
         "Similar Target for the same member already exists."),
        ('check_user_target',
         'CHECK(user_target > 0.0)',
         "The Target cannot be zero."),
    ]

    @api.depends('consultant_id', 'manager_id', 'user_target')
    def _compute_team_target(self):
        """Recalculate the team target based on the Consultant and Manager"""
        for rec in self:
            rec.team_target = 0.0  # Reset team target before calculating
            if rec.consultant_id:
                rec.team_target += rec.user_target  # Consultant's target is added
            if rec.manager_id:
                rec.team_target += rec.user_target  # Manager's target is added

    @api.depends('consultant_id', 'manager_id', 'time_span', 'team_id')
    def _compute_achieved_amt(self):
        """Compute the Achieved sales amount for each individual and team"""
        for rec in self:
            rec.person_achieved_amt = rec.team_achieved_amt = 0.0
            domain = [('state', '=', 'sale')]

            # Define the date filters based on the time_span
            if rec.time_span == 'daily':
                domain.append(('date_order', '>=', fields.Date.today()))
            elif rec.time_span == 'monthly':
                domain.append(('date_order', '>=', fields.Date.today().replace(day=1)))
            elif rec.time_span == 'yearly':
                domain.append(('date_order', '>=', fields.Date.today().replace(month=1, day=1)))

            orders = self.env['sale.order'].search(domain)

            # Compute achieved amount for consultant or manager
            for order in orders:
                if order.partner_id.id == rec.consultant_id.id:
                    rec.person_achieved_amt += order.amount_total
                if rec.manager_id and order.partner_id.id == rec.manager_id.id:
                    rec.person_achieved_amt += order.amount_total
                if order.team_id.id == rec.team_id.id:
                    rec.team_achieved_amt += order.amount_total

    @api.depends('consultant_id', 'manager_id', 'time_span', 'team_id')
    def _compute_name(self):
        """Compute the name to ensure the uniqueness of the target setting."""
        for record in self:
            record.name = f"{record.consultant_id.name if record.consultant_id else ''}" \
                          f"{record.manager_id.name if record.manager_id else ''}" \
                          f" : {record.team_id.name if record.team_id else ''}"

    def action_confirm(self):
        """Confirm the target setting and activate it."""
        for record in self:
            # Add any confirmation logic here
            # For now, we'll just ensure it's properly set up
            if record.user_target <= 0:
                raise models.ValidationError(_("Target amount must be greater than zero."))
        return True

    @api.ondelete(at_uninstall=False)
    def delete_record(self):
        """When a record is deleted, reset the team target."""
        for record in self:
            if record.team_id:
                record.team_id.update({
                    'team_target': record.team_id.team_target - record.user_target})
