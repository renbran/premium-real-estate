/** @odoo-module **/

import { Component, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CRMDashboardView extends Component {
    static template = "crm_dashboard.Dashboard";
    
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        
        // Chart references
        this.chartRefs = {
            overdue_chart: useRef("overdue_chart"),
            pipeline_chart: useRef("pipeline_chart"),
            lead_chart: useRef("lead_chart"),
            won_chart: useRef("won_chart"),
            yearly_chart: useRef("yearly_chart"),
            won_chart_year: useRef("won_chart_year"),
            expected_chart: useRef("expected_chart")
        };
        
        onMounted(() => {
            this.willStart();
        });
        
        onWillUnmount(() => {
            // Cleanup charts if needed
            Object.values(this.chartInstances || {}).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
        });
        
        this.chartInstances = {};
    }

    async willStart() {
        try {
            await this.get_details();
            await this.render_dashboards();
            await this.render_graphs();
        } catch (error) {
            console.error("Error initializing CRM Dashboard:", error);
            this.notification.add(
                _t("Failed to load dashboard data"),
                { type: "danger" }
            );
        }
    }

    // Events - Convert to modern event handling
    async action_overdue_opportunities() {
        'click .my_pipeline': 'action_my_pipeline',
        'click .open_opportunities': 'action_open_opportunities',
        'click .won_count': 'action_won_count',
        'click .loss_count': 'action_loss_count',
        'click .tot_exp_revenue': 'action_tot_exp_revenue',
	},
	init: function(parent, context) {
        this._super(parent, context);
        var crm_data = [];
        var self = this;
        if (context.tag == 'crm_dashboard.dashboard') {
            self._rpc({
                model: 'crm.dashboard',
                method: 'get_crm_info',
            }, []).then(function(result){
                self.crm_data = result[0]
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });
        }
    },
    async willStart() {
        try {
            await this.loadLibraries();
            await super.willStart();
        } catch (error) {
            console.error("Error in willStart:", error);
        }
    },
    
    async loadLibraries() {
        // Modern library loading would happen here
        // In OWL components, libraries are typically loaded via imports
        console.log("Libraries loaded");
    },
    start() {
        try {
            return super.start();
        } catch (error) {
            console.error("Error in start:", error);
        }
    },
    render() {
        const superRender = super.render;
        
        try {
            // Modern template rendering in OWL is handled automatically
            // The template is already defined in static template
            
            // Hide control panel using modern DOM methods
            const controlPanel = document.querySelector(".o_control_panel");
            if (controlPanel) {
                controlPanel.classList.add("o_hidden");
            }
            
            // Trigger graph rendering
            this.graph();
            
            return true;
        } catch (error) {
            console.error("Error in render:", error);
            return false;
        }
    },
    reload: function () {
            window.location.href = this.href;
    },
    action_overdue_opportunities: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Overdue Opportunities"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {                        
                        'search_default_ep_overdue_opportunities':true,                   
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_my_pipeline: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("My Pipeline"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
            context: {                        
                        'search_default_assigned_to_me':true,                   
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_open_opportunities: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Open Opportunities"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
            context: {                        
                        'search_default_ep_open_opportunities':true,                   
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_won_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Won"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
            context: {                        
                        'search_default_ep_won':true,                   
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_loss_count: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Loss"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            context: {                        
                        'search_default_ep_lost':true,                   
                    },
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    action_tot_exp_revenue: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Loss"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],                
            search_view_id: self.crm_data.crm_search_view_id,
            target: 'current'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },

    // Here we are plotting bar,pie chart
    graph: function() {
        var self = this
        var ctx = this.$el.find('#Chart')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                //labels: ["January","February", "March", "April", "May", "June", "July", "August", "September",
                // "October", "November", "December"],
                labels: self.crm_data.graph_exp_revenue_label,
                datasets: [{
                    label: 'Expected Revenue',
                    data: self.crm_data.graph_exp_revenue_dataset,
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.crm_data.graph_exp_revenue_dataset),
                            //min: 1000,
                            //max: 100000,
                            stepSize: self.crm_data.
                            graph_exp_revenue_dataset.reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /self.crm_data.graph_exp_revenue_dataset.length
                          }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black'
                    }
                },
            },
        });
       

    },
    
});
core.action_registry.add('crm_dashboard.dashboard', CRMDashboardView);
return CRMDashboardView
    
});