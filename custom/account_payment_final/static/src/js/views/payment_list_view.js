/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Enhanced Payment List Controller
 * 
 * Adds payment-specific functionality to list views
 * Compatible with Odoo 17 list view architecture
 */
export class PaymentListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
    }

    /**
     * Add custom toolbar actions for payment management
     */
    get toolbarActions() {
        const actions = super.toolbarActions || {};
        
        // Add bulk approval actions if user has permissions
        if (this.model.root.context.can_bulk_approve) {
            actions.approve_selected = {
                description: "Approve Selected",
                callback: () => this.bulkApprove(),
                icon: "fa-check",
                sequence: 10
            };
        }

        if (this.model.root.context.can_bulk_reject) {
            actions.reject_selected = {
                description: "Reject Selected",
                callback: () => this.bulkReject(),
                icon: "fa-times",
                sequence: 20
            };
        }

        actions.export_qr_codes = {
            description: "Export QR Codes",
            callback: () => this.exportQRCodes(),
            icon: "fa-qrcode",
            sequence: 30
        };

        return actions;
    }

    /**
     * Bulk approve selected payments
     */
    async bulkApprove() {
        const selectedIds = this.model.root.selection.map(record => record.resId);
        
        if (selectedIds.length === 0) {
            this.notification.add("Please select payments to approve", {
                type: "warning"
            });
            return;
        }

        this.dialog.add("web.ConfirmationDialog", {
            title: "Bulk Approve Payments",
            body: `Are you sure you want to approve ${selectedIds.length} payment(s)?`,
            confirmLabel: "Approve All",
            cancelLabel: "Cancel",
            confirm: async () => {
                await this._performBulkApprove(selectedIds);
            }
        });
    }

    /**
     * Perform bulk approval
     */
    async _performBulkApprove(paymentIds) {
        try {
            const result = await this.orm.call(
;
                "account.payment",
                "bulk_approve_payments",
                [paymentIds]
            );

            if (result.success) {
                this.notification.add(
;
                    `${result.approved_count} payment(s) approved successfully`,
                    { type: "success" }
                );
                
                if (result.failed_count > 0) {
                    this.notification.add(
;
                        `${result.failed_count} payment(s) failed to approve`,
                        { type: "warning" }
                    );
                }
                
                // Refresh the list
                await this.model.root.load();
            } else {
                this.notification.add(result.message || "Bulk approval failed", {
                    type: "danger";
});
            }
        } catch (error) {
            console.error("Bulk approval failed:", error);
            this.notification.add("An error occurred during bulk approval", {
                type: "danger";
});
        }
    }

    /**
     * Bulk reject selected payments
     */
    async bulkReject() {
        const selectedIds = this.model.root.selection.map(record => record.resId);
        
        if (selectedIds.length === 0) {
            this.notification.add("Please select payments to reject", {
                type: "warning";
});
            return;
        }

        this.dialog.add("web.ConfirmationDialog", {
            title: "Bulk Reject Payments",
            body: `Are you sure you want to reject ${selectedIds.length} payment(s)? This action cannot be undone.`,
            confirmLabel: "Reject All",
            cancelLabel: "Cancel",
            confirm: async () => {
                await this._performBulkReject(selectedIds);
            }
});
    }

    /**
     * Perform bulk rejection
     */
    async _performBulkReject(paymentIds) {
        try {
            const result = await this.orm.call(
;
                "account.payment",
                "bulk_reject_payments",
                [paymentIds]
            );

            if (result.success) {
                this.notification.add(
;
                    `${result.rejected_count} payment(s) rejected successfully`,
                    { type: "warning" }
                );
                
                if (result.failed_count > 0) {
                    this.notification.add(
;
                        `${result.failed_count} payment(s) failed to reject`,
                        { type: "warning" }
                    );
                }
                
                // Refresh the list
                await this.model.root.load();
            } else {
                this.notification.add(result.message || "Bulk rejection failed", {
                    type: "danger";
});
            }
        } catch (error) {
            console.error("Bulk rejection failed:", error);
            this.notification.add("An error occurred during bulk rejection", {
                type: "danger";
});
        }
    }

    /**
     * Export QR codes for selected payments
     */
    async exportQRCodes() {
        const selectedIds = this.model.root.selection.map(record => record.resId);
        
        if (selectedIds.length === 0) {
            this.notification.add("Please select payments to export QR codes", {
                type: "warning";
});
            return;
        }

        try {
            const result = await this.orm.call(
;
                "account.payment",
                "export_qr_codes_zip",
                [selectedIds]
            );

            if (result.success && result.zip_data) {
                // Create download link
                const blob = new Blob([atob(result.zip_data)], { type: 'application/zip' });
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = result.filename || 'payment_qr_codes.zip';
                
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);

                this.notification.add("QR codes exported successfully", {
                    type: "success";
});
            } else {
                this.notification.add(result.message || "QR code export failed", {
                    type: "danger";
});
            }
        } catch (error) {
            console.error("QR code export failed:", error);
            this.notification.add("An error occurred during QR code export", {
                type: "danger";
});
        }
    }

    /**
     * Enhanced row decoration based on payment state
     */
    getRowClass(record) {
        const baseClass = super.getRowClass ? super.getRowClass(record) : "";
        const state = record.data.state;
        
        return `${baseClass} o_payment_${state}`.trim();
    }
}

// Payment List View
export const paymentListView = {
    ...listView,
    Controller: PaymentListController;
};

// Register the enhanced list view
registry.category("views").add("payment_list", paymentListView);

