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
        

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CRMExecutiveDashboard extends Component {
    static template = "crm_executive_dashboard.Dashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            isLoading: true,
            dateRange: {
                start: this.getDefaultStartDate(),
                end: this.getDefaultEndDate(),
            },
            selectedTeams: [],
            dashboardData: {
                kpis: {},
                pipeline: {},
                trends: {},
                team_performance: {},
                customer_acquisition: {},
                agent_metrics: {
                    top_agents_with_progress: [],
                    most_converted_agents: []
                },
                lead_quality: {
                    most_junked_agents: [],
                    source_quality: []
                },
                response_metrics: {
                    fast_responders: [],
                    slow_responders: [],
                    fast_updaters: [],
                    slow_updaters: []
                }
            },
            overdueOpportunities: [],
            topPerformers: [],
            autoRefresh: true,
            refreshInterval: 300000, // 5 minutes
        });

        this.charts = {};
        this.refreshTimer = null;

        onWillStart(this.loadInitialData);
        onMounted(this.initializeCharts);
        onMounted(this.setupAutoRefresh);
    }

    getDefaultStartDate() {
        const date = new Date();
        date.setDate(1); // First day of current month
        return date.toISOString().split('T')[0];
    }

    getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadDashboardData(),
                this.loadOverdueOpportunities(),
                this.loadTopPerformers(),
                this.loadTeamsList(),
            ]);
        } catch (error) {
            console.error("Error loading initial data:", error);
            this.notification.add(
                _t("Failed to load dashboard data: %s", error.message),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    async loadDashboardData() {
        try {
            const result = await this.rpc("/crm/dashboard/data", {
                date_from: this.state.dateRange.start,
                date_to: this.state.dateRange.end,
                team_ids: this.state.selectedTeams,
            });

            if (result.success) {
                this.state.dashboardData = result.data;
            } else {
                throw new Error(result.error || "Unknown error");
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            throw error;
        }
    }

    async loadOverdueOpportunities() {
        try {
            const result = await this.rpc("/crm/dashboard/overdue", {
                team_ids: this.state.selectedTeams,
            });

            if (result.success) {
                this.state.overdueOpportunities = result.data;
            }
        } catch (error) {
            console.error("Error loading overdue opportunities:", error);
        }
    }

    async loadTopPerformers() {
        try {
            const result = await this.rpc("/crm/dashboard/performers", {
                date_from: this.state.dateRange.start,
                date_to: this.state.dateRange.end,
                limit: 5,
            });

            if (result.success) {
                this.state.topPerformers = result.data;
            }
        } catch (error) {
            console.error("Error loading top performers:", error);
        }
    }

    async loadTeamsList() {
        try {
            this.availableTeams = await this.orm.searchRead(
                "crm.team",
                [],
                ["id", "name"],
                { order: "name" }
            );
        } catch (error) {
            console.error("Error loading teams list:", error);
        }
    }

    initializeCharts() {
        // Wait for the DOM to be ready and Chart.js to be available
        const initCharts = () => {
            if (typeof Chart !== 'undefined') {
                try {
                    this.renderAllCharts();
                } catch (error) {
                    console.error("Error rendering charts:", error);
                    this.showChartError();
                }
            } else {
                console.warn("Chart.js not available, using fallback visualization");
                this.showChartFallback();
            }
        };

        // Use a small delay to ensure DOM is ready
        setTimeout(initCharts, 100);
    }

    showChartError() {
        // Show error message instead of breaking the component
        const chartContainers = document.querySelectorAll('.chart-container canvas');
        chartContainers.forEach(canvas => {
            const container = canvas.parentElement;
            container.innerHTML = `
                <div class="alert alert-warning text-center p-4">
                    <i class="fa fa-exclamation-triangle fa-2x mb-2"></i>
                    <h5>Chart Loading Error</h5>
                    <p>Unable to load charts. Please refresh the page.</p>
                </div>
            `;
        });
    }

    showChartFallback() {
        // Show fallback content when Chart.js is not available
        const chartContainers = document.querySelectorAll('.chart-container canvas');
        chartContainers.forEach(canvas => {
            const container = canvas.parentElement;
            container.innerHTML = `
                <div class="alert alert-info text-center p-4">
                    <i class="fa fa-chart-bar fa-2x mb-2"></i>
                    <h5>Charts Unavailable</h5>
                    <p>Chart library is loading. Data is available in tables below.</p>
                </div>
            `;
        });
    }

    async loadChartJsFallback() {
        // Simplified fallback - just return false to indicate failure
        return Promise.resolve(false);
    }

    renderAllCharts() {
        requestAnimationFrame(() => {
            try {
                this.renderPipelineChart();
                this.renderTrendsChart();
                this.renderTeamPerformanceChart();
                this.renderSourcesChart();
            } catch (error) {
                console.error("Error in renderAllCharts:", error);
                this.showChartError();
            }
        });
    }

    renderPipelineChart() {
        if (typeof Chart === 'undefined') {
            console.warn("Chart.js not available for pipeline chart");
            return;
        }

        const canvas = document.getElementById('pipelineChart');
        if (!canvas || !this.state.dashboardData.pipeline.labels) return;

        try {
            if (this.charts.pipeline) {
                this.charts.pipeline.destroy();
            }

            const ctx = canvas.getContext('2d');
            this.charts.pipeline = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.state.dashboardData.pipeline.labels,
                datasets: [{
                    data: this.state.dashboardData.pipeline.data,
                    backgroundColor: this.state.dashboardData.pipeline.colors,
                    borderWidth: 2,
                    borderColor: '#fff',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = this.formatCurrency(context.parsed);
                                return `${context.label}: ${value}`;
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        this.openPipelineStage(elements[0].index);
                    }
                }
            }
        });
        } catch (error) {
            console.error("Error rendering pipeline chart:", error);
        }
    }

    renderTrendsChart() {
        const canvas = document.getElementById('trendsChart');
        if (!canvas || !this.state.dashboardData.trends.labels) return;

        if (this.charts.trends) {
            this.charts.trends.destroy();
        }

        const ctx = canvas.getContext('2d');
        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.state.dashboardData.trends.labels,
                datasets: [
                    {
                        label: 'Leads',
                        data: this.state.dashboardData.trends.leads,
                        borderColor: '#36A2EB',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Opportunities',
                        data: this.state.dashboardData.trends.opportunities,
                        borderColor: '#FF6384',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Won Revenue',
                        data: this.state.dashboardData.trends.won_revenue,
                        borderColor: '#4BC0C0',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Revenue'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                if (context.datasetIndex === 2) {
                                    return `${context.dataset.label}: ${this.formatCurrency(context.parsed.y)}`;
                                }
                                return `${context.dataset.label}: ${context.parsed.y}`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderTeamPerformanceChart() {
        const canvas = document.getElementById('teamPerformanceChart');
        if (!canvas || !this.state.dashboardData.team_performance.labels) return;

        if (this.charts.teamPerformance) {
            this.charts.teamPerformance.destroy();
        }

        const ctx = canvas.getContext('2d');
        this.charts.teamPerformance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.state.dashboardData.team_performance.labels,
                datasets: [
                    {
                        label: 'Won Revenue',
                        data: this.state.dashboardData.team_performance.won_revenue,
                        backgroundColor: 'rgba(75, 192, 192, 0.8)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Conversion Rate %',
                        data: this.state.dashboardData.team_performance.conversion_rates,
                        backgroundColor: 'rgba(255, 206, 86, 0.8)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1,
                        yAxisID: 'y1',
                        type: 'line',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Revenue'
                        },
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Conversion Rate %'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        min: 0,
                        max: 100,
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                if (context.datasetIndex === 0) {
                                    return `${context.dataset.label}: ${this.formatCurrency(context.parsed.y)}`;
                                }
                                return `${context.dataset.label}: ${context.parsed.y}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderSourcesChart() {
        const canvas = document.getElementById('sourcesChart');
        if (!canvas || !this.state.dashboardData.customer_acquisition.sources.labels) return;

        if (this.charts.sources) {
            this.charts.sources.destroy();
        }

        const ctx = canvas.getContext('2d');
        this.charts.sources = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: this.state.dashboardData.customer_acquisition.sources.labels,
                datasets: [{
                    data: this.state.dashboardData.customer_acquisition.sources.counts,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                        '#9966FF', '#FF9F40', '#FF6384', '#36A2EB'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Event handlers
    async onDateRangeChange() {
        this.state.isLoading = true;
        try {
            await this.loadDashboardData();
            await this.loadTopPerformers();
            this.renderAllCharts();
            
            this.notification.add(_t("Dashboard updated successfully"), {
                type: "success",
            });
        } catch (error) {
            this.notification.add(
                _t("Failed to update dashboard: %s", error.message),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    async onTeamSelectionChange() {
        this.state.isLoading = true;
        try {
            await this.loadDashboardData();
            await this.loadOverdueOpportunities();
            this.renderAllCharts();
        } finally {
            this.state.isLoading = false;
        }
    }

    async onRefreshClick() {
        await this.loadInitialData();
        this.renderAllCharts();
    }

    setupAutoRefresh() {
        if (this.state.autoRefresh) {
            this.refreshTimer = setInterval(() => {
                this.loadDashboardData();
                this.loadOverdueOpportunities();
            }, this.state.refreshInterval);
        }
    }

    toggleAutoRefresh() {
        this.state.autoRefresh = !this.state.autoRefresh;
        
        if (this.state.autoRefresh) {
            this.setupAutoRefresh();
        } else if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    // Navigation handlers
    openPipelineStage(stageIndex) {
        // Open opportunities for specific stage
        this.action.doAction({
            name: _t("Pipeline Opportunities"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            target: 'current',
            context: {
                'search_default_opportunities': true,
                'search_default_open': true,
            },
        });
    }

    openOverdueOpportunities() {
        this.action.doAction({
            name: _t("Overdue Opportunities"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            domain: [
                ['type', '=', 'opportunity'],
                ['date_deadline', '<', new Date().toISOString().split('T')[0]],
                ['stage_id.is_won', '=', false],
                ['active', '=', true]
            ],
        });
    }

    openTopPerformersView() {
        this.action.doAction({
            name: _t("Sales Team"),
            type: 'ir.actions.act_window',
            res_model: 'res.users',
            view_mode: 'kanban,tree,form',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            target: 'current',
            domain: [['groups_id', 'in', [this.env.ref('sales_team.group_sale_salesman').id]]],
        });
    }

    async exportData() {
        try {
            const url = `/crm/dashboard/export?date_from=${this.state.dateRange.start}&date_to=${this.state.dateRange.end}&team_ids=${this.state.selectedTeams.join(',')}&format=xlsx`;
            window.open(url, '_blank');
            
            this.notification.add(_t("Export started successfully"), {
                type: "success",
            });
        } catch (error) {
            this.notification.add(
                _t("Failed to export data: %s", error.message),
                { type: "danger" }
            );
        }
    }

    // Utility methods
    formatNumber(value) {
        if (typeof value !== 'number') return '0';
        return new Intl.NumberFormat().format(value);
    }

    formatCurrency(value) {
        if (typeof value !== 'number') return '0';
        const currency = this.state.dashboardData.currency_symbol || '€';
        return `${currency}${new Intl.NumberFormat().format(value)}`;
    }

    formatPercentage(value) {
        if (typeof value !== 'number') return '0%';
        return `${value.toFixed(1)}%`;
    }

    getKpiTrend(current, previous) {
        if (!previous || previous === 0) return { trend: 'neutral', percentage: 0 };
        
        const percentage = ((current - previous) / previous * 100);
        const trend = percentage > 0 ? 'up' : percentage < 0 ? 'down' : 'neutral';
        
        return { trend, percentage: Math.abs(percentage).toFixed(1) };
    }

    willUnmount() {
        // Cleanup charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        // Cleanup auto-refresh timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
    }
}

// Register the component with the action registry
registry.category("actions").add("crm_executive_dashboard", CRMExecutiveDashboard);
