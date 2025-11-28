#!/usr/bin/env python3
"""
OSUS Invoice Report - Bulk Print Verification Script
Checks if all components are properly configured for bulk printing
"""
import os
import sys
import xml.etree.ElementTree as ET

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING {description}: {filepath}")
        return False

def check_xml_content(filepath, xpath, description):
    """Check if XML file contains specific content"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        elements = root.findall(xpath)
        if elements:
            print(f"✅ {description}: Found {len(elements)} element(s)")
            return True
        else:
            print(f"❌ {description}: Not found in {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error parsing {filepath}: {e}")
        return False

def check_python_methods(filepath):
    """Check if Python file contains bulk print methods"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        methods = [
            'action_bulk_print_invoices',
            'action_bulk_print_bills', 
            'action_bulk_print_mixed'
        ]
        
        found_methods = []
        for method in methods:
            if f"def {method}(" in content:
                found_methods.append(method)
                print(f"✅ Method found: {method}")
            else:
                print(f"❌ Method missing: {method}")
        
        return len(found_methods) == len(methods)
    except Exception as e:
        print(f"❌ Error checking Python methods: {e}")
        return False

def main():
    """Main verification function"""
    print("OSUS Invoice Report - Bulk Print Verification")
    print("=" * 50)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    all_checks_passed = True
    
    # Check core files
    files_to_check = [
        ('__manifest__.py', 'Manifest file'),
        ('models/custom_invoice.py', 'Python model file'),
        ('views/account_move_views.xml', 'Account move views'),
        ('views/bulk_print_menus.xml', 'Bulk print menus'),
        ('report/report_action.xml', 'Report actions'),
        ('report/bulk_report.xml', 'Bulk report templates')
    ]
    
    print("\n1. Checking File Existence:")
    print("-" * 30)
    for filename, description in files_to_check:
        filepath = os.path.join(base_path, filename)
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check Python methods
    print("\n2. Checking Python Methods:")
    print("-" * 30)
    python_file = os.path.join(base_path, 'models/custom_invoice.py')
    if not check_python_methods(python_file):
        all_checks_passed = False
    
    # Check XML configurations
    print("\n3. Checking XML Configurations:")
    print("-" * 30)
    
    # Check report actions
    report_actions_file = os.path.join(base_path, 'report/report_action.xml')
    if os.path.exists(report_actions_file):
        xml_checks = [
            ('.//record[@id="action_report_osus_invoice_bulk"]', 'Bulk invoice report action'),
            ('.//record[@id="action_report_osus_bill_bulk"]', 'Bulk bill report action'),
            ('.//record[@id="action_report_osus_mixed_bulk"]', 'Bulk mixed report action')
        ]
        
        for xpath, description in xml_checks:
            if not check_xml_content(report_actions_file, xpath, description):
                all_checks_passed = False
    
    # Check server actions
    views_file = os.path.join(base_path, 'views/account_move_views.xml')
    if os.path.exists(views_file):
        server_actions = [
            ('.//record[@id="action_bulk_print_customer_invoices"]', 'Bulk print invoices server action'),
            ('.//record[@id="action_bulk_print_vendor_bills"]', 'Bulk print bills server action'),
            ('.//record[@id="action_bulk_print_mixed_documents"]', 'Bulk print mixed server action')
        ]
        
        for xpath, description in server_actions:
            if not check_xml_content(views_file, xpath, description):
                all_checks_passed = False
    
    # Check bulk report templates
    bulk_report_file = os.path.join(base_path, 'report/bulk_report.xml')
    if os.path.exists(bulk_report_file):
        template_checks = [
            ('.//template[@id="report_osus_invoice_bulk_document"]', 'Bulk invoice template'),
            ('.//template[@id="report_osus_bill_bulk_document"]', 'Bulk bill template'),
            ('.//template[@id="report_osus_mixed_bulk_document"]', 'Bulk mixed template')
        ]
        
        for xpath, description in template_checks:
            if not check_xml_content(bulk_report_file, xpath, description):
                all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\nBulk printing functionality is properly configured.")
        print("\nTo test:")
        print("1. Install/Update the osus_invoice_report module")
        print("2. Go to Accounting > OSUS Bulk Print")
        print("3. Select multiple invoices and use 'Actions' menu")
        print("4. Choose appropriate bulk print action")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\nPlease review the missing components above.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
