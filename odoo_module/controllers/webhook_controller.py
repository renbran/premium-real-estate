# -*- coding: utf-8 -*-
"""
Bill Automation Webhook Controller
==================================

This controller handles incoming webhook requests for automated bill processing.
It provides a RESTful API endpoint that receives bill data from external systems
(like Zapier) and creates vendor bills in Odoo automatically.

Features:
- JSON payload processing
- Vendor auto-creation
- Duplicate detection
- File attachment support
- Comprehensive error handling
- Request logging
- API key authentication (optional)
- CORS support for web integrations

API Endpoints:
- POST /api/v1/bills/create - Create new vendor bill
- GET /api/v1/bills/health - Health check endpoint
- GET /api/v1/bills/status - Service status information

Author: Bill Automation Project Team
"""

import json
import logging
import base64
import requests
from datetime import datetime, date
import re

from odoo import http, api, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)


class BillAutomationController(http.Controller):
    """Main controller for bill automation webhook endpoints"""

    @http.route('/api/v1/bills/create', type='json', auth='none', 
                methods=['POST'], csrf=False, cors="*")
    def create_bill_webhook(self, **kwargs):
        """
        Main endpoint for creating vendor bills from webhook data
        
        Expected JSON payload:
        {
            "vendor_name": "Company Name",
            "amount": 123.45,
            "invoice_date": "2024-10-28",
            "description": "Services description",
            "reference": "INV-001",
            "file_url": "https://...",
            "file_name": "bill.pdf",
            "currency": "USD",
            "tax_amount": 12.34,
            "api_key": "optional-security-key"
        }
        
        Returns:
        {
            "success": True/False,
            "message": "Status message",
            "data": {...} or "error": "Error details"
        }
        """
        webhook_log = None
        
        try:
            with api.Environment.manage():
                with request.registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    
                    # Get configuration
                    config = self._get_webhook_config(env)
                    
                    # Check if webhook is enabled
                    if not config or not config.webhook_enabled:
                        return self._error_response('Webhook is disabled')
                    
                    # Get and validate request data
                    request_data = self._get_request_data()
                    if not request_data:
                        return self._error_response('No data received')
                    
                    # Create webhook log entry
                    webhook_log = self._create_webhook_log(env, request_data, 'processing')
                    
                    # Validate API key if required
                    if config.api_key_required:
                        api_key_valid = self._validate_api_key(env, request_data.get('api_key'))
                        if not api_key_valid:
                            self._update_webhook_log(webhook_log, 'failed', 'Invalid API key')
                            return self._error_response('Invalid API key', 401)
                    
                    # Extract and validate bill data
                    bill_data = self._extract_bill_data(request_data)
                    if 'error' in bill_data:
                        self._update_webhook_log(webhook_log, 'failed', bill_data['error'])
                        return self._error_response(bill_data['error'])
                    
                    # Process the bill creation
                    result = self._process_bill_creation(env, config, bill_data)
                    
                    if result['success']:
                        # Update log with success
                        self._update_webhook_log(
                            webhook_log, 'success', 
                            f"Bill created: {result['data']['bill_number']}",
                            result['data']
                        )
                        
                        _logger.info(f"Bill created successfully via webhook: {result['data']['bill_number']}")
                        return self._success_response(result['message'], result['data'])
                    else:
                        # Update log with error
                        self._update_webhook_log(webhook_log, 'failed', result['error'])
                        return self._error_response(result['error'])
                        
        except Exception as e:
            error_msg = f"Unexpected webhook error: {str(e)}"
            _logger.error(error_msg, exc_info=True)
            
            if webhook_log:
                try:
                    self._update_webhook_log(webhook_log, 'failed', error_msg)
                except:
                    pass  # Don't fail on log update error
            
            return self._error_response(error_msg, 500)

    @http.route('/api/v1/bills/health', type='json', auth='none', 
                methods=['GET'], csrf=False, cors="*")
    def health_check(self):
        """Health check endpoint for monitoring"""
        try:
            with api.Environment.manage():
                with request.registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    
                    # Check basic requirements
                    checks = self._run_health_checks(env)
                    
                    all_healthy = all(check['status'] for check in checks['checks'])
                    
                    return {
                        'status': 'healthy' if all_healthy else 'unhealthy',
                        'timestamp': datetime.now().isoformat(),
                        'checks': checks['checks'],
                        'version': '1.0.0'
                    }
                    
        except Exception as e:
            _logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    @http.route('/api/v1/bills/status', type='json', auth='none', 
                methods=['GET'], csrf=False, cors="*")
    def service_status(self):
        """Service status information endpoint"""
        try:
            with api.Environment.manage():
                with request.registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    
                    config = self._get_webhook_config(env)
                    
                    # Get recent statistics
                    stats = self._get_webhook_statistics(env)
                    
                    return {
                        'service': 'Bill Automation Webhook',
                        'version': '1.0.0',
                        'status': 'enabled' if config and config.webhook_enabled else 'disabled',
                        'timestamp': datetime.now().isoformat(),
                        'statistics': stats,
                        'endpoints': {
                            'create_bill': '/api/v1/bills/create',
                            'health_check': '/api/v1/bills/health',
                            'status': '/api/v1/bills/status'
                        }
                    }
                    
        except Exception as e:
            _logger.error(f"Status check failed: {str(e)}")
            return {
                'service': 'Bill Automation Webhook',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_request_data(self):
        """Extract JSON data from request"""
        try:
            if hasattr(request, 'httprequest'):
                if request.httprequest.is_json:
                    return request.httprequest.get_json()
                else:
                    return json.loads(request.httprequest.data.decode('utf-8'))
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
            _logger.error(f"Failed to parse request data: {str(e)}")
            return None

    def _get_webhook_config(self, env):
        """Get webhook configuration"""
        try:
            return env['bill.automation.config'].search([], limit=1)
        except:
            return None

    def _validate_api_key(self, env, provided_key):
        """Validate API key if required"""
        if not provided_key:
            return False
        
        config = self._get_webhook_config(env)
        return config and config.api_key == provided_key

    def _create_webhook_log(self, env, request_data, status):
        """Create webhook log entry"""
        try:
            return env['webhook.log'].create({
                'request_data': json.dumps(request_data, indent=2),
                'status': status,
                'ip_address': request.httprequest.environ.get('REMOTE_ADDR', ''),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', ''),
            })
        except Exception as e:
            _logger.error(f"Failed to create webhook log: {str(e)}")
            return None

    def _update_webhook_log(self, log, status, message, response_data=None):
        """Update webhook log entry"""
        if not log:
            return
        
        try:
            update_vals = {
                'status': status,
                'error_message': message if status == 'failed' else None,
                'response_data': json.dumps(response_data, indent=2) if response_data else None,
            }
            log.write(update_vals)
        except Exception as e:
            _logger.error(f"Failed to update webhook log: {str(e)}")

    def _extract_bill_data(self, request_data):
        """Extract and validate bill data from request"""
        try:
            # Handle ChatGPT JSON string response
            if isinstance(request_data.get('vendor_name'), str) and request_data.get('vendor_name', '').startswith('{'):
                try:
                    chatgpt_data = json.loads(request_data.get('vendor_name', '{}'))
                    request_data.update(chatgpt_data)
                except json.JSONDecodeError:
                    pass
            
            # Validate required fields
            vendor_name = str(request_data.get('vendor_name', '')).strip()
            if not vendor_name or vendor_name.lower() in ['unknown vendor', 'unknown', '']:
                return {'error': 'Vendor name is required and cannot be empty'}
            
            # Parse and validate amount
            amount_str = str(request_data.get('amount', 0))
            amount = self._parse_amount(amount_str)
            if amount <= 0:
                return {'error': f'Invalid amount: {amount_str}'}
            
            # Parse date
            invoice_date = self._parse_date(request_data.get('invoice_date', ''))
            if not invoice_date:
                invoice_date = date.today().strftime('%Y-%m-%d')
            
            # Extract other fields
            description = str(request_data.get('description', 'Automated Bill Entry')).strip()
            reference = str(request_data.get('reference', '')).strip()
            file_url = str(request_data.get('file_url', '')).strip()
            file_name = str(request_data.get('file_name', 'bill.pdf')).strip()
            currency = str(request_data.get('currency', 'USD')).strip().upper()
            
            # Parse optional tax amount
            tax_amount = 0
            if request_data.get('tax_amount'):
                tax_amount = self._parse_amount(str(request_data.get('tax_amount', 0)))
            
            return {
                'vendor_name': vendor_name,
                'amount': amount,
                'invoice_date': invoice_date,
                'description': description,
                'reference': reference,
                'file_url': file_url,
                'file_name': file_name,
                'currency': currency,
                'tax_amount': tax_amount
            }
            
        except Exception as e:
            return {'error': f'Data extraction failed: {str(e)}'}

    def _parse_amount(self, amount_str):
        """Parse amount string to float"""
        try:
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[^\\d.,\\-]', '', str(amount_str))
            
            # Handle different decimal separators
            if ',' in cleaned and '.' in cleaned:
                if cleaned.rindex(',') > cleaned.rindex('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned and cleaned.count(',') == 1:
                parts = cleaned.split(',')
                if len(parts[1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0

    def _parse_date(self, date_str):
        """Parse date string to YYYY-MM-DD format"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(str(date_str), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # Extract numbers and try to construct date
            digits = re.findall(r'\\d+', str(date_str))
            if len(digits) >= 3:
                year = int(digits[2]) if int(digits[2]) > 31 else int(digits[2]) + 2000
                if year < 2000:
                    year += 2000
                
                if int(digits[0]) <= 12 and int(digits[1]) <= 31:
                    return f"{year:04d}-{int(digits[0]):02d}-{int(digits[1]):02d}"
                elif int(digits[1]) <= 12 and int(digits[0]) <= 31:
                    return f"{year:04d}-{int(digits[1]):02d}-{int(digits[0]):02d}"
                    
        except Exception as e:
            _logger.warning(f"Date parsing failed for '{date_str}': {str(e)}")
        
        return None

    def _process_bill_creation(self, env, config, bill_data):
        """Process the actual bill creation"""
        try:
            # Find or create vendor
            partner_result = self._find_or_create_vendor(env, config, bill_data['vendor_name'])
            if 'error' in partner_result:
                return {'success': False, 'error': partner_result['error']}
            
            partner = partner_result['partner']
            
            # Check for duplicates
            if config.duplicate_detection:
                duplicate_check = self._check_duplicate_bill(env, partner, bill_data)
                if duplicate_check['is_duplicate']:
                    return {
                        'success': False, 
                        'error': f"Duplicate bill detected: {duplicate_check['existing_bill'].name}"
                    }
            
            # Get Odoo objects
            odoo_objects = self._get_odoo_objects(env)
            if 'error' in odoo_objects:
                return {'success': False, 'error': odoo_objects['error']}
            
            # Create the bill
            bill_result = self._create_vendor_bill(env, bill_data, partner, odoo_objects)
            if 'error' in bill_result:
                return {'success': False, 'error': bill_result['error']}
            
            bill = bill_result['bill']
            
            # Attach file if enabled and URL provided
            file_attached = False
            if config.file_attachment_enabled and bill_data['file_url']:
                attachment_result = self._attach_file_to_bill(env, bill, bill_data)
                file_attached = attachment_result.get('success', False)
                if 'error' in attachment_result:
                    _logger.warning(f"File attachment failed: {attachment_result['error']}")
            
            return {
                'success': True,
                'message': 'Bill created successfully',
                'data': {
                    'bill_id': bill.id,
                    'bill_number': bill.name,
                    'vendor': partner.name,
                    'amount': bill.amount_total,
                    'invoice_date': bill_data['invoice_date'],
                    'reference': bill_data['reference'],
                    'file_attached': file_attached
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Bill creation failed: {str(e)}'}

    def _find_or_create_vendor(self, env, config, vendor_name):
        """Find existing vendor or create new one"""
        try:
            # Search for existing vendor
            partners = env['res.partner'].search([
                ('name', 'ilike', vendor_name),
                ('is_company', '=', True)
            ], limit=5)
            
            # Try exact match first
            for partner in partners:
                if partner.name.lower().strip() == vendor_name.lower().strip():
                    return {'partner': partner}
            
            # Try partial match
            for partner in partners:
                if (vendor_name.lower() in partner.name.lower() or 
                    partner.name.lower() in vendor_name.lower()):
                    return {'partner': partner}
            
            # Create new vendor if auto-creation is enabled
            if config.auto_create_vendors:
                partner_vals = {
                    'name': vendor_name,
                    'is_company': True,
                    'supplier_rank': 1,
                    'customer_rank': 0,
                }
                
                partner = env['res.partner'].create(partner_vals)
                _logger.info(f"Created new vendor: {vendor_name}")
                return {'partner': partner}
            else:
                return {'error': f'Vendor not found and auto-creation is disabled: {vendor_name}'}
                
        except Exception as e:
            return {'error': f'Vendor processing failed: {str(e)}'}

    def _check_duplicate_bill(self, env, partner, bill_data):
        """Check for duplicate bills"""
        try:
            domain = [
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'in_invoice'),
                ('state', 'in', ['draft', 'posted'])
            ]
            
            # Check by reference
            if bill_data['reference']:
                existing_by_ref = env['account.move'].search(domain + [
                    ('ref', '=', bill_data['reference'])
                ], limit=1)
                if existing_by_ref:
                    return {'is_duplicate': True, 'existing_bill': existing_by_ref}
            
            # Check by amount and date
            existing_by_amount = env['account.move'].search(domain + [
                ('amount_total', '=', bill_data['amount']),
                ('invoice_date', '=', bill_data['invoice_date'])
            ], limit=1)
            
            if existing_by_amount:
                return {'is_duplicate': True, 'existing_bill': existing_by_amount}
            
            return {'is_duplicate': False}
            
        except Exception as e:
            _logger.warning(f"Duplicate check failed: {str(e)}")
            return {'is_duplicate': False}

    def _get_odoo_objects(self, env):
        """Get required Odoo objects"""
        try:
            journal = env['account.journal'].search([('type', '=', 'purchase')], limit=1)
            if not journal:
                return {'error': 'No purchase journal found'}
            
            expense_account = env['account.account'].search([
                ('account_type', '=', 'expense')
            ], limit=1)
            
            if not expense_account:
                expense_account = env['account.account'].search([
                    ('code', '=like', '6%')
                ], limit=1)
            
            if not expense_account:
                return {'error': 'No expense account found'}
            
            return {
                'journal': journal,
                'expense_account': expense_account
            }
            
        except Exception as e:
            return {'error': f'Odoo objects retrieval failed: {str(e)}'}

    def _create_vendor_bill(self, env, bill_data, partner, odoo_objects):
        """Create the vendor bill"""
        try:
            line_amount = bill_data['amount']
            if bill_data['tax_amount'] > 0:
                line_amount = bill_data['amount'] - bill_data['tax_amount']
            
            bill_vals = {
                'move_type': 'in_invoice',
                'partner_id': partner.id,
                'invoice_date': bill_data['invoice_date'],
                'ref': bill_data['reference'] or bill_data['description'],
                'journal_id': odoo_objects['journal'].id,
                'invoice_line_ids': [(0, 0, {
                    'name': bill_data['description'],
                    'quantity': 1,
                    'price_unit': line_amount,
                    'account_id': odoo_objects['expense_account'].id,
                })]
            }
            
            # Add tax if specified
            if bill_data['tax_amount'] > 0:
                default_tax = env['account.tax'].search([
                    ('type_tax_use', '=', 'purchase'),
                    ('amount_type', '=', 'percent')
                ], limit=1)
                
                if default_tax:
                    bill_vals['invoice_line_ids'][0][2]['tax_ids'] = [(6, 0, [default_tax.id])]
            
            bill = env['account.move'].create(bill_vals)
            bill._compute_amount()
            
            return {'bill': bill}
            
        except Exception as e:
            return {'error': f'Bill creation failed: {str(e)}'}

    def _attach_file_to_bill(self, env, bill, bill_data):
        """Download and attach file to bill"""
        if not bill_data['file_url']:
            return {'success': False, 'message': 'No file URL provided'}
        
        try:
            # Convert Google Drive URL if needed
            file_url = bill_data['file_url']
            if 'drive.google.com' in file_url and '/file/d/' in file_url:
                file_id = file_url.split('/file/d/')[1].split('/')[0]
                file_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            
            response = requests.get(file_url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if response.status_code == 200 and len(response.content) > 0:
                file_content = base64.b64encode(response.content)
                
                content_type = response.headers.get('content-type', 'application/pdf')
                if not content_type or content_type == 'text/html':
                    if bill_data['file_name'].lower().endswith('.pdf'):
                        content_type = 'application/pdf'
                    elif bill_data['file_name'].lower().endswith(('.jpg', '.jpeg')):
                        content_type = 'image/jpeg'
                    elif bill_data['file_name'].lower().endswith('.png'):
                        content_type = 'image/png'
                    else:
                        content_type = 'application/octet-stream'
                
                attachment = env['ir.attachment'].create({
                    'name': bill_data['file_name'],
                    'datas': file_content,
                    'res_model': 'account.move',
                    'res_id': bill.id,
                    'mimetype': content_type,
                    'description': f'Automated attachment from webhook'
                })
                
                return {'success': True, 'attachment_id': attachment.id}
            else:
                return {'error': f'Failed to download file: HTTP {response.status_code}'}
                
        except Exception as e:
            return {'error': f'File attachment failed: {str(e)}'}

    def _run_health_checks(self, env):
        """Run system health checks"""
        checks = []
        
        try:
            # Check webhook config
            config = self._get_webhook_config(env)
            checks.append({
                'name': 'Webhook Configuration',
                'status': bool(config),
                'message': 'OK' if config else 'Configuration not found'
            })
            
            # Check purchase journal
            journal = env['account.journal'].search([('type', '=', 'purchase')], limit=1)
            checks.append({
                'name': 'Purchase Journal',
                'status': bool(journal),
                'message': journal.name if journal else 'Not found'
            })
            
            # Check expense account
            expense_account = env['account.account'].search([('account_type', '=', 'expense')], limit=1)
            checks.append({
                'name': 'Expense Account',
                'status': bool(expense_account),
                'message': expense_account.code if expense_account else 'Not found'
            })
            
            # Check permissions
            can_create_bills = env['account.move'].check_access_rights('create', raise_exception=False)
            checks.append({
                'name': 'Create Bills Permission',
                'status': can_create_bills,
                'message': 'OK' if can_create_bills else 'Missing'
            })
            
        except Exception as e:
            checks.append({
                'name': 'Health Check Error',
                'status': False,
                'message': str(e)
            })
        
        return {'checks': checks}

    def _get_webhook_statistics(self, env):
        """Get webhook processing statistics"""
        try:
            logs = env['webhook.log'].search([])
            
            total_requests = len(logs)
            successful = len(logs.filtered(lambda l: l.status == 'success'))
            failed = len(logs.filtered(lambda l: l.status == 'failed'))
            
            return {
                'total_requests': total_requests,
                'successful': successful,
                'failed': failed,
                'success_rate': round((successful / total_requests * 100) if total_requests > 0 else 0, 2)
            }
        except:
            return {
                'total_requests': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0
            }

    def _success_response(self, message, data=None):
        """Create success response"""
        response = {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            response['data'] = data
        return response

    def _error_response(self, message, status_code=400):
        """Create error response"""
        return {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code
        }