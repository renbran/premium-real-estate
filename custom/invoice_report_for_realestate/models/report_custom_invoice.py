from odoo import models

class ReportCustomInvoice(models.AbstractModel):
    _name = 'report.invoice_report_for_realestate.report_invoice'
    _description = 'OSUS Custom Invoice Report'

    def _get_report_values(self, docids, data=None):
        # Filter to only get active (non-cancelled) account moves
        docs = self.env['account.move'].browse(docids).filtered(lambda m: m.state != 'cancel')
        return {
            'docs': docs,
        }
