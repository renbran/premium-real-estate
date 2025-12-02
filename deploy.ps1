# OSUS Properties Deployment Script
# Enhanced with error handling and verification

$ErrorActionPreference = "Stop"

Write-Host ''
Write-Host '═══════════════════════════════════════════════' -ForegroundColor Cyan
Write-Host '   OSUS Properties - Deployment Script' -ForegroundColor Cyan
Write-Host '═══════════════════════════════════════════════' -ForegroundColor Cyan
Write-Host ''

# Check if we're in the right directory
if (-not (Test-Path "index.html")) {
    Write-Host '❌ Error: index.html not found!' -ForegroundColor Red
    Write-Host '   Please run this script from the project root directory.' -ForegroundColor Yellow
    exit 1
}

# Clean previous build
Write-Host '🗑️  Cleaning previous build...' -ForegroundColor Yellow
npm run clean 2>$null
Write-Host '✓ Cleaned' -ForegroundColor Green
Write-Host ''

# Build
Write-Host '🔨 Building project...' -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host '❌ Build failed!' -ForegroundColor Red
    Write-Host '   Check the error messages above.' -ForegroundColor Yellow
    exit 1
}

Write-Host '✓ Build complete!' -ForegroundColor Green
Write-Host ''

# Verify build output
Write-Host '🔍 Verifying build output...' -ForegroundColor Yellow
if (-not (Test-Path "dist/index.html")) {
    Write-Host '❌ Error: dist/index.html not found after build!' -ForegroundColor Red
    exit 1
}

$distFiles = (Get-ChildItem -Path dist -Recurse -File).Count
Write-Host "✓ Found $distFiles files in dist/" -ForegroundColor Green
Write-Host ''

# Check Wrangler authentication
Write-Host '🔐 Checking Cloudflare authentication...' -ForegroundColor Yellow
$wranglerCheck = npx wrangler whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host '❌ Not logged in to Cloudflare!' -ForegroundColor Red
    Write-Host ''
    Write-Host 'Please run the following command first:' -ForegroundColor Yellow
    Write-Host '  npx wrangler login' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Then run this deployment script again.' -ForegroundColor Yellow
    exit 1
}
Write-Host '✓ Authenticated' -ForegroundColor Green
Write-Host ''

# Deploy
Write-Host '🚀 Deploying to Cloudflare Pages...' -ForegroundColor Yellow
Write-Host '   Project: osusrealestatepremium' -ForegroundColor Gray
Write-Host '   Branch: main' -ForegroundColor Gray
Write-Host ''

npx wrangler pages deploy dist --project-name=osusrealestatepremium --branch=main

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host '❌ Deployment failed!' -ForegroundColor Red
    Write-Host ''
    Write-Host 'Common issues:' -ForegroundColor Yellow
    Write-Host '  1. Not logged in - Run: npx wrangler login' -ForegroundColor Gray
    Write-Host '  2. Project does not exist - Create it in Cloudflare dashboard' -ForegroundColor Gray
    Write-Host '  3. Network issues - Check your internet connection' -ForegroundColor Gray
    Write-Host ''
    exit 1
}

Write-Host ''
Write-Host '═══════════════════════════════════════════════' -ForegroundColor Green
Write-Host '   ✅ Deployment Successful!' -ForegroundColor Green
Write-Host '═══════════════════════════════════════════════' -ForegroundColor Green
Write-Host ''
Write-Host '🌐 Your website is now live!' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Production URL:' -ForegroundColor White
Write-Host '  https://properties.erposus.com' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Preview URL:' -ForegroundColor White
Write-Host '  https://osusrealestatepremium.pages.dev' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next steps:' -ForegroundColor Yellow
Write-Host '  • Test your site at the URLs above' -ForegroundColor Gray
Write-Host '  • Check deployment status: npm run deploy:check' -ForegroundColor Gray
Write-Host '  • Monitor performance: npm run monitor' -ForegroundColor Gray
Write-Host ''
