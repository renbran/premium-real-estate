#!/usr/bin/env python3
"""
Final Module Safety Check - Odoo 17 Installation Readiness
==========================================================

This script performs a comprehensive safety check to ensure the module
can be installed without errors in Odoo 17.
"""

import os
import xml.etree.ElementTree as ET
import ast
import subprocess
import sys

def check_critical_errors(base_path):
    """Check for issues that would prevent module installation"""
    print("🔒 CRITICAL ERROR CHECK")
    print("-" * 30)
    
    critical_issues = []
    
    # Check for duplicate external IDs
    external_ids = {}
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                try:
                    tree = ET.parse(file_path)
                    for elem in tree.iter():
                        if 'id' in elem.attrib:
                            ext_id = elem.attrib['id']
                            if ext_id in external_ids:
                                critical_issues.append(f"Duplicate external ID: {ext_id}")
                                print(f"❌ Duplicate external ID: {ext_id}")
                            else:
                                external_ids[ext_id] = file_path
                except:
                    critical_issues.append(f"XML parse error: {file_path}")
                    print(f"❌ XML parse error: {file_path}")
    
    # Check for non-Python files in models directory
    models_path = os.path.join(base_path, 'models')
    if os.path.exists(models_path):
        for file in os.listdir(models_path):
            if not file.endswith('.py') and not file.startswith('__'):
                critical_issues.append(f"Non-Python file in models: {file}")
                print(f"❌ Non-Python file in models: {file}")
    
    # Check for non-JS/CSS files in static directories
    static_path = os.path.join(base_path, 'static', 'src')
    if os.path.exists(static_path):
        for root, dirs, files in os.walk(static_path):
            for file in files:
                if not file.endswith(('.js', '.css', '.scss', '.xml', '.png', '.jpg', '.gif', '.svg')):
                    critical_issues.append(f"Unexpected file in static: {file}")
                    print(f"❌ Unexpected file in static: {file}")
    
    if not critical_issues:
        print("✅ No critical errors found")
    
    return critical_issues

def check_manifest_integrity(manifest_path):
    """Check manifest file for common issues"""
    print("\n📋 MANIFEST INTEGRITY CHECK")
    print("-" * 35)
    
    issues = []
    
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Execute the manifest file to get the dictionary
        namespace = {}
        exec(content, namespace)
        # Find the dictionary in the namespace
        manifest_data = None
        for value in namespace.values():
            if isinstance(value, dict) and 'name' in value:
                manifest_data = value
                break
        
        if manifest_data is None:
            # Fallback: try to evaluate the content directly
            manifest_data = eval(content)
        
        # Check required fields
        required_fields = ['name', 'version', 'depends', 'data']
        for field in required_fields:
            if field not in manifest_data:
                issues.append(f"Missing required field: {field}")
                print(f"❌ Missing required field: {field}")
            else:
                print(f"✅ Required field present: {field}")
        
        # Check data files exist
        if 'data' in manifest_data:
            base_path = os.path.dirname(manifest_path)
            for data_file in manifest_data['data']:
                full_path = os.path.join(base_path, data_file)
                if not os.path.exists(full_path):
                    issues.append(f"Missing data file: {data_file}")
                    print(f"❌ Missing data file: {data_file}")
                else:
                    print(f"✅ Data file exists: {data_file}")
        
        # Check assets exist
        if 'assets' in manifest_data:
            base_path = os.path.dirname(manifest_path)
            for bundle, files in manifest_data['assets'].items():
                for asset_file in files:
                    # Remove module prefix if present
                    if asset_file.startswith('order_status_override/'):
                        asset_file = asset_file[len('order_status_override/'):]
                    full_path = os.path.join(base_path, asset_file)
                    if not os.path.exists(full_path):
                        issues.append(f"Missing asset: {asset_file}")
                        print(f"❌ Missing asset: {asset_file}")
                    else:
                        print(f"✅ Asset exists: {asset_file}")
    
    except Exception as e:
        issues.append(f"Manifest parse error: {e}")
        print(f"❌ Manifest parse error: {e}")
    
    return issues

def check_dependencies(base_path):
    """Check if all Python dependencies are available"""
    print("\n🔗 DEPENDENCY CHECK")
    print("-" * 25)
    
    missing_deps = []
    
    # Common Odoo imports to check
    common_imports = [
        'odoo',
        'datetime',
        'logging'
    ]
    
    for dep in common_imports:
        try:
            __import__(dep)
            print(f"✅ {dep} available")
        except ImportError:
            missing_deps.append(dep)
            print(f"❌ {dep} missing")
    
    return missing_deps

def security_check(base_path):
    """Check for basic security configurations"""
    print("\n🛡️  SECURITY CONFIGURATION CHECK")
    print("-" * 40)
    
    issues = []
    
    # Check if security files exist
    security_files = [
        'security/ir.model.access.csv',
        'security/security.xml'
    ]
    
    for sec_file in security_files:
        full_path = os.path.join(base_path, sec_file)
        if os.path.exists(full_path):
            print(f"✅ Security file exists: {sec_file}")
        else:
            issues.append(f"Missing security file: {sec_file}")
            print(f"⚠️  Security file missing: {sec_file}")
    
    return issues

def main():
    """Main safety check function"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(base_path, '__manifest__.py')
    
    print("🔒 ODOO 17 MODULE SAFETY CHECK")
    print("=" * 50)
    print(f"Module: {os.path.basename(base_path)}")
    print("=" * 50)
    
    # Run all checks
    critical_issues = check_critical_errors(base_path)
    manifest_issues = check_manifest_integrity(manifest_path)
    missing_deps = check_dependencies(base_path)
    security_issues = security_check(base_path)
    
    # Compile results
    all_issues = critical_issues + manifest_issues + security_issues
    
    print("\n" + "=" * 50)
    print("🎯 SAFETY CHECK RESULTS")
    print("=" * 50)
    
    if not all_issues and not missing_deps:
        print("🎉 MODULE IS SAFE FOR INSTALLATION!")
        print("\n✅ No critical issues found")
        print("✅ All dependencies available")
        print("✅ Manifest integrity confirmed")
        print("✅ Security configuration present")
        print("\n🚀 Ready for deployment to Odoo 17")
        return True
    else:
        print("⚠️  ISSUES FOUND - REVIEW BEFORE INSTALLATION")
        if critical_issues:
            print(f"\n❌ Critical issues ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  • {issue}")
        
        if manifest_issues:
            print(f"\n📋 Manifest issues ({len(manifest_issues)}):")
            for issue in manifest_issues:
                print(f"  • {issue}")
        
        if missing_deps:
            print(f"\n🔗 Missing dependencies ({len(missing_deps)}):")
            for dep in missing_deps:
                print(f"  • {dep}")
        
        if security_issues:
            print(f"\n🛡️  Security issues ({len(security_issues)}):")
            for issue in security_issues:
                print(f"  • {issue}")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
