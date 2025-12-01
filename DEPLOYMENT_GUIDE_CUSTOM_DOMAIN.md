# Deploy to properties.erposus.com - Step by Step Guide

## 🚀 Quick Deployment Steps

### **Option 1: Deploy to Cloudflare Pages (Recommended)**

#### Step 1: Build the Project
```bash
npm run build
```

#### Step 2: Deploy to Cloudflare Pages
```bash
npx wrangler pages deploy dist --project-name=osusrealestatepremium
```

#### Step 3: Configure Custom Domain in Cloudflare Dashboard

1. Go to **Cloudflare Dashboard** → **Pages**
2. Select your project: `osusrealestatepremium`
3. Go to **Custom domains** tab
4. Click **Set up a custom domain**
5. Enter: `properties.erposus.com`
6. Click **Continue**

Cloudflare will automatically:
- Create DNS records (CNAME pointing to your Pages project)
- Issue SSL/TLS certificate
- Enable automatic HTTPS

**DNS Configuration (Automatic):**
```
Type: CNAME
Name: properties
Target: osusrealestatepremium.pages.dev
Proxy: Yes (Orange cloud)
```

---

### **Option 2: Manual DNS Setup (If needed)**

If you need to manually configure DNS:

1. Log in to **Cloudflare Dashboard**
2. Select domain: `erposus.com`
3. Go to **DNS** → **Records**
4. Add a new record:
   - **Type**: CNAME
   - **Name**: properties
   - **Target**: osusrealestatepremium.pages.dev
   - **Proxy status**: Proxied (orange cloud)
   - **TTL**: Auto

---

## 📋 Deployment Checklist

- [ ] Run `npm run build` successfully
- [ ] Deploy with `npx wrangler pages deploy dist`
- [ ] Add custom domain in Cloudflare Pages dashboard
- [ ] Verify DNS records are created
- [ ] Wait for SSL certificate (usually 1-5 minutes)
- [ ] Test website at https://properties.erposus.com
- [ ] Verify all videos, images, and links work
- [ ] Test responsive design on mobile devices

---

## 🔧 Troubleshooting

### SSL Certificate Pending
**Issue**: "Your SSL certificate is pending"
**Solution**: Wait 1-5 minutes. Cloudflare automatically issues certificates.

### 404 Errors
**Issue**: Pages return 404
**Solution**: Ensure `_redirects` file is in `dist/` folder:
```
/*  /index.html  200
```

### Videos Not Loading
**Issue**: Videos show broken/not playing
**Solution**: Check video paths in HTML files use `/media/videos/` or `/static/media/videos/`

### Custom Domain Not Working
**Issue**: Domain shows "DNS address could not be found"
**Solution**: 
1. Verify CNAME record points to `osusrealestatepremium.pages.dev`
2. Ensure proxy is enabled (orange cloud)
3. Clear browser cache or try incognito mode

---

## 🎯 Expected Results

✅ **Website live at**: https://properties.erposus.com
✅ **SSL/HTTPS**: Automatically enabled
✅ **Global CDN**: Content delivered from edge locations worldwide
✅ **Auto-deploy**: Future pushes to main branch auto-deploy

---

## 📊 Post-Deployment Verification

Test these URLs:
- https://properties.erposus.com (Homepage)
- https://properties.erposus.com/index.html (Direct HTML)
- https://properties.erposus.com/media/videos/hero-video-1.mp4 (Video test)

Check:
- [ ] Videos play at 70% volume
- [ ] Staff carousel animates correctly
- [ ] Property cards display properly
- [ ] Contact form submits
- [ ] All sections scroll smoothly
- [ ] Mobile responsive works

---

## 🔄 Update Workflow (Future Changes)

1. Make code changes locally
2. Test locally by opening `index.html`
3. Run `npm run build`
4. Deploy: `npx wrangler pages deploy dist`
5. Changes live in ~30 seconds

---

## 📞 Support

If issues persist:
1. Check Cloudflare Pages deployment logs
2. Verify DNS propagation: https://dnschecker.org
3. Clear CDN cache in Cloudflare dashboard
4. Contact Cloudflare support if needed

---

**Deployment configured for**: properties.erposus.com
**Last updated**: November 29, 2025
