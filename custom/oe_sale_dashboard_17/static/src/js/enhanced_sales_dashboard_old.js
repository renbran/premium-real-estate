/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class EnhancedSalesDashboardView extends Component {
    static template = "oe_sale_dashboard_17.EnhancedDashboard";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            loading: true,
            data: {
                performance: {},
                monthly_trend: [],
                sales_by_state: {},
                top_customers: {},
                team_performance: {},
                agent_ranking: {},
                broker_ranking: {},
                recent_orders: [],
                sale_type_options: [],
                predefined_ranges: {}
            },
            dateRange: {
                start: this.getDefaultStartDate(),
                end: this.getDefaultEndDate()
            },
            selectedSaleTypes: [],
            selectedPredefinedRange: 'last_30_days'
        });
        
        // Chart references
        this.monthlyTrendChart = useRef("monthlyTrendChart");
        this.salesStateChart = useRef("salesStateChart");
        this.topCustomersChart = useRef("topCustomersChart");
        this.teamPerformanceChart = useRef("teamPerformanceChart");
        this.agentRankingChart = useRef("agentRankingChart");
        this.brokerRankingChart = useRef("brokerRankingChart");
        
        // Chart instances
        this.chartInstances = {};
        
        onMounted(async () => {
            await this.loadDashboardData();
            this.setupEventListeners();
        });
        
        onWillUnmount(() => {
            this.destroyAllCharts();
        });
    }
    
    getDefaultStartDate() {
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
        return thirtyDaysAgo.toISOString().split('T')[0];
    }
    
    getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }
    
    async loadDashboardData() {
        try {
            this.state.loading = true;
            
            const data = await this.orm.call(
                "sale.dashboard", 
                "get_comprehensive_dashboard_data", 
                [this.state.dateRange.start, this.state.dateRange.end, this.state.selectedSaleTypes]
            );
            
            this.state.data = data;
            
            // Render all charts after data load
            await this.renderAllCharts();
            
            this.state.loading = false;
            
        } catch (error) {
            console.error("Enhanced dashboard error:", error);
            this.notification.add(_t("Failed to load enhanced dashboard data"), { type: "danger" });
            this.state.loading = false;
        }
    }
    
    setupEventListeners() {
        // Date range change listeners
        const startDateInput = document.getElementById('start_date_enhanced');
        const endDateInput = document.getElementById('end_date_enhanced');
        
        if (startDateInput) {
            startDateInput.addEventListener('change', (e) => {
                this.state.dateRange.start = e.target.value;
                this.state.selectedPredefinedRange = 'custom';
                this.loadDashboardData();
            });
        }
        
        if (endDateInput) {
            endDateInput.addEventListener('change', (e) => {
                this.state.dateRange.end = e.target.value;
                this.state.selectedPredefinedRange = 'custom';
                this.loadDashboardData();
            });
        }
        
        // Predefined range selector
        const predefinedSelect = document.getElementById('predefined_range_select');
        if (predefinedSelect) {
            predefinedSelect.addEventListener('change', (e) => {
                this.onPredefinedRangeChange(e.target.value);
            });
        }
        
        // Sale type filter
        const saleTypeSelect = document.getElementById('sale_type_enhanced_filter');
        if (saleTypeSelect) {
            saleTypeSelect.addEventListener('change', (e) => {
                const selectedOptions = Array.from(e.target.selectedOptions);
                this.state.selectedSaleTypes = selectedOptions.map(option => parseInt(option.value)).filter(v => !isNaN(v));
                this.loadDashboardData();
            });
        }
    }
    
    onPredefinedRangeChange(rangeKey) {
        if (rangeKey === 'custom') {
            this.state.selectedPredefinedRange = 'custom';
            return;
        }
        
        const range = this.state.data.predefined_ranges[rangeKey];
        if (range) {
            this.state.dateRange.start = range.start_date;
            this.state.dateRange.end = range.end_date;
            this.state.selectedPredefinedRange = rangeKey;
            
            // Update input fields
            const startInput = document.getElementById('start_date_enhanced');
            const endInput = document.getElementById('end_date_enhanced');
            if (startInput) startInput.value = range.start_date;
            if (endInput) endInput.value = range.end_date;
            
            this.loadDashboardData();
        }
    }
    
    async renderAllCharts() {
        // Wait for DOM to be ready
        await new Promise(resolve => setTimeout(resolve, 100));
        
        this.destroyAllCharts();
        
        // Render each chart
        this.renderMonthlyTrendChart();
        this.renderSalesStateChart();
        this.renderTopCustomersChart();
        this.renderTeamPerformanceChart();
        this.renderAgentRankingChart();
        this.renderBrokerRankingChart();
    }
    
    renderMonthlyTrendChart() {
        const canvas = this.monthlyTrendChart.el;
        if (!canvas || !this.state.data.monthly_trend) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.monthly_trend;
        
        this.chartInstances.monthlyTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.month),
                datasets: [{
                    label: _t("Monthly Sales Revenue"),
                    data: data.map(item => item.amount),
                    backgroundColor: 'rgba(128, 0, 32, 0.1)',
                    borderColor: '#800020',
                    borderWidth: 4,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#800020',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 3,
                    pointRadius: 8,
                    pointHoverRadius: 12,
                    pointHoverBackgroundColor: '#FFD700',
                    pointHoverBorderColor: '#800020',
                    pointHoverBorderWidth: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Monthly Sales Trend (Booking Date)"),
                        font: { size: 18, weight: 'bold' },
                        color: '#800020',
                        padding: 20
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#800020',
                            font: { weight: 'bold', size: 12 },
                            padding: 20
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatCurrency(value);
                            }.bind(this),
                            color: '#495057',
                            font: { weight: 'bold' }
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)',
                            lineWidth: 1
                        }
                    },
                    x: {
                        ticks: {
                            color: '#495057',
                            font: { weight: 'bold' }
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.05)',
                            lineWidth: 1
                        }
                    }
                },
                elements: {
                    point: {
                        hoverRadius: 12
                    }
                }
            }
        });
    }
    
    renderSalesStateChart() {
        const canvas = this.salesStateChart.el;
        if (!canvas || !this.state.data.sales_by_state) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.sales_by_state;
        
        this.chartInstances.salesState = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.counts || [],
                    backgroundColor: [
                        '#800020',     // Primary Burgundy
                        '#A0002A',     // Darker Burgundy 
                        '#FFD700',     // Gold Accent
                        '#B8860B',     // Dark Gold
                        '#600018',     // Deep Burgundy
                        '#C41E3A'      // Crimson Red
                    ],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 4,
                    hoverBorderColor: '#800020'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Sales by State"),
                        font: { size: 16, weight: 'bold' },
                        color: '#800020'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    renderTopCustomersChart() {
        const canvas = this.topCustomersChart.el;
        if (!canvas || !this.state.data.top_customers) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.top_customers;
        
        this.chartInstances.topCustomers = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: _t("Revenue"),
                    data: data.amounts || [],
                    backgroundColor: 'rgba(128, 0, 32, 0.8)',
                    borderColor: '#800020',
                    borderWidth: 2,
                    hoverBackgroundColor: 'rgba(128, 0, 32, 1)',
                    hoverBorderColor: '#FFD700',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    title: {
                        display: true,
                        text: _t("Top Customers by Revenue"),
                        font: { size: 16, weight: 'bold' },
                        color: '#800020'
                    },
                    legend: {
                        labels: {
                            color: '#800020',
                            font: { weight: 'bold' }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatCurrency(value);
                            }.bind(this),
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    renderTeamPerformanceChart() {
        const canvas = this.teamPerformanceChart.el;
        if (!canvas || !this.state.data.team_performance) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.team_performance;
        
        this.chartInstances.teamPerformance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: _t("Team Revenue"),
                    data: data.amounts || [],
                    backgroundColor: 'rgba(255, 215, 0, 0.8)',  // Gold theme for teams
                    borderColor: '#FFD700',
                    borderWidth: 2,
                    hoverBackgroundColor: 'rgba(255, 215, 0, 1)',
                    hoverBorderColor: '#800020',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Sales Team Performance"),
                        font: { size: 16, weight: 'bold' },
                        color: '#800020'
                    },
                    legend: {
                        labels: {
                            color: '#800020',
                            font: { weight: 'bold' }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatCurrency(value);
                            }.bind(this),
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    renderAgentRankingChart() {
        const canvas = this.agentRankingChart.el;
        if (!canvas || !this.state.data.agent_ranking) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.agent_ranking;
        
        this.chartInstances.agentRanking = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.agents || [],
                datasets: [{
                    label: _t("Total Revenue"),
                    data: data.total_amounts || [],
                    backgroundColor: 'rgba(128, 0, 32, 0.8)',
                    borderColor: '#800020',
                    borderWidth: 2,
                    yAxisID: 'y',
                    hoverBackgroundColor: 'rgba(128, 0, 32, 1)',
                    hoverBorderColor: '#FFD700',
                    hoverBorderWidth: 3
                }, {
                    label: _t("Deal Count"),
                    data: data.deal_counts || [],
                    backgroundColor: 'rgba(255, 215, 0, 0.8)',
                    borderColor: '#FFD700',
                    borderWidth: 2,
                    yAxisID: 'y1',
                    hoverBackgroundColor: 'rgba(255, 215, 0, 1)',
                    hoverBorderColor: '#800020',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Top Agents Performance"),
                        font: { size: 16, weight: 'bold' },
                        color: '#800020'
                    },
                    legend: {
                        labels: {
                            color: '#800020',
                            font: { weight: 'bold' }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatCurrency(value);
                            }.bind(this),
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        ticks: {
                            color: '#495057'
                        },
                        grid: {
                            drawOnChartArea: false,
                            color: 'rgba(255, 215, 0, 0.1)'
                        },
                    },
                    x: {
                        ticks: {
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    renderBrokerRankingChart() {
        const canvas = this.brokerRankingChart.el;
        if (!canvas || !this.state.data.broker_ranking) return;
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.broker_ranking;
        
        this.chartInstances.brokerRanking = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.brokers || [],
                datasets: [{
                    label: _t("Total Revenue"),
                    data: data.total_amounts || [],
                    backgroundColor: 'rgba(255, 215, 0, 0.8)',
                    borderColor: '#FFD700',
                    borderWidth: 2,
                    yAxisID: 'y',
                    hoverBackgroundColor: 'rgba(255, 215, 0, 1)',
                    hoverBorderColor: '#800020',
                    hoverBorderWidth: 3
                }, {
                    label: _t("Deal Count"),
                    data: data.deal_counts || [],
                    backgroundColor: 'rgba(128, 0, 32, 0.8)',
                    borderColor: '#800020',
                    borderWidth: 2,
                    yAxisID: 'y1',
                    hoverBackgroundColor: 'rgba(128, 0, 32, 1)',
                    hoverBorderColor: '#FFD700',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Top Brokers Performance"),
                        font: { size: 16, weight: 'bold' },
                        color: '#800020'
                    },
                    legend: {
                        labels: {
                            color: '#800020',
                            font: { weight: 'bold' }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatCurrency(value);
                            }.bind(this),
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        ticks: {
                            color: '#495057'
                        },
                        grid: {
                            drawOnChartArea: false,
                            color: 'rgba(255, 215, 0, 0.1)'
                        },
                    },
                    x: {
                        ticks: {
                            color: '#495057'
                        },
                        grid: {
                            color: 'rgba(128, 0, 32, 0.1)'
                        }
                    }
                }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }
    
    destroyAllCharts() {
        Object.values(this.chartInstances).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        this.chartInstances = {};
    }
    
    formatNumber(value) {
        if (!value || value === 0) return "0";
        
        const absValue = Math.abs(value);
        
        if (absValue >= 1_000_000_000) {
            return (value / 1_000_000_000).toFixed(2) + "B";
        } else if (absValue >= 1_000_000) {
            return (value / 1_000_000).toFixed(2) + "M";
        } else if (absValue >= 1_000) {
            return (value / 1_000).toFixed(0) + "K";
        } else {
            return Math.round(value).toString();
        }
    }
    
    formatCurrency(value) {
        if (!value || value === 0) return "$0";
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }
    
    async refreshData() {
        await this.loadDashboardData();
        this.notification.add(_t("Dashboard data refreshed"), { type: "success" });
    }
    
    async testBackendConnectivity() {
        try {
            const result = await this.orm.call("sale.dashboard", "get_predefined_date_ranges", []);
            if (result) {
                this.notification.add(_t("Backend connectivity test successful"), { type: "success" });
            } else {
                this.notification.add(_t("Backend connectivity test failed"), { type: "warning" });
            }
        } catch (error) {
            console.error("Backend test error:", error);
            this.notification.add(_t("Backend connectivity test failed"), { type: "danger" });
        }
    }
}

registry.category("views").add("enhanced_sales_dashboard", EnhancedSalesDashboardView);
