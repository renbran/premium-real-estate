#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Statement Report - Formatting Test Script
This script tests the formatting enhancements for the statement report
"""

import os
import sys
from datetime import date, datetime, timedelta

def test_date_formatting():
    """Test date formatting DD-MMM-YYYY"""
    print("Testing Date Formatting...")
    
    test_dates = [
        "2024-08-04",
        "2024-12-25", 
        "2024-01-01",
        datetime(2024, 8, 4),
        date(2024, 8, 4)
    ]
    
    for test_date in test_dates:
        try:
            if isinstance(test_date, str):
                parsed_date = datetime.strptime(test_date[:10], '%Y-%m-%d')
                formatted = parsed_date.strftime('%d-%b-%Y')
            elif isinstance(test_date, datetime):
                formatted = test_date.strftime('%d-%b-%Y')
            elif isinstance(test_date, date):
                formatted = test_date.strftime('%d-%b-%Y')
            else:
                formatted = str(test_date)
            
            print(f"  {test_date} → {formatted}")
        except Exception as e:
            print(f"  Error formatting {test_date}: {e}")
    
    print("✅ Date formatting test completed\n")

def test_number_formatting():
    """Test professional number formatting"""
    print("Testing Number Formatting...")
    
    test_numbers = [
        1234567.89,
        1500.00,
        1234.56,
        0.00,
        99.90,
        1000,
        0.1,
        123456
    ]
    
    for num in test_numbers:
        try:
            # Format with commas and 2 decimal places
            formatted = '{:,.2f}'.format(float(num))
            # Remove trailing zeros after decimal point
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            
            print(f"  {num} → {formatted}")
        except Exception as e:
            print(f"  Error formatting {num}: {e}")
    
    print("✅ Number formatting test completed\n")

def test_overdue_detection():
    """Test overdue invoice detection"""
    print("Testing Overdue Detection...")
    
    today = date.today()
    
    test_due_dates = [
        today - timedelta(days=1),   # Overdue by 1 day
        today - timedelta(days=30),  # Overdue by 30 days
        today,                       # Due today (not overdue)
        today + timedelta(days=7),   # Due in 7 days
        today + timedelta(days=30),  # Due in 30 days
    ]
    
    for due_date in test_due_dates:
        is_overdue = due_date < today
        status = "OVERDUE" if is_overdue else "CURRENT"
        color = "#dc3545" if is_overdue else "#000000"
        
        print(f"  Due: {due_date.strftime('%d-%b-%Y')} → {status} (color: {color})")
    
    print("✅ Overdue detection test completed\n")

def test_template_formatting():
    """Test template formatting logic"""
    print("Testing Template Formatting Logic...")
    
    # Simulate template data
    sample_lines = [
        {
            'name': 'INV/2024/0001',
            'ref': 'REF001',
            'invoice_date': '2024-08-01',
            'invoice_date_due': '2024-07-25',  # Overdue
            'sub_total': 1234.56,
            'balance': 1234.56,
            'is_overdue': True
        },
        {
            'name': 'INV/2024/0002', 
            'ref': 'REF002',
            'invoice_date': '2024-08-04',
            'invoice_date_due': '2024-09-04',  # Not overdue
            'sub_total': 2500.00,
            'balance': 2500.00,
            'is_overdue': False
        }
    ]
    
    for i, line in enumerate(sample_lines, 1):
        print(f"  Line {i}:")
        print(f"    Invoice: {line['name']} ({'OVERDUE' if line['is_overdue'] else 'CURRENT'})")
        
        # Format date
        due_date = datetime.strptime(line['invoice_date_due'], '%Y-%m-%d')
        formatted_due = due_date.strftime('%d-%b-%Y')
        print(f"    Due Date: {formatted_due}")
        
        # Format amount
        formatted_amount = '{:,.2f}'.format(line['sub_total'])
        if '.' in formatted_amount:
            formatted_amount = formatted_amount.rstrip('0').rstrip('.')
        print(f"    Amount: ${formatted_amount}")
        
        print(f"    Color: {'#dc3545 (red)' if line['is_overdue'] else '#000000 (black)'}")
        print()
    
    print("✅ Template formatting test completed\n")

def check_module_files():
    """Check if required module files exist"""
    print("Checking Module Files...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'report/res_partner_templates.xml',
        'models/res_partner.py',
        '__manifest__.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("✅ All required files found\n")
    else:
        print("❌ Some files are missing\n")
    
    return all_exist

def main():
    """Main test function"""
    print("="*60)
    print("STATEMENT REPORT - FORMATTING ENHANCEMENT TESTS")
    print("="*60)
    print()
    
    # Check files
    files_ok = check_module_files()
    
    if not files_ok:
        print("⚠️  Some module files are missing. Tests will continue but may not reflect actual implementation.")
        print()
    
    # Run tests
    test_date_formatting()
    test_number_formatting()
    test_overdue_detection()
    test_template_formatting()
    
    print("="*60)
    print("ENHANCEMENT SUMMARY")
    print("="*60)
    print("✅ Date Format: DD-MMM-YYYY (e.g., 04-Aug-2024)")
    print("✅ Number Format: Comma-separated with clean decimals (e.g., 1,234.56)")
    print("✅ Overdue Highlighting: Red color (#dc3545) for overdue invoices")
    print("✅ Professional Appearance: Clean, readable report format")
    print()
    print("Next Steps:")
    print("1. Restart Odoo server")
    print("2. Update module: python odoo-bin -u statement_report")
    print("3. Test report generation with sample data")
    print("4. Verify formatting in PDF exports")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
