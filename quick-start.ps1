# ====================================================
# OSUS Properties - Quick Deployment Script
# ====================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     OSUS Properties - Quick Deploy             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "📍 Project location: $scriptPath" -ForegroundColor Gray
Write-Host ""

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "   ✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Node.js not found!" -ForegroundColor Red
    Write-Host "   Please install Node.js from: https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Host "   ✓ npm: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ npm not found!" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host ""
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ✗ Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✓ Dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Ask what to do
Write-Host ""
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [1] 🔨 Build only" -ForegroundColor White
Write-Host "  [2] 🧪 Build and test" -ForegroundColor White
Write-Host "  [3] 🚀 Build and deploy to Cloudflare" -ForegroundColor White
Write-Host "  [4] 🌐 Start local server" -ForegroundColor White
Write-Host "  [5] 📊 Check deployment status" -ForegroundColor White
Write-Host "  [0] ❌ Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-5 or 0)"

Write-Host ""

switch ($choice) {
    "1" {
        Write-Host "🔨 Building project..." -ForegroundColor Yellow
        npm run build
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Build complete!" -ForegroundColor Green
            Write-Host "   Output directory: dist/" -ForegroundColor Gray
        }
    }
    "2" {
        Write-Host "🧪 Building and testing..." -ForegroundColor Yellow
        npm run test
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Build and verification complete!" -ForegroundColor Green
        }
    }
    "3" {
        Write-Host "🚀 Deploying to Cloudflare Pages..." -ForegroundColor Yellow
        Write-Host ""
        
        # Check if logged in to Wrangler
        Write-Host "🔐 Checking authentication..." -ForegroundColor Yellow
        $wranglerCheck = npx wrangler whoami 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "⚠️  Not logged in to Cloudflare!" -ForegroundColor Yellow
            Write-Host ""
            $login = Read-Host "Would you like to login now? (y/n)"
            if ($login -eq "y" -or $login -eq "Y") {
                npx wrangler login
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "Login failed!" -ForegroundColor Red
                    exit 1
                }
            } else {
                Write-Host "Deployment cancelled." -ForegroundColor Yellow
                exit 0
            }
        } else {
            Write-Host "   ✓ Authenticated" -ForegroundColor Green
        }
        
        Write-Host ""
        npm run deploy
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Green
            Write-Host "║          🎉 Deployment Successful!            ║" -ForegroundColor Green
            Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green
            Write-Host ""
            Write-Host "Your website is now live at:" -ForegroundColor Cyan
            Write-Host "  https://properties.erposus.com" -ForegroundColor White
            Write-Host ""
        }
    }
    "4" {
        Write-Host "🌐 Starting local development server..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Server will be available at:" -ForegroundColor Cyan
        Write-Host "  http://localhost:8000" -ForegroundColor White
        Write-Host ""
        Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
        Write-Host ""
        npm start
    }
    "5" {
        Write-Host "📊 Checking deployment status..." -ForegroundColor Yellow
        Write-Host ""
        npm run deploy:check
    }
    "0" {
        Write-Host "👋 Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
