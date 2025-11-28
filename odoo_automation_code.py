#!/usr/bin/env python3
"""
Odoo Bill Automation - Quick Setup Code
=======================================

This script provides the Python code for setting up automated vendor bill creation 
in Odoo from webhook data received from Zapier automation.

Usage:
1. Copy the webhook code to Odoo Server Action
2. Create webhook endpoint routing
3. Test with provided test functions

Compatible with: Odoo 17, 18, 19
Author: Bill Automation Project
Version: 1.0.0
"""

import json
import logging
import base64
import requests
from datetime import datetime, date
import re

_logger = logging.getLogger(__name__)

# =============================================================================
# MAIN WEBHOOK HANDLER - Copy this to Odoo Server Action
# =============================================================================

def create_bill_from_webhook():
    """
    Main webhook handler function for creating vendor bills from automation data.
    
    Expected JSON payload:
    {
        "vendor_name": "Vendor Company Name",
        "amount": 123.45,
        "invoice_date": "2024-10-28",
        "description": "Services rendered",
        "reference": "INV-001",
        "file_url": "https://drive.google.com/file/d/xyz/view",
        "file_name": "bill.pdf",
        "currency": "USD" (optional),
        "tax_amount": 12.34 (optional)
    }
    
    Returns JSON response with success/error status
    """
    try:
        # Get the request data
        if hasattr(request, 'httprequest'):
            request_data = request.httprequest.get_json()
        else:
            # Fallback for different Odoo versions
            request_data = json.loads(request.get_data().decode('utf-8'))
        
        if not request_data:
            return _create_error_response('No data received in webhook')
        
        # Log incoming request for debugging
        _logger.info(f"Webhook received data: {json.dumps(request_data, indent=2)}")
        
        # Extract and validate bill information
        bill_data = _extract_bill_data(request_data)
        if 'error' in bill_data:
            return _create_error_response(bill_data['error'])
        
        # Find or create vendor
        partner_result = _find_or_create_vendor(bill_data['vendor_name'])
        if 'error' in partner_result:
            return _create_error_response(partner_result['error'])
        
        partner = partner_result['partner']
        
        # Check for duplicate bills
        duplicate_check = _check_duplicate_bill(partner, bill_data)
        if duplicate_check['is_duplicate']:
            return _create_error_response(
                f"Duplicate bill detected: {duplicate_check['existing_bill'].name}",
                {'existing_bill_id': duplicate_check['existing_bill'].id}
            )
        
        # Get required Odoo objects
        odoo_objects = _get_odoo_objects()
        if 'error' in odoo_objects:
            return _create_error_response(odoo_objects['error'])
        
        # Create the vendor bill
        bill_result = _create_vendor_bill(bill_data, partner, odoo_objects)
        if 'error' in bill_result:
            return _create_error_response(bill_result['error'])
        
        bill = bill_result['bill']
        
        # Attach file if URL provided
        attachment_result = _attach_file_to_bill(bill, bill_data)
        if 'error' in attachment_result:
            _logger.warning(f"File attachment failed: {attachment_result['error']}")
        
        # Return success response
        success_response = {
            'success': True,
            'message': 'Bill created successfully',
            'data': {
                'bill_id': bill.id,
                'bill_number': bill.name,
                'vendor': partner.name,
                'amount': bill.amount_total,
                'invoice_date': bill_data['invoice_date'],
                'reference': bill_data['reference'],
                'file_attached': attachment_result.get('success', False)
            }
        }
        
        _logger.info(f"Bill created successfully: {bill.name} for {partner.name}")
        return _create_json_response(success_response)
        
    except Exception as e:
        error_msg = f"Unexpected error in webhook: {str(e)}"
        _logger.error(error_msg, exc_info=True)
        return _create_error_response(error_msg)

def _extract_bill_data(request_data):
    """Extract and validate bill data from webhook payload"""
    try:
        # Handle ChatGPT response parsing if it's a string
        if isinstance(request_data.get('vendor_name'), str) and request_data.get('vendor_name', '').startswith('{'):
            # Parse JSON string from ChatGPT response
            try:
                chatgpt_data = json.loads(request_data.get('vendor_name', '{}'))
                request_data.update(chatgpt_data)
            except json.JSONDecodeError:
                pass
        
        vendor_name = request_data.get('vendor_name', '').strip()
        if not vendor_name or vendor_name.lower() == 'unknown vendor':
            return {'error': 'Vendor name is required'}
        
        # Parse amount
        amount_str = str(request_data.get('amount', 0))
        amount = _parse_amount(amount_str)
        if amount <= 0:
            return {'error': f'Invalid amount: {amount_str}'}
        
        # Parse date
        invoice_date = _parse_date(request_data.get('invoice_date', ''))
        if not invoice_date:
            invoice_date = date.today().strftime('%Y-%m-%d')
        
        # Clean up other fields
        description = request_data.get('description', 'Automated Bill Entry').strip()
        reference = request_data.get('reference', '').strip()
        file_url = request_data.get('file_url', '').strip()
        file_name = request_data.get('file_name', 'bill.pdf').strip()
        currency = request_data.get('currency', 'USD').strip().upper()
        
        # Parse optional tax amount
        tax_amount = 0
        if request_data.get('tax_amount'):
            tax_amount = _parse_amount(str(request_data.get('tax_amount', 0)))
        
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

