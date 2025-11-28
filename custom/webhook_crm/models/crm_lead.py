# -*- coding: utf-8 -*-

from odoo import models, api
import json
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    @api.model
    def create_from_webhook(self, webhook_data, source_name=None):
        """Create CRM lead from webhook data"""
        try:
            # Find appropriate mapping
            mapping = None
            if source_name:
                mapping = self.env['webhook.mapping'].search([
                    ('source_name', '=', source_name),
                    ('active', '=', True)
                ], limit=1)
            
            if not mapping:
                # Try to find a default mapping
                mapping = self.env['webhook.mapping'].search([
                    ('source_name', '=', 'default'),
                    ('active', '=', True)
                ], limit=1)
            
            if not mapping:
                _logger.error("No webhook mapping found for source: %s", source_name)
                return False
            
            # Process webhook data
            mapped_data = mapping.process_webhook_data(webhook_data)
            
            # Handle special fields
            mapped_data = self._process_special_fields(mapped_data)
            
            # Validate required fields
            if not self._validate_required_fields(mapped_data):
                _logger.error("Required fields missing in webhook data")
                return False
            
            # Create the lead
            lead = self.create(mapped_data)
            
            _logger.info("Successfully created lead %s from webhook", lead.name)
            return lead
            
        except Exception as e:
            _logger.error("Error creating lead from webhook: %s", str(e))
            return False
    
    def _process_special_fields(self, data):
        """Process special fields that need additional handling"""
        processed_data = data.copy()
        
        # Handle state_id (convert state name/code to ID)
        if 'state_id' in data and isinstance(data['state_id'], str):
            state = self.env['res.country.state'].search([
                '|', ('name', '=', data['state_id']), ('code', '=', data['state_id'])
            ], limit=1)
            processed_data['state_id'] = state.id if state else False
        
        # Handle country_id (convert country name/code to ID)
        if 'country_id' in data and isinstance(data['country_id'], str):
            country = self.env['res.country'].search([
                '|', ('name', '=', data['country_id']), ('code', '=', data['country_id'])
            ], limit=1)
            processed_data['country_id'] = country.id if country else False
        
        # Handle user_id (convert user name/email to ID)
        if 'user_id' in data and isinstance(data['user_id'], str):
            user = self.env['res.users'].search([
                '|', ('name', '=', data['user_id']), ('email', '=', data['user_id'])
            ], limit=1)
            processed_data['user_id'] = user.id if user else False
        
        # Handle team_id (convert team name to ID)
        if 'team_id' in data and isinstance(data['team_id'], str):
            team = self.env['crm.team'].search([('name', '=', data['team_id'])], limit=1)
            processed_data['team_id'] = team.id if team else False
        
        # Handle tag_ids (convert tag names to IDs)
        if 'tag_ids' in data:
            if isinstance(data['tag_ids'], str):
                tag_names = [tag.strip() for tag in data['tag_ids'].split(',')]
            elif isinstance(data['tag_ids'], list):
                tag_names = data['tag_ids']
            else:
                tag_names = []
            
            tag_ids = []
            for tag_name in tag_names:
                tag = self.env['crm.tag'].search([('name', '=', tag_name)], limit=1)
                if not tag:
                    tag = self.env['crm.tag'].create({'name': tag_name})
                tag_ids.append(tag.id)
            processed_data['tag_ids'] = [(6, 0, tag_ids)]
        
        # Handle source_id, medium_id, campaign_id
        for field in ['source_id', 'medium_id', 'campaign_id']:
            if field in data and isinstance(data[field], str):
                model_name = 'utm.' + field.replace('_id', '')
                record = self.env[model_name].search([('name', '=', data[field])], limit=1)
                if not record:
                    record = self.env[model_name].create({'name': data[field]})
                processed_data[field] = record.id
        
        return processed_data
    
    def _validate_required_fields(self, data):
        """Validate that required fields are present"""
        # At minimum, we need a name or contact_name
        if not data.get('name') and not data.get('contact_name'):
            return False
        
        # If name is missing, use contact_name
        if not data.get('name') and data.get('contact_name'):
            data['name'] = data['contact_name']
        
        return True
