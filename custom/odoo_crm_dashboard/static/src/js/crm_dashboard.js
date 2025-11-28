/** @odoo-module **/

import {
  Component,
  useState,
  useRef,
  onMounted,
  onWillUnmount,
} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";

export class ModernCRMDashboard extends Component {
  static template = "odoo_crm_dashboard.Dashboard";
  static props = ["*"];

  setup() {
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.notification = useService("notification");

    this.state = useState({
      isLoading: true,
      crmData: {},
      error: null,
    });

    this.chartRefs = {
      overdue_chart: useRef("overdue_chart"),
      pipeline_chart: useRef("pipeline_chart"),
      lead_chart: useRef("lead_chart"),
      won_chart: useRef("won_chart"),
      yearly_chart: useRef("yearly_chart"),
    };

    this.chartInstances = {};

    onMounted(async () => {
      try {
        await this.loadChartLibraries();
        await this.loadDashboardData();
        await this.renderGraphs();
        this.state.isLoading = false;
      } catch (error) {
        console.error("CRM Dashboard initialization error:", error);
        this.state.error = error.message;
        this.state.isLoading = false;
      }
    });

    onWillUnmount(() => {
      this.destroyCharts();
    });
  }

  async loadChartLibraries() {
    await loadJS("/odoo_crm_dashboard/static/lib/charts/Chart.min.js");
  }

  async loadDashboardData() {
    try {
      const data = await this.orm.call(
        "crm.lead",
        "get_crm_dashboard_data",
        []
      );
      this.state.crmData = data;
    } catch (error) {
      console.error("Failed to load CRM data:", error);
      throw error;
    }
  }

  async renderGraphs() {
    const chartConfigs = {
      overdue_chart: {
        type: "doughnut",
        data: this.state.crmData.overdueData || {},
        title: _t("Overdue Opportunities"),
      },
      pipeline_chart: {
        type: "bar",
        data: this.state.crmData.pipelineData || {},
        title: _t("Sales Pipeline"),
      },
      lead_chart: {
        type: "pie",
        data: this.state.crmData.leadData || {},
        title: _t("Lead Sources"),
      },
      won_chart: {
        type: "line",
        data: this.state.crmData.wonData || {},
        title: _t("Won Opportunities"),
      },
      yearly_chart: {
        type: "bar",
        data: this.state.crmData.yearlyData || {},
        title: _t("Yearly Performance"),
      },
    };

    for (const [chartId, config] of Object.entries(chartConfigs)) {
      this.renderChart(chartId, config);
    }
  }

  renderChart(chartId, config) {
    const chartRef = this.chartRefs[chartId];
    if (!chartRef?.el) return;

    const ctx = chartRef.el.getContext("2d");

    // Destroy existing chart if it exists
    if (this.chartInstances[chartId]) {
      this.chartInstances[chartId].destroy();
    }

    // Apply OSUS branding colors
    if (config.data.datasets) {
      config.data.datasets = config.data.datasets.map((dataset) => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || [
          "#800020",
          "#FFD700",
          "#A0522D",
          "#FFF8DC",
        ],
        borderColor: dataset.borderColor || "#800020",
      }));
    }

    this.chartInstances[chartId] = new Chart(ctx, {
      type: config.type,
      data: config.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: config.title,
            color: "#800020",
            font: {
              size: 16,
              weight: "bold",
            },
          },
          legend: {
            labels: {
              color: "#800020",
            },
          },
        },
        scales:
          config.type !== "doughnut" && config.type !== "pie"
            ? {
                x: {
                  ticks: {
                    color: "#800020",
                  },
                },
                y: {
                  ticks: {
                    color: "#800020",
                  },
                },
              }
            : {},
      },
    });
  }

  destroyCharts() {
    Object.values(this.chartInstances).forEach((chart) => {
      if (chart && typeof chart.destroy === "function") {
        chart.destroy();
      }
    });
    this.chartInstances = {};
  }

  async onRefreshData() {
    try {
      this.state.isLoading = true;
      await this.loadDashboardData();
      await this.renderGraphs();
      this.notification.add(_t("Dashboard refreshed successfully"), {
        type: "success",
      });
    } catch (error) {
      this.notification.add(_t("Failed to refresh dashboard"), {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
    }
  }
}

registry.category("views").add("modern_crm_dashboard", ModernCRMDashboard);
