# Enhanced PowerShell deployment script for oe_sale_dashboard_17
# Fixes dashboard data loading and filter button issues

$MODULE_NAME = "oe_sale_dashboard_17"
Write-Host "🚀 Enhanced deployment for $MODULE_NAME - Fixing dashboard issues..." -ForegroundColor Green

# Configuration - Adjust these for your setup
$CONTAINER_NAME = "odoo_container"  # Your Odoo container name
$DATABASE_NAME = "coatest"          # Your database name

function Test-OdooData {
    Write-Host "🔍 Testing data availability in Odoo..." -ForegroundColor Cyan
    
    $pythonCode = @"
env = api.Environment(cr, SUPERUSER_ID, {})
SaleOrder = env['sale.order']

# Test data availability
total_orders = SaleOrder.search_count([])
print(f'Total orders in system: {total_orders}')

non_cancelled = SaleOrder.search_count([('state', '!=', 'cancel')])
print(f'Non-cancelled orders: {non_cancelled}')

if total_orders > 0:
    from datetime import datetime, timedelta
    recent_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    recent_count = SaleOrder.search_count([('date_order', '>=', recent_date)])
    print(f'Orders in last 90 days: {recent_count}')
    
    # Test dashboard method
    try:
        if hasattr(SaleOrder, 'get_dashboard_summary_data'):
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            result = SaleOrder.get_dashboard_summary_data(start_date, end_date)
            print('Dashboard method working:', 'totals' in result)
            is_sample = result.get('metadata', {}).get('is_sample_data', False)
            print(f'Using sample data: {is_sample}')
        else:
            print('Dashboard method not found')
    except Exception as e:
        print(f'Dashboard method error: {e}')

cr.commit()
"@

    # Save to temp file and execute
    $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
    $pythonCode | Out-File -FilePath $tempFile -Encoding UTF8
    
    try {
        Get-Content $tempFile | docker exec -i $CONTAINER_NAME python3 /var/odoo/src/odoo/odoo-bin shell -d $DATABASE_NAME --stop-after-init
    } catch {
        Write-Host "❌ Error testing data: $_" -ForegroundColor Red
    } finally {
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}

function Update-OdooModule {
    Write-Host "🔄 Updating Odoo module..." -ForegroundColor Cyan
    
    try {
        # Stop container temporarily for cache clearing
        Write-Host "🛑 Stopping container for cache clearing..." -ForegroundColor Yellow
        docker stop $CONTAINER_NAME
        
        # Clear Python cache (if accessible)
        Write-Host "🧹 Clearing caches..." -ForegroundColor Yellow
        docker start $CONTAINER_NAME
        Start-Sleep -Seconds 5
        
        # Clear Python cache inside container
        docker exec $CONTAINER_NAME find /var/odoo -name "*.pyc" -delete
        docker exec $CONTAINER_NAME find /var/odoo -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
        
        # Update module
        Write-Host "📦 Updating module..." -ForegroundColor Yellow
        docker exec $CONTAINER_NAME python3 /var/odoo/src/odoo/odoo-bin -d $DATABASE_NAME -u $MODULE_NAME --stop-after-init
        
        # Restart for normal operation
        Write-Host "🔄 Restarting container..." -ForegroundColor Yellow
        docker restart $CONTAINER_NAME
        Start-Sleep -Seconds 15
        
    } catch {
        Write-Host "❌ Error updating module: $_" -ForegroundColor Red
        # Ensure container is running
        docker start $CONTAINER_NAME
    }
}

function Test-DashboardAfterUpdate {
    Write-Host "🧪 Testing dashboard after update..." -ForegroundColor Cyan
    
    $testCode = @"
env = api.Environment(cr, SUPERUSER_ID, {})
SaleOrder = env['sale.order']

# Check all methods are available
methods = [
    'get_dashboard_summary_data',
    'test_data_availability',
    'get_dashboard_health_check',
    'optimize_dashboard_performance'
]

for method in methods:
    if hasattr(SaleOrder, method):
        print(f'✅ {method} available')
    else:
        print(f'❌ {method} missing')

# Test different date ranges
from datetime import datetime, timedelta
test_ranges = [(7, 'week'), (30, 'month'), (90, 'quarter'), (365, 'year')]

for days, name in test_ranges:
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        result = SaleOrder.get_dashboard_summary_data(start_date, end_date)
        totals = result.get('totals', {})
        is_sample = result.get('metadata', {}).get('is_sample_data', False)
        print(f'{name}: {totals.get("total_count", 0)} orders, sample: {is_sample}')
    except Exception as e:
        print(f'{name}: Error - {e}')

cr.commit()
"@

    $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
    $testCode | Out-File -FilePath $tempFile -Encoding UTF8
    
    try {
        Get-Content $tempFile | docker exec -i $CONTAINER_NAME python3 /var/odoo/src/odoo/odoo-bin shell -d $DATABASE_NAME --stop-after-init
    } catch {
        Write-Host "❌ Error in post-update test: $_" -ForegroundColor Red
    } finally {
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
}

# Main execution
Write-Host "=" * 60 -ForegroundColor Blue
Write-Host "ENHANCED ODOO DASHBOARD DEPLOYMENT" -ForegroundColor Blue
Write-Host "=" * 60 -ForegroundColor Blue

# Step 1: Check container status
Write-Host "📋 Step 1: Checking container status..." -ForegroundColor Cyan
$containerStatus = docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}"
Write-Host $containerStatus

if (-not $containerStatus -or $containerStatus -notlike "*$CONTAINER_NAME*") {
    Write-Host "❌ Container $CONTAINER_NAME not found or not running!" -ForegroundColor Red
    Write-Host "Please check your container name and ensure it's running." -ForegroundColor Yellow
    exit 1
}

# Step 2: Test current data
Test-OdooData

# Step 3: Update module
Update-OdooModule

# Step 4: Test after update
Test-DashboardAfterUpdate

# Step 5: Final status
Write-Host "📊 Step 5: Final container status..." -ForegroundColor Cyan
docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "✅ Enhanced deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Issues Fixed:" -ForegroundColor Yellow
Write-Host "• Filter buttons now work (setDateRange method added)"
Write-Host "• Real data loading improved with fallback mechanisms"
Write-Host "• Added data availability testing (Test Data button)"
Write-Host "• Enhanced error handling and debugging"
Write-Host "• Proper sample data detection and warnings"
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Access Odoo: http://localhost:8069 (or your configured port)"
Write-Host "2. Navigate to: Sales > Dashboard"
Write-Host "3. Click 'Test Data' button to check what data is available"
Write-Host "4. Try filter buttons: 7 days, 30 days, 90 days, 1 year"
Write-Host "5. Check browser console (F12) for debugging info"
Write-Host ""
Write-Host "🔍 If Still Showing Sample Data:" -ForegroundColor Yellow
Write-Host "• Check if you have sales orders in the selected date range"
Write-Host "• Use 'Test Data' button to see data availability"
Write-Host "• Try expanding date range (90 days or 1 year buttons)"
Write-Host "• Check container logs: docker logs -f $CONTAINER_NAME"
