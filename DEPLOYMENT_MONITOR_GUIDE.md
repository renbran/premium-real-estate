# 🚀 OSUS Properties - Deployment & Monitoring Guide

## Quick Deploy to properties.erposus.com

### **Option 1: Automated Deploy & Monitor (Recommended)**

```powershell
npm run deploy
```

This single command will:
- ✅ Build the mobile-first website
- ✅ Deploy to Cloudflare Pages
- ✅ Verify deployment
- ✅ Open monitoring dashboard
- ✅ Run health checks

---

## 📊 Monitoring Options

### **1. Real-Time Terminal Monitor**

```powershell
npm run monitor
```

**Features:**
- Live status checks every 30 seconds
- Response time tracking
- Uptime percentage
- Automatic alerts for issues
- Saves reports to `monitoring-report.json`

**Output:**
```
═══════════════════════════════════════════════════
🚀 OSUS Properties - Real-Time Monitoring
═══════════════════════════════════════════════════
📊 Status: ONLINE
🌐 URL: https://properties.erposus.com
⏱️  Last Check: 2025-11-29T10:30:45.123Z
───────────────────────────────────────────────────
✓ Total Checks: 120
✓ Successful: 120
✗ Failed: 0
📈 Uptime: 100.00%
⚡ Avg Response: 245ms
═══════════════════════════════════════════════════
```

### **2. Web Dashboard Monitor**

After running `npm run deploy`, a browser-based dashboard opens automatically:

**Features:**
- Visual status indicators
- Performance metrics (FCP, LCP, TTI, CLS)
- SSL certificate status
- Mobile performance score
- Auto-refresh every 30 seconds
- Direct links to website and Cloudflare dashboard

---

## 🔧 Manual Deployment Steps

### Step 1: Install Wrangler CLI (if not installed)

```powershell
npm install -g wrangler
```

### Step 2: Login to Cloudflare

```powershell
npx wrangler login
```

### Step 3: Build the Project

```powershell
npm run build
```

### Step 4: Deploy to Cloudflare Pages

```powershell
npm run deploy:cloudflare
```

**Expected Output:**
```
✨ Success! Uploaded 1 file (3.45 sec)

✨ Deployment complete! Take a peek over at
   https://osusrealestatepremium.pages.dev
```

### Step 5: Configure Custom Domain

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Pages** → **osusrealestatepremium**
3. Click **Custom domains** → **Set up a custom domain**
4. Enter: `properties.erposus.com`
5. Click **Continue** → Cloudflare auto-configures DNS
6. Wait 2-5 minutes for propagation

---

## 🎯 GitHub Actions Auto-Deploy

The project is configured for automatic deployment on every push to `main` branch.

### Setup Required Secrets:

1. Go to GitHub repository settings
2. Navigate to **Secrets and variables** → **Actions**
3. Add these secrets:

| Secret Name | How to Get |
|-------------|------------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare Dashboard → My Profile → API Tokens → Create Token |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Dashboard → Overview → Account ID |

### Token Permissions:
- **Account** → Cloudflare Pages → Edit
- **Zone** → DNS → Edit (if using custom domain)

### Auto-Deploy Workflow:

Every time you push code:
```bash
git add .
git commit -m "Updated website"
git push origin main
```

GitHub Actions will automatically:
1. ✅ Install dependencies
2. ✅ Build the project
3. ✅ Deploy to Cloudflare
4. ✅ Update properties.erposus.com
5. ✅ Generate deployment summary

---

## 📈 Performance Monitoring Tools

### **1. Cloudflare Analytics (Built-in)**

