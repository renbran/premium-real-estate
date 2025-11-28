#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Account Payment Final Module - Modern Syntax Validation
Validates all JavaScript, SCSS, CSS files for modern Odoo 17 compliance
"""

import os
import re
import json
from pathlib import Path

def validate_javascript_files():
    """Validate JavaScript files for modern Odoo 17 syntax"""
    js_files = list(Path('account_payment_final/static').rglob('*.js'))
    results = {'valid': [], 'issues': []}
    
    for js_file in js_files:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for proper module declaration
        if not content.strip().startswith('/** @odoo-module **/'):
            issues.append("Missing /** @odoo-module **/ declaration")
        
        # Check for legacy odoo.define (except in compatibility files)
        if 'odoo.define(' in content and 'compatibility' not in str(js_file).lower():
            issues.append("Contains legacy odoo.define() - should use ES6 imports")
        
        # Check for proper import order (imports should come first after module declaration)
        lines = content.split('\n')
        found_module_decl = False
        found_import = False
        found_other_code = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('/** @odoo-module **/'):
                found_module_decl = True
            elif line.startswith('import ') and found_module_decl:
                found_import = True
                if found_other_code:
                    issues.append("Import statements should come immediately after /** @odoo-module **/")
            elif line and not line.startswith('//') and not line.startswith('/*') and found_import:
                if not line.startswith('import ') and not line.startswith('export'):
                    found_other_code = True
        
        # Check for syntax errors (basic)
        if '};' in content or '{;' in content:
            issues.append("Potential syntax error: '}; or {;' found")
        
        if issues:
            results['issues'].append({'file': str(js_file), 'issues': issues})
        else:
            results['valid'].append(str(js_file))
    
    return results

def validate_scss_files():
    """Validate SCSS files for modern syntax and BEM methodology"""
    scss_files = list(Path('account_payment_final/static').rglob('*.scss'))
    results = {'valid': [], 'issues': []}
    
    for scss_file in scss_files:
        with open(scss_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for proper BEM naming conventions
        if not re.search(r'\.o_account_payment_final__', content):
            issues.append("Should use BEM methodology with .o_account_payment_final__ prefix")
        
        # Check for consistent comment style (should use /* */ for CSS compatibility)
        if '//' in content and '/*' in content:
            issues.append("Mixed comment styles - prefer /* */ for CSS compatibility")
        
        # Check for proper CSS custom properties
        css_vars = re.findall(r'var\(([^)]+)\)', content)
        for var in css_vars:
            if var.startswith('--') and var.endswith('--'):
                issues.append(f"Malformed CSS custom property: {var}")
        
        if issues:
            results['issues'].append({'file': str(scss_file), 'issues': issues})
        else:
            results['valid'].append(str(scss_file))
    
    return results

def validate_css_files():
    """Validate CSS files for modern syntax"""
    css_files = list(Path('account_payment_final/static').rglob('*.css'))
    results = {'valid': [], 'issues': []}
    
    for css_file in css_files:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for proper BEM naming conventions
        if not re.search(r'\.o_account_payment_final__', content):
            issues.append("Should use BEM methodology with .o_account_payment_final__ prefix")
        
        # Check for malformed CSS custom properties
        malformed_vars = re.findall(r'var\(--[^-][^)]*--[^)]*\)', content)
        if malformed_vars:
            issues.append(f"Malformed CSS custom properties: {malformed_vars}")
        
        if issues:
            results['issues'].append({'file': str(css_file), 'issues': issues})
        else:
            results['valid'].append(str(css_file))
    
    return results

def validate_xml_templates():
    """Validate XML template files for proper OWL syntax"""
    xml_files = list(Path('account_payment_final/static').rglob('*.xml'))
    results = {'valid': [], 'issues': []}
    
    for xml_file in xml_files:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for proper OWL template syntax
        if '<t t-name=' in content and 'owl="1"' not in content:
            issues.append("OWL templates should include owl=\"1\" attribute")
        
        # Check for deprecated t-* attributes
        deprecated_attrs = ['t-foreach-key', 't-foreach-value']
        for attr in deprecated_attrs:
            if attr in content:
                issues.append(f"Deprecated attribute {attr} found")
        
        if issues:
            results['issues'].append({'file': str(xml_file), 'issues': issues})
        else:
            results['valid'].append(str(xml_file))
    
    return results

def main():
    """Main validation function"""
    print("🔍 Account Payment Final - Modern Syntax Validation")
    print("=" * 60)
    
    # Change to the correct directory
    if not os.path.exists('account_payment_final'):
        print("❌ Error: account_payment_final directory not found")
        print("   Make sure you're running this script from the correct directory")
        return
    
    # Validate JavaScript files
    print("\n📄 Validating JavaScript files...")
    js_results = validate_javascript_files()
    print(f"✅ Valid: {len(js_results['valid'])} files")
    if js_results['issues']:
        print(f"⚠️  Issues found in {len(js_results['issues'])} files:")
        for issue in js_results['issues']:
            print(f"   📁 {issue['file']}:")
            for problem in issue['issues']:
                print(f"      • {problem}")
    
    # Validate SCSS files
    print("\n🎨 Validating SCSS files...")
    scss_results = validate_scss_files()
    print(f"✅ Valid: {len(scss_results['valid'])} files")
    if scss_results['issues']:
        print(f"⚠️  Issues found in {len(scss_results['issues'])} files:")
        for issue in scss_results['issues']:
            print(f"   📁 {issue['file']}:")
            for problem in issue['issues']:
                print(f"      • {problem}")
    
    # Validate CSS files
    print("\n🎨 Validating CSS files...")
    css_results = validate_css_files()
    print(f"✅ Valid: {len(css_results['valid'])} files")
    if css_results['issues']:
        print(f"⚠️  Issues found in {len(css_results['issues'])} files:")
        for issue in css_results['issues']:
            print(f"   📁 {issue['file']}:")
            for problem in issue['issues']:
                print(f"      • {problem}")
    
    # Validate XML templates
    print("\n📋 Validating XML template files...")
    xml_results = validate_xml_templates()
    print(f"✅ Valid: {len(xml_results['valid'])} files")
    if xml_results['issues']:
        print(f"⚠️  Issues found in {len(xml_results['issues'])} files:")
        for issue in xml_results['issues']:
            print(f"   📁 {issue['file']}:")
            for problem in issue['issues']:
                print(f"      • {problem}")
    
    # Summary
    total_issues = len(js_results['issues']) + len(scss_results['issues']) + len(css_results['issues']) + len(xml_results['issues'])
    total_valid = len(js_results['valid']) + len(scss_results['valid']) + len(css_results['valid']) + len(xml_results['valid'])
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"✅ Total valid files: {total_valid}")
    print(f"⚠️  Files with issues: {total_issues}")
    
    if total_issues == 0:
        print("\n🎉 All files pass modern Odoo 17 syntax validation!")
        print("✅ Module is ready for deployment")
    else:
        print(f"\n⚠️  Please fix {total_issues} file(s) before deployment")
        print("💡 See issues listed above for specific fixes needed")

if __name__ == "__main__":
    main()
