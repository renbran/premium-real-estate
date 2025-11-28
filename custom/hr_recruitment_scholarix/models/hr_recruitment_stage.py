# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    is_contract_proposal = fields.Boolean(
        string='Contract Proposal Stage',
        help='Mark this stage as the contract proposal stage to trigger automatic email sending',
        default=False
    )

    @api.model
    def create(self, vals):
        """Create default contract proposal stage if name contains 'contract proposal'"""
        stage = super(HrRecruitmentStage, self).create(vals)
        
        if stage.name and 'contract proposal' in stage.name.lower():
            stage.is_contract_proposal = True
            
        return stage