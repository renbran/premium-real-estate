# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import json

_logger = logging.getLogger(__name__)


class WebhookMapping(models.Model):
    _name = 'webhook.mapping'
    _description = 'Webhook Field Mapping Configuration'
    _order = 'name, sequence'

    name = fields.Char(
        string='Mapping Name',
        required=True,
        help="Name for this webhook mapping configuration"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering mappings"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Whether this mapping is active"
    )
    
    endpoint_url = fields.Char(
        string='Webhook Endpoint URL',
        required=True,
        help="The URL endpoint for this webhook"
    )
    
    method = fields.Selection([
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH')
    ], string='HTTP Method', default='POST', required=True,
       help="HTTP method to use for the webhook")
    
    description = fields.Text(
        string='Description',
        help="Description of this webhook mapping"
    )
    
    field_mapping_ids = fields.One2many(
        'webhook.field.mapping',
        'webhook_mapping_id',
        string='Field Mappings',
        help="Field mapping configurations"
    )
    
    default_values = fields.Text(
        string='Default Values (JSON)',
        help="Default values to set on created records (JSON format)"
    )
    
    transformation_rules = fields.Text(
        string='Transformation Rules (JSON)',
        help="Data transformation rules (JSON format)"
    )
    
    @api.constrains('default_values')
    def _check_default_values_json(self):
        """Validate that default_values is valid JSON"""
        for record in self:
            if record.default_values:
                try:
                    json.loads(record.default_values)
                except json.JSONDecodeError:
                    raise ValidationError(_("Default Values must be valid JSON format"))
    
    @api.constrains('transformation_rules')
    def _check_transformation_rules_json(self):
        """Validate that transformation_rules is valid JSON"""
        for record in self:
            if record.transformation_rules:
                try:
                    json.loads(record.transformation_rules)
                except json.JSONDecodeError:
                    raise ValidationError(_("Transformation Rules must be valid JSON format"))
    
    def get_default_values_dict(self):
        """Parse default_values JSON string into dictionary"""
        try:
            return json.loads(self.default_values) if self.default_values else {}
        except json.JSONDecodeError:
            _logger.warning("Invalid JSON in default_values for mapping %s", self.name)
            return {}
    
    def get_transformation_rules_dict(self):
        """Parse transformation_rules JSON string into dictionary"""
        try:
            return json.loads(self.transformation_rules) if self.transformation_rules else {}
        except json.JSONDecodeError:
            _logger.warning("Invalid JSON in transformation_rules for mapping %s", self.name)
            return {}
    
    def transform_webhook_data(self, webhook_data):
        """Transform webhook data according to field mappings"""
        transformed_data = {}
        
        # Process field mappings
        for field_mapping in self.field_mapping_ids:
            if field_mapping.source_field in webhook_data:
                source_value = webhook_data[field_mapping.source_field]
                transformed_value = field_mapping.transform_value(source_value)
                if transformed_value is not None:
                    transformed_data[field_mapping.target_field] = transformed_value
        
        # Apply default values
        default_values = self.get_default_values_dict()
        for field_name, default_value in default_values.items():
            if field_name not in transformed_data:
                transformed_data[field_name] = default_value
        
        # Apply transformation rules
        transformation_rules = self.get_transformation_rules_dict()
        if transformation_rules:
            # Apply custom transformation logic here
            # This could be extended based on specific needs
            pass
        
        return transformed_data


class WebhookFieldMapping(models.Model):
    _name = 'webhook.field.mapping'
    _description = 'Webhook Field Mapping'
    _order = 'webhook_mapping_id, sequence, source_field'

    webhook_mapping_id = fields.Many2one(
        'webhook.mapping',
        string='Webhook Mapping',
        required=True,
        ondelete='cascade',
        help="Parent webhook mapping configuration"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering field mappings"
    )
    
    source_field = fields.Char(
        string='Source Field',
        required=True,
        help="Field name in the webhook payload"
    )
    
    target_field = fields.Char(
        string='Target Field',
        required=True,
        help="Field name in the target Odoo model"
    )
    
    field_type = fields.Selection([
        ('char', 'Character'),
        ('text', 'Text'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('selection', 'Selection'),
        ('many2one', 'Many2one'),
        ('one2many', 'One2many'),
        ('many2many', 'Many2many'),
    ], string='Field Type', default='char',
       help="Type of the target field")
    
    transformation_type = fields.Selection([
        ('direct', 'Direct Copy'),
        ('strip', 'Strip Whitespace'),
        ('upper', 'Uppercase'),
        ('lower', 'Lowercase'),
        ('title', 'Title Case'),
        ('default', 'Use Default Value'),
        ('custom', 'Custom Function'),
    ], string='Transformation Type', default='direct',
       help="Type of transformation to apply")
    
    default_value = fields.Char(
        string='Default Value',
        help="Default value to use if source field is empty or transformation type is 'default'"
    )
    
    required = fields.Boolean(
        string='Required',
        default=False,
        help="Whether this field mapping is required"
    )
    
    custom_function = fields.Char(
        string='Custom Function',
        help="Name of custom function to call for transformation (only used with 'custom' transformation type)"
    )
    
    def transform_value(self, source_value):
        """Transform a single value according to the mapping configuration"""
        if source_value is None and self.required:
            if self.default_value:
                return self.default_value
            return None
        
        if source_value is None:
            return self.default_value if self.default_value else None
        
        # Apply transformation based on type
        if self.transformation_type == 'direct':
            return source_value
        elif self.transformation_type == 'strip':
            return str(source_value).strip() if source_value else None
        elif self.transformation_type == 'upper':
            return str(source_value).upper() if source_value else None
        elif self.transformation_type == 'lower':
            return str(source_value).lower() if source_value else None
        elif self.transformation_type == 'title':
            return str(source_value).title() if source_value else None
        elif self.transformation_type == 'default':
            return self.default_value
        elif self.transformation_type == 'custom':
            return self._apply_custom_transformation(source_value)
        
        return source_value
    
    def _apply_custom_transformation(self, source_value):
        """Apply custom transformation function"""
        if not self.custom_function:
            return source_value
        
        # Here you could implement a registry of custom transformation functions
        # For now, just return the source value and log a warning
        _logger.info("Custom transformation function %s not implemented", self.custom_function)
        return source_value
    
    @api.constrains('source_field', 'target_field')
    def _check_field_names(self):
        """Validate field names"""
        for record in self:
            if not record.source_field or not record.target_field:
                raise ValidationError(_("Source and target field names are required"))
            
            # Check for duplicate mappings within the same webhook mapping
            domain = [
                ('webhook_mapping_id', '=', record.webhook_mapping_id.id),
                ('source_field', '=', record.source_field),
                ('id', '!=', record.id)
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_("Duplicate source field mapping: %s") % record.source_field)
