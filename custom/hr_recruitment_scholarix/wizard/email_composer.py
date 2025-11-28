# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrRecruitmentEmailComposer(models.TransientModel):
    _name = 'hr.recruitment.email.composer'
    _description = 'HR Recruitment Email Composer'
    _inherit = ['mail.composer.mixin']

    applicant_id = fields.Many2one('hr.applicant', string='Applicant', required=True)
    template_id = fields.Many2one('mail.template', string='Email Template', required=True)
    subject = fields.Char(string='Subject', required=True)
    body_html = fields.Html(string='Body', required=True)
    preview_html = fields.Html(string='Preview', readonly=True)
    email_to = fields.Char(string='To', required=True)
    email_cc = fields.Char(string='CC')
    email_bcc = fields.Char(string='BCC')
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        result = super(HrRecruitmentEmailComposer, self).default_get(fields_list)
        
        applicant_id = self.env.context.get('default_res_id')
        template_id = self.env.context.get('default_template_id')
        
        if applicant_id:
            result['applicant_id'] = applicant_id
            applicant = self.env['hr.applicant'].browse(applicant_id)
            result['email_to'] = applicant.email_from
            
        if template_id:
            result['template_id'] = template_id
            template = self.env['mail.template'].browse(template_id)
            if template and applicant_id:
                applicant = self.env['hr.applicant'].browse(applicant_id)
                result['subject'] = template._render_field('subject', [applicant_id])[applicant_id]
                result['body'] = template._render_field('body_html', [applicant_id])[applicant_id]
                
        return result

    @api.onchange('template_id', 'applicant_id')
    def _onchange_template_id(self):
        """Update subject and body when template changes"""
        if self.template_id and self.applicant_id:
            self.subject = self.template_id._render_field('subject', [self.applicant_id.id])[self.applicant_id.id]
            self.body_html = self.template_id._render_field('body_html', [self.applicant_id.id])[self.applicant_id.id]
            self.preview_html = self.body_html

    def action_send_mail(self):
        """Send the email"""
        self.ensure_one()
        
        if not self.email_to:
            raise UserError(_("Please specify recipient email address."))
        
        # Create mail values
        mail_values = {
            'subject': self.subject,
            'body_html': self.body_html,
            'email_to': self.email_to,
            'email_cc': self.email_cc,
            'email_bcc': self.email_bcc,
            'model': 'hr.applicant',
            'res_id': self.applicant_id.id,
            'auto_delete': False,
        }
        
        # Send email
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        
        # Log message on applicant
        self.applicant_id.message_post(
            body=_("Training period offer email sent to: %s") % self.email_to,
            subject=self.subject,
            message_type='email'
        )
        
        return {'type': 'ir.actions.act_window_close'}

    def preview_email(self):
        """Update email preview"""
        self.ensure_one()
        self.preview_html = self.body_html
        return True

    def action_preview(self):
        """Preview the email"""
        self.ensure_one()
        
        # Create a temporary mail message for preview
        preview_msg = self.env['mail.message'].create({
            'subject': self.subject,
            'body': self.body_html,
            'model': 'hr.applicant',
            'res_id': self.applicant_id.id,
            'message_type': 'email',
            'email_from': self.env.user.email_formatted,
        })
        
        # Return action to display preview
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.message',
            'res_id': preview_msg.id,
            'view_mode': 'form',
            'target': 'new',
            'name': _('Email Preview'),
        }