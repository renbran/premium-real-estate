#!/bin/bash

# Enhanced deployment script for oe_sale_dashboard_17
# This script fixes the dashboard issues and ensures proper deployment

MODULE_NAME="oe_sale_dashboard_17"
echo "🚀 Enhanced deployment for $MODULE_NAME - Fixing dashboard data and filter issues..."

# Function to execute Odoo shell commands
execute_odoo_shell() {
    local python_code="$1"
    echo "📋 Executing Python code in Odoo shell..."
    python3 /var/odoo/coatest/src/odoo/odoo-bin shell -d coatest --stop-after-init << EOF
$python_code
EOF
}

# Step 1: Check data availability
echo "🔍 Step 1: Checking data availability..."
execute_odoo_shell "
env = api.Environment(cr, SUPERUSER_ID, {})
SaleOrder = env['sale.order']

# Test the new method
if hasattr(SaleOrder, 'test_data_availability'):
    result = SaleOrder.test_data_availability()
    print('Data availability test result:', result)
else:
    print('test_data_availability method not found')

# Manual check
total_orders = SaleOrder.search_count([])
print(f'Total orders in system: {total_orders}')

non_cancelled = SaleOrder.search_count([('state', '!=', 'cancel')])  
print(f'Non-cancelled orders: {non_cancelled}')

if total_orders > 0:
    # Check recent orders
    from datetime import datetime, timedelta
    recent_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_count = SaleOrder.search_count([('date_order', '>=', recent_date)])
    print(f'Orders in last 30 days: {recent_count}')
    
    # Check states
    states = SaleOrder.read_group([], ['state'], ['state'])
    print('States distribution:', {s['state']: s['state_count'] for s in states})

cr.commit()
"

# Step 2: Test dashboard method
echo "🧪 Step 2: Testing dashboard method..."
execute_odoo_shell "
env = api.Environment(cr, SUPERUSER_ID, {})
SaleOrder = env['sale.order']

from datetime import datetime, timedelta

# Test with last 90 days
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

print(f'Testing dashboard for date range: {start_date} to {end_date}')

try:
    if hasattr(SaleOrder, 'get_dashboard_summary_data'):
        result = SaleOrder.get_dashboard_summary_data(start_date, end_date)
        print('Dashboard method result:')
        print('- Totals:', result.get('totals', {}))
        print('- Metadata:', result.get('metadata', {}))
        print('- Categories count:', len(result.get('categories', {})))
    else:
        print('get_dashboard_summary_data method not found')
except Exception as e:
    print(f'Error testing dashboard method: {e}')

cr.commit()
"

# Step 3: Clear caches and restart
echo "🧹 Step 3: Clearing caches..."
systemctl stop odoo

# Clear Python cache
find /var/odoo -name "*.pyc" -delete
find /var/odoo -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Step 4: Upgrade module
echo "🔄 Step 4: Upgrading module..."
python3 /var/odoo/coatest/src/odoo/odoo-bin -d coatest -u $MODULE_NAME --stop-after-init

# Step 5: Test after upgrade
echo "🎯 Step 5: Testing after upgrade..."
execute_odoo_shell "
env = api.Environment(cr, SUPERUSER_ID, {})
SaleOrder = env['sale.order']

# Check if all methods are available
methods_to_check = [
    'get_dashboard_summary_data',
    'test_data_availability', 
    'get_dashboard_health_check',
    'optimize_dashboard_performance',
    'clear_dashboard_cache'
]

for method in methods_to_check:
    if hasattr(SaleOrder, method):
        print(f'✅ Method {method} is available')
    else:
        print(f'❌ Method {method} is missing')

# Test the dashboard with various date ranges
test_ranges = [
    ('Last 7 days', 7),
    ('Last 30 days', 30), 
    ('Last 90 days', 90),
    ('Last year', 365)
]

from datetime import datetime, timedelta

for name, days in test_ranges:
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    try:
        result = SaleOrder.get_dashboard_summary_data(start_date, end_date)
        totals = result.get('totals', {})
        is_sample = result.get('metadata', {}).get('is_sample_data', False)
        
        print(f'{name}: {totals.get(\"total_count\", 0)} orders, Sample: {is_sample}')
    except Exception as e:
        print(f'{name}: Error - {e}')

cr.commit()
"

# Step 6: Start Odoo
echo "▶️ Step 6: Starting Odoo..."
systemctl start odoo

# Wait for startup
sleep 10

# Step 7: Final status check
echo "📊 Step 7: Final status check..."
systemctl status odoo --no-pager

echo ""
echo "✅ Enhanced deployment completed!"
echo ""
echo "🔧 Fixes Applied:"
echo "• Added missing JavaScript methods: setDateRange, refreshDashboard, exportDashboardData"
echo "• Enhanced backend error handling and data detection"
echo "• Added test_data_availability method for debugging"
echo "• Improved date range validation and fallback mechanisms"
echo "• Added proper sample data detection and warnings"
echo ""
echo "📋 Next Steps:"
echo "1. Access dashboard: [Your Odoo URL]/web#action=oe_sale_dashboard_17.action_sale_dashboard"
echo "2. Click 'Test Data' button to check data availability"
echo "3. Use date filter buttons (7 days, 30 days, 90 days, 1 year)"
echo "4. Check browser console for debugging information"
echo ""
echo "🔍 Troubleshooting:"
echo "• If still showing sample data, check date ranges"
echo "• Use 'Test Data' button to see what's available"
echo "• Check logs: sudo journalctl -u odoo -f"
