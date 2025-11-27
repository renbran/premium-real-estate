#!/usr/bin/env python3
"""
Module validation script for oe_sale_dashboard_17
Checks for common Odoo 17 compatibility issues
"""

import os
import xml.etree.ElementTree as ET
import json

def validate_manifest():
    """Validate __manifest__.py file"""
    manifest_path = "__manifest__.py"
    print("🔍 Validating manifest file...")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for common issues
        issues = []
        
        if "'states'" in content:
            issues.append("❌ Deprecated 'states' attribute found")
        if "'attrs'" in content:
            issues.append("❌ Deprecated 'attrs' attribute found")
        if "'qweb'" in content:
            issues.append("❌ Deprecated 'qweb' field found, use 'assets' instead")
            
        if not issues:
            print("✅ Manifest file validation passed")
        else:
            for issue in issues:
                print(issue)
                
    except Exception as e:
        print(f"❌ Error validating manifest: {e}")

def validate_xml_files():
    """Validate XML files for Odoo 17 compliance"""
    xml_files = []
    
    # Find all XML files
    for root, dirs, files in os.walk('views'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    print(f"🔍 Validating {len(xml_files)} XML files...")
    
    for xml_file in xml_files:
        try:
            print(f"  📄 Checking {xml_file}...")
            
            # Parse XML
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Check for deprecated attributes
            issues = []
            
            for elem in root.iter():
                if elem.get('states'):
                    issues.append(f"❌ Deprecated 'states' attribute in {elem.tag}")
                if elem.get('attrs'):
                    issues.append(f"❌ Deprecated 'attrs' attribute in {elem.tag}")
                    
                # Check labels without 'for' attribute
                if elem.tag == 'label' and elem.get('string') and not elem.get('for'):
                    issues.append(f"❌ Label without 'for' attribute: '{elem.get('string')}'")
            
            if not issues:
                print(f"    ✅ {xml_file} validation passed")
            else:
                for issue in issues:
                    print(f"    {issue}")
                    
        except ET.ParseError as e:
            print(f"    ❌ XML parsing error in {xml_file}: {e}")
        except Exception as e:
            print(f"    ❌ Error validating {xml_file}: {e}")

def validate_assets():
    """Validate that referenced assets exist"""
    print("🔍 Validating asset files...")
    
    assets = [
        'static/src/js/dashboard.js',
        'static/src/css/dashboard.css',
        'static/src/xml/dashboard_template.xml'
    ]
    
    for asset in assets:
        if os.path.exists(asset):
            print(f"  ✅ {asset} exists")
        else:
            print(f"  ❌ {asset} missing")

def main():
    """Main validation function"""
    print("🚀 Starting Odoo 17 module validation...")
    print("=" * 50)
    
    validate_manifest()
    print()
    validate_xml_files()
    print()
    validate_assets()
    
    print("=" * 50)
    print("🏁 Validation completed!")

if __name__ == "__main__":
    main()
