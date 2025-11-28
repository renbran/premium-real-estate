/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

// OSUS Properties Brand Colors
const OSUS_COLORS = {
    primary: '#722f37',
    secondary: '#b8860b',
    accent: '#8b3a42',
    light: '#f8f9fa',
    border: '#dee2e6'
};

/**
 * Payment Workflow Controller
 * Handles all payment approval workflow functionality
 */
export class PaymentWorkflowController {
    constructor(orm, notification, dialog) {
        this.orm = orm;
        this.notification = notification;
        this.dialog = dialog;
    }

    /**
     * Submit payment for approval
     */
    async submitForApproval(paymentId) {
        try {
            const result = await this.orm.call(
                'account.payment',
                'action_submit_for_approval',
                [paymentId]
            );
            
            if (result.success) {
                this.notification.add(_t("Payment submitted for approval"), {
                    type: "success"
                });
                return true;
            } else {
                this.notification.add(result.message || _t("Failed to submit payment"), {
                    type: "warning"
                });
                return false;
            }
        } catch (error) {
            this.notification.add(_t("Error submitting payment: ") + error.message, {
                type: "danger"
            });
            return false;
        }
    }

    /**
     * Approve payment
     */
    async approvePayment(paymentId, comments = '') {
        try {
            const result = await this.orm.call(
                'account.payment',
                'action_approve',
                [paymentId],
                { comments }
            );
            
            if (result.success) {
                this.notification.add(_t("Payment approved successfully"), {
                    type: "success"
                });
                return true;
            } else {
                this.notification.add(result.message || _t("Failed to approve payment"), {
                    type: "warning"
                });
                return false;
            }
        } catch (error) {
            this.notification.add(_t("Error approving payment: ") + error.message, {
                type: "danger"
            });
            return false;
        }
    }

    /**
     * Reject payment
     */
    async rejectPayment(paymentId, reason) {
        try {
            const result = await this.orm.call(
                'account.payment',
                'action_reject',
                [paymentId],
                { reason }
            );
            
            if (result.success) {
                this.notification.add(_t("Payment rejected"), {
                    type: "info"
                });
                return true;
            } else {
                this.notification.add(result.message || _t("Failed to reject payment"), {
                    type: "warning"
                });
                return false;
            }
        } catch (error) {
            this.notification.add(_t("Error rejecting payment: ") + error.message, {
                type: "danger"
            });
            return false;
        }
    }

    /**
     * Get approval history
     */
    async getApprovalHistory(paymentId) {
        try {
            return await this.orm.call(
                'account.payment',
                'get_approval_history',
                [paymentId]
            );
        } catch (error) {
            console.error('Error getting approval history:', error);
            return [];
        }
    }
}

/**
 * Payment Approval Widget Component
 * Displays approval workflow with actions
 */
export class PaymentApprovalWidget extends Component {
    static template = "account_payment_final.PaymentApprovalWidget";
    static props = {
        readonly: { type: Boolean, optional: true },
        record: Object,
        update: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        
        this.workflowController = new PaymentWorkflowController(
            this.orm, 
            this.notification, 
            this.dialog
        );
        
        this.state = useState({
            isLoading: false,
            approvalHistory: [],
            canApprove: false,
            canReject: false,
            currentStage: 'draft'
        });

        onWillStart(async () => {
            await this.loadWorkflowData();
        });
    }

    async loadWorkflowData() {
        if (!this.props.record.resId) return;
        
        this.state.isLoading = true;
        try {
            const history = await this.workflowController.getApprovalHistory(
                this.props.record.resId
            );
            this.state.approvalHistory = history;
            this.state.currentStage = this.props.record.data.state || 'draft';
            this.state.canApprove = this.props.record.data.can_approve || false;
            this.state.canReject = this.props.record.data.can_reject || false;
        } catch (error) {
            console.error('Error loading workflow data:', error);
        } finally {
            this.state.isLoading = false;
        }
    }

    async onApprove() {
        if (!this.props.record.resId) return;
        
        const success = await this.workflowController.approvePayment(
            this.props.record.resId
        );
        
        if (success) {
            await this.props.update();
            await this.loadWorkflowData();
        }
    }

    async onReject() {
        if (!this.props.record.resId) return;
        
        this.dialog.add("web.PromptDialog", {
            title: _t("Reject Payment"),
            body: _t("Please provide a reason for rejection:"),
            confirmLabel: _t("Reject"),
            cancelLabel: _t("Cancel"),
            confirm: async (reason) => {
                if (!reason.trim()) {
                    this.notification.add(_t("Rejection reason is required"), {
                        type: "warning"
                    });
                    return;
                }
                
                const success = await this.workflowController.rejectPayment(
                    this.props.record.resId,
                    reason
                );
                
                if (success) {
                    await this.props.update();
                    await this.loadWorkflowData();
                }
            }
        });
    }

    getStageIcon(stage) {
        const icons = {
            'draft': 'fa-edit',
            'under_review': 'fa-search',
            'approved': 'fa-check',
            'authorized': 'fa-shield',
            'posted': 'fa-check-circle',
            'rejected': 'fa-times'
        };
        return icons[stage] || 'fa-circle';
    }

    getStageColor(stage) {
        const colors = {
            'draft': 'text-secondary',
            'under_review': 'text-info',
            'approved': 'text-success',
            'authorized': 'text-primary',
            'posted': 'text-success',
            'rejected': 'text-danger'
        };
        return colors[stage] || 'text-muted';
    }
}

// Register the component
registry.category("fields").add("payment_approval_widget", PaymentApprovalWidget);

/**
 * Global error handler for CloudPepper compatibility
 */
window.addEventListener('error', function(event) {
    if (event.message && event.message.includes('payment_workflow')) {
        console.warn('[PaymentWorkflow] Error handled:', event.message);
        event.preventDefault();
        return false;
    }
});

console.log('[PaymentWorkflow] Modern Odoo 17 payment workflow loaded successfully');
