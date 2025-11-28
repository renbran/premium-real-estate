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

export class CRMStrategicDashboard extends Component {
    static template = "crm_strategic_dashboard.Dashboard";
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
                strategic_kpis: {},
                financial_performance: {},
                market_intelligence: {},
                customer_insights: {},
                operational_efficiency: {},
                risk_indicators: {},
                predictive_analytics: {},
                team_overview: []
            },
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
            const result = await this.rpc("/crm/strategic/dashboard/data", {
                date_from: this.state.dateRange.start,
                date_to: this.state.dateRange.end,
                team_ids: this.state.selectedTeams,
            });

            if (result.success) {
                this.state.dashboardData = result.data;
                this.updateCharts();
            } else {
                throw new Error(result.error || "Unknown error");
            }
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.notification.add(
                _t("Failed to load dashboard data: %s", error.message),
                { type: "danger" }
            );
        }
    }

    async loadTeamsList() {
        try {
            this.availableTeams = await this.orm.searchRead(
                "crm.team",
                [],
                ["id", "name"]
            );
        } catch (error) {
            console.error("Error loading teams:", error);
        }
    }

    initializeCharts() {
        // Wait for the DOM to be ready and Chart.js to be available
        const initCharts = () => {
            if (typeof Chart !== 'undefined') {
                try {
                    this.createFinancialChart();
                    this.createRiskChart();
                    this.createPredictiveChart();
                    this.createTeamPerformanceChart();
                } catch (error) {
                    console.error("Error rendering strategic charts:", error);
                    this.showChartError();
                }
            } else {
                console.warn("Chart.js not available for strategic dashboard, using fallback");
                this.showChartFallback();
            }
        };

        // Use a small delay to ensure DOM is ready
        setTimeout(initCharts, 150);
    }

    showChartError() {
        // Show error message instead of breaking the component
        const chartContainers = document.querySelectorAll('.strategic-chart-container canvas');
        chartContainers.forEach(canvas => {
            const container = canvas.parentElement;
            container.innerHTML = `
                <div class="alert alert-warning text-center p-4">
                    <i class="fa fa-exclamation-triangle fa-2x mb-2"></i>
                    <h5>Chart Loading Error</h5>
                    <p>Unable to load strategic charts. Please refresh the page.</p>
                </div>
            `;
        });
    }

    showChartFallback() {
        // Show fallback content when Chart.js is not available
        const chartContainers = document.querySelectorAll('.strategic-chart-container canvas');
        chartContainers.forEach(canvas => {
            const container = canvas.parentElement;
            container.innerHTML = `
                <div class="alert alert-info text-center p-4">
                    <i class="fa fa-chart-line fa-2x mb-2"></i>
                    <h5>Strategic Charts Unavailable</h5>
                    <p>Chart library is loading. Strategic data is available in metrics above.</p>
                </div>
            `;
        });
    }

    createFinancialChart() {
        if (typeof Chart === 'undefined') {
            console.warn("Chart.js not available for financial chart");
            return;
        }

        const ctx = document.getElementById('financialChart');
        if (!ctx) {
            console.warn("Financial chart canvas not found");
            return;
        }

        try {
            const financial = this.state.dashboardData.financial_performance;
            const monthlyData = financial.monthly_revenue || {};
            
            this.charts.financial = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Object.keys(monthlyData),
                datasets: [{
                    label: 'Monthly Revenue',
                    data: Object.values(monthlyData),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Revenue Trend'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatCurrency(value);
                            }.bind(this)
                        }
                    }
                }
            }
        });
        } catch (error) {
            console.error("Error creating financial chart:", error);
        }
    }

    createRiskChart() {
        const ctx = document.getElementById('riskChart');
        if (!ctx) return;

        const risk = this.state.dashboardData.risk_indicators;
        
        this.charts.risk = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Overdue', 'Stagnant', 'At Risk', 'Healthy'],
                datasets: [{
                    data: [
                        risk.overdue_opportunities_count || 0,
                        risk.stagnant_opportunities_count || 0,
                        risk.at_risk_high_value_count || 0,
                        100 // Placeholder for healthy opportunities
                    ],
                    backgroundColor: [
                        '#dc3545',
                        '#ffc107',
                        '#fd7e14',
                        '#28a745'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Risk Indicators'
                    }
                }
            }
        });
    }

    createPredictiveChart() {
        const ctx = document.getElementById('predictiveChart');
        if (!ctx) return;

        const predictive = this.state.dashboardData.predictive_analytics;
        
        this.charts.predictive = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Current Pipeline', 'Next Month', 'Next Quarter'],
                datasets: [{
                    label: 'Forecasted Revenue',
                    data: [
                        predictive.weighted_pipeline || 0,
                        predictive.next_month_forecast || 0,
                        predictive.next_quarter_forecast || 0
                    ],
                    backgroundColor: [
                        '#17a2b8',
                        '#28a745',
                        '#007bff'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Revenue Forecast'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatCurrency(value);
                            }.bind(this)
                        }
                    }
                }
            }
        });
    }

    createTeamPerformanceChart() {
        const ctx = document.getElementById('teamChart');
        if (!ctx) return;

        const teams = this.state.dashboardData.team_overview || [];
        
        this.charts.team = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Revenue', 'Win Rate', 'Target Achievement', 'Opportunities'],
                datasets: teams.slice(0, 3).map((team, index) => ({
                    label: team.team_name,
                    data: [
                        (team.revenue / 100000), // Normalized
                        team.win_rate,
                        team.target_achievement,
                        (team.opportunities / 10) // Normalized
                    ],
                    borderColor: ['#007bff', '#28a745', '#dc3545'][index],
                    backgroundColor: [`rgba(0, 123, 255, 0.1)`, `rgba(40, 167, 69, 0.1)`, `rgba(220, 53, 69, 0.1)`][index]
                }))
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Team Performance Comparison'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    updateCharts() {
        if (this.charts.financial) {
            this.charts.financial.destroy();
            this.createFinancialChart();
        }
        if (this.charts.risk) {
            this.charts.risk.destroy();
            this.createRiskChart();
        }
        if (this.charts.predictive) {
            this.charts.predictive.destroy();
            this.createPredictiveChart();
        }
        if (this.charts.team) {
            this.charts.team.destroy();
            this.createTeamPerformanceChart();
        }
    }

    setupAutoRefresh() {
        if (this.state.autoRefresh) {
            this.refreshTimer = setInterval(() => {
                this.loadDashboardData();
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

    async onDateRangeChange() {
        await this.loadDashboardData();
    }

    async onTeamSelectionChange() {
        await this.loadDashboardData();
    }

    async onRefreshClick() {
        this.state.isLoading = true;
        await this.loadDashboardData();
        this.state.isLoading = false;
        
        this.notification.add(
            _t("Dashboard data refreshed successfully"),
            { type: "success" }
        );
    }

    formatCurrency(value) {
        const symbol = this.state.dashboardData.currency_symbol || '$';
        return `${symbol}${this.formatNumber(value)}`;
    }

    formatNumber(value) {
        if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'K';
        }
        return value.toString();
    }

    formatPercentage(value) {
        return `${value}%`;
    }

    async exportData() {
        try {
            const url = `/crm/strategic/dashboard/export?date_from=${this.state.dateRange.start}&date_to=${this.state.dateRange.end}&team_ids=${this.state.selectedTeams.join(',')}`;
            window.open(url, '_blank');
        } catch (error) {
            this.notification.add(
                _t("Failed to export data: %s", error.message),
                { type: "danger" }
            );
        }
    }

    // Action handlers for drilling down into specific metrics
    onKPIClick(kpiType) {
        switch(kpiType) {
            case 'pipeline_value':
                this.action.doAction({
                    type: 'ir.actions.act_window',
                    name: 'Pipeline Opportunities',
                    res_model: 'crm.lead',
                    view_mode: 'tree,form',
                    domain: [['type', '=', 'opportunity'], ['active', '=', true]],
                    context: {}
                });
                break;
            case 'overdue':
                this.action.doAction({
                    type: 'ir.actions.act_window',
                    name: 'Overdue Opportunities',
                    res_model: 'crm.lead',
                    view_mode: 'tree,form',
                    domain: [
                        ['type', '=', 'opportunity'],
                        ['date_deadline', '<', new Date().toISOString().split('T')[0]],
                        ['active', '=', true]
                    ],
                    context: {}
                });
                break;
            // Add more cases as needed
        }
    }

    willUnmount() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Register the component
registry.category("actions").add("crm_strategic_dashboard", CRMStrategicDashboard);
