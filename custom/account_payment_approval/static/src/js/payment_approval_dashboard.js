/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class PaymentApprovalDashboard extends Component {
    static template = "account_payment_approval.PaymentApprovalDashboard";
    static props = {
        record: Object,
        name: String;
};

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            isLoading: true,
            stats: {},
            userPermissions: {},
            recentPayments: [],
            error: null;
});

        onWillStart(this.loadDashboardData);
    }

    async loadDashboardData() {
        this.state.isLoading = true;
        this.state.error = null;

        try {
            // Load approval statistics
            const statsResult = await this.orm.call(;
                "account.payment",
                "get_approval_dashboard_data",
                []
            );

            if (statsResult.success) {
                this.state.stats = statsResult.stats;
                this.state.userPermissions = statsResult.user_permissions;
                this.state.recentPayments = statsResult.recent_payments || [];
            } else {
                throw new Error(statsResult.error || _t("Failed to load dashboard data"));
            }

        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = error.message || _t("Failed to load dashboard data");
            this.notification.add(;
                _t("Error loading dashboard: %s", this.state.error),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    async refreshDashboard() {
        await this.loadDashboardData();
        this.notification.add(_t("Dashboard refreshed"), { type: "success" });
    }

    async openPaymentList(domain, title) {
        try {
            await this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'account.payment',
                name: title,
                view_mode: 'tree,form',
                views: [[false, 'tree'], [false, 'form']],
                domain: domain,
                context: {
                    'default_payment_type': 'outbound';
},
                target: 'current';
});
        } catch (error) {
            console.error("Error opening payment list:", error);
            this.notification.add(;
                _t("Failed to open payment list"),
                { type: "danger" }
            );
        }
    }

    onPendingReviewClick() {
        this.openPaymentList(;
            [['voucher_state', '=', 'submitted']],
            _t("Payments Pending Review");
        );
    }

    onPendingApprovalClick() {
        this.openPaymentList(;
            [['voucher_state', '=', 'under_review']],
            _t("Payments Pending Approval");
        );
    }

    onPendingAuthorizationClick() {
        this.openPaymentList(;
            [['voucher_state', '=', 'approved']],
            _t("Payments Pending Authorization");
        );
    }

    onPendingPostingClick() {
        this.openPaymentList(;
            [['voucher_state', '=', 'authorized']],
            _t("Payments Pending Posting");
        );
    }

    onMyPaymentsClick() {
        this.openPaymentList(;
            [['create_uid', '=', this.env.services.user.userId]],
            _t("My Payments");
        );
    }

    async onQuickAction(paymentId, action) {
        try {
            const result = await this.orm.call(;
                "account.payment",
                `action_${action}`,
                [paymentId]
            );

            if (result) {
                this.notification.add(;
                    _t("Action completed successfully"),
                    { type: "success" }
                );
                await this.loadDashboardData(); // Refresh data;
            } else {
                throw new Error(_t("Action failed"));
            }

        } catch (error) {
            console.error(`Error performing ${action}:`, error);
            this.notification.add(;
                _t("Failed to perform action: %s", error.message || error),
                { type: "danger" }
            );
        }
    }

    async openPaymentForm(paymentId) {
        try {
            await this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'account.payment',
                res_id: paymentId,
                name: _t("Payment"),
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'current';
});
        } catch (error) {
            console.error("Error opening payment form:", error);
            this.notification.add(;
                _t("Failed to open payment"),
                { type: "danger" }
            );
        }
    }

    getStateLabel(state) {
        const stateLabels = {
            'draft': _t('Draft'),
            'submitted': _t('Submitted'),
            'reviewed': _t('Reviewed'),
            'approved': _t('Approved'),
            'authorized': _t('Authorized'),
            'posted': _t('Posted'),
            'rejected': _t('Rejected');
};
        return stateLabels[state] || state;
    }

    getStateBadgeClass(state) {
        const badgeClasses = {
            'draft': 'badge-secondary',
            'submitted': 'badge-info',
            'reviewed': 'badge-primary',
            'approved': 'badge-warning',
            'authorized': 'badge-success',
            'posted': 'badge-success',
            'rejected': 'badge-danger';
};
        return `badge ${badgeClasses[state] || 'badge-secondary'}`;
    }

    canPerformAction(payment, action) {
        const permissions = this.state.userPermissions;
        
        switch (action) {
            case 'review':;
                return payment.voucher_state === 'submitted' && permissions.can_review;
            case 'approve':;
                return payment.voucher_state === 'under_review' && permissions.can_approve;
            case 'authorize':;
                return payment.voucher_state === 'approved' && permissions.can_authorize;
            case 'post':;
                return payment.voucher_state === 'authorized' && permissions.can_post;
            default:;
                return false;
        }
    }

    get hasPermissions() {
        const perms = this.state.userPermissions;
        return perms.can_submit || perms.can_review || perms.can_approve || ;
               perms.can_authorize || perms.can_post || perms.is_manager;
    }

    get totalPendingCount() {
        const stats = this.state.stats;
        return (stats.pending_review || 0) + ;
               (stats.pending_approval || 0) + ;
               (stats.pending_authorization || 0) + ;
               (stats.pending_posting || 0);
    }
}

// Register the dashboard widget
registry.category("fields").add("payment_approval_dashboard", PaymentApprovalDashboard);

