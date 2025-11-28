/**
 * CloudPepper Dashboard Emergency Fix
 * Safe error handling for dashboard modules
 */

(function () {
  "use strict";

  console.log("🔧 CloudPepper Dashboard Fix Loading...");

  // OSUS Properties Brand Colors
  window.OSUSBrandColors = {
    primary: "#4d1a1a", // OSUS burgundy
    gold: "#b8a366", // OSUS gold
    lightGold: "#f5f5e6", // Light gold
    darkGold: "#9d7f47", // Dark gold
    white: "#ffffff",
    accent: "#7d1e2d", // Dark burgundy

    chartColors: [
      "#4d1a1a", // burgundy
      "#b8a366", // gold
      "#7d1e2d", // dark burgundy
      "#d4c299", // light gold
      "#cc4d66", // burgundy light
    ],

    chartBackgrounds: [
      "rgba(77, 26, 26, 0.1)", // burgundy with transparency
      "rgba(184, 163, 102, 0.1)", // gold with transparency
      "rgba(125, 30, 45, 0.1)", // dark burgundy with transparency
      "rgba(212, 194, 153, 0.1)", // light gold with transparency
      "rgba(204, 77, 102, 0.1)", // burgundy light with transparency
    ],
  };

  // Global dashboard error handler
  window.dashboardErrorHandler = function (error, context) {
    console.warn("Dashboard Error Handled:", error, context);

    // Show user-friendly message
    if (window.location.pathname.includes("dashboard")) {
      const notification = document.createElement("div");
      notification.innerHTML = `
                <div style="
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #4d1a1a;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    z-index: 99999;
                    font-family: system-ui;
                    font-size: 14px;
                    box-shadow: 0 4px 12px rgba(77, 26, 26, 0.3);
                ">
                    ⚠️ Dashboard loading... Please wait.
                </div>
            `;
      document.body.appendChild(notification);

      // Remove notification after 3 seconds
      setTimeout(() => {
        notification.remove();
      }, 3000);
    }

    return true;
  };

  // Chart.js error prevention
  window.addEventListener("error", function (event) {
    if (event.message && event.message.includes("Chart")) {
      console.log("Chart.js error intercepted and handled");
      window.dashboardErrorHandler(event.error, "Chart.js");
      event.preventDefault();
      return true;
    }
  });

  // RPC error handling for dashboard
  window.addEventListener("unhandledrejection", function (event) {
    if (event.reason && event.reason.toString().includes("dashboard")) {
      console.log("Dashboard RPC error intercepted and handled");
      window.dashboardErrorHandler(event.reason, "RPC");
      event.preventDefault();
      return true;
    }
  });

  // Dashboard initialization helper
  window.initializeDashboard = function (callback) {
    try {
      // Wait for Chart.js if needed
      if (typeof Chart === "undefined") {
        console.log("Waiting for Chart.js to load...");
        setTimeout(() => window.initializeDashboard(callback), 100);
        return;
      }

      // Execute callback with error handling
      if (typeof callback === "function") {
        try {
          callback();
        } catch (error) {
          window.dashboardErrorHandler(error, "Dashboard Init");
        }
      }
    } catch (error) {
      window.dashboardErrorHandler(error, "Dashboard Helper");
    }
  };

  // Safe fetch wrapper for dashboard data
  window.safeDashboardFetch = async function (url, options = {}) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      window.dashboardErrorHandler(error, "Dashboard Fetch");
      return { error: error.message };
    }
  };

  console.log("✅ CloudPepper Dashboard Fix Ready");
})();
