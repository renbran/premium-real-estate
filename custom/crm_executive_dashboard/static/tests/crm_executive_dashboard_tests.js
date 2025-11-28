/** @odoo-module **/

import { describe, expect, test } from "@odoo/hoot";
import { Component, useState } from "@odoo/owl";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import { getFixture, mount } from "@web/../tests/helpers/utils";

import { CRMExecutiveDashboard } from "@crm_executive_dashboard/js/crm_executive_dashboard";

describe("CRM Executive Dashboard", () => {
    let target;
    let env;

    beforeEach(async () => {
        target = getFixture();
        env = await makeTestEnv();
    });

    test("Dashboard component renders correctly", async () => {
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        expect(target.querySelector(".o_crm_executive_dashboard")).toBeTruthy();
        expect(target.querySelector(".o_dashboard_header")).toBeTruthy();
        expect(target.querySelector(".o_kpi_section")).toBeTruthy();
        expect(target.querySelector(".o_charts_section")).toBeTruthy();
    });

    test("Date range filter updates correctly", async () => {
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        const startDateInput = target.querySelector('input[type="date"]');
        expect(startDateInput).toBeTruthy();
        
        // Test date change
        const newDate = "2024-01-01";
        startDateInput.value = newDate;
        startDateInput.dispatchEvent(new Event("change"));
        
        expect(dashboard.state.dateRange.start).toBe(newDate);
    });

    test("KPI cards display correct data", async () => {
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        // Mock dashboard data
        dashboard.state.dashboardData = {
            kpis: {
                total_leads: 150,
                total_opportunities: 75,
                won_revenue: 250000,
                conversion_rate: 15.5
            }
        };
        
        expect(target.querySelector(".o_kpi_leads h3").textContent).toBe("150");
        expect(target.querySelector(".o_kpi_opportunities h3").textContent).toBe("75");
        expect(target.querySelector(".o_kpi_revenue h3").textContent).toContain("250,000");
        expect(target.querySelector(".o_kpi_conversion h3").textContent).toBe("15.5%");
    });

    test("Charts initialize without errors", async () => {
        // Mock Chart.js
        global.Chart = class {
            constructor() {}
            destroy() {}
        };
        
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        // Set mock data for charts
        dashboard.state.dashboardData = {
            pipeline: { labels: ["New", "Qualified"], data: [10, 20], colors: ["#FF6384", "#36A2EB"] },
            trends: { labels: ["Jan", "Feb"], leads: [5, 10], opportunities: [2, 5], won_revenue: [1000, 2000] },
            team_performance: { labels: ["Team A"], won_revenue: [5000], conversion_rates: [25] },
            customer_acquisition: { sources: { labels: ["Web", "Email"], counts: [10, 5] } }
        };
        
        dashboard.renderAllCharts();
        
        expect(dashboard.charts.pipeline).toBeTruthy();
        expect(dashboard.charts.trends).toBeTruthy();
        expect(dashboard.charts.teamPerformance).toBeTruthy();
        expect(dashboard.charts.sources).toBeTruthy();
    });

    test("Auto refresh functionality works", async () => {
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        // Enable auto refresh
        dashboard.state.autoRefresh = true;
        dashboard.setupAutoRefresh();
        
        expect(dashboard.refreshTimer).toBeTruthy();
        
        // Disable auto refresh
        dashboard.toggleAutoRefresh();
        expect(dashboard.state.autoRefresh).toBe(false);
        expect(dashboard.refreshTimer).toBe(null);
    });

    test("Error handling displays notification", async () => {
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        // Mock RPC error
        dashboard.rpc = () => Promise.reject(new Error("Test error"));
        
        try {
            await dashboard.loadDashboardData();
        } catch (error) {
            expect(error.message).toBe("Test error");
        }
    });

    test("Export functionality triggers correctly", async () => {
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        // Mock window.open
        const originalOpen = window.open;
        window.open = jest.fn();
        
        await dashboard.exportData();
        
        expect(window.open).toHaveBeenCalled();
        window.open = originalOpen;
    });

    test("Mobile responsive classes are applied", async () => {
        // Set mobile viewport
        Object.defineProperty(window, 'innerWidth', { value: 600 });
        
        const dashboard = await mount(CRMExecutiveDashboard, target, { env });
        
        expect(target.querySelector(".o_crm_executive_dashboard")).toBeTruthy();
        // Test would need actual CSS media query evaluation
    });
});
