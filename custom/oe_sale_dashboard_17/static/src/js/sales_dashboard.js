/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";

export class SalesDashboardView extends Component {
    static template = "oe_sale_dashboard_17.Dashboard";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: true,
            salesData: {},
            chartData: null
        });
        
        this.chartRef = useRef("salesChart");
        this.chartInstance = null;
        
        onMounted(async () => {
            await this.loadChartLibrary();
            await this.loadSalesData();
            this.renderChart();
        });
    }
    
    async loadChartLibrary() {
        await loadJS("/oe_sale_dashboard_17/static/lib/charts/Chart.min.js");
    }
    
    async loadSalesData() {
        try {
            const data = await this.orm.call("sale.dashboard", "get_dashboard_data", []);
            this.state.salesData = data;
            this.prepareChartData(data);
        } catch (error) {
            console.error("Sales dashboard error:", error);
            this.notification.add(_t("Failed to load sales data"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    prepareChartData(data) {
        this.state.chartData = {
            labels: data.labels || [],
            datasets: [{
                label: _t("Sales"),
                data: data.values || [],
                backgroundColor: '#80002020',
                borderColor: '#800020',
                borderWidth: 2
            }]
        };
    }
    
    renderChart() {
        if (!this.chartRef.el || !this.state.chartData) return;
        
        const ctx = this.chartRef.el.getContext('2d');
        this.chartInstance = new Chart(ctx, {
            type: 'bar',
            data: this.state.chartData,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Sales Dashboard")
                    }
                }
            }
        });
    }
}

registry.category("views").add("sales_dashboard", SalesDashboardView);
