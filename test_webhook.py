#!/usr/bin/env python3
"""
Webhook Test Script for Bill Automation
=======================================

This script tests the bill automation webhook endpoint to ensure it's working correctly.
It can run health checks, create test bills, and validate the entire automation pipeline.

Features:
- Health check endpoint testing
- Test bill creation with sample data
- Custom test data support
- Verbose logging and error reporting
- Response validation
- Multiple test scenarios
- Performance testing

Usage Examples:
  python test_webhook.py --url https://your-odoo.com --health-only
  python test_webhook.py --url https://your-odoo.com --vendor "Test Corp" --amount 150.75
  python test_webhook.py --url https://your-odoo.com --test-all
  python test_webhook.py --url https://your-odoo.com --performance-test --count 10

Author: Bill Automation Project Team
Version: 1.0.0
"""

import requests
import json
import argparse
import sys
import time
import random
from datetime import datetime, date, timedelta
from urllib.parse import urlparse
import os


class WebhookTester:
    """Main class for testing webhook functionality"""
    
    def __init__(self, base_url, api_key=None, verbose=False):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.verbose = verbose
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Bill-Automation-Tester/1.0.0'
        })
        
        # Validate URL
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {base_url}")
    
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌"
            }.get(level, "📝")
            print(f"[{timestamp}] {prefix} {message}")
    
    def test_health_check(self):
        """Test the health check endpoint"""
        self.log("Testing health check endpoint...")
        
        try:
            url = f"{self.base_url}/api/v1/bills/health"
            response = self.session.get(url, timeout=10)
            
            self.log(f"Health check response: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log(f"Health status: {data.get('status', 'unknown')}")
                    
                    if 'checks' in data:
                        for check in data['checks']:
                            status_icon = "✅" if check['status'] else "❌"
                            self.log(f"  {status_icon} {check['name']}: {check['message']}")
                    
                    return data.get('status') == 'healthy'
                except json.JSONDecodeError:
                    self.log("Invalid JSON response from health check", "ERROR")
                    return False
            else:
                self.log(f"Health check failed with status {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Health check request failed: {str(e)}", "ERROR")
            return False
    
    def test_service_status(self):
        """Test the service status endpoint"""
        self.log("Testing service status endpoint...")
        
        try:
            url = f"{self.base_url}/api/v1/bills/status"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Service: {data.get('service', 'unknown')}")
                self.log(f"Version: {data.get('version', 'unknown')}")
                self.log(f"Status: {data.get('status', 'unknown')}")
                
                if 'statistics' in data:
                    stats = data['statistics']
                    self.log(f"Total requests: {stats.get('total_requests', 0)}")
                    self.log(f"Success rate: {stats.get('success_rate', 0)}%")
                
                return True
            else:
                self.log(f"Status check failed with status {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Status check request failed: {str(e)}", "ERROR")
            return False
        except json.JSONDecodeError:
            self.log("Invalid JSON response from status check", "ERROR")
            return False
    
    def create_test_bill(self, vendor_name=None, amount=None, **kwargs):
        """Create a test bill with provided or default data"""
        # Generate test data
        test_data = self.generate_test_data(vendor_name, amount, **kwargs)
        
        self.log(f"Creating test bill for vendor: {test_data['vendor_name']}")
        self.log(f"Amount: ${test_data['amount']}")
        
        try:
            url = f"{self.base_url}/api/v1/bills/create"
            
            # Add API key if provided
            if self.api_key:
                test_data['api_key'] = self.api_key
            
            response = self.session.post(url, json=test_data, timeout=30)
            
            self.log(f"Response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if data.get('success'):
                        self.log("Bill created successfully!", "SUCCESS")
                        if 'data' in data:
                            bill_data = data['data']
                            self.log(f"  Bill ID: {bill_data.get('bill_id')}")
                            self.log(f"  Bill Number: {bill_data.get('bill_number')}")
                            self.log(f"  Vendor: {bill_data.get('vendor')}")
                            self.log(f"  Amount: ${bill_data.get('amount')}")
                            self.log(f"  File Attached: {bill_data.get('file_attached', False)}")
                        return True
                    else:
                        error = data.get('error', 'Unknown error')
                        self.log(f"Bill creation failed: {error}", "ERROR")
                        return False
                except json.JSONDecodeError:
                    self.log("Invalid JSON response", "ERROR")
                    return False
            else:
                self.log(f"Request failed with status {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        self.log(f"Error details: {error_data['error']}", "ERROR")
                except:
                    self.log(f"Response body: {response.text}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            return False
    
    def generate_test_data(self, vendor_name=None, amount=None, **kwargs):
        """Generate test bill data"""
        # Default test vendors
        test_vendors = [
            "Test Corporation Ltd",
            "Sample Services Inc",
            "Demo Supplies Co",
            "Example Consulting Group",
            "Mock Industries LLC"
        ]
        
        # Default test descriptions
        test_descriptions = [
            "Office supplies and materials",
            "Professional consulting services",
            "Software licensing fees",
            "Equipment maintenance service",
            "Marketing and advertising costs"
        ]
        
        # Generate data
        vendor = vendor_name or random.choice(test_vendors)
        bill_amount = amount or round(random.uniform(50.0, 2000.0), 2)
        description = kwargs.get('description') or random.choice(test_descriptions)
        
        # Generate invoice date (last 30 days)
        days_ago = random.randint(1, 30)
        invoice_date = (date.today() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Generate reference number
        reference = kwargs.get('reference') or f"TEST-{int(time.time())}-{random.randint(100, 999)}"
        
        return {
            'vendor_name': vendor,
            'amount': bill_amount,
            'invoice_date': kwargs.get('invoice_date') or invoice_date,
            'description': description,
            'reference': reference,
            'currency': kwargs.get('currency', 'USD'),
            'file_url': kwargs.get('file_url', ''),
            'file_name': kwargs.get('file_name', 'test_bill.pdf')
        }
    
    def test_duplicate_prevention(self):
        """Test duplicate bill prevention"""
        self.log("Testing duplicate bill prevention...")
        
        # Create first bill
        test_data = self.generate_test_data("Duplicate Test Corp", 123.45, 
                                          reference="DUPLICATE-TEST-001")
        
        self.log("Creating first bill...")
        result1 = self.create_test_bill(**test_data)
        
        if result1:
            self.log("Attempting to create duplicate bill...")
            # Try to create the same bill again
            result2 = self.create_test_bill(**test_data)
            
            if not result2:
                self.log("Duplicate prevention working correctly!", "SUCCESS")
                return True
            else:
                self.log("Duplicate bill was created - prevention not working!", "ERROR")
                return False
        else:
            self.log("Failed to create first bill for duplicate test", "ERROR")
            return False
    
    def test_vendor_autocreation(self):
        """Test vendor auto-creation with unique vendor name"""
        unique_vendor = f"AutoCreate-Test-{int(time.time())}"
        self.log(f"Testing vendor auto-creation with: {unique_vendor}")
        
        return self.create_test_bill(vendor_name=unique_vendor, amount=99.99)
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        self.log("Testing error handling with invalid data...")
        
        # Test with missing vendor name
        invalid_data = {
            'vendor_name': '',
            'amount': 100.0,
            'invoice_date': '2024-10-28',
            'description': 'Error test'
        }
        
        try:
            url = f"{self.base_url}/api/v1/bills/create"
            response = self.session.post(url, json=invalid_data, timeout=10)
            
            if response.status_code >= 400:
                self.log("Error handling working correctly (rejected invalid data)", "SUCCESS")
                return True
            else:
                self.log("Invalid data was accepted - error handling may need improvement", "WARNING")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Error handling test failed: {str(e)}", "ERROR")
            return False
    
    def performance_test(self, count=5):
        """Run performance test with multiple requests"""
        self.log(f"Running performance test with {count} requests...")
        
        results = []
        for i in range(count):
            start_time = time.time()
            
            vendor_name = f"Performance-Test-{i+1}-{int(time.time())}"
            success = self.create_test_bill(vendor_name=vendor_name, 
                                          amount=round(random.uniform(100, 500), 2))
            
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                'success': success,
                'duration': duration
            })
            
            self.log(f"Request {i+1}/{count}: {'✅' if success else '❌'} ({duration:.2f}s)")
            
            # Small delay between requests
            time.sleep(0.5)
        
        # Calculate statistics
        successful = sum(1 for r in results if r['success'])
        total_time = sum(r['duration'] for r in results)
        avg_time = total_time / len(results)
        
        self.log(f"Performance test complete:", "SUCCESS")
        self.log(f"  Success rate: {successful}/{count} ({successful/count*100:.1f}%)")
        self.log(f"  Average response time: {avg_time:.2f}s")
        self.log(f"  Total time: {total_time:.2f}s")
        
        return successful == count
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        self.log("Starting comprehensive webhook test suite...", "SUCCESS")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Service Status", self.test_service_status),
            ("Basic Bill Creation", lambda: self.create_test_bill()),
            ("Vendor Auto-creation", self.test_vendor_autocreation),
            ("Duplicate Prevention", self.test_duplicate_prevention),
            ("Error Handling", self.test_error_handling),
            ("Performance Test", lambda: self.performance_test(3))
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- Running: {test_name} ---")
            try:
                if test_func():
                    self.log(f"{test_name}: PASSED", "SUCCESS")
                    passed += 1
                else:
                    self.log(f"{test_name}: FAILED", "ERROR")
            except Exception as e:
                self.log(f"{test_name}: ERROR - {str(e)}", "ERROR")
        
        self.log(f"\n=== Test Results ===", "SUCCESS")
        self.log(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 All tests passed! Webhook is working correctly.", "SUCCESS")
        elif passed >= total * 0.8:
            self.log("⚠️ Most tests passed. Minor issues may need attention.", "WARNING")
        else:
            self.log("❌ Multiple test failures. Please review configuration.", "ERROR")
        
        return passed == total


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Test Bill Automation Webhook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://your-odoo.com --health-only
  %(prog)s --url https://your-odoo.com --vendor "Test Corp" --amount 150.75
  %(prog)s --url https://your-odoo.com --test-all
  %(prog)s --url https://your-odoo.com --performance-test --count 10
        """
    )
    
    parser.add_argument('--url', required=True,
                       help='Base URL of your Odoo instance (e.g., https://your-odoo.com)')
    
    parser.add_argument('--api-key',
                       help='API key for authentication (if required)')
    
    parser.add_argument('--health-only', action='store_true',
                       help='Only run health check')
    
    parser.add_argument('--test-all', action='store_true',
                       help='Run comprehensive test suite')
    
    parser.add_argument('--performance-test', action='store_true',
                       help='Run performance test')
    
    parser.add_argument('--count', type=int, default=5,
                       help='Number of requests for performance test (default: 5)')
    
    parser.add_argument('--vendor',
                       help='Vendor name for test bill')
    
    parser.add_argument('--amount', type=float,
                       help='Amount for test bill')
    
    parser.add_argument('--description',
                       help='Description for test bill')
    
    parser.add_argument('--reference',
                       help='Reference number for test bill')
    
    parser.add_argument('--invoice-date',
                       help='Invoice date (YYYY-MM-DD format)')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        tester = WebhookTester(args.url, args.api_key, args.verbose)
        
        if args.health_only:
            success = tester.test_health_check()
            tester.test_service_status()
        elif args.test_all:
            success = tester.run_comprehensive_test()
        elif args.performance_test:
            success = tester.performance_test(args.count)
        else:
            # Single bill creation test
            kwargs = {}
            if args.description:
                kwargs['description'] = args.description
            if args.reference:
                kwargs['reference'] = args.reference
            if args.invoice_date:
                kwargs['invoice_date'] = args.invoice_date
            
            success = tester.create_test_bill(args.vendor, args.amount, **kwargs)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()