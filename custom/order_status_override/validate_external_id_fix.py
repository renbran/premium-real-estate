#!/usr/bin/env python3
"""
Commission Report External ID Fix Validation
This script validates the fix for the External ID error in the commission report implementation.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_external_id_fix():
    """Validate that the External ID references are correct"""
    print("🔧 EXTERNAL ID FIX VALIDATION")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    errors = []
    fixes = []
    
    # 1. Check manifest file loading order
    print("\n📋 1. Checking __manifest__.py loading order...")
    manifest_path = base_path / "__manifest__.py"
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        # Find the data section
        data_section_start = manifest_content.find("'data': [")
        data_section_end = manifest_content.find("],", data_section_start)
        data_section = manifest_content[data_section_start:data_section_end]
        
        # Check order: reports should come before views
        report_index = data_section.find("'reports/sale_commission_report.xml'")
        view_index = data_section.find("'views/order_views_assignment.xml'")
        
        if report_index != -1 and view_index != -1:
            if report_index < view_index:
                print("   ✅ Reports loaded before views - FIXED")
                fixes.append("Loading order corrected in manifest")
            else:
                errors.append("❌ Views loaded before reports - order issue")
        else:
            errors.append("❌ Could not find report or view files in manifest")
    
    # 2. Check report definition ID
    print("\n📄 2. Checking report definition ID...")
    report_def_path = base_path / "reports" / "sale_commission_report.xml"
    report_id = None
    if report_def_path.exists():
        try:
            tree = ET.parse(report_def_path)
            root = tree.getroot()
            
            # Find the report record
            report_record = root.find(".//record[@model='ir.actions.report']")
            if report_record is not None:
                report_id = report_record.get('id')
                print(f"   ✅ Report ID found: {report_id}")
                fixes.append(f"Report defined with ID: {report_id}")
            else:
                errors.append("❌ Report record not found")
        except ET.ParseError as e:
            errors.append(f"❌ XML Parse Error in report definition: {e}")
    
    # 3. Check view reference
    print("\n👁️  3. Checking view button reference...")
    views_path = base_path / "views" / "order_views_assignment.xml"
    if views_path.exists():
        try:
            tree = ET.parse(views_path)
            root = tree.getroot()
            views_content = ET.tostring(root, encoding='unicode')
            
            # Check for correct external ID reference
            correct_ref = f"%(order_status_override.{report_id})d"
            if correct_ref in views_content:
                print(f"   ✅ Correct external ID reference found: {correct_ref}")
                fixes.append("External ID reference corrected in view")
            else:
                # Check for incorrect references
                if "%(report_sale_commission)d" in views_content:
                    errors.append("❌ Incorrect external ID reference found: %(report_sale_commission)d")
                elif f"%({report_id})d" in views_content:
                    errors.append(f"❌ Partial external ID reference found: %({report_id})d")
                else:
                    errors.append("❌ No commission report button reference found")
                    
        except ET.ParseError as e:
            errors.append(f"❌ XML Parse Error in view file: {e}")
    
    # 4. Check QWeb template ID
    print("\n🎨 4. Checking QWeb template ID...")
    template_path = base_path / "reports" / "sale_commission_template.xml"
    if template_path.exists():
        try:
            tree = ET.parse(template_path)
            root = tree.getroot()
            
            # Find the template
            template = root.find(".//template[@id='sale_commission_document']")
            if template is not None:
                template_id = template.get('id')
                print(f"   ✅ QWeb template ID found: {template_id}")
                
                # Check if report_name matches
                if report_id:
                    report_tree = ET.parse(base_path / "reports" / "sale_commission_report.xml")
                    report_name_field = report_tree.find(".//field[@name='report_name']")
                    if report_name_field is not None:
                        expected_name = f"order_status_override.{template_id}"
                        if report_name_field.text == expected_name:
                            print(f"   ✅ Report name matches template: {expected_name}")
                            fixes.append("Report name correctly references QWeb template")
                        else:
                            errors.append(f"❌ Report name mismatch. Expected: {expected_name}, Found: {report_name_field.text}")
            else:
                errors.append("❌ QWeb template not found")
        except ET.ParseError as e:
            errors.append(f"❌ XML Parse Error in template file: {e}")
    
    # 5. Check all XML files parse correctly
    print("\n🔍 5. Final XML validation...")
    xml_files = [
        'reports/sale_commission_report.xml',
        'reports/sale_commission_template.xml', 
        'views/order_views_assignment.xml'
    ]
    
    all_valid = True
    for xml_file in xml_files:
        if os.path.exists(xml_file):
            try:
                ET.parse(xml_file)
                print(f"   ✅ {xml_file} - Valid XML syntax")
            except ET.ParseError as e:
                print(f"   ❌ {xml_file} - Parse Error: {e}")
                errors.append(f"XML Parse Error in {xml_file}")
                all_valid = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FIX VALIDATION SUMMARY")
    print("=" * 50)
    
    if not errors:
        print("🎉 SUCCESS! All External ID issues have been resolved!")
        print("✅ All references are correct and properly ordered")
        
        if fixes:
            print(f"\n🔧 FIXES APPLIED ({len(fixes)}):")
            for fix in fixes:
                print(f"   ✅ {fix}")
        
        print("\n🚀 Ready for deployment!")
        print("\n📋 DEPLOYMENT COMMAND:")
        print("   ./odoo-bin -u order_status_override -d your_database")
        
    else:
        print(f"❌ ISSUES FOUND ({len(errors)}):")
        for error in errors:
            print(f"   {error}")
        
        if fixes:
            print(f"\n✅ FIXES APPLIED ({len(fixes)}):")
            for fix in fixes:
                print(f"   ✅ {fix}")
        
        print("\n🔧 Additional fixes may be needed before deployment")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = validate_external_id_fix()
    sys.exit(0 if success else 1)
