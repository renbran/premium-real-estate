#!/usr/bin/env python3
"""
Comprehensive Theme Validation Script
Tests the Scholarix AI Theme for completeness, syntax, and compatibility
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class ScholarixThemeValidator:
    def __init__(self):
        self.theme_path = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def log_error(self, message):
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ ERROR: {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  WARNING: {message}")
        print(f"⚠️  WARNING: {message}")
        
    def log_success(self, message):
        print(f"✅ {message}")
        
    def test_file_structure(self):
        """Test that all required files exist"""
        print("\n🔍 Testing File Structure...")
        
        required_files = [
            "__manifest__.py",
            "__init__.py",
            "models/__init__.py",
            "models/theme_utils.py",
            "static/src/js/scholarix_main.js",
            "static/src/js/scholarix_loader.js",
            "static/src/js/scholarix_cursor.js",
            "static/src/js/scholarix_3d_hero.js",
            "static/src/js/scholarix_animations.js",
            "static/src/js/scholarix_particles.js",
            "static/src/scss/primary_variables.scss",
            "static/src/scss/bootstrap_overrides.scss",
            "static/src/scss/scholarix_main.scss",
            "static/src/scss/scholarix_loading.scss",
            "static/src/scss/scholarix_cursor.scss",
            "static/src/scss/scholarix_animations.scss",
            "views/layout_templates.xml",
            "views/homepage_sections.xml",
            "views/snippets.xml",
            "static/description/index.html"
        ]
        
        for file_path in required_files:
            full_path = self.theme_path / file_path
            if full_path.exists():
                self.log_success(f"Found: {file_path}")
            else:
                self.log_error(f"Missing required file: {file_path}")
                
        # Check for logo placeholder
        logo_path = self.theme_path / "static/src/img/logo.png"
        if not logo_path.exists():
            # Create img directory if it doesn't exist
            logo_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_warning("Logo file missing - created directory placeholder")
        else:
            self.log_success("Logo file found")
            
    def test_manifest_structure(self):
        """Test the __manifest__.py file"""
        print("\n📋 Testing Manifest Structure...")
        
        manifest_path = self.theme_path / "__manifest__.py"
        try:
            # Read and execute manifest as Python code
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic syntax check
            compile(content, str(manifest_path), 'exec')
            self.log_success("Manifest syntax is valid")
            
            # Check for required keys
            local_vars = {}
            exec(content, {}, local_vars)
            
            if not local_vars:
                self.log_error("Manifest doesn't define any variables")
                return
                
            # Get the manifest dict (should be the only top-level dict)
            manifest = None
            for var in local_vars.values():
                if isinstance(var, dict) and 'name' in var:
                    manifest = var
                    break
                    
            if not manifest:
                self.log_error("No manifest dictionary found")
                return
                
            required_keys = ['name', 'version', 'category', 'depends', 'data', 'assets']
            for key in required_keys:
                if key in manifest:
                    self.log_success(f"Manifest has '{key}' key")
                else:
                    self.log_error(f"Manifest missing '{key}' key")
                    
            # Check version format
            version = manifest.get('version', '')
            if version.startswith('18.0.'):
                self.log_success(f"Version format correct: {version}")
            else:
                self.log_warning(f"Version should start with '18.0.': {version}")
                
        except Exception as e:
            self.log_error(f"Manifest validation failed: {str(e)}")
            
    def test_javascript_syntax(self):
        """Test JavaScript files for basic syntax"""
        print("\n🔧 Testing JavaScript Syntax...")
        
        js_files = [
            "static/src/js/scholarix_main.js",
            "static/src/js/scholarix_loader.js",
            "static/src/js/scholarix_cursor.js",
            "static/src/js/scholarix_3d_hero.js",
            "static/src/js/scholarix_animations.js",
            "static/src/js/scholarix_particles.js"
        ]
        
        for js_file in js_files:
            file_path = self.theme_path / js_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Basic checks
                    if 'odoo.define' in content:
                        self.log_success(f"{js_file}: Has Odoo module definition")
                    else:
                        self.log_warning(f"{js_file}: Missing Odoo module definition")
                        
                    # Check for syntax issues
                    if content.count('{') != content.count('}'):
                        self.log_error(f"{js_file}: Mismatched curly braces")
                    else:
                        self.log_success(f"{js_file}: Bracket syntax looks good")
                        
                except Exception as e:
                    self.log_error(f"Error reading {js_file}: {str(e)}")
            else:
                self.log_error(f"JavaScript file not found: {js_file}")
                
    def test_scss_syntax(self):
        """Test SCSS files for basic syntax"""
        print("\n🎨 Testing SCSS Syntax...")
        
        scss_files = [
            "static/src/scss/primary_variables.scss",
            "static/src/scss/bootstrap_overrides.scss",
            "static/src/scss/scholarix_main.scss",
            "static/src/scss/scholarix_loading.scss",
            "static/src/scss/scholarix_cursor.scss",
            "static/src/scss/scholarix_animations.scss"
        ]
        
        for scss_file in scss_files:
            file_path = self.theme_path / scss_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Basic SCSS checks
                    if '$' in content:
                        self.log_success(f"{scss_file}: Contains SCSS variables")
                    
                    # Check for balanced braces
                    if content.count('{') == content.count('}'):
                        self.log_success(f"{scss_file}: Balanced braces")
                    else:
                        self.log_error(f"{scss_file}: Mismatched braces")
                        
                    # Check for empty rules (common lint issue)
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if line.endswith('{') and i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line == '}':
                                self.log_warning(f"{scss_file} line {i+1}: Empty CSS rule")
                        
                except Exception as e:
                    self.log_error(f"Error reading {scss_file}: {str(e)}")
            else:
                self.log_error(f"SCSS file not found: {scss_file}")
                
    def test_xml_syntax(self):
        """Test XML files for basic syntax"""
        print("\n📄 Testing XML Syntax...")
        
        xml_files = [
            "views/layout_templates.xml",
            "views/homepage_sections.xml", 
            "views/snippets.xml"
        ]
        
        for xml_file in xml_files:
            file_path = self.theme_path / xml_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Basic XML checks
                    if '<?xml' in content:
                        self.log_success(f"{xml_file}: Has XML declaration")
                    else:
                        self.log_warning(f"{xml_file}: Missing XML declaration")
                        
                    if '<odoo>' in content and '</odoo>' in content:
                        self.log_success(f"{xml_file}: Has Odoo root element")
                    else:
                        self.log_warning(f"{xml_file}: Missing Odoo root element")
                        
                    # Try basic XML parsing
                    try:
                        import xml.etree.ElementTree as ET
                        ET.fromstring(content)
                        self.log_success(f"{xml_file}: XML syntax is valid")
                    except ET.ParseError as e:
                        self.log_error(f"{xml_file}: XML parse error: {str(e)}")
                        
                except Exception as e:
                    self.log_error(f"Error reading {xml_file}: {str(e)}")
            else:
                self.log_error(f"XML file not found: {xml_file}")
                
    def test_python_syntax(self):
        """Test Python files for syntax"""
        print("\n🐍 Testing Python Syntax...")
        
        python_files = [
            "__init__.py",
            "models/__init__.py",
            "models/theme_utils.py"
        ]
        
        for py_file in python_files:
            file_path = self.theme_path / py_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Compile check
                    compile(content, str(file_path), 'exec')
                    self.log_success(f"{py_file}: Python syntax is valid")
                    
                except SyntaxError as e:
                    self.log_error(f"{py_file}: Python syntax error: {str(e)}")
                except Exception as e:
                    self.log_error(f"Error reading {py_file}: {str(e)}")
            else:
                self.log_error(f"Python file not found: {py_file}")
                
    def create_test_report(self):
        """Create a comprehensive test report"""
        print("\n📊 Creating Test Report...")
        
        report = f"""
