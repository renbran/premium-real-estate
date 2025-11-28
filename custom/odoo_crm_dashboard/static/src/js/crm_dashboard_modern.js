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

export class CRMDashboardView extends Component {
  static template = "crm_dashboard.Dashboard";
  static props = {
    resModel: { type: String, optional: true },
    action: { type: Object, optional: true },
  };

  setup() {
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.notification = useService("notification");

    this.state = useState({
      isLoading: true,
      crmData: {},
      error: null,
    });

    // Chart references
    this.chartRefs = {
      overdue_chart: useRef("overdue_chart"),
      pipeline_chart: useRef("pipeline_chart"),
      lead_chart: useRef("lead_chart"),
      won_chart: useRef("won_chart"),
      yearly_chart: useRef("yearly_chart"),
      won_chart_year: useRef("won_chart_year"),
      expected_chart: useRef("expected_chart"),
    };

    this.chartInstances = {};

    onMounted(async () => {
      try {
        await this.loadChartLibraries();
        await this.loadDashboardData();
        await this.renderGraphs();
        this.state.isLoading = false;
      } catch (error) {
        console.error("Error initializing CRM Dashboard:", error);
        this.state.error = error.message;
        this.state.isLoading = false;
        this.notification.add(
          _t("Failed to load dashboard data: %s", error.message),
          { type: "danger" }
        );
      }
    });

    onWillUnmount(() => {
      this.cleanupCharts();
    });
  }

  async loadChartLibraries() {
    try {
      await loadJS("/odoo_crm_dashboard/static/lib/charts/Chart.min.js");
      await loadJS(
        "/odoo_crm_dashboard/static/lib/dataTables/jquery.dataTables.min.js"
      );
    } catch (error) {
      console.warn("Error loading chart libraries:", error);
    }
  }

  async loadDashboardData() {
    try {
      const result = await this.orm.call("crm.dashboard", "get_crm_info", []);
      this.state.crmData = result[0] || {};
    } catch (error) {
      console.error("Error loading CRM data:", error);
      throw error;
    }
  }

  cleanupCharts() {
    Object.values(this.chartInstances).forEach((chart) => {
      if (chart && typeof chart.destroy === "function") {
        chart.destroy();
      }
    });
    this.chartInstances = {};
  }

  async renderGraphs() {
    if (!window.Chart) {
      console.warn("Chart.js not loaded, skipping graph rendering");
      return;
    }

    try {
      await this.renderOverdueChart();
      await this.renderPipelineChart();
      await this.renderLeadChart();
      await this.renderWonChart();
      await this.renderYearlyChart();
      await this.renderExpectedChart();
    } catch (error) {
      console.error("Error rendering charts:", error);
    }
  }

