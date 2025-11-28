from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrderEnhanced(models.Model):
    _inherit = 'purchase.order'

    # Additional fields for vendor bill automation
    auto_create_bill = fields.Boolean(
        string="Auto Create Vendor Bill", 
        default=False,
        help="Automatically create vendor bill when payment is received"
    )
    vendor_bill_ids = fields.One2many(
        'account.move', 
        'purchase_id', 
        string="Vendor Bills",
        domain=[('move_type', '=', 'in_invoice')]
    )
    vendor_bill_count = fields.Integer(
        string="Vendor Bills Count", 
        compute="_compute_vendor_bill_count"
    )
    payment_received = fields.Boolean(
        string="Payment Received",
        compute="_compute_payment_received",
        store=True
    )
    payment_amount = fields.Monetary(
        string="Payment Amount Received",
        compute="_compute_payment_received",
        store=True
    )
    origin_so_id = fields.Many2one(
        'sale.order',
        string='Source Sales Order',
        compute='_compute_origin_so_id',
        store=True
    )

    @api.depends('origin')
    def _compute_origin_so_id(self):
        for order in self:
            so = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
            order.origin_so_id = so if so else False

    @api.depends('vendor_bill_ids', 'vendor_bill_ids.payment_state')
    def _compute_vendor_bill_count(self):
        for order in self:
            order.vendor_bill_count = len(order.vendor_bill_ids)

    @api.depends('origin_so_id.invoice_ids', 'origin_so_id.invoice_ids.payment_state')
    def _compute_payment_received(self):
        """Check if payment has been received from the source sale order"""
        for order in self:
            if order.origin_so_id:
                paid_invoices = order.origin_so_id.invoice_ids.filtered(
                    lambda inv: inv.state == 'posted' and inv.payment_state in ['paid', 'in_payment']
                )
                order.payment_received = bool(paid_invoices)
                order.payment_amount = sum(paid_invoices.mapped('amount_total'))
            else:
                order.payment_received = False
                order.payment_amount = 0.0

    def action_create_vendor_bill(self):
        """Manual action to create vendor bill for commission"""
        self.ensure_one()
        
        # Validate conditions
        if not self.origin_so_id:
            raise UserError("This is not a commission purchase order")
        
        if not self.payment_received:
            raise UserError(
                "Cannot create vendor bill: Payment not yet received from customer invoice"
            )
        
        if self.vendor_bill_ids.filtered(lambda b: b.state != 'cancel'):
            raise UserError("Vendor bill already exists for this commission")
        
        if self.state not in ['purchase', 'done']:
            raise UserError("Purchase order must be confirmed before creating vendor bill")
        
        return self._create_commission_vendor_bill()

    def _create_commission_vendor_bill(self):
        """Create vendor bill for commission payment"""
        self.ensure_one()
        
        # Prepare vendor bill values
        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'purchase_id': self.id,
            'currency_id': self.currency_id.id,
            'invoice_origin': f"Commission for {self.origin_so_id.name}",
            'payment_reference': f"COMM-{self.origin_so_id.name}-{self.partner_id.name}",
            'invoice_date': fields.Date.today(),
            'ref': f"Commission Payment - {self.origin_so_id.name}",
            'invoice_line_ids': []
        }
        
        # Create invoice lines from purchase order lines
        for line in self.order_line:
            line_vals = {
                'name': f"Commission: {line.name}",
                'product_id': line.product_id.id,
                'quantity': line.product_qty,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, line.taxes_id.ids)],
                'purchase_line_id': line.id,
                'account_id': self._get_commission_expense_account().id,
            }
            bill_vals['invoice_line_ids'].append((0, 0, line_vals))
        
        # Create the vendor bill
        vendor_bill = self.env['account.move'].create(bill_vals)
        
        # Log the creation
        _logger.info(f"Created vendor bill {vendor_bill.name} for commission PO {self.name}")
        
        # Add message to both PO and SO
        self.message_post(
            body=f"Vendor bill {vendor_bill.name} created for commission payment",
            subject="Vendor Bill Created"
        )
        
        if self.origin_so_id:
            self.origin_so_id.message_post(
                body=f"Vendor bill {vendor_bill.name} created for commission PO {self.name}",
                subject="Commission Vendor Bill Created"
            )
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'res_model': 'account.move',
            'res_id': vendor_bill.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_commission_expense_account(self):
        """Get the commission expense account from configuration"""
        commission_account_id = self.env['ir.config_parameter'].sudo().get_param(
            'commission_ax.commission_expense_account_id'
        )
        
        if commission_account_id:
            try:
                account = self.env['account.account'].browse(int(commission_account_id))
                if account.exists():
                    return account
            except (ValueError, TypeError):
                _logger.warning("Invalid commission expense account configuration")
        
        # Fallback to default expense account
        expense_account = self.env['account.account'].search([
            ('user_type_id.name', '=', 'Expenses'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not expense_account:
            raise UserError(
                "No commission expense account configured. "
                "Please configure it in Settings > Commission AX Configuration"
            )
        
        return expense_account

    def action_view_vendor_bills(self):
        """Action to view vendor bills for this commission PO"""
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        
        if len(self.vendor_bill_ids) > 1:
            action['domain'] = [('id', 'in', self.vendor_bill_ids.ids)]
        elif self.vendor_bill_ids:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.vendor_bill_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
        return action

    @api.model
    def _cron_auto_create_vendor_bills(self):
        """Cron job to automatically create vendor bills for commission POs"""
        _logger.info("Starting automatic vendor bill creation for commissions")
        
        # Find commission POs that meet criteria for auto bill creation
        eligible_pos = self.search([
            ('origin_so_id', '!=', False),  # Is a commission PO
            ('auto_create_bill', '=', True),  # Auto creation enabled
            ('payment_received', '=', True),  # Payment received
            ('state', 'in', ['purchase', 'done']),  # PO is confirmed
            ('vendor_bill_count', '=', 0),  # No vendor bill exists yet
        ])
        
        created_bills = 0
        failed_bills = 0
        
        for po in eligible_pos:
            try:
                po._create_commission_vendor_bill()
                created_bills += 1
                _logger.info(f"Auto-created vendor bill for commission PO {po.name}")
            except Exception as e:
                failed_bills += 1
                _logger.error(f"Failed to auto-create vendor bill for PO {po.name}: {str(e)}")
        
        _logger.info(
            f"Automatic vendor bill creation completed. "
            f"Created: {created_bills}, Failed: {failed_bills}"
        )

    @api.model
    def _cron_monitor_commission_payments(self):
        """Enhanced cron job to monitor commission payment status"""
        _logger.info("Starting commission payment monitoring")
        
        # Check for commissions that should be processed due to invoice payments
        sale_orders = self.env['sale.order'].search([
            ('commission_processed', '=', False),
            ('state', 'in', ['sale', 'done']),
            ('invoice_ids.state', '=', 'posted'),
            ('invoice_ids.payment_state', 'in', ['paid', 'in_payment'])
        ])
        
        auto_processed = 0
        for order in sale_orders:
            try:
                order._create_commission_purchase_orders()
                auto_processed += 1
                _logger.info(f"Auto-processed commissions for paid order {order.name}")
            except Exception as e:
                _logger.error(f"Failed to auto-process commissions for {order.name}: {str(e)}")
        
        # Check commission POs for automatic posting
        commission_pos = self.search([
            ('origin_so_id', '!=', False),
            ('commission_posted', '=', False),
            ('state', 'in', ['purchase', 'done'])
        ])
        
        auto_posted = 0
        for po in commission_pos:
            try:
                po._post_commission_on_receipt_validation()
                if not po.commission_posted:
                    po._post_commission_on_payment()
                if po.commission_posted:
                    auto_posted += 1
            except Exception as e:
                _logger.error(f"Error in commission posting check for PO {po.name}: {str(e)}")
        
        _logger.info(
            f"Commission monitoring completed. "
            f"Auto-processed orders: {auto_processed}, Auto-posted POs: {auto_posted}"
        )

    @api.model
    def _cron_commission_reconciliation(self):
        """Cron job to reconcile commission data and detect inconsistencies"""
        _logger.info("Starting commission reconciliation")
        
        issues_found = []
        
        # Check for sale orders with processed commissions but no POs
        orphaned_sales = self.env['sale.order'].search([
            ('commission_processed', '=', True),
            ('purchase_order_count', '=', 0)
        ])
        
        for sale in orphaned_sales:
            issues_found.append(f"Sale order {sale.name} shows processed but no POs found")
            sale.message_post(
                body="Warning: Commissions marked as processed but no purchase orders found. Please review.",
                subject="Commission Reconciliation Issue"
            )
        
        # Check for commission POs without corresponding sales
        orphaned_pos = self.search([
            ('origin_so_id', '!=', False),
            ('origin_so_id.commission_processed', '=', False)
        ])
        
        for po in orphaned_pos:
            issues_found.append(f"Commission PO {po.name} exists but source SO not marked as processed")
            po.message_post(
                body="Warning: Commission PO exists but source sale order not marked as processed.",
                subject="Commission Reconciliation Issue"
            )
        
        # Check for inconsistent commission amounts
        inconsistent_amounts = self.search([
            ('origin_so_id', '!=', False)
        ])
        
        for po in inconsistent_amounts:
            calculated_total = sum(po.origin_so_id._get_commission_entries()[i]['amount'] 
                                 for i, entry in enumerate(po.origin_so_id._get_commission_entries())
                                 if entry['partner'].id == po.partner_id.id)
            po_total = sum(po.order_line.mapped('price_subtotal'))
            
            if abs(calculated_total - po_total) > 0.01:  # Allow for rounding differences
                issues_found.append(
                    f"Commission amount mismatch for PO {po.name}: "
                    f"Expected {calculated_total}, PO shows {po_total}"
                )
        
        if issues_found:
            _logger.warning(f"Commission reconciliation found {len(issues_found)} issues")
            # Send summary email to commission managers
            self._send_reconciliation_report(issues_found)
        else:
            _logger.info("Commission reconciliation completed - no issues found")

    def _send_reconciliation_report(self, issues):
        """Send reconciliation report to managers"""
        manager_group = self.env.ref('sales_team.group_sale_manager', raise_if_not_found=False)
        if not manager_group:
            return
        
        managers = manager_group.users
        if not managers:
            return
        
        subject = f"Commission Reconciliation Report - {len(issues)} Issues Found"
        body = f"""
        <h3>Commission Reconciliation Report</h3>
        <p>The following issues were found during commission reconciliation:</p>
        <ul>
        {''.join(f'<li>{issue}</li>' for issue in issues)}
        </ul>
        <p>Please review and resolve these issues.</p>
        """
        
        for manager in managers:
            try:
                self.env['mail.mail'].create({
                    'subject': subject,
                    'body_html': body,
                    'recipient_ids': [(6, 0, [manager.partner_id.id])],
                    'auto_delete': True,
                }).send()
            except Exception as e:
                _logger.error(f"Failed to send reconciliation report to {manager.name}: {str(e)}")


# Enhanced Sale Order with payment monitoring
class SaleOrderPaymentMonitoring(models.Model):
    _inherit = 'sale.order'

    def _handle_invoice_payment_change(self):
        """Handle changes in invoice payment status"""
        for order in self:
            if order.invoice_ids:
                paid_invoices = order.invoice_ids.filtered(
                    lambda inv: inv.state == 'posted' and inv.payment_state == 'paid'
                )
                
                if paid_invoices and not order.commission_processed:
                    # Auto-process commissions if enabled
                    auto_process = self.env['ir.config_parameter'].sudo().get_param(
                        'commission_ax.auto_process_on_payment', default='false'
                    )
                    
                    if auto_process.lower() == 'true':
                        try:
                            order._create_commission_purchase_orders()
                            _logger.info(f"Auto-processed commissions for paid order {order.name}")
                        except Exception as e:
                            _logger.error(f"Auto-processing failed for {order.name}: {str(e)}")
                
                # Enable auto vendor bill creation for commission POs
                if paid_invoices and order.commission_processed:
                    commission_pos = order.purchase_order_ids.filtered('origin_so_id')
                    commission_pos.write({'auto_create_bill': True})

    @api.model
    def create(self, vals):
        """Override create to set up monitoring"""
        order = super(SaleOrderPaymentMonitoring, self).create(vals)
        return order

    def write(self, vals):
        """Override write to monitor invoice payment changes"""
        result = super(SaleOrderPaymentMonitoring, self).write(vals)
        
        # Check if any invoice-related fields changed
        if any(field.startswith('invoice') for field in vals.keys()):
            self._handle_invoice_payment_change()
        
        return result