Access: [Cloudflare Dashboard](https://dash.cloudflare.com) → Pages → osusrealestatepremium → Analytics

**Metrics Available:**
- Page views
- Unique visitors
- Bandwidth usage
- Top pages
- Geographic distribution
- Real-time traffic

### **2. Google PageSpeed Insights**

Check mobile performance:
```
https://pagespeed.web.dev/analysis?url=https://properties.erposus.com
```

**Target Scores:**
- ✅ Performance: 90+
- ✅ Accessibility: 95+
- ✅ Best Practices: 95+
- ✅ SEO: 100

### **3. Uptime Monitoring (Free Tools)**

**UptimeRobot** (Recommended):
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add new monitor
3. URL: `https://properties.erposus.com`
4. Type: HTTPS
5. Interval: 5 minutes
6. Alerts: Email/SMS

**StatusCake Alternative:**
- Go to [statuscake.com](https://www.statuscake.com)
- Similar setup as UptimeRobot
- Free tier: 10 monitors, 5-minute checks

### **4. Real User Monitoring (RUM)**

Add to `index.html` before `</body>`:

```html
<!-- Cloudflare Web Analytics -->
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' 
        data-cf-beacon='{"token": "YOUR_TOKEN_HERE"}'></script>
```

Get token from: Cloudflare Dashboard → Web Analytics → Add Site

---

## 🚨 Monitoring Alerts Setup

### Email Alerts for Downtime

**Using Node Monitor:**

1. Install nodemailer:
```powershell
npm install nodemailer
```

2. Update `cloudflare-monitor.js` with your email settings

3. Run with email alerts:
```powershell
npm run monitor
```

### Webhook Alerts (Slack/Discord)

Add to `cloudflare-monitor.js`:

```javascript
async function sendAlert(message) {
  await fetch('YOUR_WEBHOOK_URL', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: message })
  });
}
```

---

## 🔍 Health Check Endpoints

### Manual Health Check

```powershell
# Check website status
Invoke-WebRequest -Uri "https://properties.erposus.com" -Method Head

# Check with full details
Invoke-WebRequest -Uri "https://properties.erposus.com"
```

### cURL Health Check

```bash
curl -I https://properties.erposus.com
```

**Expected Response:**
```
HTTP/2 200
content-type: text/html
cache-control: public, max-age=0, must-revalidate
```

---

## 📊 Monitoring Dashboard Features

### Metrics Tracked:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Uptime | 99.9%+ | < 99% |
| Response Time | < 500ms | > 3000ms |
| SSL Status | Valid | Invalid/Expired |
| Mobile Score | 90+ | < 85 |
| FCP | < 1.0s | > 2.0s |
| LCP | < 2.5s | > 4.0s |
| CLS | < 0.1 | > 0.25 |

### Status Indicators:

- 🟢 **Green**: All systems normal
- 🟡 **Yellow**: Performance degraded
- 🔴 **Red**: System offline or critical issue

---

## 🛠️ Troubleshooting

### Issue: Deployment Failed

**Solution:**
```powershell
# Check Wrangler auth
npx wrangler whoami

# Re-login if needed
npx wrangler login

# Retry deployment
npm run deploy:cloudflare
```

### Issue: Custom Domain Not Working

**Check DNS:**
```powershell
nslookup properties.erposus.com
```

**Expected:**
- Should point to Cloudflare Pages IP
- May take 5-15 minutes to propagate

**Force DNS refresh:**
```powershell
ipconfig /flushdns
```

### Issue: Monitor Shows "OFFLINE"

**Checks:**
1. Verify URL is correct: `https://properties.erposus.com`
2. Check Cloudflare Pages deployment status
3. Verify DNS is propagated
4. Check browser cache (Ctrl+F5)
5. Test from different network/device

### Issue: Slow Response Times

**Optimizations:**
1. Enable Cloudflare Argo (paid)
2. Optimize images (WebP format)
3. Compress videos (lower bitrate)
4. Enable HTTP/3 in Cloudflare settings
5. Use Cloudflare CDN caching

---

## 📱 Mobile Testing Checklist

Before going live, test on:

- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] iPad (Safari)
- [ ] Desktop (Chrome, Firefox, Safari, Edge)
- [ ] Slow 3G connection
- [ ] Portrait and landscape modes

**Testing Commands:**
```powershell
# Start local server
npm start

# Open in browser
Start-Process "http://localhost:8000"
```

---

## 🎯 Success Metrics

### Day 1 Targets:
- ✅ Website is live and accessible
- ✅ HTTPS certificate is active
- ✅ Mobile responsive works correctly
- ✅ Videos load and play properly
- ✅ Monitoring is active

### Week 1 Targets:
- ✅ 99.9%+ uptime
- ✅ < 500ms average response time
- ✅ 90+ mobile performance score
- ✅ Zero critical errors
- ✅ Analytics tracking active

### Month 1 Targets:
- ✅ 100+ unique visitors
- ✅ 5+ consultation form submissions
- ✅ 99.95%+ uptime
- ✅ Performance optimizations complete
- ✅ SEO improvements implemented

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| **Live Website** | https://properties.erposus.com |
| **Cloudflare Dashboard** | https://dash.cloudflare.com |
| **Cloudflare Pages** | https://dash.cloudflare.com/pages |
| **GitHub Repository** | https://github.com/renbran/scholarix |
| **PageSpeed Insights** | https://pagespeed.web.dev |
| **Uptime Monitor** | https://uptimerobot.com |

---

## 📞 Support

**Issues with deployment?**
- Check Cloudflare status: https://www.cloudflarestatus.com
- Review deployment logs in Cloudflare Dashboard
- Test locally first: `npm start`

**Performance issues?**
- Run `npm run monitor` to diagnose
- Check Cloudflare Analytics for traffic spikes
- Review browser console for errors

**Custom domain issues?**
- Verify DNS settings in Cloudflare
- Wait 15 minutes for propagation
- Clear browser cache and DNS cache

---

## 🎉 Next Steps

1. **Deploy now:**
   ```powershell
   npm run deploy
   ```

2. **Start monitoring:**
   ```powershell
   npm run monitor
   ```

3. **Set up uptime alerts:**
   - Register at [uptimerobot.com](https://uptimerobot.com)
   - Add properties.erposus.com
   - Configure email alerts

4. **Enable analytics:**
   - Activate Cloudflare Web Analytics
   - Add Google Analytics (optional)
   - Set up conversion tracking

5. **Test thoroughly:**
   - Check all pages
   - Test forms
   - Verify videos play
   - Test on mobile devices

---

**🚀 Ready to deploy? Run:**
```powershell
npm run deploy
```

**📊 Need monitoring? Run:**
```powershell
npm run monitor
```

**Good luck with your launch! 🎉**
