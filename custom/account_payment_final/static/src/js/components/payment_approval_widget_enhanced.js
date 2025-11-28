/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

// OSUS Properties Brand Colors
const brandColors = {
    primary: '#800020',
    gold: '#FFD700',
    lightGold: '#FFF8DC',
    darkGold: '#B8860B',
    white: '#FFFFFF',
    accent: '#A0522D',
    
    chartColors: [
        '#800020',
        '#FFD700',
        '#A0522D',
    ],
    
    chartBackgrounds: [
        '#80002020',
        '#FFD70020',
        '#A0522D20',
    ]
};

/**
 * Enhanced Payment Approval Widget Component
 * 
 * OWL Component for displaying and managing payment approval workflow
 * Enhanced with modern patterns, error handling, and accessibility
 * Compatible with Odoo 17 OWL framework and CloudPepper deployment
 */
export class PaymentApprovalWidgetEnhanced extends Component {
    static template = "account_payment_final.PaymentApprovalWidget";
    static props = {
        readonly: { type: Boolean, optional: true },
        record: Object,
        update: Function,
    };

    setup() {
        // Core services
        this.orm = useService("orm");
        this.user = useService("user");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.action = useService("action");
        
        // Enhanced state management
        this.state = useState({
            // Core workflow state
            currentStage: null,
            approvalStages: [],
            approvalState: this.props.record.data.approval_state || 'draft',
            
            // Permission states
            canApprove: false,
            canReject: false,
            canSubmit: false,
            canAuthorize: false,
            
            // UI states
            isLoading: false,
            hasError: false,
            errorMessage: '',
            isSuccess: false,
            successMessage: '',
            
            // Data states
            approvalHistory: [],
            nextActions: [],
            workflowConfig: null;
});

        // Bind event handlers
        this.onApprovalAction = this.onApprovalAction.bind(this);
        this.onRejectAction = this.onRejectAction.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);

        onWillStart(async () => {
            await this.loadApprovalData();
        });

