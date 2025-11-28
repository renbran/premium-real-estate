# 🚀 Scholarix AI Theme - Quick Deployment Guide

## Prerequisites
- Odoo 18 server running
- Admin access to Odoo instance
- Scholarix logo file (place at `static/src/img/logo.png`)

## Installation Steps

### Method 1: Using Installation Scripts

**Windows:**
```bash
# Run the batch file
install.bat
```

**Linux/Mac:**
```bash
# Make script executable and run
chmod +x install.sh
./install.sh
```

### Method 2: Manual Installation

1. **Copy Theme Directory**
   ```
   Copy the entire scholarix_theme folder to your Odoo addons directory
   Example: /opt/odoo/addons/ or /path/to/your/addons/
   ```

2. **Add Logo File**
   ```
   Place your Scholarix logo at:
   scholarix_theme/static/src/img/logo.png
   ```

3. **Update Odoo Configuration**
   ```
   Add the addons path to your odoo.conf file:
   addons_path = /existing/path,/path/to/scholarix_theme
   ```

4. **Restart Odoo Server**
   ```bash
   # Restart your Odoo service
   sudo systemctl restart odoo
   # Or if running manually:
   python3 odoo-bin -c /path/to/odoo.conf
   ```

5. **Install via Odoo Interface**
   - Login to Odoo as administrator
   - Go to Apps → Update Apps List
   - Search for "Scholarix AI Theme"
   - Click Install

6. **Activate Theme**
   - Go to Website → Configuration → Settings
   - Select "Scholarix AI Theme" as your theme
   - Save changes

## File Structure Verification

Make sure these key files exist:
```
scholarix_theme/
├── __manifest__.py
├── static/
│   └── src/
│       ├── img/
│       │   └── logo.png                 # Your logo here
│       ├── js/
│       │   ├── scholarix_loader.js      # Loading screen
│       │   ├── scholarix_cursor.js      # Custom cursor
│       │   ├── scholarix_3d_hero.js     # 3D hero section
│       │   ├── scholarix_animations.js  # Animations
│       │   ├── scholarix_particles.js   # Particle effects
│       │   └── scholarix_main.js        # Main controller
│       └── scss/
│           ├── scholarix_loading.scss   # Loading styles
│           ├── scholarix_cursor.scss    # Cursor styles
│           ├── scholarix_animations.scss# Animation styles
│           └── scholarix_main.scss      # Main styles
└── views/
    ├── layout_templates.xml
    ├── homepage_sections.xml
    └── snippets.xml
```

## Feature Configuration

### 1. Loading Screen
- Automatically enabled on theme activation
- Displays animated Scholarix logo
- Progress tracking with steps
- Skip option available

### 2. Custom Cursor
- Activates on desktop devices
- Interactive hover effects
- Click ripple animations
- Disabled on mobile for performance

### 3. 3D Hero Section
- Parallax scrolling effects
- Floating holographic elements
- Logo display with animations
- Responsive design

## Testing Checklist

After installation, verify:
- [ ] Theme appears in Website settings
- [ ] Loading screen shows with logo
- [ ] Custom cursor works on desktop
- [ ] Hero section displays properly
- [ ] Mobile responsiveness
- [ ] All animations work smoothly
- [ ] No console errors

## Performance Optimization

1. **Enable Gzip Compression**
   ```nginx
   gzip on;
   gzip_types text/css application/javascript;
   ```

2. **Browser Caching**
   ```nginx
   location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

3. **Image Optimization**
   - Use WebP format for images when possible
   - Compress PNG/JPG files
   - Optimize SVG files

## Troubleshooting

### Theme Not Appearing
1. Check addons path in configuration
2. Restart Odoo server
3. Update apps list in Odoo interface

### Loading Screen Issues
1. Verify logo.png exists at correct path
2. Check browser console for JavaScript errors
3. Clear browser cache

### Performance Issues
1. Test on different devices
2. Check network tab in developer tools
3. Enable reduced motion for accessibility

### Mobile Issues
1. Advanced features are optimized for mobile
2. Some effects may be reduced for performance
3. Test on actual devices, not just browser simulation

## Support

For issues related to:
- **Odoo Installation**: Check Odoo documentation
- **Theme Customization**: Modify SCSS/JS files as needed
- **Performance**: Follow optimization guidelines above

## Additional Resources

- `ENHANCED_FEATURES.md` - Detailed feature documentation
- `THEME_CUSTOMIZATION.md` - Customization guide
- Odoo 18 Website Documentation
- Theme development best practices

---

🎉 **Congratulations!** Your Scholarix AI Theme is now ready to showcase your futuristic tech consultancy with cutting-edge interactive features!
