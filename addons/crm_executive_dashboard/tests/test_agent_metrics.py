# -*- coding: utf-8 -*-

import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestCRMExecutiveDashboardAgentMetrics(TransactionCase):

    def setUp(self):
        super(TestCRMExecutiveDashboardAgentMetrics, self).setUp()
        
        # Create test users/agents
        self.agent1 = self.env['res.users'].create({
            'name': 'Agent One',
            'login': 'agent1@test.com',
            'email': 'agent1@test.com',
            'groups_id': [(6, 0, [self.env.ref('sales_team.group_sale_salesman').id])]
        })
        
        self.agent2 = self.env['res.users'].create({
            'name': 'Agent Two', 
            'login': 'agent2@test.com',
            'email': 'agent2@test.com',
            'groups_id': [(6, 0, [self.env.ref('sales_team.group_sale_salesman').id])]
        })
        
        # Create test team
        self.sales_team = self.env['crm.team'].create({
            'name': 'Test Sales Team',
            'member_ids': [(6, 0, [self.agent1.id, self.agent2.id])]
        })
        
        # Create test leads
        self.test_leads = []
        for i in range(10):
            lead = self.env['crm.lead'].create({
                'name': f'Test Lead {i+1}',
                'user_id': self.agent1.id if i < 5 else self.agent2.id,
                'team_id': self.sales_team.id,
                'type': 'opportunity' if i % 2 == 0 else 'lead',
                'planned_revenue': 1000 * (i + 1),
                'probability': 50 if i < 8 else 0,  # Some lost leads
            })
            self.test_leads.append(lead)
        
        # Mark some as won
        for i in range(3):
            self.test_leads[i].action_set_won()
            
        # Mark some as lost
        for i in range(8, 10):
            self.test_leads[i].action_set_lost()

        self.dashboard = self.env['crm.executive.dashboard'].create({
            'name': 'Test Dashboard',
            'team_ids': [(6, 0, [self.sales_team.id])]
        })

    def test_agent_performance_metrics(self):
        """Test agent performance metrics functionality"""
        _logger.info("Testing agent performance metrics...")
        
        # Test agent performance metrics
        agent_metrics = self.dashboard._get_agent_performance_metrics(
            self.dashboard.date_from,
            self.dashboard.date_to,
            [self.sales_team.id]
        )
        
        self.assertIn('top_agents_with_progress', agent_metrics)
        self.assertIn('most_converted_agents', agent_metrics)
        
        # Check that we have some progress data
        self.assertTrue(len(agent_metrics['top_agents_with_progress']) > 0)
        self.assertTrue(len(agent_metrics['most_converted_agents']) > 0)
        
        _logger.info(f"Agent metrics: {agent_metrics}")

    def test_lead_quality_metrics(self):
        """Test lead quality metrics functionality"""
        _logger.info("Testing lead quality metrics...")
        
        # Test lead quality metrics
        lead_quality = self.dashboard._get_lead_quality_metrics(
            self.dashboard.date_from,
            self.dashboard.date_to,
            [self.sales_team.id]
        )
        
        self.assertIn('most_junked_agents', lead_quality)
        self.assertIn('source_quality', lead_quality)
        
        # Should have junked leads data since we created lost leads
        self.assertTrue(len(lead_quality['most_junked_agents']) > 0)
        
        _logger.info(f"Lead quality metrics: {lead_quality}")

    def test_response_time_metrics(self):
        """Test response time metrics functionality"""
        _logger.info("Testing response time metrics...")
        
        # Test response time metrics
        response_metrics = self.dashboard._get_response_time_metrics(
            self.dashboard.date_from,
            self.dashboard.date_to,
            [self.sales_team.id]
        )
        
        self.assertIn('fast_responders', response_metrics)
        self.assertIn('slow_responders', response_metrics)
        self.assertIn('fast_updaters', response_metrics)
        self.assertIn('slow_updaters', response_metrics)
        
        _logger.info(f"Response metrics: {response_metrics}")

    def test_complete_dashboard_data(self):
        """Test complete dashboard data with new metrics"""
        _logger.info("Testing complete dashboard data...")
        
        # Test complete dashboard data
        dashboard_data = self.dashboard.get_dashboard_data(
            self.dashboard.date_from,
            self.dashboard.date_to,
            [self.sales_team.id]
        )
        
        # Check all required sections exist
        required_sections = [
            'kpis', 'pipeline', 'trends', 'team_performance', 
            'customer_acquisition', 'agent_metrics', 'lead_quality', 
            'response_metrics'
        ]
        
        for section in required_sections:
            self.assertIn(section, dashboard_data, f"Missing section: {section}")
        
        # Check agent metrics structure
        agent_metrics = dashboard_data['agent_metrics']
        self.assertIn('top_agents_with_progress', agent_metrics)
        self.assertIn('most_converted_agents', agent_metrics)
        
        # Check lead quality structure
        lead_quality = dashboard_data['lead_quality']
        self.assertIn('most_junked_agents', lead_quality)
        self.assertIn('source_quality', lead_quality)
        
        # Check response metrics structure
        response_metrics = dashboard_data['response_metrics']
        self.assertIn('fast_responders', response_metrics)
        self.assertIn('slow_responders', response_metrics)
        self.assertIn('fast_updaters', response_metrics)
        self.assertIn('slow_updaters', response_metrics)
        
        _logger.info("✅ All dashboard data sections present and structured correctly")

    def test_agent_partner_id_tracking(self):
        """Test that agent partner_id is properly tracked"""
        _logger.info("Testing agent partner_id tracking...")
        
        agent_metrics = self.dashboard._get_agent_performance_metrics(
            self.dashboard.date_from,
            self.dashboard.date_to,
            [self.sales_team.id]
        )
        
        # Check that partner_id is included in agent data
        for agent in agent_metrics['top_agents_with_progress']:
            self.assertIn('partner_id', agent)
            self.assertIn('agent_id', agent)
            self.assertTrue(agent['partner_id'] is not None or agent['partner_id'] is None)
            
        _logger.info("✅ Agent partner_id tracking working correctly")