def _parse_amount(amount_str):
    """Parse amount string to float, handling various formats"""
    try:
        # Remove common currency symbols and spaces
        cleaned = re.sub(r'[^\d.,\-]', '', str(amount_str))
        # Handle comma as decimal separator (European format)
        if ',' in cleaned and '.' in cleaned:
            # Assume last separator is decimal
            if cleaned.rindex(',') > cleaned.rindex('.'):
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned and cleaned.count(',') == 1:
            # Single comma, likely decimal separator
            parts = cleaned.split(',')
            if len(parts[1]) <= 2:  # Likely decimal
                cleaned = cleaned.replace(',', '.')
        
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0

def _parse_date(date_str):
    """Parse date string to YYYY-MM-DD format"""
    if not date_str:
        return None
    
    try:
        # Try different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(str(date_str), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If all formats fail, try to extract date components
        digits = re.findall(r'\d+', str(date_str))
        if len(digits) >= 3:
            # Assume first is day/month, second is month/day, third is year
            year = int(digits[2]) if int(digits[2]) > 31 else int(digits[2]) + 2000
            if year < 2000:
                year += 2000
            
            # Try day/month/year format first
            try:
                if int(digits[0]) <= 12 and int(digits[1]) <= 31:
                    return f"{year:04d}-{int(digits[0]):02d}-{int(digits[1]):02d}"
                elif int(digits[1]) <= 12 and int(digits[0]) <= 31:
                    return f"{year:04d}-{int(digits[1]):02d}-{int(digits[0]):02d}"
            except ValueError:
                pass
                
    except Exception as e:
        _logger.warning(f"Date parsing failed for '{date_str}': {str(e)}")
    
    return None

def _find_or_create_vendor(vendor_name):
    """Find existing vendor or create new one"""
    try:
        # Search for existing vendor (case-insensitive, partial match)
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
            if vendor_name.lower() in partner.name.lower() or partner.name.lower() in vendor_name.lower():
                _logger.info(f"Found similar vendor: '{partner.name}' for '{vendor_name}'")
                return {'partner': partner}
        
        # Create new vendor
        partner_vals = {
            'name': vendor_name,
            'is_company': True,
            'supplier_rank': 1,
            'customer_rank': 0,
            'category_id': [(6, 0, [])]  # No categories by default
        }
        
        partner = env['res.partner'].create(partner_vals)
        _logger.info(f"Created new vendor: {vendor_name}")
        
        return {'partner': partner}
        
    except Exception as e:
        return {'error': f'Vendor creation failed: {str(e)}'}

def _check_duplicate_bill(partner, bill_data):
    """Check for duplicate bills to prevent double-entry"""
    try:
        # Search criteria for duplicates
        domain = [
            ('partner_id', '=', partner.id),
            ('move_type', '=', 'in_invoice'),
            ('state', 'in', ['draft', 'posted'])
        ]
        
        # Check by reference if provided
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

def _get_odoo_objects():
    """Get required Odoo objects (journal, accounts, etc.)"""
    try:
        # Get purchase journal
        journal = env['account.journal'].search([
            ('type', '=', 'purchase')
        ], limit=1)
        
        if not journal:
            return {'error': 'No purchase journal found. Please create one in Accounting > Configuration > Journals'}
        
        # Get default expense account
        expense_account = env['account.account'].search([
            ('account_type', '=', 'expense')
        ], limit=1)
        
        if not expense_account:
            # Fallback to account starting with 6 (common expense account prefix)
            expense_account = env['account.account'].search([
                ('code', '=like', '6%')
            ], limit=1)
        
        if not expense_account:
            return {'error': 'No expense account found. Please create one in Accounting > Configuration > Chart of Accounts'}
        
        return {
            'journal': journal,
            'expense_account': expense_account
        }
        
    except Exception as e:
        return {'error': f'Odoo objects retrieval failed: {str(e)}'}

