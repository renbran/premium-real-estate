# Custom Domain Setup for properties.erposus.com

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   Custom Domain Setup - properties.erposus.com" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$projectName = "osusrealestatepremium"
$customDomain = "properties.erposus.com"

# Check authentication
Write-Host "🔐 Checking Cloudflare authentication..." -ForegroundColor Yellow
$wranglerCheck = npx wrangler whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Not logged in to Cloudflare!" -ForegroundColor Red
    Write-Host "Please run: npx wrangler login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Authenticated" -ForegroundColor Green
Write-Host ""

# Display manual setup instructions
Write-Host "Custom Domain: $customDomain" -ForegroundColor Cyan
Write-Host "Project: $projectName" -ForegroundColor Cyan
Write-Host ""
Write-Host "Custom domains must be added via Cloudflare Dashboard" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Gray
Write-Host "Step-by-Step Instructions:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Gray
Write-Host ""
Write-Host "[1] Open Cloudflare Dashboard" -ForegroundColor White
Write-Host "    https://dash.cloudflare.com" -ForegroundColor Gray
Write-Host ""
Write-Host "[2] Navigate to Pages Project" -ForegroundColor White
Write-Host "    Workers and Pages -> Pages -> $projectName" -ForegroundColor Gray
Write-Host ""
Write-Host "[3] Go to Custom Domains Tab" -ForegroundColor White
Write-Host "    Click the Custom domains tab" -ForegroundColor Gray
Write-Host ""
Write-Host "[4] Add Your Domain" -ForegroundColor White
Write-Host "    Click: Set up a custom domain" -ForegroundColor Gray
Write-Host "    Enter: $customDomain" -ForegroundColor Gray
Write-Host "    Click: Activate domain" -ForegroundColor Gray
Write-Host ""
Write-Host "[5] DNS Configuration (Automatic)" -ForegroundColor White
Write-Host "    Cloudflare will automatically:" -ForegroundColor Gray
Write-Host "    - Create CNAME record: properties -> $projectName.pages.dev" -ForegroundColor Gray
Write-Host "    - Enable Cloudflare proxy" -ForegroundColor Gray
Write-Host "    - Provision SSL certificate" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================" -ForegroundColor Gray
Write-Host ""

# Check current domains
Write-Host "📋 Checking current project domains..." -ForegroundColor Yellow
Write-Host ""
npx wrangler pages project list | Select-String -Pattern $projectName

Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Wait 5-10 minutes for SSL certificate" -ForegroundColor White
Write-Host "2. Test your site: https://$customDomain" -ForegroundColor White
Write-Host "3. Deploy latest changes: npm run deploy" -ForegroundColor White
Write-Host ""
Write-Host "📊 Monitor deployment:" -ForegroundColor Yellow
Write-Host "   npm run deploy:check" -ForegroundColor Gray
Write-Host ""
