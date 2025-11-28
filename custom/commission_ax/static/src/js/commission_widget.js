/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CommissionWidget extends Component {
  constructor() {
    super(...arguments);
    // Global error boundary for CloudPepper
    window.addEventListener("error", (event) => {
      if (event.error) {
        this.notification.add(_t(`Global JS error: ${event.error.message}`), {
          type: "danger",
        });
      }
    });
    window.addEventListener("unhandledrejection", (event) => {
      this.notification.add(
        _t(`Unhandled promise rejection: ${event.reason}`),
        { type: "danger" }
      );
    });
  }
  static template = "commission_ax.CommissionWidget";
  static props = ["*"];

  setup() {
    this.orm = useService("orm");
    this.notification = useService("notification");

    this.state = useState({
      commissionData: null,
      isCalculating: false,
    });

    onMounted(() => {
      this.loadCommissionData();
    });
  }

  async loadCommissionData() {
    try {
      const data = await this.orm.call("commission.ax", "get_commission_data", [
        this.props.recordId,
      ]);
      this.state.commissionData = data;
    } catch (error) {
      console.error("Commission error:", error);
      this.notification.add(_t("Failed to load commission data"), {
        type: "danger",
      });
    }
  }

  async calculateCommission() {
    try {
      this.state.isCalculating = true;
      await this.orm.call("commission.ax", "calculate_commission", [
        this.props.recordId,
      ]);
      await this.loadCommissionData();
      this.notification.add(_t("Commission calculated successfully"), {
        type: "success",
      });
    } catch (error) {
      this.notification.add(_t("Failed to calculate commission"), {
        type: "danger",
      });
    } finally {
      this.state.isCalculating = false;
    }
  }
}

registry.category("fields").add("commission_widget", CommissionWidget);