def _create_vendor_bill(bill_data, partner, odoo_objects):
    """Create the actual vendor bill in Odoo"""
    try:
        # Calculate line amount (subtract tax if provided)
        line_amount = bill_data['amount']
        if bill_data['tax_amount'] > 0:
            line_amount = bill_data['amount'] - bill_data['tax_amount']
        
        # Prepare bill values
        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': partner.id,
            'invoice_date': bill_data['invoice_date'],
            'ref': bill_data['reference'] or bill_data['description'],
            'journal_id': odoo_objects['journal'].id,
            'currency_id': env.ref('base.USD').id,  # Default to USD, can be enhanced
            'invoice_line_ids': [(0, 0, {
                'name': bill_data['description'],
                'quantity': 1,
                'price_unit': line_amount,
                'account_id': odoo_objects['expense_account'].id,
            })]
        }
        
        # Add tax if specified
        if bill_data['tax_amount'] > 0:
            # Find default tax (you may need to customize this)
            default_tax = env['account.tax'].search([
                ('type_tax_use', '=', 'purchase'),
                ('amount_type', '=', 'percent')
            ], limit=1)
            
            if default_tax:
                bill_vals['invoice_line_ids'][0][2]['tax_ids'] = [(6, 0, [default_tax.id])]
        
        # Create the bill
        bill = env['account.move'].create(bill_vals)
        
        # Compute taxes and totals
        bill._compute_amount()
        
        return {'bill': bill}
        
    except Exception as e:
        return {'error': f'Bill creation failed: {str(e)}'}

