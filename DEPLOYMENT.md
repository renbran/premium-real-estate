# OSUS Properties - Deployment Guide

## 🚀 Quick Deploy

```powershell
# One command to deploy everything
npm run deploy
```

This will:
1. Clean previous builds
2. Build the project
3. Verify build output
4. Deploy to Cloudflare Pages

---

## 📋 Prerequisites

### 1. Node.js and npm
Make sure you have Node.js installed:
```powershell
node --version  # Should be v14 or higher
npm --version   # Should be v6 or higher
```

### 2. Cloudflare Account
- Sign up at https://dash.cloudflare.com
- Create a Cloudflare Pages project named: `osusrealestatepremium`

### 3. Wrangler CLI Authentication
```powershell
npx wrangler login
```
This will open a browser window to authenticate with Cloudflare.

---

## 🛠️ Available Commands

### Build Commands
```powershell
npm run build       # Build the project
npm run clean       # Clean dist directory
npm run verify      # Verify build output
npm run test        # Build and verify
```

### Deployment Commands
```powershell
npm run deploy              # Full build and deploy
npm run deploy:cloudflare   # Deploy only (no build)
npm run deploy:check        # Check deployment status
```

### Development Commands
```powershell
npm start          # Start local development server (port 8000)
npm run serve      # Same as npm start
npm run monitor    # Monitor Cloudflare deployment
```

---

## 📁 Project Structure

```
premium-real-estate/
├── index.html              # Main website file
├── _redirects              # Cloudflare routing rules
├── build.js                # Build script
├── verify-build.js         # Build verification
├── deploy.ps1              # Deployment script
├── wrangler.toml           # Cloudflare configuration
├── package.json            # Project configuration
├── static/
│   └── media/
│       ├── images/
│       │   ├── osus-logo.png
│       │   ├── properties/    # 6 property images
│       │   └── staff/         # 19 staff photos
│       └── videos/            # Background videos
└── dist/                   # Build output (generated)
    ├── index.html
    ├── _redirects
    └── static/            # Copied from source
```

---

## 🔧 Build Process

The build script (`build.js`) does the following:

1. **Clean**: Removes old `dist/` directory
2. **Create**: Creates fresh `dist/` directory
3. **Copy HTML**: Copies `index.html` to `dist/`
4. **Copy Redirects**: Copies `_redirects` to `dist/`
5. **Copy Assets**: Recursively copies `static/` folder
6. **Verify**: Runs verification to ensure all files are present

### What Gets Built

- ✅ 1 HTML file (index.html)
- ✅ 1 Redirects file (_redirects)
- ✅ 1 Logo image
- ✅ 6 Property images
- ✅ 19 Staff photos
- ✅ 4 Background videos
- ✅ **Total: ~32 files, ~27 MB**

---

## 🌐 Deployment to Cloudflare Pages

### Method 1: Automated Script (Recommended)
```powershell
npm run deploy
```

### Method 2: Manual Deployment
```powershell
# Step 1: Build
npm run build

# Step 2: Verify
npm run verify

# Step 3: Deploy
npx wrangler pages deploy dist --project-name=osusrealestatepremium --branch=main
```

### Method 3: PowerShell Script
```powershell
.\deploy.ps1
```

---

## 🔍 Verifying Deployment

### Check Deployment Status
```powershell
npm run deploy:check
```

### Test URLs

**Production (with custom domain):**
```
https://properties.erposus.com
```

**Preview (Cloudflare subdomain):**
```
https://osusrealestatepremium.pages.dev
```

### What to Check
- ✅ Homepage loads without errors
- ✅ Logo appears in header
- ✅ YouTube video plays in hero section
- ✅ All 6 property images display
- ✅ Staff carousel shows all 19 team members
- ✅ Mobile menu works on small screens
- ✅ Contact form submits (shows alert)
- ✅ All animations work smoothly

---

## 🐛 Troubleshooting

### Build Fails

**Issue**: `index.html not found`
```powershell
# Make sure you're in the project root directory
cd "d:\osusproperties website\premium-real-estate"
```