# Scholarix AI Theme - Test Report
Generated: {os.popen('date').read().strip()}

## Summary
- Total Errors: {len(self.errors)}
- Total Warnings: {len(self.warnings)}

## Test Results

### Errors
"""
        for error in self.errors:
            report += f"{error}\n"
            
        report += "\n### Warnings\n"
        for warning in self.warnings:
            report += f"{warning}\n"
            
        report += f"""

## Deployment Status
{"🔴 NOT READY - Fix errors before deployment" if self.errors else "🟢 READY FOR DEPLOYMENT"}

## Next Steps
"""
        if self.errors:
            report += "1. Fix all errors listed above\n"
            report += "2. Re-run validation script\n"
            report += "3. Test in Docker environment\n"
        else:
            report += "1. Deploy to Docker for testing\n"
            report += "2. Install in Odoo instance\n"
            report += "3. Test all features\n"
            
        # Save report
        report_path = self.theme_path / "TEST_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"📄 Test report saved to: {report_path}")
        
    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Comprehensive Theme Validation...")
        print(f"📁 Theme Path: {self.theme_path}")
        
        self.test_file_structure()
        self.test_manifest_structure()
        self.test_python_syntax()
        self.test_javascript_syntax()
        self.test_scss_syntax()
        self.test_xml_syntax()
        self.create_test_report()
        
        print(f"\n🎯 Validation Complete!")
        print(f"   Errors: {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")
        
        return len(self.errors) == 0

if __name__ == "__main__":
    validator = ScholarixThemeValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)
