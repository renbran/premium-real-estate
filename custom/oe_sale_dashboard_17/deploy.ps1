# PowerShell deployment script for oe_sale_dashboard_17 on Windows
# For use with Docker-based Odoo installations

$MODULE_NAME = "oe_sale_dashboard_17"
$CONTAINER_NAME = "odoo_container"  # Adjust based on your container name

Write-Host "🚀 Starting deployment of $MODULE_NAME..." -ForegroundColor Green

# Function to execute Docker commands
function Execute-DockerOdoo {
    param($Command)
    Write-Host "📋 Executing: $Command" -ForegroundColor Yellow
    docker exec -it $CONTAINER_NAME $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Command failed: $Command" -ForegroundColor Red
        return $false
    }
    return $true
}

# Step 1: Stop Odoo container (if needed)
Write-Host "🛑 Checking container status..." -ForegroundColor Cyan
docker ps | Select-String $CONTAINER_NAME

# Step 2: Clear Python cache inside container
Write-Host "🧹 Clearing Python cache..." -ForegroundColor Cyan
Execute-DockerOdoo "find /var/odoo -name '*.pyc' -delete"
Execute-DockerOdoo "find /var/odoo -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"

# Step 3: Update module list
Write-Host "📦 Updating module list..." -ForegroundColor Cyan
Execute-DockerOdoo "python3 /var/odoo/src/odoo/odoo-bin -d coatest --update-list --stop-after-init"

# Step 4: Upgrade module
Write-Host "🔄 Upgrading module..." -ForegroundColor Cyan
Execute-DockerOdoo "python3 /var/odoo/src/odoo/odoo-bin -d coatest -u $MODULE_NAME --stop-after-init"

# Step 5: Clear assets cache
Write-Host "🌐 Clearing web assets cache..." -ForegroundColor Cyan
Execute-DockerOdoo "python3 /var/odoo/src/odoo/odoo-bin -d coatest --dev=all --stop-after-init"

# Step 6: Restart container (if needed)
Write-Host "🔄 Restarting container..." -ForegroundColor Cyan
docker restart $CONTAINER_NAME

# Wait for container to be ready
Write-Host "⏳ Waiting for container to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Check container status
Write-Host "🔍 Checking container status..." -ForegroundColor Cyan
docker ps | Select-String $CONTAINER_NAME

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Check container logs: docker logs -f $CONTAINER_NAME"
Write-Host "2. Access Odoo: http://localhost:8069"
Write-Host "3. Navigate to Sales > Dashboard"
Write-Host "4. If issues persist, check the XML validation and module dependencies"
