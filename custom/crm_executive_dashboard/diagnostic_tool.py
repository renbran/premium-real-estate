#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRM Executive Dashboard - Diagnostic Script
This script helps diagnose and test the CRM Executive Dashboard module
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

class OdooDashboardDiagnostic:
    def __init__(self, odoo_url, username, password, database):
        self.odoo_url = odoo_url.rstrip('/')
        self.username = username
        self.password = password
        self.database = database
        self.session = requests.Session()
        self.session_id = None
        
    def authenticate(self):
        """Authenticate with Odoo"""
        try:
            # Get session info
            auth_data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'common',
                    'method': 'authenticate',
                    'args': [self.database, self.username, self.password, {}]
                },
                'id': 1
            }
            
            response = self.session.post(
                f"{self.odoo_url}/jsonrpc",
                json=auth_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and result['result']:
                    print("‚úÖ Authentication successful")
                    return True
                else:
                    print("‚ùå Authentication failed")
                    return False
            else:
                print(f"‚ùå HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"‚ùå Authentication error: {str(e)}")
            return False
    
    def test_module_installed(self):
        """Check if CRM Executive Dashboard module is installed"""
        try:
            data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'object',
                    'method': 'execute',
                    'args': [
                        self.database, 
                        self.username, 
                        self.password,
                        'ir.module.module',
                        'search_read',
                        [('name', '=', 'crm_executive_dashboard')],
                        ['name', 'state', 'installed_version']
                    ]
                },
                'id': 2
            }
            
            response = self.session.post(
                f"{self.odoo_url}/jsonrpc",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and result['result']:
                    module = result['result'][0]
                    print(f"‚úÖ Module found: {module['name']}")
                    print(f"   State: {module['state']}")
                    print(f"   Version: {module.get('installed_version', 'N/A')}")
                    return module['state'] == 'installed'
                else:
                    print("‚ùå CRM Executive Dashboard module not found")
                    return False
            else:
                print(f"‚ùå HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"‚ùå Module check error: {str(e)}")
            return False
    
    def test_dashboard_model(self):
        """Test if the dashboard model exists and is accessible"""
        try:
            data = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'object',
                    'method': 'execute',
                    'args': [
                        self.database, 
                        self.username, 
                        self.password,
                        'crm.executive.dashboard',
                        'search_count',
                        []
                    ]
                },
                'id': 3
            }
            
            response = self.session.post(
                f"{self.odoo_url}/jsonrpc",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    count = result['result']
                    print(f"‚úÖ Dashboard model accessible: {count} records found")
                    return True
                else:
                    print("‚ùå Dashboard model error:", result.get('error', 'Unknown error'))
                    return False
            else:
                print(f"‚ùå HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"‚ùå Model test error: {str(e)}")
            return False
    
    def test_dashboard_endpoints(self):
        """Test dashboard API endpoints"""
        endpoints = [
            '/crm/dashboard/data',
            '/crm/dashboard/overdue',
            '/crm/dashboard/performers'
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                # Test with POST request (JSON-RPC style)
                test_data = {
                    'date_from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'date_to': datetime.now().strftime('%Y-%m-%d'),
                    'team_ids': []
                }
                
                response = self.session.post(
                    f"{self.odoo_url}{endpoint}",
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get('success', False):
                            print(f"‚úÖ Endpoint {endpoint}: Working")
                            results[endpoint] = 'success'
                        else:
                            print(f"‚ö†Ô∏è  Endpoint {endpoint}: Returned error - {result.get('error', 'Unknown')}")
                            results[endpoint] = 'error'
                    except json.JSONDecodeError:
                        print(f"‚ùå Endpoint {endpoint}: Invalid JSON response")
                        results[endpoint] = 'invalid_json'
                else:
                    print(f"‚ùå Endpoint {endpoint}: HTTP {response.status_code}")
                    results[endpoint] = f'http_{response.status_code}'
                    
            except Exception as e:
                print(f"‚ùå Endpoint {endpoint}: Exception - {str(e)}")
                results[endpoint] = 'exception'
        
        return results
    
    def test_assets_loading(self):
        """Test if static assets are loading properly"""
        assets = [
            '/crm_executive_dashboard/static/src/js/crm_executive_dashboard.js',
            '/crm_executive_dashboard/static/src/scss/dashboard.scss',
            '/crm_executive_dashboard/static/src/xml/dashboard_templates.xml'
        ]
        
        results = {}
        
        for asset in assets:
            try:
                response = self.session.get(f"{self.odoo_url}{asset}")
                
                if response.status_code == 200:
                    print(f"‚úÖ Asset {asset}: Loading OK")
                    results[asset] = 'success'
                elif response.status_code == 404:
                    print(f"‚ùå Asset {asset}: Not found (404)")
                    results[asset] = 'not_found'
                else:
                    print(f"‚ö†Ô∏è  Asset {asset}: HTTP {response.status_code}")
                    results[asset] = f'http_{response.status_code}'
                    
            except Exception as e:
                print(f"‚ùå Asset {asset}: Exception - {str(e)}")
                results[asset] = 'exception'
        
        return results
    
    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print("üîç Starting CRM Executive Dashboard Diagnostic")
        print("=" * 50)
        
        # Test 1: Authentication
        print("\n1. Testing Authentication...")
        if not self.authenticate():
            print("‚ùå Cannot proceed without authentication")
            return
        
        # Test 2: Module Installation
        print("\n2. Testing Module Installation...")
        if not self.test_module_installed():
            print("‚ùå Module not installed properly")
            return
        
        # Test 3: Model Access
        print("\n3. Testing Dashboard Model...")
        if not self.test_dashboard_model():
            print("‚ö†Ô∏è  Dashboard model has issues")
        
        # Test 4: API Endpoints
        print("\n4. Testing API Endpoints...")
        endpoint_results = self.test_dashboard_endpoints()
        
        # Test 5: Static Assets
        print("\n5. Testing Static Assets...")
        asset_results = self.test_assets_loading()
        
        # Summary
        print("\n" + "=" * 50)
        print("üìä DIAGNOSTIC SUMMARY")
        print("=" * 50)
        
        print("\nAPI Endpoints:")
        for endpoint, status in endpoint_results.items():
            status_icon = "‚úÖ" if status == 'success' else "‚ùå"
            print(f"  {status_icon} {endpoint}: {status}")
        
        print("\nStatic Assets:")
        for asset, status in asset_results.items():
            status_icon = "‚úÖ" if status == 'success' else "‚ùå"
            print(f"  {status_icon} {asset}: {status}")
        
        # Recommendations
        print("\nüîß RECOMMENDATIONS:")
        failed_endpoints = [k for k, v in endpoint_results.items() if v != 'success']
        failed_assets = [k for k, v in asset_results.items() if v != 'success']
        
        if failed_endpoints:
            print("‚Ä¢ Check server logs for endpoint errors")
            print("‚Ä¢ Verify user permissions (sales_team.group_sale_salesman)")
            print("‚Ä¢ Ensure module is properly installed and updated")
        
        if failed_assets:
            print("‚Ä¢ Check if static files exist in module directory")
            print("‚Ä¢ Verify assets are properly declared in __manifest__.py")
            print("‚Ä¢ Try updating the module or restarting Odoo")
        
        if not failed_endpoints and not failed_assets:
            print("‚úÖ All tests passed! Dashboard should be working properly.")

def main():
    """Main diagnostic function"""
    print("CRM Executive Dashboard - Diagnostic Tool")
    print("=========================================")
    
    # Configuration - Update these values for your setup
    ODOO_URL = input("Enter Odoo URL (e.g., http://your-server:8069): ").strip()
    DATABASE = input("Enter database name: ").strip()
    USERNAME = input("Enter username: ").strip()
    PASSWORD = input("Enter password: ").strip()
    
    if not all([ODOO_URL, DATABASE, USERNAME, PASSWORD]):
        print("‚ùå Please provide all required information")
        return
    
    # Run diagnostic
    diagnostic = OdooDashboardDiagnostic(ODOO_URL, USERNAME, PASSWORD, DATABASE)
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()
