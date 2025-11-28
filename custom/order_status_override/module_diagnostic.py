#!/usr/bin/env python3
"""
Comprehensive Odoo 17 Module Diagnostic Tool
===========================================

This script identifies and reports potential issues that could cause
JavaScript errors, database loading problems, and other instability issues
in Odoo 17 modules.
"""

import os
import xml.etree.ElementTree as ET
import ast
import re
from collections import defaultdict

def check_external_id_conflicts(base_path):
    """Check for duplicate external IDs across XML files"""
    print("🔍 CHECKING FOR EXTERNAL ID CONFLICTS")
    print("-" * 50)
    
    external_ids = defaultdict(list)
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                try:
                    tree = ET.parse(file_path)
                    for elem in tree.iter():
                        if 'id' in elem.attrib:
                            ext_id = elem.attrib['id']
                            external_ids[ext_id].append(file_path)
                except ET.ParseError as e:
                    print(f"❌ XML Parse Error in {file_path}: {e}")
    
    conflicts = {k: v for k, v in external_ids.items() if len(v) > 1}
    
    if conflicts:
        print("❌ EXTERNAL ID CONFLICTS FOUND:")
        for ext_id, files in conflicts.items():
            print(f"  - ID '{ext_id}' defined in:")
            for file in files:
                print(f"    * {file}")
    else:
        print("✅ No external ID conflicts found")
    
    return conflicts

def check_asset_references(manifest_path, static_path):
    """Check if all assets referenced in manifest exist"""
    print("\n🎨 CHECKING ASSET REFERENCES")
    print("-" * 40)
    
    issues = []
    
    try:
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        # Extract asset references
        asset_pattern = r"'([^']+\.(?:js|css|scss))'"
        assets = re.findall(asset_pattern, manifest_content)
        
        for asset in assets:
            # Convert relative path to full path
            full_path = os.path.join(os.path.dirname(manifest_path), asset)
            if not os.path.exists(full_path):
                issues.append(f"Missing asset: {asset}")
                print(f"❌ Missing asset: {asset}")
            else:
                # Check if file is empty
                if os.path.getsize(full_path) == 0:
                    print(f"⚠️  Empty asset file: {asset}")
                else:
                    print(f"✅ Asset found: {asset}")
    
    except Exception as e:
        print(f"❌ Error checking assets: {e}")
        issues.append(f"Error checking assets: {e}")
    
    return issues

def check_unused_files(base_path, manifest_path):
    """Check for files that exist but aren't referenced"""
    print("\n🧹 CHECKING FOR UNUSED FILES")
    print("-" * 35)
    
    unused_files = []
    
    try:
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        # Get all files in the module
        all_files = []
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(('.xml', '.py', '.js', '.css', '.scss')):
                    rel_path = os.path.relpath(os.path.join(root, file), base_path)
                    all_files.append(rel_path.replace('\\', '/'))
        
        # Check which files are not referenced
        for file_path in all_files:
            if file_path not in manifest_content and not file_path.startswith('__pycache__'):
                # Exclude certain files that don't need to be in manifest
                if not any(x in file_path for x in ['__init__.py', '__pycache__', '.pyc']):
                    unused_files.append(file_path)
                    print(f"⚠️  Potentially unused: {file_path}")
        
        if not unused_files:
            print("✅ No unused files detected")
            
    except Exception as e:
        print(f"❌ Error checking unused files: {e}")
    
    return unused_files

def check_import_dependencies(base_path):
    """Check for missing import dependencies in Python files"""
    print("\n🐍 CHECKING PYTHON IMPORT DEPENDENCIES")
    print("-" * 45)
    
    issues = []
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for potential issues
                    if 'from odoo import' in content and 'models' not in content:
                        if 'fields' in content or 'api' in content:
                            issues.append(f"{file}: May be missing 'models' import")
                            print(f"⚠️  {file}: May be missing 'models' import")
                    
                    # Check syntax
                    ast.parse(content)
                    print(f"✅ Python syntax OK: {file}")
                    
                except SyntaxError as e:
                    issues.append(f"{file}: Python syntax error - {e}")
                    print(f"❌ Python syntax error in {file}: {e}")
                except Exception as e:
                    print(f"⚠️  Could not check {file}: {e}")
    
    return issues

def check_odoo17_compatibility(base_path):
    """Check for Odoo 17 compatibility issues"""
    print("\n🔧 CHECKING ODOO 17 COMPATIBILITY")
    print("-" * 40)
    
    issues = []
    
    # Check for deprecated patterns
    deprecated_patterns = [
        (r'@api\.one', 'Use @api.model or remove decorator'),
        (r'@api\.multi', 'Use @api.model or remove decorator'),
        (r'\.sudo\(\)', 'Check if sudo() usage is appropriate'),
        (r'website\.website_form', 'May need updating for Odoo 17'),
    ]
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern, message in deprecated_patterns:
                        if re.search(pattern, content):
                            issues.append(f"{file}: {message}")
                            print(f"⚠️  {file}: {message}")
                            
                except Exception as e:
                    print(f"⚠️  Could not check {file}: {e}")
    
    if not issues:
        print("✅ No obvious compatibility issues found")
    
    return issues

def main():
    """Main diagnostic function"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(base_path, '__manifest__.py')
    static_path = os.path.join(base_path, 'static')
    
    print("🔧 ODOO 17 MODULE DIAGNOSTIC TOOL")
    print("=" * 50)
    print(f"Analyzing module: {os.path.basename(base_path)}")
    print("=" * 50)
    
    all_issues = []
    
    # Run all checks
    conflicts = check_external_id_conflicts(base_path)
    asset_issues = check_asset_references(manifest_path, static_path)
    unused_files = check_unused_files(base_path, manifest_path)
    import_issues = check_import_dependencies(base_path)
    compatibility_issues = check_odoo17_compatibility(base_path)
    
    # Compile all issues
    all_issues.extend([f"External ID conflict: {k}" for k in conflicts.keys()])
    all_issues.extend(asset_issues)
    all_issues.extend([f"Unused file: {f}" for f in unused_files])
    all_issues.extend(import_issues)
    all_issues.extend(compatibility_issues)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if all_issues:
        print(f"❌ Found {len(all_issues)} potential issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        print("\n💡 Recommendation: Address these issues before deployment")
    else:
        print("🎉 No critical issues found! Module appears ready for deployment.")
    
    print("\n🚀 Next steps:")
    print("1. Address any issues listed above")
    print("2. Test module installation in development environment")
    print("3. Verify all functionality works as expected")
    print("4. Deploy to production")

if __name__ == "__main__":
    main()
