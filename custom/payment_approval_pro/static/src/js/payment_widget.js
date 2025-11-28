/** @odoo-module **/

import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

/**
 * Payment Voucher Widget - Modern OWL Component for Odoo 17
 * 
 * Provides interactive payment voucher management with:
 * - Workflow state visualization
 * - Action buttons based on user permissions
 * - Real-time status updates
 * - QR code display and verification
 * - Responsive design for mobile compatibility
 */
export class PaymentVoucherWidget extends Component {
    static template = "payment_approval_pro.PaymentVoucherWidget";
    static props = {
        record: Object,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        // Core services
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.action = useService("action");
        
        // Component state
        this.state = useState({
            isProcessing: false,
            currentState: null,
            workflowData: {},
            canReview: false,
            canApprove: false,
            canAuthorize: false,
            showQRCode: false,
            lastUpdate: null,
        });
        
        // References
        this.widgetRef = useRef("paymentWidget");
        
        // Load initial data
        onWillStart(this.loadWorkflowData);
        
        // Auto-refresh every 30 seconds for real-time updates
        this.refreshInterval = setInterval(() => {
            this.loadWorkflowData(false);
        }, 30000);
    }

    /**
     * Load workflow data and user permissions
     */
    async loadWorkflowData(showLoading = true) {
        if (showLoading) {
            this.state.isProcessing = true;
        }
        
        try {
            const voucherId = this.props.record.resId;
            
            if (!voucherId) {
                return;
            }
            
            // Fetch workflow state and permissions
            const workflowData = await this.orm.call(
                "payment.voucher",
                "get_workflow_state",
                [voucherId]
            );
            
            // Update state
            Object.assign(this.state, {
                currentState: workflowData.state,
                workflowData: workflowData,
                canReview: workflowData.can_review || false,
                canApprove: workflowData.can_approve || false,
                canAuthorize: workflowData.can_authorize || false,
                showQRCode: workflowData.qr_code ? true : false,
                lastUpdate: new Date().toLocaleTimeString(),
            });
            
        } catch (error) {
            console.error("Failed to load workflow data:", error);
            this.notification.add(
                _t("Failed to load workflow data: %s", error.message || error),
                { type: "danger", sticky: false }
            );
        } finally {
            this.state.isProcessing = false;
        }
    }

    /**
     * Submit voucher for review
     */
    async onSubmitForReview() {
        if (this.state.isProcessing) return;
        
        this.state.isProcessing = true;
        
        try {
            await this.orm.call(
                "payment.voucher",
                "action_submit_for_review",
                [this.props.record.resId]
            );
            
            await this._refreshRecordAndWidget();
            
            this.notification.add(
                _t("Payment voucher submitted for review successfully"),
                { type: "success" }
            );
            
        } catch (error) {
            this._handleActionError("submit for review", error);
        } finally {
            this.state.isProcessing = false;
        }
    }

    /**
     * Approve voucher
     */
    async onApprove() {
        if (!this.state.canApprove || this.state.isProcessing) return;
        
        this.dialog.add(ConfirmationDialog, {
            title: _t("Approve Payment Voucher"),
            body: _t("Are you sure you want to approve this payment voucher? This will send it for authorization."),
            confirm: async () => {
                await this._performApproval();
            },
            confirmLabel: _t("Approve"),
            confirmClass: "btn-success",
        });
    }

    async _performApproval() {
        this.state.isProcessing = true;
        
        try {
            await this.orm.call(
                "payment.voucher",
                "action_approve",
                [this.props.record.resId]
            );
            
            await this._refreshRecordAndWidget();
            
            this.notification.add(
                _t("Payment voucher approved successfully"),
                { type: "success" }
            );
            
        } catch (error) {
            this._handleActionError("approve", error);
        } finally {
            this.state.isProcessing = false;
        }
    }

    /**
     * Authorize voucher and create payment
     */
    async onAuthorize() {
        if (!this.state.canAuthorize || this.state.isProcessing) return;
        
        const voucher = this.state.workflowData;
        const amountFormatted = this._formatAmount(voucher.amount, voucher.currency_symbol);
        
        this.dialog.add(ConfirmationDialog, {
            title: _t("Authorize Payment"),
            body: _t(
                "Are you sure you want to authorize this payment of %s to %s? " +
                "This will create the actual payment entry in the accounting system.",
                amountFormatted,
                voucher.partner_name || "Unknown"
            ),
            confirm: async () => {
                await this._performAuthorization();
            },
            confirmLabel: _t("Authorize Payment"),
            confirmClass: "btn-primary",
        });
    }

