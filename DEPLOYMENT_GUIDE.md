# 🚀 Deploy to properties.erposus.com

## Quick Deployment Steps

### Option 1: Static File Upload (Recommended for now)

1. **Upload these files to your web server:**
   ```
   index.html (mobile-first version)
   /static/media/videos/
   /static/media/images/
   /static/css/ (if any)
   ```

2. **Configure your web server:**
   - Point domain `properties.erposus.com` to document root
   - Enable HTTPS
   - Configure MIME types for video files

3. **Test the deployment:**
   ```bash
   curl -I https://properties.erposus.com
   ```

### Option 2: Build & Deploy with Node.js

```bash
# Install dependencies (if needed)
npm install

# Build for production
npm run build

# Deploy to server
# (Configure your deployment method)
```

### Option 3: Cloudflare Pages (Fast & Free)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Mobile-first rebuild complete"
   git push origin main
   ```

2. **Connect to Cloudflare Pages:**
   - Go to Cloudflare Dashboard
   - Pages → Create a project
   - Connect GitHub repo
   - Build settings:
     - Build command: (leave empty for static)
     - Output directory: `/`
   - Deploy!

3. **Custom Domain:**
   - Go to Custom domains
   - Add `properties.erposus.com`
   - Update DNS records as instructed

---

## 📋 Pre-Deployment Checklist

- [ ] All videos are uploaded and accessible
- [ ] All images are uploaded and accessible
- [ ] Logo file exists at `/static/media/images/osus-logo.png`
- [ ] Test on mobile device
- [ ] Test on desktop browser
- [ ] Check video playback with 70% volume
- [ ] Verify navigation menu works
- [ ] Test all forms
- [ ] Check page load speed

---

## 🔧 Server Configuration

### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name properties.erposus.com;
    
    root /var/www/properties;
    index index.html;
    
    # SSL Configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Gzip compression
    gzip on;
    gzip_types text/css application/javascript image/svg+xml;
    
    # Video MIME types
    types {
        video/mp4 mp4;
    }
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|mp4)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Handle SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Apache .htaccess
```apache
# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css application/javascript
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType video/mp4 "access plus 1 year"
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
</IfModule>

# MIME types for video
AddType video/mp4 .mp4
AddType video/webm .webm

# Rewrite rules
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^ index.html [L]
```

---

## 🎯 Performance Optimization

### Before Going Live:

1. **Optimize Images:**
   ```bash
   # Install imagemin
   npm install -g imagemin-cli imagemin-mozjpeg imagemin-pngquant
   
   # Optimize all images
   imagemin static/media/images/*.{jpg,png} --out-dir=static/media/images/optimized --plugin=mozjpeg --plugin=pngquant
   ```

2. **Compress Videos:**
   ```bash
   # Using ffmpeg
   ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4
   ```

3. **Enable CDN:**
   - Use Cloudflare or similar CDN
   - Configure asset caching
   - Enable auto-minification

---

## 📊 Monitoring & Analytics

### Add Analytics (Optional)
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

---

## ✅ Post-Deployment Testing

Test these URLs:
- https://properties.erposus.com
- https://properties.erposus.com/#properties
- https://properties.erposus.com/#contact

Test on devices:
- iPhone (Safari)
- Android (Chrome)
- iPad
- Desktop (Chrome, Firefox, Safari)

Check performance:
- Google PageSpeed Insights
- GTmetrix
- WebPageTest

---

## 🆘 Troubleshooting

### Videos not playing?
- Check MIME types are configured
- Verify file paths are correct
- Check file permissions (644 for files)
- Test video files directly in browser

### Mobile menu not working?
- Check JavaScript is loading
- Verify no console errors
- Test on actual mobile device (not just DevTools)

### Styles look broken?
- Clear browser cache
- Check CSS file paths
- Verify fonts are loading
- Test in incognito mode

---

## 📞 Support

Deployment ready! The mobile-first website is optimized and ready for production at `properties.erposus.com`.
