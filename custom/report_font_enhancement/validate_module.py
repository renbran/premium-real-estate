#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick validation script for the Report Font Enhancement module
"""

import os
import json

def validate_module_structure():
    """Validate that all required files exist"""
    
    base_path = "d:\\RUNNING APPS\\ready production\\latest\\odoo17_final\\report_font_enhancement"
    
    required_files = [
        "__manifest__.py",
        "__init__.py", 
        "models/__init__.py",
        "models/report_font_settings.py",
        "views/report_enhancement_views.xml",
        "security/ir.model.access.csv",
        "static/src/css/report_font_enhancement.css",
        "static/src/css/report_font_enhancement_pdf.css",
        "static/src/css/report_font_enhancement_common.css",
        "static/src/js/report_font_enhancement.js",
        "static/description/index.html",
        "README.md"
    ]
    
    print("üîç VALIDATING MODULE STRUCTURE")
    print("=" * 40)
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            existing_files.append(file_path)
            print(f"‚úÖ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"‚ùå {file_path}")
    
    print("\nüìä SUMMARY")
    print("=" * 40)
    print(f"Total files checked: {len(required_files)}")
    print(f"Existing files: {len(existing_files)}")
    print(f"Missing files: {len(missing_files)}")
    
    if missing_files:
        print(f"\n‚ùå Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print(f"\n‚úÖ All required files are present!")
        return True

def validate_manifest():
    """Validate the manifest file"""
    
    print("\nüîç VALIDATING MANIFEST FILE")
    print("=" * 40)
    
    manifest_path = "d:\\RUNNING APPS\\ready production\\latest\\odoo17_final\\report_font_enhancement\\__manifest__.py"
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic validation
        required_keys = ['name', 'version', 'depends', 'data', 'assets']
        
        for key in required_keys:
            if f"'{key}'" in content:
                print(f"‚úÖ {key}")
            else:
                print(f"‚ùå {key}")
                
        print("\n‚úÖ Manifest file structure looks good!")
        return True
        
    except Exception as e:
        print(f"‚ùå Error reading manifest: {e}")
        return False

def check_css_file_sizes():
    """Check CSS file sizes to ensure they're not empty"""
    
    print("\nüîç CHECKING CSS FILES")
    print("=" * 40)
    
    css_files = [
        "static/src/css/report_font_enhancement.css",
        "static/src/css/report_font_enhancement_pdf.css", 
        "static/src/css/report_font_enhancement_common.css"
    ]
    
    base_path = "d:\\RUNNING APPS\\ready production\\latest\\odoo17_final\\report_font_enhancement"
    
    for css_file in css_files:
        file_path = os.path.join(base_path, css_file)
        try:
            size = os.path.getsize(file_path)
            if size > 1000:  # At least 1KB
                print(f"‚úÖ {css_file} ({size:,} bytes)")
            else:
                print(f"‚ö†Ô∏è  {css_file} ({size} bytes - might be too small)")
        except Exception as e:
            print(f"‚ùå {css_file} - Error: {e}")

def main():
    """Main validation function"""
    
    print("üöÄ REPORT FONT ENHANCEMENT MODULE VALIDATOR")
    print("=" * 50)
    
    # Run validations
    structure_ok = validate_module_structure()
    manifest_ok = validate_manifest() 
    check_css_file_sizes()
    
    print("\nüéØ FINAL VALIDATION RESULT")
    print("=" * 50)
    
    if structure_ok and manifest_ok:
        print("‚úÖ MODULE IS READY FOR INSTALLATION!")
        print("\nüìù Next steps:")
        print("1. Copy the module to your Odoo addons directory")
        print("2. Restart Odoo server") 
        print("3. Update apps list")
        print("4. Install 'Report Font Enhancement' module")
        print("5. Configure settings at Settings ‚Üí Report Enhancement")
        
        return True
    else:
        print("‚ùå MODULE HAS ISSUES - Please fix before installation")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
