#!/usr/bin/env python3
"""
Commission Report Validation Script for order_status_override Module
This script validates the commission report implementation and ensures all components are properly configured.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_commission_report():
    """Validate the commission report implementation"""
    print("🔍 COMMISSION REPORT VALIDATION")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    errors = []
    warnings = []
    
    # 1. Validate manifest.py includes new files
    print("\n📋 1. Checking __manifest__.py...")
    manifest_path = base_path / "__manifest__.py"
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        required_files = [
            'reports/sale_commission_report.xml',
            'reports/sale_commission_template.xml'
        ]
        
        for file_path in required_files:
            if file_path in manifest_content:
                print(f"   ✅ {file_path} included in manifest")
            else:
                errors.append(f"❌ {file_path} not found in manifest")
    else:
        errors.append("❌ __manifest__.py not found")
    
    # 2. Validate report definition XML
    print("\n📄 2. Checking sale_commission_report.xml...")
    report_def_path = base_path / "reports" / "sale_commission_report.xml"
    if report_def_path.exists():
        try:
            tree = ET.parse(report_def_path)
            root = tree.getroot()
            
            # Check report record
            report_record = root.find(".//record[@model='ir.actions.report']")
            if report_record is not None:
                print("   ✅ Report definition found")
                
                # Check required fields
                required_fields = ['name', 'model', 'report_type', 'report_name']
                for field_name in required_fields:
                    field = report_record.find(f".//field[@name='{field_name}']")
                    if field is not None:
                        print(f"   ✅ Field '{field_name}': {field.text}")
                    else:
                        errors.append(f"❌ Missing field '{field_name}' in report definition")
            else:
                errors.append("❌ Report record not found")
                
        except ET.ParseError as e:
            errors.append(f"❌ XML Parse Error in sale_commission_report.xml: {e}")
    else:
        errors.append("❌ sale_commission_report.xml not found")
    
    # 3. Validate QWeb template
    print("\n🎨 3. Checking sale_commission_template.xml...")
    template_path = base_path / "reports" / "sale_commission_template.xml"
    if template_path.exists():
        try:
            tree = ET.parse(template_path)
            root = tree.getroot()
            
            # Check template record
            template = root.find(".//template[@id='sale_commission_document']")
            if template is not None:
                print("   ✅ QWeb template found")
                
                # Check for required field mappings
                template_content = ET.tostring(template, encoding='unicode')
                required_fields = [
                    'o.partner_id.name',  # Customer Name
                    'o.name',             # Order Reference
                    'o.booking_date',     # Booking Date
                    'o.project_id.name',  # Project Name
                    'o.amount_total',     # Total Amount
                    'o.broker_partner_id.name',  # Broker Name
                    'o.broker_amount',    # Broker Amount
                    'o.agent1_partner_id.name',  # Agent 1 Name
                    'o.agent1_amount',    # Agent 1 Amount
                ]
                
                for field in required_fields:
                    if field in template_content:
                        print(f"   ✅ Field mapping found: {field}")
                    else:
                        warnings.append(f"⚠️  Field mapping not found: {field}")
                
                # Check for CSS styles
                if '<style>' in template_content:
                    print("   ✅ CSS styles included")
                else:
                    warnings.append("⚠️  CSS styles not found")
                    
                # Check for OSUS branding
                if 'OSUS' in template_content:
                    print("   ✅ OSUS branding included")
                else:
                    warnings.append("⚠️  OSUS branding not found")
                    
            else:
                errors.append("❌ QWeb template not found")
                
        except ET.ParseError as e:
            errors.append(f"❌ XML Parse Error in sale_commission_template.xml: {e}")
    else:
        errors.append("❌ sale_commission_template.xml not found")
    
    # 4. Validate view modifications
    print("\n👁️  4. Checking view modifications...")
    views_path = base_path / "views" / "order_views_assignment.xml"
    if views_path.exists():
        try:
            tree = ET.parse(views_path)
            root = tree.getroot()
            views_content = ET.tostring(root, encoding='unicode')
            
            # Check for commission report button
            if 'report_sale_commission' in views_content:
                print("   ✅ Commission report button found in views")
            else:
                warnings.append("⚠️  Commission report button not found in views")
                
            # Check for booking_date field
            if 'booking_date' in views_content:
                print("   ✅ booking_date field found in views")
            else:
                warnings.append("⚠️  booking_date field not found in views")
                
        except ET.ParseError as e:
            errors.append(f"❌ XML Parse Error in order_views_assignment.xml: {e}")
    else:
        errors.append("❌ order_views_assignment.xml not found")
    
    # 5. Validate Python model
    print("\n🐍 5. Checking Python model...")
    model_path = base_path / "models" / "sale_order.py"
    if model_path.exists():
        with open(model_path, 'r', encoding='utf-8') as f:
            model_content = f.read()
        
        # Check for commission fields
        commission_fields = [
            'booking_date',
            'broker_partner_id',
            'broker_amount',
            'agent1_partner_id',
            'agent1_amount',
            'total_commission_amount'
        ]
        
        for field in commission_fields:
            if field in model_content:
                print(f"   ✅ Field defined: {field}")
            else:
                warnings.append(f"⚠️  Field not defined: {field}")
                
        # Check for QR code functionality
        if 'qr_code' in model_content:
            print("   ✅ QR code functionality found")
        else:
            warnings.append("⚠️  QR code functionality not found")
    else:
        errors.append("❌ sale_order.py not found")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if not errors and not warnings:
        print("🎉 PERFECT! Commission report implementation is complete and validated!")
        print("✅ All required components are present and properly configured")
        print("\n🚀 Ready for deployment!")
    else:
        if errors:
            print(f"❌ ERRORS FOUND ({len(errors)}):")
            for error in errors:
                print(f"   {error}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"   {warning}")
        
        if not errors:
            print("\n✅ No critical errors - Module should work with minor adjustments needed")
        else:
            print("\n🔧 Critical errors found - Please fix before deployment")
    
    # Installation instructions
    print("\n" + "=" * 50)
    print("📋 INSTALLATION INSTRUCTIONS")
    print("=" * 50)
    print("1. Upgrade the module:")
    print("   ./odoo-bin -u order_status_override -d your_database")
    print("\n2. Test the commission report:")
    print("   - Go to Sales → Orders")
    print("   - Open a confirmed sale order")
    print("   - Click 'Commission Report' button")
    print("   - Verify PDF generation")
    print("\n3. Required fields for optimal report:")
    print("   - booking_date (for filtering)")
    print("   - project_id (project information)")
    print("   - unit_id (unit details)")
    print("   - Commission partner assignments")
    print("   - Commission rates and amounts")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = validate_commission_report()
    sys.exit(0 if success else 1)