def _attach_file_to_bill(bill, bill_data):
    """Download and attach file to the bill if URL is provided"""
    if not bill_data['file_url']:
        return {'success': False, 'message': 'No file URL provided'}
    
    try:
        # Convert Google Drive sharing URL to direct download if needed
        file_url = bill_data['file_url']
        if 'drive.google.com' in file_url and '/file/d/' in file_url:
            file_id = file_url.split('/file/d/')[1].split('/')[0]
            file_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        
        # Download file with timeout
        response = requests.get(file_url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        if response.status_code == 200 and len(response.content) > 0:
            # Encode file content
            file_content = base64.b64encode(response.content)
            
            # Determine MIME type
            content_type = response.headers.get('content-type', 'application/pdf')
            if not content_type or content_type == 'text/html':
                # Guess from file extension
                if bill_data['file_name'].lower().endswith('.pdf'):
                    content_type = 'application/pdf'
                elif bill_data['file_name'].lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif bill_data['file_name'].lower().endswith('.png'):
                    content_type = 'image/png'
                else:
                    content_type = 'application/octet-stream'
            
            # Create attachment
            attachment = env['ir.attachment'].create({
                'name': bill_data['file_name'],
                'datas': file_content,
                'res_model': 'account.move',
                'res_id': bill.id,
                'mimetype': content_type,
                'description': f'Automated attachment from {bill_data["file_name"]}'
            })
            
            _logger.info(f"File attached successfully: {bill_data['file_name']} to bill {bill.name}")
            return {'success': True, 'attachment_id': attachment.id}
        else:
            return {'error': f'Failed to download file: HTTP {response.status_code}'}
            
    except requests.exceptions.RequestException as e:
        return {'error': f'File download failed: {str(e)}'}
    except Exception as e:
        return {'error': f'File attachment failed: {str(e)}'}

def _create_error_response(message, extra_data=None):
    """Create standardized error response"""
    error_response = {
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if extra_data:
        error_response.update(extra_data)
    
    _logger.error(f"Webhook error: {message}")
    return _create_json_response(error_response, status_code=400)

def _create_json_response(data, status_code=200):
    """Create JSON response with proper headers"""
    try:
        import werkzeug.wrappers
        return werkzeug.wrappers.Response(
            json.dumps(data, indent=2),
            content_type='application/json',
            status=status_code
        )
    except ImportError:
        # Fallback for different Odoo versions
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'context': {'default_name': json.dumps(data)}
        }

# =============================================================================
# WEBHOOK ENDPOINT SETUP CODE - For Odoo Controller Method
# =============================================================================

CONTROLLER_CODE = '''
from odoo import http, api, SUPERUSER_ID
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class BillWebhookController(http.Controller):
    
    @http.route('/web/hook/<string:hook_id>', type='json', auth='none', 
                methods=['POST'], csrf=False, cors="*")
    def handle_bill_webhook(self, hook_id=None, **kwargs):
        """Handle incoming webhook for bill automation"""
        
        # Verify hook ID (basic security)
        expected_hook_id = "b43b901e-1346-4c99-afab-1ea8b6946ba2"
        if hook_id != expected_hook_id:
            return {'error': 'Invalid webhook ID'}
        
        try:
            with api.Environment.manage():
                with request.registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    
                    # Get request data
                    request_data = json.loads(request.httprequest.data.decode('utf-8'))
                    
                    # Execute bill creation (copy the create_bill_from_webhook function here)
                    # ... (function implementation)
                    
                    return {'success': True, 'message': 'Bill processed successfully'}
                    
        except Exception as e:
            _logger.error(f"Webhook error: {str(e)}", exc_info=True)
            return {'error': str(e)}
'''

# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_webhook_locally():
    """Test function to validate webhook logic without external calls"""
    print("Testing webhook logic locally...")
    
    # Sample test data
    test_data = {
        "vendor_name": "Test Vendor Corp",
        "amount": "1,234.56",
        "invoice_date": "2024-10-28",
        "description": "Test invoice for validation",
        "reference": "TEST-INV-001",
        "currency": "USD"
    }
    
    # Test data extraction
    bill_data = _extract_bill_data(test_data)
    print(f"Extracted data: {json.dumps(bill_data, indent=2)}")
    
    # Test amount parsing
    test_amounts = ["1,234.56", "$1234.56", "1.234,56", "1234"]
    for amount in test_amounts:
        parsed = _parse_amount(amount)
        print(f"Amount '{amount}' -> {parsed}")
    
    # Test date parsing
    test_dates = ["2024-10-28", "28/10/2024", "10-28-2024", "Oct 28, 2024"]
    for date_str in test_dates:
        parsed = _parse_date(date_str)
        print(f"Date '{date_str}' -> {parsed}")
    
    print("Local testing completed!")

def validate_odoo_setup():
    """Validate Odoo environment for bill automation"""
    checks = []
    
    try:
        # Check for purchase journal
        journal = env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        checks.append(("Purchase Journal", bool(journal), journal.name if journal else "Not found"))
        
        # Check for expense account
        expense_account = env['account.account'].search([('account_type', '=', 'expense')], limit=1)
        checks.append(("Expense Account", bool(expense_account), expense_account.code if expense_account else "Not found"))
        
        # Check for default currency
        currency = env.ref('base.USD', False)
        checks.append(("USD Currency", bool(currency), currency.name if currency else "Not found"))
        
        # Check permissions
        can_create_bills = env['account.move'].check_access_rights('create', raise_exception=False)
        checks.append(("Create Bills Permission", can_create_bills, "OK" if can_create_bills else "Missing"))
        
        can_create_vendors = env['res.partner'].check_access_rights('create', raise_exception=False)
        checks.append(("Create Vendors Permission", can_create_vendors, "OK" if can_create_vendors else "Missing"))
        
        print("\\nOdoo Environment Validation:")
        print("-" * 50)
        for check_name, status, details in checks:
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {check_name}: {details}")
        
        all_passed = all(status for _, status, _ in checks)
        print(f"\\nOverall Status: {'✅ Ready' if all_passed else '❌ Issues Found'}")
        
        return all_passed
        
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        return False

# =============================================================================
# INSTALLATION HELPER
# =============================================================================

def generate_installation_script():
    """Generate installation commands for quick setup"""
    
    script = """
# Odoo Bill Automation - Quick Installation Commands
# =================================================

# 1. Create Server Action for Webhook
# Go to: Settings -> Technical -> Server Actions -> Create

Name: Bill Automation Webhook
Model: ir.http  
Action Type: Python Code

# Copy the create_bill_from_webhook() function to the Python Code field

# 2. Create Website Menu (for webhook routing)
# Go to: Settings -> Technical -> User Interface -> Website Menus -> Create

URL: /web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2
Action: [Select your "Bill Automation Webhook" server action]

# 3. Test the setup
# Run this in Odoo shell or create a simple script:

webhook_url = "https://your-domain.odoo.com/web/hook/b43b901e-1346-4c99-afab-1ea8b6946ba2"

test_data = {
    "vendor_name": "Test Corp",
    "amount": 100.00,
    "invoice_date": "2024-10-28",
    "description": "Test bill",
    "reference": "TEST-001"
}

# Use requests.post(webhook_url, json=test_data) to test
    """
    
    print(script)
    return script

# =============================================================================
# MAIN EXECUTION - Copy this function to Odoo Server Action
# =============================================================================

# Execute the main function
result = create_bill_from_webhook()

# This will be returned as the webhook response
print(f"Webhook result: {result}")