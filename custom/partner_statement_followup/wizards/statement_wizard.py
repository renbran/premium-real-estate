# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import base64
from datetime import datetime, timedelta


class StatementWizard(models.TransientModel):
    _name = 'statement.wizard'
    _description = 'Partner Statement Wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        domain=[('is_company', '=', True)]
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    date_from = fields.Date(
        string='From Date',
        default=lambda self: fields.Date.subtract(fields.Date.today(), days=365)
    )
    
    date_to = fields.Date(
        string='To Date',
        default=fields.Date.today
    )
    
    include_reconciled = fields.Boolean(
        string='Include Reconciled Items',
        default=False
    )
    
    show_ageing = fields.Boolean(
        string='Show Ageing Analysis',
        default=True
    )
    
    output_format = fields.Selection([
        ('screen', 'View on Screen'),
        ('pdf', 'PDF Report'),
        ('excel', 'Excel Export')
    ], string='Output Format', default='screen', required=True)
    
    # Statement data (computed)
    line_ids = fields.One2many(
        'statement.wizard.line',
        'wizard_id',
        string='Statement Lines',
        readonly=True
    )
    
    ageing_current = fields.Monetary(
        string='Current',
        currency_field='currency_id',
        readonly=True
    )
    
    ageing_30 = fields.Monetary(
        string='1-30 Days',
        currency_field='currency_id',
        readonly=True
    )
    
    ageing_60 = fields.Monetary(
        string='31-60 Days',
        currency_field='currency_id',
        readonly=True
    )
    
    ageing_90 = fields.Monetary(
        string='61-90 Days',
        currency_field='currency_id',
        readonly=True
    )
    
    ageing_90_plus = fields.Monetary(
        string='90+ Days',
        currency_field='currency_id',
        readonly=True
    )
    
    total_balance = fields.Monetary(
        string='Total Outstanding',
        currency_field='currency_id',
        readonly=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    @api.onchange('partner_id', 'company_id', 'date_from', 'date_to', 'include_reconciled')
    def _onchange_refresh_data(self):
        """Refresh statement data when parameters change"""
        if self.partner_id and self.company_id:
            self._compute_statement_data()

    def _compute_statement_data(self):
        """Compute statement lines and ageing data"""
        if not self.partner_id or not self.company_id:
            return
        
        # Get configuration
        config = self.env['res.partner.statement.config'].get_company_config(self.company_id.id)
        
        # Build domain for account move lines
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('account_id.account_type', '=', 'asset_receivable'),
            ('company_id', '=', self.company_id.id)
        ]
        
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        
        if not self.include_reconciled:
            domain.append(('reconciled', '=', False))
        else:
            # If including reconciled, show only if amount_residual != 0 OR reconciled in period
            domain.append('|')
            domain.append(('amount_residual', '!=', 0))
            domain.append(('reconciled', '=', True))
        
        lines = self.env['account.move.line'].search(domain, order='date desc, move_id desc')
        
        # Clear existing lines
        self.line_ids.unlink()
        
        # Create wizard lines
        wizard_lines = []
        ageing_data = {
            'current': 0.0,
            'bucket_1': 0.0,
            'bucket_2': 0.0,
            'bucket_3': 0.0,
            'bucket_4': 0.0,
            'total': 0.0
        }
        
        for line in lines:
            # Calculate ageing for unreconciled lines only
            amount_for_ageing = line.amount_residual if not line.reconciled else 0.0
            
            if amount_for_ageing > 0:
                ageing_data['total'] += amount_for_ageing
                
                if line.ageing_bucket == 'current':
                    ageing_data['current'] += amount_for_ageing
                elif line.ageing_bucket == '1_30':
                    ageing_data['bucket_1'] += amount_for_ageing
                elif line.ageing_bucket == '31_60':
                    ageing_data['bucket_2'] += amount_for_ageing
                elif line.ageing_bucket == '61_90':
                    ageing_data['bucket_3'] += amount_for_ageing
                else:
                    ageing_data['bucket_4'] += amount_for_ageing
            
            wizard_lines.append((0, 0, {
                'move_line_id': line.id,
                'date': line.date,
                'date_maturity': line.date_maturity,
                'reference': line.move_id.name,
                'description': line.name or line.move_id.ref or '',
                'debit': line.debit,
                'credit': line.credit,
                'amount_residual': line.amount_residual,
                'reconciled': line.reconciled,
                'days_overdue': line.days_overdue,
                'ageing_bucket': line.ageing_bucket,
            }))
        
        # Update wizard fields
        self.line_ids = wizard_lines
        self.ageing_current = ageing_data['current']
        self.ageing_30 = ageing_data['bucket_1']
        self.ageing_60 = ageing_data['bucket_2']
        self.ageing_90 = ageing_data['bucket_3']
        self.ageing_90_plus = ageing_data['bucket_4']
        self.total_balance = ageing_data['total']

    def action_view_statement(self):
        """Display statement on screen"""
        self._compute_statement_data()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner Statement - %s') % self.partner_id.name,
            'res_model': 'statement.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context, statement_view=True),
        }

    def action_print_pdf(self):
        """Generate PDF statement"""
        self._compute_statement_data()
        
        return self.env.ref('partner_statement_followup.action_report_partner_statement').report_action(self)

    def action_export_excel(self):
        """Export statement to Excel"""
        self._compute_statement_data()
        
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("xlsxwriter library is required for Excel export"))
        
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Statement')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#CCE5FF',
            'border': 1,
            'align': 'center'
        })
        
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        
        # Write header information
        row = 0
        worksheet.write(row, 0, 'Partner Statement', header_format)
        worksheet.merge_range(row, 0, row, 8, 'Partner Statement', header_format)
        
        row += 2
        worksheet.write(row, 0, 'Partner:', text_format)
        worksheet.write(row, 1, self.partner_id.name, text_format)
        
        row += 1
        worksheet.write(row, 0, 'Date Range:', text_format)
        worksheet.write(row, 1, f"{self.date_from} to {self.date_to}", text_format)
        
        row += 1
        worksheet.write(row, 0, 'Company:', text_format)
        worksheet.write(row, 1, self.company_id.name, text_format)
        
        # Ageing analysis
        if self.show_ageing:
            row += 3
            worksheet.write(row, 0, 'Ageing Analysis', header_format)
            worksheet.merge_range(row, 0, row, 5, 'Ageing Analysis', header_format)
            
            row += 1
            ageing_headers = ['Current', '1-30 Days', '31-60 Days', '61-90 Days', '90+ Days', 'Total']
            for col, header in enumerate(ageing_headers):
                worksheet.write(row, col, header, header_format)
            
            row += 1
            ageing_values = [
                self.ageing_current, self.ageing_30, self.ageing_60,
                self.ageing_90, self.ageing_90_plus, self.total_balance
            ]
            for col, value in enumerate(ageing_values):
                worksheet.write(row, col, value, money_format)
        
        # Statement lines
        row += 3
        headers = [
            'Date', 'Due Date', 'Reference', 'Description',
            'Debit', 'Credit', 'Balance', 'Days Overdue', 'Status'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        
        row += 1
        for line in self.line_ids:
            worksheet.write(row, 0, line.date, date_format)
            worksheet.write(row, 1, line.date_maturity or '', date_format)
            worksheet.write(row, 2, line.reference, text_format)
            worksheet.write(row, 3, line.description, text_format)
            worksheet.write(row, 4, line.debit, money_format)
            worksheet.write(row, 5, line.credit, money_format)
            worksheet.write(row, 6, line.amount_residual, money_format)
            worksheet.write(row, 7, line.days_overdue, text_format)
            worksheet.write(row, 8, 'Paid' if line.reconciled else 'Outstanding', text_format)
            row += 1
        
        # Adjust column widths
        worksheet.set_column('A:A', 12)  # Date
        worksheet.set_column('B:B', 12)  # Due Date
        worksheet.set_column('C:C', 15)  # Reference
        worksheet.set_column('D:D', 30)  # Description
        worksheet.set_column('E:G', 12)  # Money columns
        worksheet.set_column('H:H', 12)  # Days Overdue
        worksheet.set_column('I:I', 12)  # Status
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        filename = f"Statement_{self.partner_id.name}_{fields.Date.today()}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def action_send_email(self):
        """Send statement via email"""
        self.ensure_one()
        
        if not self.partner_id.email:
            raise UserError(_("Partner %s has no email address") % self.partner_id.name)
        
        # Generate PDF first
        pdf_report = self.env.ref('partner_statement_followup.action_report_partner_statement')
        pdf_content, _ = pdf_report._render_qweb_pdf(self.id)
        
        # Create attachment
        filename = f"Statement_{self.partner_id.name}_{fields.Date.today()}.pdf"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
        })
        
        # Send email
        template = self.env.ref('partner_statement_followup.statement_email_template', raise_if_not_found=False)
        
        if template:
            template.attachment_ids = [(6, 0, [attachment.id])]
            template.send_mail(self.id, force_send=True)
            template.attachment_ids = [(5, 0, 0)]  # Clear attachments
        
        return {'type': 'ir.actions.act_window_close'}

    def action_quick_reconcile_line(self, line_id):
        """Quick reconcile a specific line"""
        line = self.env['account.move.line'].browse(line_id)
        result = line.action_quick_reconcile()
        
        if result:
            # Refresh statement data
            self._compute_statement_data()
        
        return result


class StatementWizardLine(models.TransientModel):
    _name = 'statement.wizard.line'
    _description = 'Statement Wizard Line'
    _order = 'date desc'

    wizard_id = fields.Many2one(
        'statement.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
        required=True
    )
    
    date = fields.Date(string='Date')
    date_maturity = fields.Date(string='Due Date')
    reference = fields.Char(string='Reference')
    description = fields.Char(string='Description')
    debit = fields.Monetary(string='Debit', currency_field='currency_id')
    credit = fields.Monetary(string='Credit', currency_field='currency_id')
    amount_residual = fields.Monetary(string='Balance', currency_field='currency_id')
    reconciled = fields.Boolean(string='Reconciled')
    days_overdue = fields.Integer(string='Days Overdue')
    ageing_bucket = fields.Char(string='Ageing Bucket')
    
    currency_id = fields.Many2one(
        'res.currency',
        related='wizard_id.currency_id'
    )

    def action_view_move(self):
        """View related journal entry"""
        self.ensure_one()
        return self.move_line_id.action_view_move()

    def action_reconcile(self):
        """Quick reconcile this line"""
        self.ensure_one()
        return self.wizard_id.action_quick_reconcile_line(self.move_line_id.id)
