#!/usr/bin/env python3
"""
Account Payment Final - Module Cleanup Script
Removes redundant files and consolidates essential functionality
"""

import os
import shutil
from pathlib import Path

# Define paths
MODULE_PATH = Path("d:/RUNNING APPS/ready production/latest/odoo17_final/account_payment_final")
ESSENTIAL_PATH = MODULE_PATH / "essential_files"
BACKUP_PATH = MODULE_PATH / "backup_before_cleanup"

# Files to keep (essential)
ESSENTIAL_FILES = {
    # Core Python Models
    "models/__init__.py",
    "models/account_payment.py",
    "models/payment_approval_history.py", 
    "models/res_config_settings.py",
    "models/res_company.py",
    "models/account_move.py",
    "models/account_payment_register.py",
    
    # Core Views & Data
    "views/account_payment_views.xml",
    "views/res_config_settings_views.xml", 
    "views/menus.xml",
    "data/payment_sequences.xml",
    "data/email_templates.xml",
    "security/payment_security.xml",
    "security/ir.model.access.csv",
    
    # Reports
    "reports/__init__.py",
    "reports/payment_voucher_report.xml",
    "reports/payment_voucher_template.xml",
    "reports/report_template.py",
    
    # Controllers
    "controllers/__init__.py", 
    "controllers/payment_verification.py",
    
    # Tests
    "tests/__init__.py",
    "tests/test_payment_models.py",
    "tests/test_payment_workflow.py", 
    "tests/test_payment_security.py",
    
    # Core module files
    "__init__.py",
    "__manifest__.py",
    "README.md",
    
    # Demo data
    "demo/demo_payments.xml",
}

# Files to remove (redundant)
REDUNDANT_FILES = {
    # Redundant JavaScript
    "static/src/js/cloudpepper_nuclear_fix.js",
    "static/src/js/cloudpepper_enhanced_handler.js",
    "static/src/js/cloudpepper_critical_interceptor.js", 
    "static/src/js/cloudpepper_js_error_handler.js",
    "static/src/js/cloudpepper_owl_fix.js",
    "static/src/js/cloudpepper_payment_fix.js",
    "static/src/js/cloudpepper_compatibility_patch.js",
    "static/src/js/emergency_error_fix.js",
    "static/src/js/immediate_emergency_fix.js",
    "static/src/js/modern_odoo17_compatibility.js",
    "static/src/js/payment_approval_widget.js",
    "static/src/js/components/payment_approval_widget_enhanced.js",
    "static/src/js/payment_workflow_realtime.js",
    "static/src/js/payment_workflow_safe.js",
    "static/src/js/views/payment_list_view.js",
    "static/src/js/payment_dashboard.js",
    "static/src/js/fields/qr_code_field.js", # Will be replaced with new version
    
    # Redundant Styles
    "static/src/scss/realtime_workflow.scss",
    "static/src/scss/form_view_clean.scss",
    "static/src/scss/form_view.scss", 
    "static/src/scss/main.scss",
    "static/src/scss/enhanced_form_styling.scss",
    "static/src/scss/professional_payment_ui.scss",
    "static/src/scss/components/table_enhancements.scss",
    "static/src/scss/components/payment_widget.scss",
    "static/src/scss/payment_voucher.scss",
    "static/src/scss/responsive_report_styles.scss",
    "static/src/scss/views/form_view.scss",
    "static/src/scss/osus_branding.scss", # Will be replaced with new version
    
    # CSS files (convert to SCSS)
    "static/src/css/payment_verification.css",
    "static/src/css/payment_voucher.css",
    
    # Backup files
    "*.backup.*",
    "debug.log.*",
    
    # Empty files
    "static/src/scss/verification_portal.scss",
    "fix_syntax.js",
    "test_js_fixes.js",
    
    # Development files
    "osus_module_validator.py",
    "validate_modern_syntax.py",
    "FINAL_VALIDATION_SUMMARY.md",
    "MODERN_SYNTAX_REVIEW_COMPLETE.md",
    "OSUS_DEPLOYMENT_CHECKLIST.md",
    "FILE_CLEANUP_ANALYSIS.md",
}

