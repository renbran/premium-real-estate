/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class OrderStatusWidget extends Component {
    static template = "order_status_override.StatusWidget";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            orderStatus: null,
            isLoading: false
        });
        
        onMounted(() => {
            this.loadOrderStatus();
        });
    }
    
    async loadOrderStatus() {
        try {
            this.state.isLoading = true;
            const status = await this.orm.call("sale.order", "get_order_status", [this.props.orderId]);
            this.state.orderStatus = status;
        } catch (error) {
            console.error("Order status error:", error);
            this.notification.add(_t("Failed to load order status"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    async onStatusChange(newStatus) {
        try {
            await this.orm.call("sale.order", "update_status", [this.props.orderId, newStatus]);
            await this.loadOrderStatus();
            this.notification.add(_t("Status updated successfully"), { type: "success" });
        } catch (error) {
            this.notification.add(_t("Failed to update status"), { type: "danger" });
        }
    }
}

registry.category("fields").add("order_status_widget", OrderStatusWidget);
