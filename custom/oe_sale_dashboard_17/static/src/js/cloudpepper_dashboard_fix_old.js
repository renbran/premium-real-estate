/** @odoo-module **/
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
 * CloudPepper Dashboard Module Error Fix - Compatible Version
 * Specific fixes for dashboard modules and Chart.js errors
 * Uses CloudPepper-safe patterns to avoid import conflicts
 */

// CloudPepper-compatible dashboard error handling
(function () {
  "use strict";

  console.log("[CloudPepper] Loading dashboard error protection...");

  // Global dashboard error handling
  const DashboardErrorHandler = {
    handleChartError(error, chartType = "Unknown") {
      console.warn(`[CloudPepper] Chart.js error in ${chartType}:`, error);
      return {
        labels: ["No Data"],
        datasets: [
          {
            label: "Error Loading Data",
            data: [0],
            backgroundColor: ["#ff6b6b"],
          },
        ],
      };
    },

    async safeDataLoad(loader, fallback = {}) {
      try {
        return await loader();
      } catch (error) {
        console.warn("[CloudPepper] Dashboard data load error:", error);
        return fallback;
      }
    },

    handleDashboardError(error, dashboardName = "Unknown") {
      console.warn(`[CloudPepper] Dashboard error in ${dashboardName}:`, error);

      if (
        error.message &&
        (error.message.includes("Chart") ||
          error.message.includes("RPC_ERROR") ||
          error.message.includes("XMLHttpRequest"))
      ) {
        return {
          handled: true,
          fallbackData: {
            message: "Dashboard data temporarily unavailable",
            charts: [],
          },
        };
      }

      return { handled: false };
    },
  };

  // Enhanced Chart.js error protection
  setTimeout(function () {
    try {
      // Override Chart.js constructor if available
      if (window.Chart) {
        const OriginalChart = window.Chart;

        window.Chart = function (ctx, config) {
          try {
            return new OriginalChart(ctx, config);
          } catch (error) {
            console.warn("[CloudPepper] Chart.js error handled:", error);

            // Create fallback chart
            const fallbackConfig = {
              type: "bar",
              data: DashboardErrorHandler.handleChartError(error, config.type),
              options: {
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: "Chart temporarily unavailable",
                  },
                },
              },
            };

            try {
              return new OriginalChart(ctx, fallbackConfig);
            } catch (fallbackError) {
              console.warn(
                "[CloudPepper] Fallback chart failed:",
                fallbackError
              );
              return null;
            }
          }
        };

        // Copy static properties
        Object.setPrototypeOf(window.Chart, OriginalChart);
        Object.assign(window.Chart, OriginalChart);

        console.log("[CloudPepper] Chart.js error protection enabled");
      }
    } catch (chartError) {
      console.warn("[CloudPepper] Could not protect Chart.js:", chartError);
    }
  }, 100);

  // Dashboard component protection
  const dashboardComponents = [
    "SalesDashboard",
    "CRMDashboard",
    "PaymentDashboard",
    "ExecutiveDashboard",
  ];

  setTimeout(function () {
    dashboardComponents.forEach((componentName) => {
      try {
        // Look for dashboard elements in DOM
        const dashboardElements = document.querySelectorAll(
          `[class*="${componentName}"], [data-dashboard="${componentName}"]`
        );

        dashboardElements.forEach((element) => {
          // Add error event listener
          element.addEventListener("error", function (event) {
            console.warn(
              `[CloudPepper] Dashboard error prevented in ${componentName}:`,
              event.error
            );
            event.preventDefault();

            // Show fallback content
            if (element.innerHTML) {
              element.innerHTML = `
                                <div style="padding: 20px; text-align: center; color: #666;">
                                    <i class="fa fa-chart-bar" style="font-size: 48px; color: #ccc;"></i>
                                    <p>Dashboard temporarily unavailable</p>
                                    <button onclick="location.reload()" class="btn btn-sm btn-primary">Refresh</button>
                                </div>
                            `;
            }
          });
        });

        console.log(
          `[CloudPepper] Protected dashboard component: ${componentName}`
        );
      } catch (error) {
        console.warn(
          `[CloudPepper] Could not protect ${componentName}:`,
          error
        );
      }
    });
  }, 200);

  // Global error handler for dashboard operations
  window.addEventListener("error", function (event) {
    if (event.error && event.error.message) {
      const error = event.error;

      // Check if it's a dashboard related error
      if (
        error.message.includes("Chart") ||
        error.message.includes("dashboard") ||
        (error.stack &&
          (error.stack.includes("oe_sale_dashboard") ||
            error.stack.includes("Chart.js") ||
            error.stack.includes("dashboard")))
      ) {
        console.warn("[CloudPepper] Dashboard error intercepted:", error);

        const result = DashboardErrorHandler.handleDashboardError(error);
        if (result.handled) {
          event.preventDefault();

          // Show user-friendly message
          if (window.Notification && Notification.permission === "granted") {
            new Notification("Dashboard Notice", {
              body: "Dashboard data temporarily unavailable",
              icon: "/web/static/img/favicon.ico",
            });
          }
        }
      }
    }
  });

  // Enhanced RPC error handling for dashboards
  window.addEventListener("unhandledrejection", function (event) {
    if (event.reason && event.reason.message) {
      const error = event.reason;

      if (
        (error.message.includes("RPC_ERROR") ||
          error.message.includes("XMLHttpRequest")) &&
        error.stack &&
        (error.stack.includes("dashboard") ||
          error.stack.includes("Chart") ||
          error.stack.includes("oe_sale_dashboard"))
      ) {
        console.warn("[CloudPepper] Dashboard RPC error prevented:", error);
        event.preventDefault();

        // Attempt graceful recovery
        setTimeout(function () {
          const dashboards = document.querySelectorAll('[class*="dashboard"]');
          dashboards.forEach((dashboard) => {
            if (dashboard.style) {
              dashboard.style.opacity = "0.7";
              dashboard.title =
                "Dashboard data temporarily unavailable - click to refresh";
            }
          });
        }, 500);
      }
    }
  });

  // Safe dashboard data loader for global use
  window.cloudpepperSafeDashboardLoad = async function (
    loader,
    fallbackData = {}
  ) {
    return await DashboardErrorHandler.safeDataLoad(loader, fallbackData);
  };

  console.log("[CloudPepper] Dashboard Error Protection Loaded Successfully");
})();
