#!/usr/bin/env python3
"""
SCHOLARIX Custom Reports PDF Module Installation Script
This script helps install the custom_reports_pdf module in Odoo 18
"""

import os
import sys
import shutil
from pathlib import Path

def install_module():
    """Install the custom_reports_pdf module"""
    print("=" * 60)
    print("SCHOLARIX Custom Reports PDF Module Installation")
    print("=" * 60)
    
    # Get the current module directory
    current_dir = Path(__file__).parent.absolute()
    module_name = "custom_reports_pdf"
    
    print(f"Module directory: {current_dir}")
    print(f"Module name: {module_name}")
    
    # Check if this is the correct module directory
    manifest_file = current_dir / "__manifest__.py"
    if not manifest_file.exists():
        print("❌ Error: __manifest__.py not found in current directory")
        print("Please run this script from the custom_reports_pdf module directory")
        return False
    
    print("✅ Module manifest found")
    
    # Check required files
    required_files = [
        "models/__init__.py",
        "models/account_move.py",
        "models/sale_order.py", 
        "models/report_models.py",
        "controllers/__init__.py",
        "controllers/main.py",
        "reports/report_actions.xml",
        "reports/report_invoice_templates.xml",
        "reports/report_sale_templates.xml",
        "reports/report_styles.xml",
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/sale_order_views.xml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (current_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files present")
    
    # Instructions for manual installation
    print("\n" + "=" * 60)
    print("INSTALLATION INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. Copy Module to Addons Directory:")
    print(f"   Copy the entire '{module_name}' folder to your Odoo addons directory")
    print("   Example locations:")
    print("   - /opt/odoo/addons/")
    print("   - /usr/lib/python3/dist-packages/odoo/addons/")
    print("   - Your custom addons path")
    
    print("\n2. Update Addons List:")
    print("   - Go to Settings > Apps")
    print("   - Click 'Update Apps List'")
    print("   - Search for 'SCHOLARIX Custom Reports PDF'")
    
    print("\n3. Install Module:")
    print("   - Find the module in the apps list")
    print("   - Click 'Install'")
    
    print("\n4. Verify Installation:")
    print("   - Go to Invoicing > Invoices")
    print("   - Open any invoice")
    print("   - Look for 'Print SCHOLARIX Invoice' button")
    print("   - Go to Sales > Quotations")
    print("   - Open any quotation")
    print("   - Look for 'Print SCHOLARIX Quotation' button")
    
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING")
    print("=" * 60)
    
    print("\nIf you encounter issues:")
    print("1. Check Odoo logs for error messages")
    print("2. Ensure all dependencies are installed (base, account, sale, web)")
    print("3. Restart Odoo server after copying the module")
    print("4. Update apps list before attempting installation")
    print("5. Check file permissions (ensure Odoo can read the files)")
    
    print("\n✅ Module is ready for installation!")
    print("Follow the instructions above to complete the installation.")
    
    return True

if __name__ == "__main__":
    try:
        install_module()
    except Exception as e:
        print(f"❌ Installation script error: {e}")
        sys.exit(1)