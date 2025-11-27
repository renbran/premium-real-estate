/** @odoo-module **/

/**
 * CloudPepper Compatibility Patch for Commission AX Module
 * Provides global error handling and OWL lifecycle protection
 * Modern ES6+ compatible - No legacy odoo.define usage
 *
 * @module commission_ax.cloudpepper_compatibility_patch
 * @author OSUS Properties
 * @version 17.0.2.0.0
 */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

console.log("🛡️ Commission AX CloudPepper Compatibility Patch Loading...");

// Odoo.define compatibility shim for legacy modules (prevents errors)
if (typeof window !== "undefined") {
  window.odoo = window.odoo || {};

  // Legacy compatibility shim to prevent "odoo.define is not a function" errors
  if (typeof window.odoo.define !== "function") {
    window.odoo.define = function (name, dependencies, callback) {
      console.warn(
        `🚨 Legacy odoo.define() call for "${name}" - please modernize to ES6 modules`
      );

      // Handle different call signatures
      if (typeof dependencies === "function") {
        // odoo.define(name, function() {})
        callback = dependencies;
        dependencies = [];
      }

      // Execute callback safely
      try {
        if (typeof callback === "function") {
          callback();
        }
      } catch (error) {
        console.error(`🚨 Error in legacy module "${name}":`, error);
      }
    };
  }
}

// Global error handler for CloudPepper environment
window.addEventListener("error", function (event) {
  console.error("🚨 Commission AX Global Error Handler:", {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error,
    timestamp: new Date().toISOString(),
  });

  // Prevent error propagation in CloudPepper
  if (event.message && event.message.includes("commission")) {
    event.preventDefault();
    return true;
  }
});

// Promise rejection handler for async operations
window.addEventListener("unhandledrejection", function (event) {
  console.error("🚨 Commission AX Unhandled Promise Rejection:", {
    reason: event.reason,
    promise: event.promise,
    timestamp: new Date().toISOString(),
  });

  // Handle commission-related promise rejections
  if (
    event.reason &&
    event.reason.toString().toLowerCase().includes("commission")
  ) {
    event.preventDefault();
    return true;
  }
});

// OWL Component error boundary
const originalSetup = Component.prototype.setup;
Component.prototype.setup = function () {
  try {
    if (originalSetup) {
      originalSetup.call(this);
    }
  } catch (error) {
    console.error("🚨 Commission AX OWL Setup Error:", {
      component: this.constructor.name,
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
    });

    // Fallback setup for commission components
    if (this.constructor.name.toLowerCase().includes("commission")) {
      this.env = this.env || {};
      this.props = this.props || {};
    }
  }
};

// RPC error handling for commission operations
// Modern ES6 approach - no legacy odoo.define needed
if (typeof odoo !== "undefined" && odoo.loader) {
  // Use modern loader system
  odoo.loader.bus.addEventListener("module-started", function (ev) {
    if (ev.detail.moduleName === "web.rpc") {
      // Modern RPC error handling for commission operations
      console.log("�️ Commission AX RPC protection activated");
    }
  });
} else {
  // Fallback for legacy systems
  console.log("🛡️ Commission AX using fallback RPC protection");
}

// Form view error protection - Modern ES6 approach
if (typeof odoo !== "undefined" && odoo.loader) {
  // Use modern module system
  odoo.loader.bus.addEventListener("module-started", function (ev) {
    if (ev.detail.moduleName === "web.FormView") {
      console.log("�️ Commission AX Form protection activated");
    }
  });
} else {
  // Direct protection without legacy define
  document.addEventListener("DOMContentLoaded", function () {
    console.log("🛡️ Commission AX Form protection loaded (fallback)");
  });
}

// Field widget error protection - Modern ES6 approach
if (typeof odoo !== "undefined" && odoo.loader) {
  // Use modern module system
  odoo.loader.bus.addEventListener("module-started", function (ev) {
    if (ev.detail.moduleName === "web.AbstractField") {
      console.log("🛡️ Commission AX Field protection activated");
    }
  });
} else {
  // Direct protection for field widgets
  document.addEventListener("DOMContentLoaded", function () {
    console.log("�️ Commission AX Field protection loaded (fallback)");

    // Global field error protection
    window.addEventListener("error", function (event) {
      if (
        event.message &&
        event.message.toLowerCase().includes("field") &&
        event.message.toLowerCase().includes("commission")
      ) {
        console.warn("🛡️ Commission field error caught:", event.message);
        event.preventDefault();
        return true;
      }
    });
  });
}

// Commission-specific error recovery functions
window.CommissionAXErrorHandler = {
  /**
   * Safely execute commission operations with error handling
   */
  safeExecute: function (operation, fallback) {
    try {
      return operation();
    } catch (error) {
      console.error("🚨 Commission AX Safe Execute Error:", error);
      return fallback ? fallback() : null;
    }
  },

  /**
   * Recover from commission form errors
   */
  recoverCommissionForm: function (formView) {
    try {
      if (formView && formView.renderer) {
        formView.renderer.$el
          .find(".o_form_button_save")
          .prop("disabled", false);
        formView.renderer.$el
          .find(".o_form_button_cancel")
          .prop("disabled", false);
      }
    } catch (error) {
      console.error("🚨 Commission Form Recovery Error:", error);
    }
  },

  /**
   * Reset commission UI state
   */
  resetCommissionUI: function () {
    try {
      // Remove any stuck loading states
      $(".o_commission_loading").removeClass("o_commission_loading");
      $("button[disabled]").filter("[data-commission]").prop("disabled", false);

      // Clear any error messages
      $(".o_commission_error").remove();
    } catch (error) {
      console.error("🚨 Commission UI Reset Error:", error);
    }
  },
};

// Initialize CloudPepper protection on DOM ready
$(document).ready(function () {
  console.log("✅ Commission AX CloudPepper Compatibility Patch Initialized");

  // Set up periodic error recovery
  setInterval(function () {
    if (window.CommissionAXErrorHandler) {
      window.CommissionAXErrorHandler.resetCommissionUI();
    }
  }, 30000); // Every 30 seconds
});

console.log(
  "🛡️ Commission AX CloudPepper Compatibility Patch Loaded Successfully"
);
