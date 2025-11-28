from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging
import base64

_logger = logging.getLogger(__name__)

class PropertySale(models.Model):
    _name = 'property.sale'
    _description = 'Property Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc, id desc'

    STATE_DRAFT = 'draft'
    STATE_CONFIRMED = 'confirmed'
    STATE_INVOICED = 'invoiced'
    STATE_CANCELLED = 'cancelled'

    name = fields.Char(string='Sale Reference', required=True, default=lambda self: _('New'))
    state = fields.Selection([
        (STATE_DRAFT, 'Draft'),
        (STATE_CONFIRMED, 'Confirmed'),
        (STATE_INVOICED, 'Invoiced'),
        (STATE_CANCELLED, 'Cancelled')
    ], string='State', default=STATE_DRAFT, tracking=True)

    property_value = fields.Float(string='Property Value', compute='_compute_property_value', store=True, digits=(16, 2))
    sale_price = fields.Float(string='Sale Price', compute='_compute_total_selling_price', store=True, digits=(16, 2))
    down_payment_percentage = fields.Float(string='Down Payment (%)', default=20.0, digits=(5, 2))
    down_payment = fields.Float(string='Down Payment', compute='_compute_down_payment', store=True, digits=(16, 2))
    dld_fee = fields.Float(string='DLD Fee', compute='_compute_dld_fee', store=True, digits=(16, 2))
    admin_fee = fields.Float(string='Admin Fee', default=1.0, digits=(16, 2))
    remaining_balance = fields.Float(string='Remaining Balance', compute='_compute_remaining_balance', store=True, digits=(16, 2))
    
    # Flexible Payment Plan Fields
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly (Every 3 Months)'),
        ('semi_annual', 'Semi-Annual (Every 6 Months)'),
        ('annual', 'Annual (Yearly)'),
        ('milestone', 'Milestone-Based'),
        ('custom', 'Custom Schedule'),
    ], string='Payment Frequency', default='monthly', required=True, tracking=True)
    
    no_of_installments = fields.Integer(string='No. of Installments', default=1)
    amount_per_installment = fields.Float(string='Amount Per Installment', compute='_compute_amount_per_installment', store=True, digits=(16, 2))
    
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    property_id = fields.Many2one('property.property', string='Property', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    desired_years = fields.Integer(string='Desired Years')
    property_sale_line_ids = fields.One2many('property.sale.line', 'property_sale_id', string='Installment Lines')
    start_date = fields.Date(string='Start Date', required=True)
    payment_progress = fields.Float(string="Payment Progress (%)", compute="_compute_payment_progress", store=True)
    sale_date = fields.Date(string="Sale Date", default=fields.Date.today)
    total_selling_price = fields.Float(string='Total Selling Price', compute='_compute_total_selling_price', store=True, digits=(16, 2))

    seller_id = fields.Many2one('res.partner', string='Seller/Broker', domain=[('is_company', '=', True)], help="The seller/broker who will receive the commission")
    broker_commission_percentage = fields.Float(string="Broker Commission (%)", default=5.0, digits=(5, 2))
    broker_commission_total_amount = fields.Monetary(string="Broker Commission Total Amount", compute='_compute_broker_commission_total_amount', store=True, currency_field='currency_id')
    broker_commission_invoice_ids = fields.One2many('broker.commission.invoice', 'property_sale_id', string="Broker Commission Invoices")
    broker_commission_count = fields.Integer(string="Commission Count", compute='_compute_broker_commission_count')

    @api.depends('property_id')
    def _compute_property_value(self):
        for record in self:
            record.property_value = record.property_id.property_price if record.property_id else 0.0

    @api.depends('property_value', 'dld_fee', 'admin_fee')
    def _compute_total_selling_price(self):
        for record in self:
            record.total_selling_price = record.property_value + record.dld_fee + record.admin_fee

    @api.depends('property_value', 'down_payment_percentage')
    def _compute_down_payment(self):
        for record in self:
            record.down_payment = (record.down_payment_percentage / 100) * record.property_value

    @api.depends('property_value')
    def _compute_dld_fee(self):
        for record in self:
            record.dld_fee = 0.04 * record.property_value

    @api.depends('total_selling_price', 'down_payment', 'dld_fee', 'admin_fee')
    def _compute_remaining_balance(self):
        for record in self:
            record.remaining_balance = record.total_selling_price - record.down_payment - record.dld_fee - record.admin_fee

    @api.depends('remaining_balance', 'no_of_installments')
    def _compute_amount_per_installment(self):
        for record in self:
            record.amount_per_installment = (record.remaining_balance / record.no_of_installments) if record.no_of_installments > 0 else 0.0

    @api.depends('broker_commission_percentage', 'property_value')
    def _compute_broker_commission_total_amount(self):
        for record in self:
            record.broker_commission_total_amount = (record.broker_commission_percentage / 100) * record.property_value

    @api.depends('broker_commission_invoice_ids')
    def _compute_broker_commission_count(self):
        for record in self:
            record.broker_commission_count = len(record.broker_commission_invoice_ids)

    @api.depends('property_sale_line_ids', 'property_sale_line_ids.collection_status')
    def _compute_payment_progress(self):
        for record in self:
            all_lines = record.property_sale_line_ids
            if all_lines:
                total_amount = sum(all_lines.mapped('capital_repayment'))
                paid_amount = sum(line.capital_repayment for line in all_lines if line.collection_status == 'paid')
                record.payment_progress = round((paid_amount / total_amount) * 100, 2) if total_amount > 0 else 0.0
            else:
                record.payment_progress = 0.0

    def action_draft(self):
        for record in self:
            if record.state == 'cancelled':
                record.state = 'draft'

    def action_confirm(self):
        for record in self:
            if record.state != self.STATE_DRAFT:
                raise UserError(_('Only draft sales can be confirmed.'))
            if not record.property_id:
                raise UserError(_('Please select a property before confirming.'))
            
            record._create_emi_lines()
            record.property_id.write({
                'state': 'sold',
                'partner_id': record.partner_id.id
            })
            record.state = self.STATE_CONFIRMED
            _logger.info("Confirmed property sale %s", record.name)
        return True

    def action_view_invoices(self):
        self.ensure_one()
        invoices = self.property_sale_line_ids.mapped('invoice_id')
        if not invoices:
            raise UserError(_('No invoices found for this sale.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', invoices.ids)],
            'target': 'current',
        }

    def action_generate_all_invoices(self):
        """Generate invoices for all unpaid installments"""
        self.ensure_one()
        if self.state != self.STATE_CONFIRMED:
            raise UserError(_('Only confirmed sales can generate invoices.'))
        
        # Get all unpaid lines that don't have an invoice yet
        unpaid_lines = self.property_sale_line_ids.filtered(
            lambda l: l.collection_status == 'unpaid' and not l.invoice_id
        )
        
        if not unpaid_lines:
            raise UserError(_('No unpaid installments found. All installments already have invoices or are paid.'))
        
        created_invoices = self.env['account.move']
        
        for line in unpaid_lines:
            try:
                # Determine invoice date - use due date if in the past, otherwise use today
                invoice_date = line.collection_date if line.collection_date <= fields.Date.today() else fields.Date.today()
                
                # Build payment type description
                payment_description = ""
                if line.line_type == 'downpayment':
                    payment_description = _("Down Payment")
                elif line.line_type == 'dld_fee':
                    payment_description = _("DLD Registration Fee")
                elif line.line_type == 'admin_fee':
                    payment_description = _("Administrative Fee")
                else:
                    payment_description = _("Installment #%s") % (line.serial_number - 3)
                
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': self.partner_id.id,
                    'invoice_date': invoice_date,
                    'invoice_date_due': line.collection_date,
                    'invoice_line_ids': [(0, 0, {
                        'name': _("%s - %s - Due: %s") % (
                            self.property_id.name,
                            payment_description,
                            line.collection_date.strftime('%d %b %Y')
                        ),
                        'quantity': 1,
                        'price_unit': line.capital_repayment,
                        'account_id': self.property_id.revenue_account_id.id,
                    })],
                    'property_order_id': self.id,
                }
                
                invoice = self.env['account.move'].create(invoice_vals)
                
                # Link invoice to the installment line but don't mark as paid
                # Invoice will be marked paid when actual payment is received
                line.write({
                    'invoice_id': invoice.id,
                })
                
                created_invoices += invoice
                _logger.info("Created invoice %s for installment line %s (Due: %s)", 
                           invoice.name, line.serial_number, line.collection_date)
                
            except Exception as e:
                _logger.error("Failed to create invoice for line %s: %s", line.id, str(e))
                raise UserError(_('Failed to create invoice for installment %s: %s') % (line.serial_number, str(e)))
        
        if created_invoices:
            self.state = self.STATE_INVOICED
            message = _("Generated %d invoices for unpaid installments. Total amount: %s %s") % (
                len(created_invoices),
                self.currency_id.symbol,
                '{:,.2f}'.format(sum(created_invoices.mapped('amount_total')))
            )
            self.message_post(body=message)
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Generated Invoices'),
                'res_model': 'account.move',
                'view_mode': 'list,form',
                'domain': [('id', 'in', created_invoices.ids)],
                'target': 'current',
            }
        
        return {'type': 'ir.actions.act_window_close'}

    def action_generate_broker_commission_invoice(self):
        self.ensure_one()
        if self.state != self.STATE_CONFIRMED:
            raise UserError(_('Only confirmed sales can generate broker commissions.'))
        if not self.seller_id:
            raise UserError(_('Please specify a seller/broker before generating a commission invoice.'))
        
        commission = self.env['broker.commission.invoice'].create({
            'property_sale_id': self.id,
            'seller_id': self.seller_id.id,
            'commission_percentage': self.broker_commission_percentage,
            'commission_amount': self.broker_commission_total_amount,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'broker.commission.invoice',
            'res_id': commission.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send_sales_offer_email(self):
        """Send sales offer report via email with PDF attachment"""
        self.ensure_one()
        template = self.env.ref('property_management.email_template_sales_offer', raise_if_not_found=False)
        if not template:
            raise UserError(_("Email template not found. Please contact administrator."))
        
        # Generate PDF report
        report = self.env.ref('property_management.action_report_sales_offer')
        pdf_content, pdf_type = report._render_qweb_pdf(report.id, self.ids)
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Sales_Offer_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'property.sale',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })
        
        # Send email with attachment
        template.attachment_ids = [(6, 0, [attachment.id])]
        template.send_mail(self.id, force_send=True)
        template.attachment_ids = [(5, 0, 0)]  # Clear template attachments
        
        self.message_post(body=_("Sales offer sent to customer via email"))
        return {'type': 'ir.actions.act_window_close'}

    def action_send_contract_email(self):
        """Send property sale contract via email with PDF attachment"""
        self.ensure_one()
        if self.state not in [self.STATE_CONFIRMED, self.STATE_INVOICED]:
            raise UserError(_('Contract can only be sent for confirmed sales.'))
        
        template = self.env.ref('property_management.email_template_contract', raise_if_not_found=False)
        if not template:
            raise UserError(_("Contract email template not found. Please contact administrator."))
        
        # Generate PDF report
        report = self.env.ref('property_management.action_property_contract_report')
        pdf_content, pdf_type = report._render_qweb_pdf(report.id, self.ids)
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Property_Contract_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'property.sale',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })
        
        # Send email with attachment
        template.attachment_ids = [(6, 0, [attachment.id])]
        template.send_mail(self.id, force_send=True)
        template.attachment_ids = [(5, 0, 0)]  # Clear template attachments
        
        self.message_post(body=_("Property sale contract sent to customer via email"))
        return {'type': 'ir.actions.act_window_close'}

    def action_send_statement_email(self):
        """Send statement of account via email with PDF attachment"""
        self.ensure_one()
        if self.state not in [self.STATE_CONFIRMED, self.STATE_INVOICED]:
            raise UserError(_('Statement can only be sent for confirmed sales.'))
        
        template = self.env.ref('property_management.email_template_statement', raise_if_not_found=False)
        if not template:
            raise UserError(_("Statement email template not found. Please contact administrator."))
        
        # Generate PDF report
        report = self.env.ref('property_management.action_statement_of_account_report')
        pdf_content, pdf_type = report._render_qweb_pdf(report.id, self.ids)
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Statement_of_Account_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'property.sale',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })
        
        # Send email with attachment
        template.attachment_ids = [(6, 0, [attachment.id])]
        template.send_mail(self.id, force_send=True)
        template.attachment_ids = [(5, 0, 0)]  # Clear template attachments
        
        self.message_post(body=_("Statement of account sent to customer via email"))
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        for record in self:
            if record.state != self.STATE_CANCELLED:
                if record.property_id:
                    record.property_id.write({'state': 'available', 'partner_id': False})
                record.state = self.STATE_CANCELLED

    def _create_emi_lines(self):
        self.ensure_one()
        if not self.start_date:
            raise UserError(_('Start date is required to create EMI lines.'))
        
        # For milestone and custom schedules, don't auto-generate lines
        if self.payment_frequency in ['milestone', 'custom']:
            raise UserError(_(
                'For %s payment schedules, please manually add installment lines or import them. '
                'Click "Add a line" in the Payment Schedule tab to create custom payment dates and amounts.'
            ) % (dict(self._fields['payment_frequency'].selection).get(self.payment_frequency)))
        
        if self.no_of_installments <= 0:
            raise UserError(_("Number of installments must be greater than 0."))

        self.property_sale_line_ids.unlink()

        start_date = fields.Date.from_string(self.start_date)
        serial = 1
        
        # Create initial payment lines (down payment, DLD fee, admin fee)
        self._create_line('downpayment', self.down_payment, start_date, serial)
        serial += 1
        self._create_line('dld_fee', self.dld_fee, start_date, serial)
        serial += 1
        self._create_line('admin_fee', self.admin_fee, start_date, serial)
        serial += 1
        
        # Create installment lines based on frequency
        for i in range(self.no_of_installments):
            due_date = self._calculate_due_date(start_date, i + 1)
            self._create_line('emi', self.amount_per_installment, due_date, serial)
            serial += 1

    def _create_line(self, line_type, amount, collection_date, serial_number):
        self.env['property.sale.line'].create({
            'property_sale_id': self.id,
            'serial_number': serial_number,
            'capital_repayment': amount,
            'remaining_capital': amount,
            'collection_date': collection_date,
            'line_type': line_type
        })

    def _calculate_due_date(self, start_date, installment_number):
        """Calculate due date based on payment frequency"""
        try:
            if self.payment_frequency == 'monthly':
                due_date = start_date + relativedelta(months=installment_number)
            elif self.payment_frequency == 'quarterly':
                due_date = start_date + relativedelta(months=installment_number * 3)
            elif self.payment_frequency == 'semi_annual':
                due_date = start_date + relativedelta(months=installment_number * 6)
            elif self.payment_frequency == 'annual':
                due_date = start_date + relativedelta(years=installment_number)
            elif self.payment_frequency in ['milestone', 'custom']:
                # For milestone/custom, the lines should be manually created or imported
                # This is just a fallback to monthly
                due_date = start_date + relativedelta(months=installment_number)
            else:
                due_date = start_date + relativedelta(months=installment_number)
            
            # Handle month overflow (e.g., Jan 31 + 1 month = Feb 28/29)
            if due_date.month != (start_date + relativedelta(months=installment_number)).month:
                due_date = (start_date + relativedelta(months=installment_number)).replace(day=1) - relativedelta(days=1)
            
            return due_date
        except Exception as e:
            raise UserError(_('Error calculating due date: %s') % str(e))

    @api.constrains('down_payment_percentage')
    def _check_down_payment_percentage(self):
        for record in self:
            if not (0 <= record.down_payment_percentage <= 100):
                raise ValidationError(_("Down payment percentage must be between 0 and 100."))

    @api.constrains('no_of_installments')
    def _check_no_of_installments(self):
        for record in self:
            if record.no_of_installments < 1:
                raise ValidationError(_("Number of installments must be at least 1."))
    
    @api.constrains('broker_commission_percentage')
    def _check_broker_commission(self):
        for record in self:
            if not (0 <= record.broker_commission_percentage <= 100):
                raise ValidationError(_("Broker commission percentage must be between 0 and 100."))
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Sale reference must be unique!'),
        ('positive_no_installments', 'CHECK(no_of_installments > 0)', 'Number of installments must be positive!'),
        ('valid_down_payment', 'CHECK(down_payment_percentage >= 0 AND down_payment_percentage <= 100)', 'Down payment percentage must be between 0 and 100!')
    ]


