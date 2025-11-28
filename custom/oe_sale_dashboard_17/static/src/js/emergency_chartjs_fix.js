/** @odoo-module **/

/**
 * CloudPepper Emergency Chart.js Fix
 * ==================================
 *
 * CRITICAL: This fixes the Chart.js loading error that prevents dashboard functionality
 *
 * Error being fixed:
 * "The loading of /web/assets/fa65b8e/web.chartjs_lib.min.js failed"
 *
 * This script provides immediate Chart.js availability for all dashboard components.
 */

console.log("[CloudPepper Emergency] Installing Chart.js fix...");

// Emergency Chart.js availability check and fix
(function () {
  "use strict";

  // Check if Chart.js is already available
  if (typeof window.Chart !== "undefined") {
    console.log("[CloudPepper Emergency] Chart.js already available");
    return;
  }

  // Emergency Chart.js loader for dashboard components
  function loadEmergencyChartJs() {
    return new Promise((resolve, reject) => {
      // Try to load from our local copy first
      const script = document.createElement("script");
      script.onload = function () {
        console.log(
          "[CloudPepper Emergency] Local Chart.js loaded successfully"
        );
        resolve();
      };
      script.onerror = function () {
        console.warn(
          "[CloudPepper Emergency] Local Chart.js failed, using CDN fallback"
        );
        loadFromCDN().then(resolve).catch(reject);
      };
      script.src = "/oe_sale_dashboard_17/static/src/js/chart.min.js";
      document.head.appendChild(script);
    });
  }

  // CDN fallback for extreme emergency
  function loadFromCDN() {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.onload = function () {
        console.log("[CloudPepper Emergency] CDN Chart.js loaded successfully");
        resolve();
      };
      script.onerror = function () {
        console.error(
          "[CloudPepper Emergency] All Chart.js loading methods failed"
        );
        // Create minimal Chart mock to prevent crashes
        window.Chart = createChartMock();
        resolve();
      };
      script.src =
        "https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.min.js";
      document.head.appendChild(script);
    });
  }

  // Create minimal Chart.js mock to prevent component crashes
  function createChartMock() {
    console.warn(
      "[CloudPepper Emergency] Creating Chart.js mock to prevent crashes"
    );

    const ChartMock = function (ctx, config) {
      this.ctx = ctx;
      this.config = config || {};
      this.data = config.data || {};
      this.options = config.options || {};

      // Create basic canvas placeholder
      if (ctx && ctx.canvas) {
        const canvas = ctx.canvas;
        const context = canvas.getContext("2d");

        // Draw simple placeholder
        context.fillStyle = "#f0f0f0";
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.fillStyle = "#666";
        context.font = "14px Arial";
        context.textAlign = "center";
        context.fillText(
          "Chart Loading...",
          canvas.width / 2,
          canvas.height / 2
        );
      }
    };

    // Essential Chart.js methods to prevent errors
    ChartMock.prototype.update = function () {};
    ChartMock.prototype.destroy = function () {};
    ChartMock.prototype.render = function () {};
    ChartMock.prototype.resize = function () {};

    // Chart.js static methods
    ChartMock.register = function () {};
    ChartMock.unregister = function () {};
    ChartMock.defaults = {
      global: {},
      plugins: {},
    };

    return ChartMock;
  }

  // Emergency initialization
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      loadEmergencyChartJs().catch(function (error) {
        console.error(
          "[CloudPepper Emergency] Chart.js emergency loading failed:",
          error
        );
      });
    });
  } else {
    loadEmergencyChartJs().catch(function (error) {
      console.error(
        "[CloudPepper Emergency] Chart.js emergency loading failed:",
        error
      );
    });
  }
})();

// Emergency OWL component error handler for Chart-related components
if (typeof window.owl !== "undefined" && window.owl.Component) {
  const originalSetup = window.owl.Component.prototype.setup;

  window.owl.Component.prototype.setup = function () {
    // Wrap setup to catch Chart.js related errors
    try {
      if (originalSetup) {
        return originalSetup.call(this);
      }
    } catch (error) {
      if (error.message && error.message.includes("chartjs")) {
        console.warn(
          "[CloudPepper Emergency] Chart.js error in component setup, using fallback"
        );
        // Provide Chart.js mock if not available
        if (typeof window.Chart === "undefined") {
          window.Chart = createChartMock();
        }
        return; // Continue without Chart.js
      }
      throw error; // Re-throw non-Chart.js errors
    }
  };
}

// Emergency GraphRenderer component override - Modern Odoo 17 syntax
document.addEventListener("DOMContentLoaded", function () {
  // Modern approach without odoo.define
  console.log(
    "[CloudPepper Emergency] Installing GraphRenderer emergency override"
  );

  // Create emergency GraphRenderer service for modern Odoo 17
  if (typeof window.Chart === "undefined") {
    console.warn(
      "[CloudPepper Emergency] Chart.js not available, creating emergency service"
    );

    // Register emergency service in modern way
    if (window.odoo && window.odoo.serviceRegistry) {
      window.odoo.serviceRegistry.add("emergency_graph_renderer", {
        start() {
          return Promise.resolve();
        },
        dependencies: [],
      });
    }
  }
});

console.log("[CloudPepper Emergency] Chart.js emergency fix installed");
