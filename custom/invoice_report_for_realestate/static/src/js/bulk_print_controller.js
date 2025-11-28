/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(ListController.prototype, {
    setup() {
        super.setup();
    },

    /**
     * Bulk print customer invoices
     */
    async onBulkPrintInvoices() {
        const selectedRecords = await this.getSelectedResIds();
        if (!selectedRecords.length) {
            this.notification.add(_t("Please select at least one invoice to print."), {
                type: "warning",
            });
            return;
        }
        
        // Filter to only include customer invoices
        const invoices = await this.orm.searchRead(
            "account.move",
            [["id", "in", selectedRecords], ["move_type", "=", "out_invoice"]],
            ["id", "name", "partner_id"]
        );
        
        if (!invoices.length) {
            this.notification.add(_t("Please select at least one customer invoice."), {
                type: "warning",
            });
            return;
        }
        
        const invoiceIds = invoices.map(inv => inv.id);
        
        try {
            await this.orm.call(
                "account.move",
                "action_bulk_print_invoices",
                [],
                { context: { active_ids: invoiceIds } }
            );
        } catch (error) {
            this.notification.add(
                _t("Error printing invoices: %s", error.message),
                { type: "danger" }
            );
        }
    },

    /**
     * Bulk print vendor bills
     */
    async onBulkPrintBills() {
        const selectedRecords = await this.getSelectedResIds();
        if (!selectedRecords.length) {
            this.notification.add(_t("Please select at least one bill to print."), {
                type: "warning",
            });
            return;
        }
        
        // Filter to only include vendor bills
        const bills = await this.orm.searchRead(
            "account.move",
            [["id", "in", selectedRecords], ["move_type", "=", "in_invoice"]],
            ["id", "name", "partner_id"]
        );
        
        if (!bills.length) {
            this.notification.add(_t("Please select at least one vendor bill."), {
                type: "warning",
            });
            return;
        }
        
        const billIds = bills.map(bill => bill.id);
        
        try {
            await this.orm.call(
                "account.move",
                "action_bulk_print_bills",
                [],
                { context: { active_ids: billIds } }
            );
        } catch (error) {
            this.notification.add(
                _t("Error printing bills: %s", error.message),
                { type: "danger" }
            );
        }
    },

    /**
     * Bulk print mixed documents
     */
    async onBulkPrintMixed() {
        const selectedRecords = await this.getSelectedResIds();
        if (!selectedRecords.length) {
            this.notification.add(_t("Please select at least one document to print."), {
                type: "warning",
            });
            return;
        }
        
        try {
            await this.orm.call(
                "account.move",
                "action_bulk_print_mixed",
                [],
                { context: { active_ids: selectedRecords } }
            );
        } catch (error) {
            this.notification.add(
                _t("Error printing documents: %s", error.message),
                { type: "danger" }
            );
        }
    },
});

// Custom List View for Enhanced Bulk Print Experience
export class OSUSBulkPrintListController extends ListController {
    setup() {
        super.setup();
        this.displayBulkPrintInfo = this.displayBulkPrintInfo.bind(this);
    }

    get showBulkPrintActions() {
        return this.model.root.selection.length > 0;
    }

    displayBulkPrintInfo() {
        const selectedCount = this.model.root.selection.length;
        if (selectedCount > 0) {
            this.notification.add(
                _t("%s document(s) selected for bulk printing.", selectedCount),
                { type: "info", sticky: false }
            );
        }
    }
}
