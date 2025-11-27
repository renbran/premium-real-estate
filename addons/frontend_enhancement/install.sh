#!/bin/bash

# Frontend Enhancement Module Installation Script
# For Odoo 17 - OSUS Properties

echo "=========================================="
echo "Frontend Enhancement Module Installation"
echo "=========================================="

# Check if running as admin
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as administrator/root"
    exit 1
fi

# Set variables
ODOO_ADDONS_PATH="/opt/odoo/addons"
MODULE_NAME="frontend_enhancement"
BACKUP_DIR="/opt/odoo/backups"

echo "Starting installation..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if Odoo is running
if pgrep -x "odoo" > /dev/null; then
    echo "WARNING: Odoo is currently running. Consider stopping it before installation."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

# Check if module already exists
if [ -d "$ODOO_ADDONS_PATH/$MODULE_NAME" ]; then
    echo "Module already exists. Creating backup..."
    cp -r "$ODOO_ADDONS_PATH/$MODULE_NAME" "$BACKUP_DIR/${MODULE_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
    echo "Backup created."
fi

# Copy module files
echo "Copying module files..."
cp -r "./$MODULE_NAME" "$ODOO_ADDONS_PATH/"

# Set proper permissions
echo "Setting permissions..."
chown -R odoo:odoo "$ODOO_ADDONS_PATH/$MODULE_NAME"
chmod -R 755 "$ODOO_ADDONS_PATH/$MODULE_NAME"

# Install Python dependencies if requirements.txt exists
if [ -f "$ODOO_ADDONS_PATH/$MODULE_NAME/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r "$ODOO_ADDONS_PATH/$MODULE_NAME/requirements.txt"
fi

# Restart Odoo if it's running
if pgrep -x "odoo" > /dev/null; then
    echo "Restarting Odoo service..."
    systemctl restart odoo || service odoo restart
fi

echo "=========================================="
echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Go to Odoo Apps menu"
echo "2. Click 'Update Apps List'"
echo "3. Search for 'Frontend Enhancement'"
echo "4. Click 'Install'"
echo ""
echo "For support: support@osusproperties.com"
echo "=========================================="
