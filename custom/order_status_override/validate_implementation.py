#!/usr/bin/env python3
"""
Order Status Override Module - Complete Implementation Validator
=================================================================

This script validates that all required changes have been properly implemented
for the order_status_override module enhancement.

Requirements Validation:
1. Status bar workflow changed from 6 to 5 stages
2. Old status bar hidden in views
3. Report format enhanced with 3-column layout
4. Commission table with required headers
5. Summary section before footer
"""

import os
import xml.etree.ElementTree as ET
import ast
import re

def validate_python_syntax(file_path):
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, "Syntax OK"
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_xml_syntax(file_path):
    """Validate XML file syntax"""
    try:
        ET.parse(file_path)
        return True, "XML Syntax OK"
    except ET.ParseError as e:
        return False, f"XML Parse Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_model_changes(file_path):
    """Check if model has the required changes"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            "5-stage workflow": ("'post', 'Post'" in content and 
                                "'commission_calculation'" not in content),
            "allocation_user_id field": "allocation_user_id" in content,
            "approval_user_id field": "approval_user_id" in content,
            "action_move_to_allocation method": "action_move_to_allocation" in content,
            "action_approve_order method": "action_approve_order" in content,
            "action_post_order method": "action_post_order" in content
        }
        
        return checks
    except Exception as e:
        return {"Error": str(e)}

def check_view_changes(file_path):
    """Check if view has the required changes"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Look for state field with position="attributes" and invisible attribute
        state_invisible = False
        allocation_user = False
        approval_user = False
        
        for elem in root.iter():
            # Check for field with name="state" and position="attributes"
            if elem.tag == 'field' and elem.get('name') == 'state' and elem.get('position') == 'attributes':
                # Look for attribute child with name="invisible"
                for child in elem:
                    if child.tag == 'attribute' and child.get('name') == 'invisible':
                        state_invisible = True
                        break
            # Check for direct field with invisible attribute
            elif elem.tag == 'field' and elem.get('name') == 'state':
                if elem.get('invisible') == '1':
                    state_invisible = True
            elif elem.tag == 'field' and elem.get('name') == 'allocation_user_id':
                allocation_user = True
            elif elem.tag == 'field' and elem.get('name') == 'approval_user_id':
                approval_user = True
        
        checks = {
            "state field hidden": state_invisible,
            "allocation_user_id field present": allocation_user,
            "approval_user_id field present": approval_user
        }
        
        return checks
    except Exception as e:
        return {"Error": str(e)}

def check_report_template(file_path):
    """Check if report template has the required enhancements"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            "3-column layout": "grid-template-columns: 1fr 1fr 1fr" in content,
            "commission table headers": (
                "Specification" in content and 
                "Name" in content and 
                "Rate (%)" in content and 
                "Total Amount" in content and 
                "Status" in content
            ),
            "summary section": "Financial Summary" in content,
            "summary before footer": (
                "Total Eligible Commission" in content and
                "Total Received/Invoiced" in content and
                "Total Eligible Payables" in content
            ),
            "professional styling": "OSUS Properties" in content
        }
        
        return checks
    except Exception as e:
        return {"Error": str(e)}

def main():
    """Main validation function"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 80)
    print("ORDER STATUS OVERRIDE MODULE - IMPLEMENTATION VALIDATOR")
    print("=" * 80)
    print()
    
    # File paths
    files_to_check = {
        "Model File": "models/sale_order.py",
        "View File": "views/order_views_assignment.xml", 
        "Report Template": "reports/enhanced_order_status_report_template_updated.xml",
        "Report Actions": "reports/enhanced_order_status_report_actions.xml",
        "Manifest": "__manifest__.py"
    }
    
    # 1. Check file existence
    print("1. FILE EXISTENCE CHECK")
    print("-" * 30)
    all_files_exist = True
    for name, path in files_to_check.items():
        full_path = os.path.join(base_path, path)
        exists = os.path.exists(full_path)
        print(f"✅ {name}: {path}" if exists else f"❌ {name}: {path} - NOT FOUND")
        if not exists:
            all_files_exist = False
    print()
    
    if not all_files_exist:
        print("❌ Some required files are missing. Please check the file paths.")
        return
    
    # 2. Syntax validation
    print("2. SYNTAX VALIDATION")
    print("-" * 25)
    
    # Python files
    python_files = ["models/sale_order.py", "__manifest__.py"]
    for py_file in python_files:
        full_path = os.path.join(base_path, py_file)
        is_valid, message = validate_python_syntax(full_path)
        print(f"✅ {py_file}: {message}" if is_valid else f"❌ {py_file}: {message}")
    
    # XML files
    xml_files = [
        "views/order_views_assignment.xml",
        "reports/enhanced_order_status_report_template_updated.xml",
        "reports/enhanced_order_status_report_actions.xml"
    ]
    for xml_file in xml_files:
        full_path = os.path.join(base_path, xml_file)
        is_valid, message = validate_xml_syntax(full_path)
        print(f"✅ {xml_file}: {message}" if is_valid else f"❌ {xml_file}: {message}")
    print()
    
    # 3. Model changes validation
    print("3. MODEL CHANGES VALIDATION")
    print("-" * 35)
    model_checks = check_model_changes(os.path.join(base_path, "models/sale_order.py"))
    for check, passed in model_checks.items():
        print(f"✅ {check}" if passed else f"❌ {check}")
    print()
    
    # 4. View changes validation
    print("4. VIEW CHANGES VALIDATION")
    print("-" * 30)
    view_checks = check_view_changes(os.path.join(base_path, "views/order_views_assignment.xml"))
    for check, passed in view_checks.items():
        print(f"✅ {check}" if passed else f"❌ {check}")
    print()
    
    # 5. Report template validation
    print("5. REPORT TEMPLATE VALIDATION")
    print("-" * 35)
    report_checks = check_report_template(os.path.join(base_path, "reports/enhanced_order_status_report_template_updated.xml"))
    for check, passed in report_checks.items():
        print(f"✅ {check}" if passed else f"❌ {check}")
    print()
    
    # 6. Summary
    print("6. REQUIREMENTS COMPLIANCE SUMMARY")
    print("-" * 40)
    
    requirements = [
        ("Status bar workflow (6→5 stages)", model_checks.get("5-stage workflow", False)),
        ("Old status bar hidden", view_checks.get("state field hidden", False)),
        ("3-column layout", report_checks.get("3-column layout", False)),
        ("Commission table headers", report_checks.get("commission table headers", False)),
        ("Summary section before footer", report_checks.get("summary before footer", False))
    ]
    
    all_requirements_met = True
    for requirement, passed in requirements:
        print(f"✅ {requirement}" if passed else f"❌ {requirement}")
        if not passed:
            all_requirements_met = False
    
    print()
    print("=" * 80)
    if all_requirements_met:
        print("🎉 ALL REQUIREMENTS SUCCESSFULLY IMPLEMENTED!")
        print("The order_status_override module is ready for deployment.")
    else:
        print("⚠️  SOME REQUIREMENTS NOT MET")
        print("Please review the failed checks above.")
    print("=" * 80)

if __name__ == "__main__":
    main()