  async renderOverdueChart() {
    const chartRef = this.chartRefs.overdue_chart;
    if (!chartRef.el || !this.state.crmData.overdue_data) return;

    const ctx = chartRef.el.getContext("2d");
    this.chartInstances.overdue_chart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: this.state.crmData.overdue_data.labels || [],
        datasets: [
          {
            data: this.state.crmData.overdue_data.data || [],
            backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
            hoverBackgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: "bottom",
        },
      },
    });
  }

  async renderPipelineChart() {
    const chartRef = this.chartRefs.pipeline_chart;
    if (!chartRef.el || !this.state.crmData.pipeline_data) return;

    const ctx = chartRef.el.getContext("2d");
    this.chartInstances.pipeline_chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: this.state.crmData.pipeline_data.labels || [],
        datasets: [
          {
            label: _t("Pipeline"),
            data: this.state.crmData.pipeline_data.data || [],
            backgroundColor: "#36A2EB",
            borderColor: "#36A2EB",
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  async renderLeadChart() {
    const chartRef = this.chartRefs.lead_chart;
    if (!chartRef.el || !this.state.crmData.lead_data) return;

    const ctx = chartRef.el.getContext("2d");
    this.chartInstances.lead_chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: this.state.crmData.lead_data.labels || [],
        datasets: [
          {
            label: _t("Leads"),
            data: this.state.crmData.lead_data.data || [],
            borderColor: "#FFCE56",
            backgroundColor: "rgba(255, 206, 86, 0.1)",
            tension: 0.1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  async renderWonChart() {
    const chartRef = this.chartRefs.won_chart;
    if (!chartRef.el || !this.state.crmData.won_data) return;

    const ctx = chartRef.el.getContext("2d");
    this.chartInstances.won_chart = new Chart(ctx, {
      type: "pie",
      data: {
        labels: this.state.crmData.won_data.labels || [],
        datasets: [
          {
            data: this.state.crmData.won_data.data || [],
            backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
            hoverBackgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: "bottom",
        },
      },
    });
  }

  async renderYearlyChart() {
    const chartRef = this.chartRefs.yearly_chart;
    if (!chartRef.el || !this.state.crmData.yearly_data) return;

    const ctx = chartRef.el.getContext("2d");
    this.chartInstances.yearly_chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: this.state.crmData.yearly_data.labels || [],
        datasets: [
          {
            label: _t("Yearly Revenue"),
            data: this.state.crmData.yearly_data.data || [],
            backgroundColor: "#4BC0C0",
            borderColor: "#4BC0C0",
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  async renderExpectedChart() {
    const chartRef = this.chartRefs.expected_chart;
    if (!chartRef.el || !this.state.crmData.expected_data) return;

    const ctx = chartRef.el.getContext("2d");
    this.chartInstances.expected_chart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: this.state.crmData.expected_data.labels || [],
        datasets: [
          {
            data: this.state.crmData.expected_data.data || [],
            backgroundColor: ["#FF9F40", "#FF6384", "#36A2EB"],
            hoverBackgroundColor: ["#FF9F40", "#FF6384", "#36A2EB"],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: "bottom",
        },
      },
    });
  }

  // Action methods converted to modern async/await
  async onOverdueOpportunitiesClick() {
    try {
      const action = await this.orm.call(
        "crm.dashboard",
        "action_overdue_opportunities",
        []
      );
      this.actionService.doAction(action);
    } catch (error) {
      this.notification.add(_t("Error loading opportunities"), {
        type: "danger",
      });
    }
  }

  async onMyPipelineClick() {
    try {
      const action = await this.orm.call(
        "crm.dashboard",
        "action_my_pipeline",
        []
      );
      this.actionService.doAction(action);
    } catch (error) {
      this.notification.add(_t("Error loading pipeline"), { type: "danger" });
    }
  }

  async onOpenOpportunitiesClick() {
    try {
      const action = await this.orm.call(
        "crm.dashboard",
        "action_open_opportunities",
        []
      );
      this.actionService.doAction(action);
    } catch (error) {
      this.notification.add(_t("Error loading opportunities"), {
        type: "danger",
      });
    }
  }

  async onWonCountClick() {
    try {
      const action = await this.orm.call(
        "crm.dashboard",
        "action_won_count",
        []
      );
      this.actionService.doAction(action);
    } catch (error) {
      this.notification.add(_t("Error loading won opportunities"), {
        type: "danger",
      });
    }
  }

  async onLossCountClick() {
    try {
      const action = await this.orm.call(
        "crm.dashboard",
        "action_loss_count",
        []
      );
      this.actionService.doAction(action);
    } catch (error) {
      this.notification.add(_t("Error loading lost opportunities"), {
        type: "danger",
      });
    }
  }

  async onTotalExpectedRevenueClick() {
    try {
      const action = await this.orm.call(
        "crm.dashboard",
        "action_tot_exp_revenue",
        []
      );
      this.actionService.doAction(action);
    } catch (error) {
      this.notification.add(_t("Error loading revenue data"), {
        type: "danger",
      });
    }
  }
}

// Register the component in the action registry
registry.category("actions").add("crm_dashboard.dashboard", CRMDashboardView);

// Export for compatibility
export default CRMDashboardView;