class PropertySaleLine(models.Model):
    _name = 'property.sale.line'
    _description = 'Installment Line'
    _order = 'collection_date, serial_number'
    _rec_name = 'serial_number'

    property_sale_id = fields.Many2one('property.sale', string='Property Sale', required=True, ondelete='cascade', index=True)
    serial_number = fields.Integer(string='Installment Number', required=True)
    milestone_description = fields.Char(string='Milestone/Description', help='Describe the milestone or payment trigger (e.g., "Foundation Complete", "Handover", "Q1 Payment")')
    capital_repayment = fields.Monetary(string='Capital Repayment', digits=(16, 2), required=True)
    remaining_capital = fields.Monetary(string='Remaining Capital', digits=(16, 2), required=True)
    collection_date = fields.Date(string='Collection Date', required=True)
    collection_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Collection Status', default='unpaid', required=True, tracking=True, compute='_compute_collection_status', store=True)
    line_type = fields.Selection([
        ('downpayment', 'Down Payment'),
        ('dld_fee', 'DLD Fee'),
        ('admin_fee', 'Admin Fee'),
        ('emi', 'EMI')
    ], string='Line Type', required=True, default='emi')
    invoice_id = fields.Many2one('account.move', string='Invoice', ondelete='set null')
    invoice_payment_state = fields.Selection(related='invoice_id.payment_state', string='Invoice Payment Status', store=True, readonly=True)
    currency_id = fields.Many2one(related='property_sale_id.currency_id', store=True, readonly=True)

    @api.depends('invoice_id', 'invoice_id.payment_state')
    def _compute_collection_status(self):
        """Automatically update collection status based on invoice payment state"""
        for record in self:
            if record.invoice_id and record.invoice_id.payment_state == 'paid':
                record.collection_status = 'paid'
            else:
                record.collection_status = 'unpaid'

    @api.constrains('capital_repayment', 'remaining_capital')
    def _check_amounts(self):
        for record in self:
            if record.capital_repayment < 0 or record.remaining_capital < 0:
                raise ValidationError(_("Amounts cannot be negative."))
    
    _sql_constraints = [
        ('positive_capital_repayment', 'CHECK(capital_repayment >= 0)', 'Capital repayment must be positive!'),
        ('positive_remaining_capital', 'CHECK(remaining_capital >= 0)', 'Remaining capital must be positive!')
    ]