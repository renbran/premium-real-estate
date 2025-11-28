#!/bin/bash

# Production deployment script for oe_sale_dashboard_17
# This script ensures proper module deployment with cache clearing

MODULE_NAME="oe_sale_dashboard_17"
ODOO_PATH="/var/odoo/coatest"
DB_NAME="coatest"

echo "🚀 Starting deployment of $MODULE_NAME..."

# Function to execute Odoo commands
execute_odoo_cmd() {
    local cmd="$1"
    echo "📋 Executing: $cmd"
    cd "$ODOO_PATH"
    sudo -u odoo python3 src/odoo/odoo-bin "$cmd" || {
        echo "❌ Command failed: $cmd"
        return 1
    }
}

# Step 1: Stop Odoo service
echo "🛑 Stopping Odoo service..."
sudo systemctl stop odoo || echo "⚠️ Odoo service not running"

# Step 2: Clear Python cache
echo "🧹 Clearing Python cache..."
find "$ODOO_PATH" -name "*.pyc" -delete
find "$ODOO_PATH" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Step 3: Update module list
echo "📦 Updating module list..."
execute_odoo_cmd "-d $DB_NAME --update-list --stop-after-init"

# Step 4: Upgrade module if already installed
echo "🔄 Upgrading module..."
execute_odoo_cmd "-d $DB_NAME -u $MODULE_NAME --stop-after-init"

# Step 5: Install module if not installed
echo "📥 Installing module (if needed)..."
execute_odoo_cmd "-d $DB_NAME -i $MODULE_NAME --stop-after-init"

# Step 6: Clear browser cache (optional)
echo "🌐 Clearing web assets cache..."
execute_odoo_cmd "-d $DB_NAME --dev=all --stop-after-init"

# Step 7: Start Odoo service
echo "▶️ Starting Odoo service..."
sudo systemctl start odoo

# Step 8: Wait for service to be ready
echo "⏳ Waiting for Odoo to start..."
sleep 10

# Step 9: Check service status
echo "🔍 Checking service status..."
sudo systemctl status odoo --no-pager

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Check Odoo logs: sudo journalctl -u odoo -f"
echo "2. Access dashboard: [Your Odoo URL]/web#action=oe_sale_dashboard_17.action_sale_dashboard"
echo "3. If issues persist, check module dependencies and database integrity"
