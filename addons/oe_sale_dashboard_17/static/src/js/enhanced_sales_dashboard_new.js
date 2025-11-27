/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * Enhanced Sales Dashboard Component
 * Professional analytics with OSUS branding
 */
class EnhancedSalesDashboard extends Component {
  static template = "oe_sale_dashboard_17.enhanced_sales_dashboard";

  setup() {
    this.rpc = useService("rpc");
    this.notification = useService("notification");

    this.state = useState({
      isLoading: true,
      data: {
        performance: {
          total_orders: 0,
          total_quotations: 0,
          total_sales: 0,
          total_invoiced: 0,
          total_amount: 0,
          currency_symbol: "$",
        },
        monthly_trend: { labels: [], datasets: [] },
        pipeline: { labels: [], datasets: [] },
        agent_rankings: { rankings: [] },
        broker_rankings: { rankings: [] },
        sale_types: { sale_types: [] },
      },
      filters: {
        start_date: this._getDefaultStartDate(),
        end_date: this._getDefaultEndDate(),
        sale_type_ids: [],
      },
      charts: {},
    });

    onWillStart(async () => {
      await this.loadDashboardData();
    });
  }

  _getDefaultStartDate() {
    const today = new Date();
    return new Date(today.getFullYear(), today.getMonth(), 1)
      .toISOString()
      .split("T")[0];
  }

  _getDefaultEndDate() {
    return new Date().toISOString().split("T")[0];
  }

  async loadDashboardData() {
    try {
      this.state.isLoading = true;

      const result = await this.rpc("/web/dataset/call_kw", {
        model: "sale.dashboard",
        method: "get_dashboard_data",
        args: [],
        kwargs: {
          start_date: this.state.filters.start_date,
          end_date: this.state.filters.end_date,
          sale_type_ids: this.state.filters.sale_type_ids,
        },
      });

      if (result.error) {
        this.notification.add(`Dashboard Error: ${result.error}`, {
          type: "danger",
        });
        return;
      }

      this.state.data = result;
      this.state.isLoading = false;

      // Initialize charts after data is loaded
      setTimeout(() => this.initializeCharts(), 100);
    } catch (error) {
      console.error("Dashboard loading error:", error);
      this.notification.add("Failed to load dashboard data", {
        type: "danger",
      });
      this.state.isLoading = false;
    }
  }

  initializeCharts() {
    try {
      if (typeof Chart === "undefined") {
        console.warn("Chart.js not loaded, retrying...");
        setTimeout(() => this.initializeCharts(), 500);
        return;
      }

      this.renderMonthlyTrendChart();
      this.renderPipelineChart();
    } catch (error) {
      console.error("Chart initialization error:", error);
      if (window.dashboardErrorHandler) {
        window.dashboardErrorHandler(error, "Chart Init");
      }
    }
  }

  renderMonthlyTrendChart() {
    const canvas = document.getElementById("monthly_trend_chart");
    if (!canvas) return;

    // Destroy existing chart if exists
    if (this.state.charts.monthlyTrend) {
      this.state.charts.monthlyTrend.destroy();
    }

    const ctx = canvas.getContext("2d");
    const data = this.state.data.monthly_trend;

    // OSUS brand colors
    const brandColors = window.OSUSBrandColors || {
      primary: "#4d1a1a",
      gold: "#b8a366",
    };

    this.state.charts.monthlyTrend = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.labels || [],
        datasets: (data.datasets || []).map((dataset, index) => ({
          ...dataset,
          borderColor: index === 0 ? brandColors.primary : brandColors.gold,
          backgroundColor:
            index === 0 ? "rgba(77, 26, 26, 0.1)" : "rgba(184, 163, 102, 0.1)",
          tension: 0.4,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Monthly Sales Trend",
            color: brandColors.primary,
            font: { size: 16, weight: "bold" },
          },
          legend: {
            display: true,
            position: "top",
          },
        },
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
            title: { display: true, text: "Order Count" },
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",
            title: { display: true, text: "Amount" },
            grid: { drawOnChartArea: false },
          },
        },
      },
    });
  }

  renderPipelineChart() {
    const canvas = document.getElementById("pipeline_chart");
    if (!canvas) return;

    // Destroy existing chart if exists
    if (this.state.charts.pipeline) {
      this.state.charts.pipeline.destroy();
    }

    const ctx = canvas.getContext("2d");
    const data = this.state.data.pipeline;

    // OSUS brand colors
    const brandColors = window.OSUSBrandColors || {
      chartColors: ["#4d1a1a", "#b8a366", "#7d1e2d", "#d4c299", "#cc4d66"],
    };

    this.state.charts.pipeline = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: data.labels || [],
        datasets: [
          {
            data: data.datasets?.[0]?.data || [],
            backgroundColor: brandColors.chartColors,
            borderColor: "#ffffff",
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Sales Pipeline",
            color: brandColors.chartColors[0],
            font: { size: 16, weight: "bold" },
          },
          legend: {
            display: true,
            position: "bottom",
          },
        },
      },
    });
  }

  formatCurrency(amount) {
    const symbol = this.state.data.performance?.currency_symbol || "$";
    return `${symbol}${this.formatNumber(amount)}`;
  }

  formatNumber(value) {
    if (!value || value === 0) return "0";

    const abs = Math.abs(value);
    if (abs >= 1_000_000_000) {
      return (value / 1_000_000_000).toFixed(2) + "B";
    } else if (abs >= 1_000_000) {
      return (value / 1_000_000).toFixed(2) + "M";
    } else if (abs >= 1_000) {
      return (value / 1_000).toFixed(0) + "K";
    }
    return value.toFixed(0);
  }

  async onRefreshDashboard() {
    await this.loadDashboardData();
  }

  onFilterChange(field, value) {
    this.state.filters[field] = value;
  }

  async onApplyFilters() {
    await this.loadDashboardData();
  }
}

// Register the component
registry
  .category("actions")
  .add("enhanced_sales_dashboard", EnhancedSalesDashboard);
