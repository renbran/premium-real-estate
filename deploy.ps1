# OSUS Properties Deployment Script

Write-Host 'Deployment Starting...' -ForegroundColor Cyan
Write-Host ''

# Build
Write-Host 'Building project...' -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host 'Build failed!' -ForegroundColor Red
    exit 1
}

Write-Host 'Build complete!' -ForegroundColor Green
Write-Host ''

# Deploy
Write-Host 'Deploying to Cloudflare Pages...' -ForegroundColor Yellow
npx wrangler pages deploy dist --project-name=osusrealestatepremium --branch=main

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host 'Deployment failed!' -ForegroundColor Red
    Write-Host 'Run: npx wrangler login' -ForegroundColor Yellow
    exit 1
}

Write-Host ''
Write-Host 'Deployment Complete!' -ForegroundColor Green
Write-Host 'Live at: https://properties.erposus.com' -ForegroundColor Cyan
Write-Host 'Monitor: npm run monitor' -ForegroundColor Cyan
Write-Host ''