        onMounted(() => {
            this.setupAccessibility();
        });
    }

    /**
     * Enhanced approval data loading with better error handling
     */
    async loadApprovalData() {
        if (!this.props.record.resId) {
            this.state.approvalStages = this.getFallbackStages();
            return;
        }

        this.state.isLoading = true;
        this.state.hasError = false;
        
        try {
            const result = await this.orm.call(
;
                "account.payment",
                "get_approval_workflow_data",
                [this.props.record.resId],
                {
                    context: this.user.context;
}
            );

            // Update state with backend data
            this.state.approvalStages = result.stages || this.getFallbackStages();
            this.state.currentStage = result.current_stage;
            this.state.canApprove = result.can_approve || false;
            this.state.canReject = result.can_reject || false;
            this.state.canSubmit = result.can_submit || false;
            this.state.canAuthorize = result.can_authorize || false;
            this.state.approvalHistory = result.approval_history || [];
            this.state.nextActions = result.next_actions || [];
            this.state.workflowConfig = result.workflow_config || null;
            
        } catch (error) {
            console.warn("Approval data loading failed, using fallback:", error.message);
            
            // Enhanced fallback handling
            this.state.approvalStages = this.getFallbackStages();
            this.state.canApprove = this._checkFallbackPermissions('approve');
            this.state.canReject = this._checkFallbackPermissions('reject');
            this.state.canSubmit = this._checkFallbackPermissions('submit');
            
            // Only show notification for critical errors
            if (error.status && error.status !== 404 && !error.message.includes('method not found')) {
                this.state.hasError = true;
                this.state.errorMessage = _t("Failed to load approval workflow data");
                
                this.notification.add(this.state.errorMessage, {
                    type: "warning",
                    sticky: false;
});
            }
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Enhanced fallback stages with better state detection
     */
    getFallbackStages() {
        const currentState = this.props.record.data.approval_state || 
;
                           this.props.record.data.state || 'draft';
        const paymentType = this.props.record.data.payment_type || 'outbound';
        
        // Define workflow stages based on payment type
        const vendorStages = [
            { id: 'draft', name: 'Draft', icon: 'fa-edit', color: 'secondary' },
            { id: 'under_review', name: 'Under Review', icon: 'fa-search', color: 'info' },
            { id: 'for_approval', name: 'For Approval', icon: 'fa-check', color: 'warning' },
            { id: 'for_authorization', name: 'For Authorization', icon: 'fa-key', color: 'warning' },
            { id: 'approved', name: 'Approved', icon: 'fa-check-circle', color: 'success' },
            { id: 'posted', name: 'Posted', icon: 'fa-check-circle', color: 'success' }
        ];
        
        const customerStages = [
            { id: 'draft', name: 'Draft', icon: 'fa-edit', color: 'secondary' },
            { id: 'under_review', name: 'Under Review', icon: 'fa-search', color: 'info' },
            { id: 'for_approval', name: 'For Approval', icon: 'fa-check', color: 'warning' },
            { id: 'approved', name: 'Approved', icon: 'fa-check-circle', color: 'success' },
            { id: 'posted', name: 'Posted', icon: 'fa-check-circle', color: 'success' }
        ];
        
        const stages = paymentType === 'outbound' ? vendorStages : customerStages;
        const currentIndex = stages.findIndex(stage => stage.id === currentState);
        
        return stages.map((stage, index) => ({
            ...stage,
            status: this._getStageStatus(index, currentIndex),
            is_current: index === currentIndex,
            is_completed: index < currentIndex,
            is_pending: index > currentIndex
;
        }));
    }

    /**
     * Get stage status based on current position
     */
    _getStageStatus(stageIndex, currentIndex) {
        if (stageIndex < currentIndex) return 'completed';
        if (stageIndex === currentIndex) return 'current';
        return 'pending';
    }

    /**
     * Check fallback permissions based on user groups
     */
    _checkFallbackPermissions(action) {
        const currentState = this.props.record.data.approval_state || 'draft';
        const userGroups = this.user.context.user_groups || [];
        
        // Check if user has manager permissions
        const isManager = userGroups.includes('account_payment_final.group_payment_voucher_manager') ||
;
                         userGroups.includes('account.group_account_manager');
        
        // Basic permission logic
        switch (action) {
            case 'submit':
;
                return currentState === 'draft';
            case 'approve':
;
                return isManager && ['under_review', 'for_approval', 'for_authorization'].includes(currentState);
            case 'reject':
;
                return isManager && ['under_review', 'for_approval', 'for_authorization'].includes(currentState);
            default:
;
                return false;
        }
    }

    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        const widget = this.el;
        if (!widget) return;
        
        // Add ARIA labels
        widget.setAttribute('role', 'region');
        widget.setAttribute('aria-label', _t('Payment Approval Workflow'));
        
        // Setup keyboard navigation
        widget.addEventListener('keydown', this.handleKeyPress);
        
        // Focus management
        const buttons = widget.querySelectorAll('.btn');
        buttons.forEach((button, index) => {
            button.setAttribute('tabindex', index === 0 ? '0' : '-1');
        });
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyPress(event) {
        if (this.props.readonly) return;
        
        const buttons = this.el.querySelectorAll('.btn:not(:disabled)');
        const currentIndex = Array.from(buttons).findIndex(btn => btn === document.activeElement);
        
        switch (event.key) {
            case 'ArrowLeft':
;
            case 'ArrowUp':
;
                event.preventDefault();
                const prevIndex = currentIndex > 0 ? currentIndex - 1 : buttons.length - 1;
                buttons[prevIndex]?.focus();
                break;
                
            case 'ArrowRight':
;
            case 'ArrowDown':
;
                event.preventDefault();
                const nextIndex = currentIndex < buttons.length - 1 ? currentIndex + 1 : 0;
                buttons[nextIndex]?.focus();
                break;
                
            case 'Enter':
;
            case ' ':
;
                event.preventDefault();
                document.activeElement?.click();
                break;
        }
    }

    /**
     * Enhanced approval action handler
     */
    async onApprovalAction(actionType) {
        if (this.props.readonly || this.state.isLoading) return;
        
        // Validate action permissions
        if (!this._validateActionPermission(actionType)) {
            this.notification.add(_t("You don't have permission to perform this action"), {
                type: "warning";
});
            return;
        }

        this.state.isLoading = true;
        this.state.hasError = false;
        
        try {
            const methodMap = {
                'submit': 'action_submit_for_review',
                'review': 'action_review_payment', 
                'approve': 'action_approve_payment',
                'authorize': 'action_authorize_payment',
                'post': 'action_post_payment'
;
            };
            
            const method = methodMap[actionType];
            if (!method) {
                throw new Error(_t("Unknown action type: %s", actionType));
            }

            const result = await this.orm.call(
;
                "account.payment",
                method,
                [this.props.record.resId],
                {
                    context: this.user.context;
}
            );

            // Handle different response formats
            if (result.success !== false) {
                this.state.isSuccess = true;
                this.state.successMessage = result.message || _t("Action completed successfully");
                
                this.notification.add(this.state.successMessage, {
                    type: "success";
});
                
                // Update record and reload data
                await this.props.update();
                await this.loadApprovalData();
                
                // Auto-clear success state
                setTimeout(() => {
                    this.state.isSuccess = false;
                    this.state.successMessage = '';
                }, 3000);
            } else {
                throw new Error(result.message || _t("Action failed"));
            }
            
        } catch (error) {
            console.error("Approval action failed:", error);
            
            this.state.hasError = true;
            this.state.errorMessage = error.message || _t("An error occurred while processing the action");
            
            this.notification.add(this.state.errorMessage, {
                type: "danger";
});
            
            // Auto-clear error state
            setTimeout(() => {
                this.state.hasError = false;
                this.state.errorMessage = '';
            }, 5000);
            
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Enhanced rejection handler with confirmation
     */
    async onRejectAction() {
        if (this.props.readonly || this.state.isLoading) return;

        // Show confirmation dialog
        this.dialog.add("web.ConfirmationDialog", {
            title: _t("Reject Payment"),
            body: _t("Are you sure you want to reject this payment? This action cannot be undone."),
            confirmLabel: _t("Reject"),
            cancelLabel: _t("Cancel"),
            confirm: async () => {
                await this.onApprovalAction('reject');
            }
});
    }

    /**
     * Validate action permission
     */
    _validateActionPermission(actionType) {
        switch (actionType) {
            case 'submit':
;
                return this.state.canSubmit;
            case 'approve':
;
                return this.state.canApprove;
            case 'authorize':
;
                return this.state.canAuthorize;
            case 'reject':
;
                return this.state.canReject;
            default:
;
                return false;
        }
    }

    /**
     * Get CSS classes for widget state
     */
    getWidgetClasses() {
        const classes = ['o_payment_approval_widget'];
        
        if (this.props.readonly) classes.push('o_readonly');
        if (this.state.isLoading) classes.push('o_loading');
        if (this.state.hasError) classes.push('o_error');
        if (this.state.isSuccess) classes.push('o_success');
        
        return classes.join(' ');
    }

    /**
     * Get approval stage configuration
     */
    getStageConfig(stage) {
        const config = {
            name: stage.name || stage.id,
            icon: stage.icon || 'fa-circle',
            color: stage.color || 'secondary'
;
        };
        
        return config;
    }

    /**
     * Get available actions for current state
     */
    getAvailableActions() {
        const actions = [];
        
        if (this.state.canSubmit) {
            actions.push({
                type: 'submit',
                label: _t('Submit for Review'),
                class: 'btn-info o_btn_submit',
                icon: 'fa-paper-plane'
;
            });
        }
        
        if (this.state.canApprove) {
            actions.push({
                type: 'approve',
                label: _t('Approve'),
                class: 'btn-success o_btn_approve',
                icon: 'fa-check'
;
            });
        }
        
        if (this.state.canAuthorize) {
            actions.push({
                type: 'authorize',
                label: _t('Authorize'),
                class: 'btn-warning o_btn_authorize',
                icon: 'fa-key'
;
            });
        }
        
        if (this.state.canReject) {
            actions.push({
                type: 'reject',
                label: _t('Reject'),
                class: 'btn-danger o_btn_reject',
                icon: 'fa-times'
;
            });
        }
        
        return actions;
    }
}

// Register the enhanced component
registry.category("fields").add("payment_approval_widget_enhanced", PaymentApprovalWidgetEnhanced);

