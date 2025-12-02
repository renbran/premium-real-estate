# Custom Domain Setup - properties.erposus.com

## 🌐 Domain Configuration for Cloudflare Pages

Your website needs to be accessible at: **https://properties.erposus.com**

---

## 🚀 Quick Setup

### Option 1: Automated Script
```powershell
npm run domain:setup
```
This will show you step-by-step instructions.

### Option 2: Manual Setup (Recommended)
Follow the detailed instructions below.

---

## 📋 Step-by-Step Setup (5 minutes)

### Step 1: Open Cloudflare Dashboard

1. Go to: **https://dash.cloudflare.com**
2. Log in with your Cloudflare account
3. Select your account (if you have multiple)

### Step 2: Navigate to Your Pages Project

1. In the left sidebar, click **Workers & Pages**
2. Click the **Pages** tab at the top
3. Find and click on: **osusrealestatepremium**
   - This is your website's project name

### Step 3: Access Custom Domains

1. On the project page, look for tabs near the top
2. Click the **Custom domains** tab
3. You'll see a list of current domains (if any)

### Step 4: Add Your Custom Domain

1. Click the **Set up a custom domain** button
2. In the popup/form, enter: `properties.erposus.com`
3. Click **Continue** or **Activate domain**

### Step 5: DNS Configuration (Automatic)

Cloudflare will automatically:

✅ **Create DNS Record**
- Type: CNAME
- Name: `properties`
- Target: `osusrealestatepremium.pages.dev`
- Proxied: Yes (orange cloud icon)

✅ **Provision SSL Certificate**
- Free SSL/TLS certificate
- Takes 5-10 minutes to activate
- Your site will be available at: https://properties.erposus.com

### Step 6: Verify Setup

After 5-10 minutes:

1. Visit: **https://properties.erposus.com**
2. Check that the site loads correctly
3. Verify SSL certificate (padlock icon in browser)

---

## 🔍 Verification Checklist

After setup, verify:

- [ ] Domain shows in Cloudflare Pages custom domains list
- [ ] DNS record exists in Cloudflare DNS settings
- [ ] SSL certificate is active (green padlock)
- [ ] Website loads at https://properties.erposus.com
- [ ] Redirects from http:// to https:// work
- [ ] All assets (images, videos) load correctly

---

## 🌐 DNS Settings (Reference)

If you need to check DNS manually:

**Go to:** Cloudflare Dashboard → Domains → erposus.com → DNS → Records

**Expected Record:**
```
Type: CNAME
Name: properties
Target: osusrealestatepremium.pages.dev
Proxy status: Proxied (orange cloud)
TTL: Auto
```

---

## 📊 Current Configuration

**Project Name:** `osusrealestatepremium`
**Target Domain:** `properties.erposus.com`
**Preview Domain:** `osusrealestatepremium.pages.dev`

**Repository:** renbran/premium-real-estate
**Branch:** main
**Build Output:** dist/

---

## 🔧 Troubleshooting

### Issue: Domain not showing up

**Solution:**
1. Make sure `erposus.com` is added to your Cloudflare account
2. Go to: Cloudflare Dashboard → Websites
3. Verify `erposus.com` is listed
4. If not, add it by clicking **Add a site**

### Issue: SSL Certificate not activating

**Solution:**
1. Wait 10-15 minutes (can take longer)
2. Check SSL/TLS settings: Cloudflare Dashboard → erposus.com → SSL/TLS
3. Make sure encryption mode is set to: **Full** or **Full (strict)**

### Issue: DNS not resolving

**Solution:**
1. Check DNS settings: Cloudflare Dashboard → erposus.com → DNS
2. Verify CNAME record exists for `properties`
3. Make sure proxy is enabled (orange cloud)
4. Wait for DNS propagation (up to 24 hours, usually 5-10 minutes)

### Issue: 404 or white screen

**Solution:**
1. Deploy your site first: `npm run deploy`
2. Verify deployment succeeded: `npm run deploy:check`
3. Check the latest deployment in Cloudflare dashboard

---

## 🚀 After Domain Setup

Once your domain is configured:

### 1. Deploy Your Site
```powershell
npm run deploy
```

### 2. Test Your URLs

**Primary Domain:**
```
https://properties.erposus.com
```

**Preview Domain (still works):**
```
https://osusrealestatepremium.pages.dev
```

### 3. Update Links

Make sure all your marketing materials and links use:
- https://properties.erposus.com

---

## 📱 Testing Custom Domain

### Browser Test
1. Open: https://properties.erposus.com
2. Check for SSL (green padlock)
3. Verify all images load
4. Test on mobile and desktop

### Command Line Test
```powershell
# Check DNS resolution
nslookup properties.erposus.com

# Check HTTP/HTTPS
curl -I https://properties.erposus.com
```

---

## 🎯 Multiple Domains (Optional)

You can add multiple domains to the same project:

**Primary:**
- properties.erposus.com

**Additional (if needed):**
- www.properties.erposus.com
- realtor.erposus.com
- homes.erposus.com

Add each one separately in the Custom domains tab.

---

## 📧 Email & Subdomains

**Note:** Custom domains for Pages only affect your website, not email.

If you need email for your domain:
1. Use Cloudflare Email Routing
2. Or configure MX records separately
3. Email setup is independent of Pages setup

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Custom domain appears in Cloudflare Pages dashboard
2. ✅ Green "Active" status next to domain
3. ✅ SSL certificate shows as "Active"
4. ✅ Website loads at https://properties.erposus.com
5. ✅ Browser shows secure padlock icon
6. ✅ All images and videos display correctly

---

## 🔄 Deployment Workflow with Custom Domain

```powershell
# 1. Make changes to your website
# Edit index.html or files in static/

# 2. Build and deploy
npm run deploy

# 3. Verify deployment
npm run deploy:check

# 4. Test custom domain
# Visit: https://properties.erposus.com

# 5. Clear cache if needed (in browser)
# Ctrl + Shift + R (hard refresh)
```

---

## 📞 Support Resources

**Cloudflare Docs:**
- https://developers.cloudflare.com/pages/configuration/custom-domains/

**Your Project Dashboard:**
- https://dash.cloudflare.com/[account-id]/pages/view/osusrealestatepremium

**DNS Settings:**
- https://dash.cloudflare.com/[account-id]/erposus.com/dns

---

## 🎉 Summary

To set up **properties.erposus.com**:

1. ✅ Go to Cloudflare Dashboard
2. ✅ Navigate to Workers & Pages → Pages → osusrealestatepremium
3. ✅ Click Custom domains tab
4. ✅ Click "Set up a custom domain"
5. ✅ Enter: properties.erposus.com
6. ✅ Click "Activate domain"
7. ✅ Wait 5-10 minutes for SSL
8. ✅ Deploy your site: `npm run deploy`
9. ✅ Test: https://properties.erposus.com

**Your custom domain will be live!** 🚀