    async _performAuthorization() {
        this.state.isProcessing = true;
        
        try {
            const result = await this.orm.call(
                "payment.voucher",
                "action_authorize",
                [this.props.record.resId]
            );
            
            await this._refreshRecordAndWidget();
            
            this.notification.add(
                _t("Payment authorized and posted successfully"),
                { type: "success" }
            );
            
            // Optionally redirect to payment view
            if (result && result.res_id) {
                this.notification.add(
                    _t("Click here to view the created payment"),
                    { 
                        type: "info",
                        sticky: true,
                        buttons: [{
                            name: _t("View Payment"),
                            primary: true,
                            onClick: () => this._openPaymentRecord(result.res_id)
                        }]
                    }
                );
            }
            
        } catch (error) {
            this._handleActionError("authorize", error);
        } finally {
            this.state.isProcessing = false;
        }
    }

    /**
     * Cancel voucher
     */
    async onCancel() {
        if (this.state.isProcessing) return;
        
        this.dialog.add(ConfirmationDialog, {
            title: _t("Cancel Payment Voucher"),
            body: _t("Are you sure you want to cancel this payment voucher? This action cannot be undone."),
            confirm: async () => {
                await this._performCancellation();
            },
            confirmLabel: _t("Cancel Voucher"),
            confirmClass: "btn-danger",
        });
    }

    async _performCancellation() {
        this.state.isProcessing = true;
        
        try {
            await this.orm.call(
                "payment.voucher",
                "action_cancel",
                [this.props.record.resId]
            );
            
            await this._refreshRecordAndWidget();
            
            this.notification.add(
                _t("Payment voucher cancelled successfully"),
                { type: "warning" }
            );
            
        } catch (error) {
            this._handleActionError("cancel", error);
        } finally {
            this.state.isProcessing = false;
        }
    }

    /**
     * Print voucher report
     */
    async onPrintVoucher() {
        if (this.state.isProcessing) return;
        
        try {
            await this.action.doAction({
                type: "ir.actions.report",
                report_name: "payment_approval_pro.action_report_payment_voucher",
                report_type: "qweb-pdf",
                data: {
                    model: "payment.voucher",
                    ids: [this.props.record.resId],
                },
                context: this.env.context,
            });
            
        } catch (error) {
            this.notification.add(
                _t("Failed to print voucher: %s", error.message || error),
                { type: "danger" }
            );
        }
    }

    /**
     * Toggle QR code display
     */
    onToggleQRCode() {
        this.state.showQRCode = !this.state.showQRCode;
    }

    /**
     * Open QR verification URL
     */
    onVerifyQRCode() {
        if (this.state.workflowData.qr_verification_url) {
            window.open(this.state.workflowData.qr_verification_url, '_blank');
        }
    }

    /**
     * Refresh record data and widget state
     */
    async _refreshRecordAndWidget() {
        // Refresh the main record
        await this.props.record.load();
        
        // Refresh widget data
        await this.loadWorkflowData(false);
    }

    /**
     * Handle action errors consistently
     */
    _handleActionError(action, error) {
        console.error(`Payment ${action} failed:`, error);
        
        let errorMessage = error.message || error;
        
        // Handle specific error types
        if (error.data && error.data.message) {
            errorMessage = error.data.message;
        } else if (typeof error === 'string') {
            errorMessage = error;
        }
        
        this.notification.add(
            _t("Failed to %s payment voucher: %s", action, errorMessage),
            { type: "danger", sticky: true }
        );
    }

    /**
     * Format amount for display
     */
    _formatAmount(amount, currencySymbol = '$') {
        if (typeof amount !== 'number') {
            return `${currencySymbol}0.00`;
        }
        
        return `${currencySymbol}${amount.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    }

    /**
     * Open payment record
     */
    async _openPaymentRecord(paymentId) {
        try {
            await this.action.doAction({
                type: "ir.actions.act_window",
                name: _t("Payment Entry"),
                res_model: "account.payment",
                res_id: paymentId,
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
            });
        } catch (error) {
            this.notification.add(
                _t("Failed to open payment record: %s", error.message),
                { type: "warning" }
            );
        }
    }

    /**
     * Get state badge class
     */
    getStateBadgeClass() {
        const stateClasses = {
            'draft': 'badge-secondary',
            'review': 'badge-primary',
            'approve': 'badge-warning',
            'authorize': 'badge-info',
            'paid': 'badge-success',
            'cancel': 'badge-danger',
        };
        
        return stateClasses[this.state.currentState] || 'badge-secondary';
    }

    /**
     * Get state display text
     */
    getStateDisplayText() {
        const stateTexts = {
            'draft': _t('Draft'),
            'review': _t('Under Review'),
            'approve': _t('Approved'),
            'authorize': _t('Authorized'),
            'paid': _t('Paid'),
            'cancel': _t('Cancelled'),
        };
        
        return stateTexts[this.state.currentState] || _t('Unknown');
    }

    /**
     * Cleanup on component destroy
     */
    willUnmount() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Register the widget
registry.category("fields").add("payment_voucher_widget", PaymentVoucherWidget);
