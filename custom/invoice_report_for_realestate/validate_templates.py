#!/usr/bin/env python3
"""
Template Validation Script
Checks if QWeb templates have valid XML structure
"""
import os
import xml.etree.ElementTree as ET

def validate_xml_file(filepath):
    """Validate XML file structure"""
    try:
        ET.parse(filepath)
        print(f"✅ Valid XML: {os.path.basename(filepath)}")
        return True
    except ET.ParseError as e:
        print(f"❌ XML Parse Error in {os.path.basename(filepath)}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {os.path.basename(filepath)}: {e}")
        return False

def main():
    """Main validation function"""
    print("Template XML Validation")
    print("=" * 40)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # List of template files to validate
    template_files = [
        'report/invoice_report.xml',
        'report/bulk_report.xml',
        'report/bill_report.xml',
        'report/payment_voucher_report.xml',
        'report/report_action.xml',
        'report/bill_report_action.xml',
        'report/payment_voucher_report_action.xml'
    ]
    
    all_valid = True
    
    for template_file in template_files:
        filepath = os.path.join(base_path, template_file)
        if os.path.exists(filepath):
            if not validate_xml_file(filepath):
                all_valid = False
        else:
            print(f"❌ File not found: {template_file}")
            all_valid = False
    
    print("\n" + "=" * 40)
    if all_valid:
        print("✅ All template files are valid XML!")
        print("\nThe empty PDF error is likely caused by:")
        print("1. Missing fields in the model")
        print("2. Permission issues")
        print("3. QWeb template runtime errors")
        print("4. Binary field encoding issues")
        print("\nTry testing with a simple invoice first.")
    else:
        print("❌ Some template files have XML validation errors!")
        print("Fix the XML structure issues first.")

if __name__ == "__main__":
    main()
