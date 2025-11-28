# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PaymentWorkflowStage(models.Model):
    """
    Payment Workflow Stage Configuration
    
    Defines configurable workflow stages for payment approval process.
    Allows customization of approval workflow based on company needs.
    """
    _name = 'payment.workflow.stage'
    _description = 'Payment Workflow Stage'
    _order = 'sequence, id'
    _rec_name = 'name'
    
    # Basic information
    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True,
        help="Name of the workflow stage"
    )
    
    code = fields.Char(
        string='Stage Code',
        required=True,
        help="Technical code for the stage (must match payment state)"
    )
    
    description = fields.Text(
        string='Description',
        translate=True,
        help="Description of what happens in this stage"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of stages in the workflow"
    )
    
    # Visual settings
    color = fields.Integer(
        string='Color',
        default=1,
        help="Color for kanban view"
    )
    
    icon = fields.Char(
        string='Icon',
        default='fa-circle',
        help="FontAwesome icon class"
    )
    
    # Workflow configuration
    is_initial_stage = fields.Boolean(
        string='Initial Stage',
        default=False,
        help="Mark as the initial stage for new payments"
    )
    
    is_final_stage = fields.Boolean(
        string='Final Stage',
        default=False,
        help="Mark as a final stage (payment cannot progress further)"
    )
    
    allow_edit = fields.Boolean(
        string='Allow Edit',
        default=True,
        help="Allow editing payment details in this stage"
    )
    
    require_approval = fields.Boolean(
        string='Require Approval',
        default=False,
        help="Require explicit approval to move to next stage"
    )
    
    # Access control
    approval_group_ids = fields.Many2many(
        'res.groups',
        string='Approval Groups',
        help="Groups allowed to approve from this stage"
    )
    
    visibility_group_ids = fields.Many2many(
        'res.groups',
        'stage_visibility_group_rel',
        string='Visibility Groups',
        help="Groups that can see payments in this stage"
    )
    
    # Automation settings
    auto_advance = fields.Boolean(
        string='Auto Advance',
        default=False,
        help="Automatically advance to next stage when conditions are met"
    )
    
    auto_advance_condition = fields.Text(
        string='Auto Advance Condition',
        help="Python expression for auto advance condition"
    )
    
    send_notification = fields.Boolean(
        string='Send Notification',
        default=False,
        help="Send email notification when payment reaches this stage"
    )
    
    notification_template_id = fields.Many2one(
        'mail.template',
        string='Notification Template',
        help="Email template for notifications"
    )
    
    # Next stages
    next_stage_ids = fields.Many2many(
        'payment.workflow.stage',
        'payment_stage_transition_rel',
        'from_stage_id',
        'to_stage_id',
        string='Next Stages',
        help="Possible next stages from this stage"
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help="Company for which this stage is defined"
    )
    
    # Computed fields
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count',
        help="Number of payments currently in this stage"
    )
    
    @api.depends('code')
    def _compute_payment_count(self):
        """Compute number of payments in this stage"""
        for stage in self:
            if stage.code:
                count = self.env['account.payment'].search_count([
                    ('state', '=', stage.code),
                    ('company_id', '=', stage.company_id.id),
                ])
                stage.payment_count = count
            else:
                stage.payment_count = 0
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure stage code is unique per company"""
        for stage in self:
            if stage.code:
                existing = self.search([
                    ('code', '=', stage.code),
                    ('company_id', '=', stage.company_id.id),
                    ('id', '!=', stage.id),
                ])
                if existing:
                    raise ValidationError(
                        _("Stage code '%s' already exists for this company.") % stage.code
                    )
    
    @api.constrains('is_initial_stage')
    def _check_single_initial_stage(self):
        """Ensure only one initial stage per company"""
        for stage in self:
            if stage.is_initial_stage:
                existing = self.search([
                    ('is_initial_stage', '=', True),
                    ('company_id', '=', stage.company_id.id),
                    ('id', '!=', stage.id),
                ])
                if existing:
                    raise ValidationError(
                        _("Only one initial stage is allowed per company.")
                    )
    
    @api.constrains('auto_advance_condition')
    def _check_auto_advance_condition(self):
        """Validate auto advance condition syntax"""
        for stage in self:
            if stage.auto_advance_condition:
                try:
                    compile(stage.auto_advance_condition, '<string>', 'eval')
                except SyntaxError as e:
                    raise ValidationError(
                        _("Invalid auto advance condition syntax: %s") % str(e)
                    )
    
    @api.model
    def get_default_stages(self):
        """Get default workflow stages for a company"""
        default_stages = [
            {
                'name': _('Draft'),
                'code': 'draft',
                'sequence': 10,
                'is_initial_stage': True,
                'allow_edit': True,
                'icon': 'fa-pencil',
                'color': 7,  # Gray
            },
            {
                'name': _('Under Review'),
                'code': 'review',
                'sequence': 20,
                'require_approval': True,
                'allow_edit': False,
                'icon': 'fa-search',
                'color': 3,  # Orange
            },
            {
                'name': _('Approved'),
                'code': 'approve',
                'sequence': 30,
                'require_approval': True,
                'allow_edit': False,
                'icon': 'fa-check',
                'color': 4,  # Yellow
            },
            {
                'name': _('Authorized'),
                'code': 'authorize',
                'sequence': 40,
                'require_approval': True,
                'allow_edit': False,
                'icon': 'fa-key',
                'color': 1,  # Blue
            },
            {
                'name': _('Posted'),
                'code': 'post',
                'sequence': 50,
                'is_final_stage': True,
                'allow_edit': False,
                'icon': 'fa-check-circle',
                'color': 10,  # Green
            },
            {
                'name': _('Rejected'),
                'code': 'reject',
                'sequence': 60,
                'is_final_stage': True,
                'allow_edit': False,
                'icon': 'fa-times',
                'color': 2,  # Red
            },
        ]
        
        return default_stages
    
    @api.model
    def create_default_stages(self, company_id=None):
        """Create default workflow stages for a company"""
        if not company_id:
            company_id = self.env.company.id
        
        # Check if stages already exist
        existing_stages = self.search([('company_id', '=', company_id)])
        if existing_stages:
            return existing_stages
        
        # Create default stages
        default_stages = self.get_default_stages()
        created_stages = []
        
        for stage_data in default_stages:
            stage_data['company_id'] = company_id
            stage = self.create(stage_data)
            created_stages.append(stage)
        
        # Set up stage transitions
        self._setup_default_transitions(created_stages)
        
        return created_stages
    
    def _setup_default_transitions(self, stages):
        """Set up default stage transitions"""
        stage_map = {stage.code: stage for stage in stages}
        
        transitions = [
            ('draft', ['review']),
            ('review', ['approve', 'reject']),
            ('approve', ['authorize', 'reject']),
            ('authorize', ['post', 'reject']),
            ('post', []),  # Final stage
            ('reject', ['draft']),  # Can be reset
        ]
        
        for from_code, to_codes in transitions:
            from_stage = stage_map.get(from_code)
            if from_stage:
                to_stages = [stage_map[code] for code in to_codes if code in stage_map]
                from_stage.next_stage_ids = [(6, 0, [s.id for s in to_stages])]
    
    def get_next_stages(self, user=None):
        """Get possible next stages for current user"""
        if not user:
            user = self.env.user
        
        accessible_stages = []
        for stage in self.next_stage_ids:
            # Check if user has access to approve to this stage
            if stage.approval_group_ids:
                user_groups = user.groups_id
                if any(group in user_groups for group in stage.approval_group_ids):
                    accessible_stages.append(stage)
            else:
                accessible_stages.append(stage)
        
        return accessible_stages
    
    def can_user_approve(self, user=None):
        """Check if user can approve from this stage"""
        if not user:
            user = self.env.user
        
        if not self.approval_group_ids:
            return True
        
        user_groups = user.groups_id
        return any(group in user_groups for group in self.approval_group_ids)
    
    def action_view_payments(self):
        """Action to view payments in this stage"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payments in %s') % self.name,
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [
                ('state', '=', self.code),
                ('company_id', '=', self.company_id.id),
            ],
            'context': {'default_state': self.code},
        }