**Issue**: `static directory not found`
```powershell
# Verify static folder exists
Test-Path static
# Should return: True
```

### Deployment Fails

**Issue**: Not authenticated
```powershell
npx wrangler login
```

**Issue**: Project doesn't exist
1. Go to https://dash.cloudflare.com
2. Navigate to **Workers & Pages** → **Pages**
3. Click **Create a project**
4. Name it: `osusrealestatepremium`

**Issue**: Network timeout
```powershell
# Try deploying again
npm run deploy:cloudflare
```

### Site Not Loading

**Issue**: 404 errors for assets
- Check `_redirects` file is in `dist/`
- Verify file paths use `/static/media/...` (not relative paths)

**Issue**: White screen
- Open browser console (F12) to see errors
- Check if JavaScript/CSS loaded correctly

---

## 📊 Monitoring

### View Deployment Logs
```powershell
npm run monitor
```

### Check Build Output
```powershell
npm run verify
```

### List All Deployments
```powershell
npm run deploy:check
```

---

## 🎯 Custom Domain Setup

If you want to use `properties.erposus.com`:

### Step 1: Add Custom Domain in Cloudflare

1. Go to https://dash.cloudflare.com
2. Navigate to **Workers & Pages** → **Pages**
3. Select your project: `osusrealestatepremium`
4. Go to **Custom domains** tab
5. Click **Set up a custom domain**
6. Enter: `properties.erposus.com`
7. Click **Activate domain**

### Step 2: DNS Configuration

Cloudflare will automatically configure DNS if `erposus.com` is already in your Cloudflare account.

**Manual DNS (if needed):**
```
Type: CNAME
Name: properties
Target: osusrealestatepremium.pages.dev
Proxied: Yes (orange cloud)
```

### Step 3: SSL/TLS

- Cloudflare automatically provisions SSL certificates
- Wait 5-10 minutes for certificate activation
- Your site will be available at: https://properties.erposus.com

---

## 🔄 Update Workflow

When you make changes to the website:

```powershell
# 1. Edit index.html or add/update files in static/

# 2. Test locally (optional)
npm start
# Visit: http://localhost:8000

# 3. Deploy changes
npm run deploy

# 4. Verify live site
# Visit: https://properties.erposus.com
```

---

## 📦 What Gets Deployed

### HTML & Config
- `index.html` (100 KB) - Main website
- `_redirects` - Routing rules

### Images (27 files)
- `osus-logo.png` (108 KB)
- 6 property images (4.6 MB total)
- 19 staff photos (4.2 MB total)

### Videos (4 files)
- Background videos (18.4 MB total)

### Total Package
- **32 files**
- **~27.2 MB**

---

## 🌟 Features

- ✅ Mobile-first responsive design
- ✅ YouTube hero video background
- ✅ Interactive property cards
- ✅ Staff carousel with 19 team members
- ✅ Smooth GSAP animations
- ✅ Particles.js effects
- ✅ Contact form
- ✅ SEO optimized
- ✅ Fast loading via Cloudflare CDN
- ✅ SSL/HTTPS enabled
- ✅ Global content delivery

---

## 📞 Support

### Common Issues

1. **Build fails**: Run `npm install` to install dependencies
2. **Deploy fails**: Run `npx wrangler login` to authenticate
3. **Site not loading**: Check Cloudflare dashboard for deployment status
4. **Images missing**: Verify `static/media/` folder structure

### Getting Help

- Check deployment status: https://dash.cloudflare.com
- View build logs in terminal output
- Run verification: `npm run verify`

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Website loads at production URL
- [ ] Logo displays in header
- [ ] Hero video plays automatically
- [ ] All 6 properties show with images
- [ ] Staff carousel displays all 19 members
- [ ] Mobile menu works on phone/tablet
- [ ] Contact form submits successfully
- [ ] Page scrolling is smooth
- [ ] Animations work properly
- [ ] No console errors in browser

---

**Your premium real estate website is ready to impress clients!** 🏡✨
