/** @odoo-module **/
/**
 * Payment Workflow Real-time Handler
 * Real-time updates and CloudPepper-specific event handling
 */

import { Component, useState, onWillDestroy } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PaymentWorkflowRealtime extends Component {
  constructor() {
    super(...arguments);
    // Global error boundary for CloudPepper
    window.addEventListener("error", (event) => {
      if (event.error) {
        this.state.errorCount++;
        this.notification.add(`Global JS error: ${event.error.message}`, {
          type: "danger",
        });
        this.handleError(event.error);
      }
    });
    window.addEventListener("unhandledrejection", (event) => {
      this.state.errorCount++;
      this.notification.add(`Unhandled promise rejection: ${event.reason}`, {
        type: "danger",
      });
      this.handleError(event.reason);
    });
  }
  static template = "account_payment_final.PaymentWorkflowRealtime";
  static props = ["*"];

  setup() {
    this.orm = useService("orm");
    this.notification = useService("notification");
    this.state = useState({
      isConnected: false,
      lastUpdate: null,
      errorCount: 0,
    });

    // CloudPepper-specific initialization
    this.initializeCloudPepperHandlers();

    onWillDestroy(() => {
      this.cleanup();
    });
  }

  initializeCloudPepperHandlers() {
    try {
      // Real-time status monitoring for CloudPepper
      this.statusInterval = setInterval(() => {
        this.checkPaymentStatus();
      }, 5000); // Check every 5 seconds

      this.state.isConnected = true;
      console.log("[CloudPepper] Real-time handlers initialized");
    } catch (error) {
      console.error("[CloudPepper] Handler initialization error:", error);
      this.state.errorCount++;
      this.handleError(error);
    }
  }

  async checkPaymentStatus() {
    try {
      if (!this.props.paymentId) return;

      const result = await this.orm.call(
        "account.payment",
        "get_realtime_status",
        [this.props.paymentId]
      );

      if (result && result.status_changed) {
        this.state.lastUpdate = new Date().toLocaleTimeString();
        this.notification.add("Payment status updated", { type: "info" });
      }
    } catch (error) {
      console.error("[CloudPepper] Status check error:", error);
      this.handleError(error);
    }
  }

  handleError(error) {
    this.state.errorCount++;
    if (this.state.errorCount > 3) {
      // Stop real-time updates if too many errors
      this.cleanup();
      this.notification.add(
        "Real-time updates disabled due to connection issues",
        { type: "warning" }
      );
    }
  }

  cleanup() {
    if (this.statusInterval) {
      clearInterval(this.statusInterval);
      this.statusInterval = null;
    }
    this.state.isConnected = false;
    console.log("[CloudPepper] Real-time handlers cleaned up");
  }
}

// Register component for CloudPepper
console.log("[CloudPepper] Payment workflow real-time handler loaded");
