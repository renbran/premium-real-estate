# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def write(self, vals):
        """Override write to send email when stage changes to Contract Proposal"""
        result = super(HrApplicant, self).write(vals)
        
        # Check if stage_id is being updated
        if 'stage_id' in vals:
            new_stage = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            
            # Check if the new stage is marked as contract proposal stage
            if new_stage and new_stage.is_contract_proposal:
                for applicant in self:
                    applicant._send_contract_proposal_email()
        
        return result

    def _send_contract_proposal_email(self):
        """Send contract proposal email to the applicant"""
        try:
            template = self.env.ref('hr_recruitment_scholarix.hr_recruitment_training_period_offer', raise_if_not_found=False)
            if template:
                template.send_mail(self.id, force_send=True)
                
                # Log the email sending
                self.message_post(
                    body=_("Training period offer email sent to candidate: %s") % (self.email_from or self.partner_name or 'Unknown'),
                    subject=_("Contract Proposal Email Sent"),
                    message_type='notification'
                )
                _logger.info("Contract proposal email sent to applicant %s (ID: %s)", self.partner_name, self.id)
            else:
                _logger.warning("Training period offer email template not found")
        except Exception as e:
            _logger.error("Failed to send contract proposal email to applicant %s: %s", self.partner_name, str(e))
            self.message_post(
                body=_("Failed to send training period offer email: %s") % str(e),
                subject=_("Email Sending Failed"),
                message_type='notification'
            )

    def action_send_contract_email(self):
        """Manual action to send contract proposal email"""
        self.ensure_one()
        
        if not self.email_from:
            raise UserError(_("No email address found for this applicant. Please add an email address first."))
        
        # Open email composer wizard
        template = self.env.ref('hr_recruitment_scholarix.hr_recruitment_training_period_offer', raise_if_not_found=False)
        
        if not template:
            raise UserError(_("Training period offer email template not found. Please check module installation."))
        
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_template_id': template.id,
            'default_use_template': True,
            'force_email': True,
        }
        
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.recruitment.email.composer',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_preview_contract_email(self):
        """Preview the contract proposal email"""
        self.ensure_one()
        
        template = self.env.ref('hr_recruitment_scholarix.hr_recruitment_training_period_offer', raise_if_not_found=False)
        
        if not template:
            raise UserError(_("Training period offer email template not found."))
        
        # Generate preview URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        preview_url = f"{base_url}/mail/view?model=hr.applicant&res_id={self.id}&template_id={template.id}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': preview_url,
            'target': 'new',
        }