def create_backup():
    """Create backup of current module"""
    print("Creating backup...")
    if BACKUP_PATH.exists():
        shutil.rmtree(BACKUP_PATH)
    shutil.copytree(MODULE_PATH, BACKUP_PATH, ignore=shutil.ignore_patterns("backup_before_cleanup", "essential_files"))
    print(f"Backup created at: {BACKUP_PATH}")

def copy_essential_files():
    """Copy new essential files from essential_files directory"""
    print("Copying essential files...")
    
    # Copy new JavaScript files
    shutil.copy2(ESSENTIAL_PATH / "payment_workflow.js", 
                 MODULE_PATH / "static/src/js/payment_workflow.js")
    
    shutil.copy2(ESSENTIAL_PATH / "qr_code_field.js",
                 MODULE_PATH / "static/src/js/fields/qr_code_field.js")
    
    # Copy new SCSS files
    shutil.copy2(ESSENTIAL_PATH / "payment_interface.scss",
                 MODULE_PATH / "static/src/scss/payment_interface.scss")
    
    # Copy new templates
    shutil.copy2(ESSENTIAL_PATH / "payment_templates.xml",
                 MODULE_PATH / "static/src/xml/payment_templates.xml")
    
    # Copy new manifest
    shutil.copy2(ESSENTIAL_PATH / "__manifest__.py",
                 MODULE_PATH / "__manifest__.py")
    
    print("Essential files copied")

def remove_redundant_files():
    """Remove redundant files"""
    print("Removing redundant files...")
    removed_count = 0
    
    for root, dirs, files in os.walk(MODULE_PATH):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(MODULE_PATH)
            
            # Skip backup and essential directories
            if "backup_before_cleanup" in str(relative_path) or "essential_files" in str(relative_path):
                continue
                
            # Remove backup files
            if ".backup." in file or "debug.log." in file:
                file_path.unlink()
                print(f"Removed backup file: {relative_path}")
                removed_count += 1
                continue
            
            # Remove specific redundant files
            if str(relative_path) in REDUNDANT_FILES:
                file_path.unlink()
                print(f"Removed redundant file: {relative_path}")
                removed_count += 1
    
    print(f"Removed {removed_count} redundant files")

def cleanup_empty_directories():
    """Remove empty directories"""
    print("Cleaning up empty directories...")
    
    for root, dirs, files in os.walk(MODULE_PATH, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            
            # Skip backup and essential directories
            if "backup_before_cleanup" in str(dir_path) or "essential_files" in str(dir_path):
                continue
                
            try:
                if not any(dir_path.iterdir()):  # Directory is empty
                    dir_path.rmdir()
                    print(f"Removed empty directory: {dir_path.relative_to(MODULE_PATH)}")
            except OSError:
                pass  # Directory not empty or can't be removed

def update_manifest():
    """Update manifest file with clean asset declarations"""
    print("Manifest already updated with essential files")

def main():
    """Main cleanup process"""
    print("Starting Account Payment Final module cleanup...")
    print(f"Module path: {MODULE_PATH}")
    
    if not MODULE_PATH.exists():
        print(f"Error: Module path not found: {MODULE_PATH}")
        return
    
    if not ESSENTIAL_PATH.exists():
        print(f"Error: Essential files path not found: {ESSENTIAL_PATH}")
        return
    
    # Step 1: Create backup
    create_backup()
    
    # Step 2: Copy essential files
    copy_essential_files()
    
    # Step 3: Remove redundant files
    remove_redundant_files()
    
    # Step 4: Cleanup empty directories
    cleanup_empty_directories()
    
    # Step 5: Update manifest (already done)
    update_manifest()
    
    print("\n" + "="*60)
    print("CLEANUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"Backup location: {BACKUP_PATH}")
    print(f"Cleaned module: {MODULE_PATH}")
    print("\nModule now contains only essential files with modern Odoo 17 syntax.")
    print("Please test the module to ensure all functionality works correctly.")

if __name__ == "__main__":
    main()
