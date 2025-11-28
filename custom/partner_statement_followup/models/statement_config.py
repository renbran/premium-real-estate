# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StatementConfig(models.Model):
    _name = 'res.partner.statement.config'
    _description = 'Partner Statement Configuration'
    _rec_name = 'name'

    name = fields.Char(
        string='Configuration Name',
        required=True,
        help="Name for this configuration"
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Ageing configuration
    ageing_bucket_1 = fields.Integer(
        string='Bucket 1 (Days)',
        default=30,
        required=True,
        help="First ageing bucket (1-X days)"
    )
    
    ageing_bucket_2 = fields.Integer(
        string='Bucket 2 (Days)',
        default=60,
        required=True,
        help="Second ageing bucket (X+1-Y days)"
    )
    
    ageing_bucket_3 = fields.Integer(
        string='Bucket 3 (Days)',
        default=90,
        required=True,
        help="Third ageing bucket (Y+1-Z days)"
    )
    
    ageing_bucket_4 = fields.Integer(
        string='Bucket 4 (Days)',
        default=120,
        required=True,
        help="Fourth ageing bucket (Z+1-W days)"
    )
    
    # Follow-up configuration
    auto_followup = fields.Boolean(
        string='Enable Auto Follow-up',
        default=True,
        help="Enable automatic follow-up emails"
    )
    
    days_between_levels = fields.Integer(
        string='Days Between Levels',
        default=7,
        required=True,
        help="Number of days between follow-up levels"
    )
    
    max_followup_level = fields.Integer(
        string='Maximum Follow-up Level',
        default=3,
        required=True,
        help="Maximum number of follow-up levels"
    )
    
    send_email = fields.Boolean(
        string='Send Follow-up Email',
        default=True,
        help="Send email notifications for follow-up activities"
    )
    
    create_activity = fields.Boolean(
        string='Create Follow-up Activity',
        default=True,
        help="Create activities for follow-up reminders"
    )
    
    # Statement configuration
    include_reconciled = fields.Boolean(
        string='Include Reconciled Entries',
        default=False,
        help="Include reconciled entries in statements"
    )
    
    statement_period_days = fields.Integer(
        string='Statement Period (Days)',
        default=365,
        required=True,
        help="Number of days to include in statements"
    )
    
    show_payment_details = fields.Boolean(
        string='Show Payment Details',
        default=True,
        help="Show payment references and details in statements"
    )
    
    # Email settings
    followup_email_from = fields.Char(
        string='Follow-up Email From',
        help="Email address to use as sender for follow-up emails"
    )
    
    cc_accounts_team = fields.Boolean(
        string='CC Accounts Team',
        default=True,
        help="CC accounts receivable team on follow-up emails"
    )
    
    accounts_team_email = fields.Char(
        string='Accounts Team Email',
        help="Email address for accounts receivable team"
    )
    
    # Report settings
    statement_logo = fields.Binary(
        string='Statement Logo',
        help="Logo to display on statement reports"
    )
    
    statement_footer = fields.Html(
        string='Statement Footer',
        default="""
        <p style="text-align: center; margin-top: 20px; font-size: 10px; color: #666;">
            Please contact our accounts department if you have any questions about this statement.
        </p>
        """,
        help="Footer text for statement reports"
    )

    @api.constrains('ageing_bucket_1', 'ageing_bucket_2', 'ageing_bucket_3', 'ageing_bucket_4')
    def _check_ageing_buckets(self):
        """Validate ageing bucket configuration"""
        for record in self:
            if not (record.ageing_bucket_1 < record.ageing_bucket_2 < record.ageing_bucket_3 < record.ageing_bucket_4):
                raise ValidationError(_("Ageing buckets must be in ascending order"))
            
            if record.ageing_bucket_1 <= 0:
                raise ValidationError(_("Ageing buckets must be positive"))

    @api.constrains('days_between_levels', 'max_followup_level')
    def _check_followup_config(self):
        """Validate follow-up configuration"""
        for record in self:
            if record.days_between_levels <= 0:
                raise ValidationError(_("Days between levels must be positive"))
            
            if record.max_followup_level <= 0 or record.max_followup_level > 10:
                raise ValidationError(_("Maximum follow-up level must be between 1 and 10"))

    @api.model
    def get_company_config(self, company_id=None):
        """Get configuration for a company"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        
        if not config:
            # Create default configuration
                config = self.create({
                    'name': f"Default Configuration - {self.env['res.company'].browse(company_id).name}",
                'company_id': company_id,
                'ageing_bucket_1': 30,
                'ageing_bucket_2': 60,
                'ageing_bucket_3': 90,
                'ageing_bucket_4': 120,
                'auto_followup': True,
                'days_between_levels': 7,
                'max_followup_level': 3,
                'send_email': True,
                'create_activity': True,
                'statement_period_days': 365,
                'show_payment_details': True,
                'cc_accounts_team': True,
            })
        
        return config

    def get_bucket_labels(self):
        """Get formatted bucket labels"""
        self.ensure_one()
        
        return {
            'current': _('Current'),
            'bucket_1': _('1-%d Days') % self.ageing_bucket_1,
            'bucket_2': _('%d-%d Days') % (self.ageing_bucket_1 + 1, self.ageing_bucket_2),
            'bucket_3': _('%d-%d Days') % (self.ageing_bucket_2 + 1, self.ageing_bucket_3),
            'bucket_4': _('%d-%d Days') % (self.ageing_bucket_3 + 1, self.ageing_bucket_4),
            'bucket_5': _('%d+ Days') % (self.ageing_bucket_4 + 1),
        }

    def action_test_followup_template(self):
        """Test follow-up email templates"""
        self.ensure_one()
        
        # Find a partner with outstanding balance for testing
        partner = self.env['res.partner'].search([
            ('is_company', '=', True),
            ('balance_due_company_currency', '>', 0),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not partner:
            raise ValidationError(_("No partner found with outstanding balance for testing"))
        
        # Test sending level 1 template
        template = self.env.ref('partner_statement_followup.followup_level_1_template', raise_if_not_found=False)
        
        if not template:
            raise ValidationError(_("Follow-up level 1 template not found"))
        
        # Create test email (don't actually send)
        mail = template.generate_email(partner.id, ['subject', 'body_html'])
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Test Email Preview'),
            'res_model': 'mail.mail',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subject': mail.get('subject', ''),
                'default_body_html': mail.get('body_html', ''),
                'default_email_to': partner.email,
            }
        }

    @api.model
    def _cron_weekly_ageing_report(self):
        """Send weekly ageing report to accounts teams"""
        companies = self.env['res.company'].search([])
        
        for company in companies:
            config = self.get_company_config(company.id)
            
            if not config.accounts_team_email:
                continue
            
            # Generate ageing data
            ageing_data = self.env['account.move.line'].with_company(company).get_ageing_analysis()
            
            if not ageing_data:
                continue
            
            # Send email with ageing report
            template = self.env.ref('partner_statement_followup.weekly_ageing_report_template', raise_if_not_found=False)
            
            if template:
                email_values = {
                    'email_to': config.accounts_team_email,
                    'email_from': config.followup_email_from or company.email,
                }
                
                template.with_context(
                    ageing_data=ageing_data,
                    company=company,
                    config=config
                ).send_mail(config.id, email_values=email_values, force_send=True)
