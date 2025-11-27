# AI Tech White-Label Theme - Installation Guide

## 🚀 Quick Start

### Prerequisites
- Odoo 17.0 or higher
- Modern web browser (Chrome 76+, Firefox 103+, Safari 15.4+)
- CloudPepper deployment or local Odoo instance

### Installation Steps

#### 1. Module Installation

**On CloudPepper:**
```bash
# Module is already in addons directory
# Just install via Odoo interface
```

**On Local Development:**
```bash
cd /path/to/odoo/addons/
# Module already exists as ai_tech_whitelabel
```

#### 2. Update Apps List
1. Login to Odoo as Administrator
2. Navigate to **Apps** menu
3. Click **Update Apps List**
4. Click **Update** to confirm

#### 3. Install the Module
1. In Apps menu, remove "Apps" filter
2. Search for "AI Tech White-Label"
3. Click **Install** button
4. Wait for installation to complete (30-60 seconds)

#### 4. Configure the Theme

Navigate to **Settings → General Settings**, scroll to **AI Tech Theme** section:

**Branding:**
- Application Name: `OSUS ERP` (or your company name)
- Tagline: `Powered by AI Technology`

**Colors (Defaults are already optimized):**
- Primary: `#0ea5e9` (Cyan)
- Secondary: `#8b5cf6` (Purple)
- Accent: `#06b6d4` (Bright Cyan)
- Dark Background: `#0f172a`
- Sidebar: `#1e293b`

**Typography:**
- Font Family: `Inter` (Modern sans-serif)

**Visual Effects:**
- ✅ Enable Glassmorphism
- ✅ Enable Animations
- ✅ Enable Gradients
- ⚪ Enable Particles (optional - slight performance impact)

Click **Save** to apply changes.

### 5. Verify Installation

**Backend Check:**
1. Refresh the page (F5 or Ctrl+R)
2. You should see:
   - Dark themed interface with cyan/purple accents
   - Glassmorphism effects on panels
   - Smooth animations on hover
   - Gradient buttons and effects

**Login Page Check:**
1. Logout from Odoo
2. Login page should display:
   - Futuristic glassmorphism card
   - Animated gradient background
   - Custom branding if configured

## 🎨 Customization Examples

### Example 1: Company Branding

**For "Acme Corporation":**
- Application Name: `Acme ERP`
- Tagline: `Innovation in Every Solution`
- Primary Color: `#FF6B6B` (Company red)
- Secondary Color: `#4ECDC4` (Company teal)

### Example 2: Professional Services

**For "Legal Tech Solutions":**
- Application Name: `LegalTech Pro`
- Tagline: `Smart Legal Management`
- Font Family: `IBM Plex Sans` (Professional tech look)
- Primary Color: `#1E3A8A` (Deep blue)
- Secondary Color: `#60A5FA` (Light blue)

### Example 3: Creative Agency

**For "Design Studio":**
- Application Name: `Studio Creative`
- Tagline: `Where Ideas Come to Life`
- Font Family: `Poppins` (Modern, creative)
- Primary Color: `#EC4899` (Pink)
- Secondary Color: `#F59E0B` (Orange)
- Enable all visual effects for maximum impact

## 🔧 Advanced Configuration

### Custom CSS Overrides

Create a custom module that depends on `ai_tech_whitelabel`:

```python
# __manifest__.py
{
    'name': 'My Custom Theme',
    'depends': ['ai_tech_whitelabel'],
    'assets': {
        'web.assets_backend': [
            'my_custom_theme/static/src/scss/custom.scss',
        ],
    },
}
```

```scss
// static/src/scss/custom.scss
:root {
    // Override any AI Theme variables
    --ai-primary: #your-color;
    --ai-border-radius-md: 8px;
}
```

### JavaScript Customization

Listen for theme changes:

```javascript
/** @odoo-module **/
document.addEventListener('ai_theme_updated', (event) => {
    console.log('Theme colors updated:', event.detail);
    // Your custom logic here
});
```

### Performance Tuning

**For slower devices:**
1. Disable particle effects
2. Reduce animations in `animations.scss`:
   ```scss
   --ai-transition-fast: 50ms;
   --ai-transition-base: 150ms;
   ```

**For maximum performance:**
1. Disable glassmorphism (fallback to solid backgrounds)
2. Disable gradients
3. Keep animations enabled (minimal impact)

## 🐛 Troubleshooting

### Theme Not Applying

**Solution 1: Clear Cache**
```bash
# Browser: Ctrl+Shift+Delete (Clear all cached images and files)
# Then refresh: Ctrl+F5
```

**Solution 2: Restart Odoo**
```bash
# For development
./odoo-bin restart

# For CloudPepper - restart via panel
```

**Solution 3: Check Module**
- Go to Apps menu
- Search "AI Tech White-Label"
- Ensure status shows "Installed"
- Check version is 17.0.1.0.0

### Glassmorphism Not Working

**Check Browser Support:**
- Chrome/Edge: Version 76+
- Firefox: Version 103+
- Safari: Version 15.4+

**Test Support:**
```javascript
// Open browser console (F12)
console.log(CSS.supports('backdrop-filter', 'blur(10px)'));
// Should return: true
```

**Workaround:**
If browser doesn't support backdrop-filter, theme will automatically fall back to solid backgrounds.

### Colors Not Changing

**Check Configuration:**
1. Settings → General Settings
2. AI Tech Theme section
3. Verify colors are saved
4. Click "Save" button at top

**Force Refresh:**
```javascript
// Browser console
document.dispatchEvent(new CustomEvent('ai_theme_updated', {
    detail: {
        primary: '#0ea5e9',
        secondary: '#8b5cf6'
    }
}));
```

### Performance Issues

**Disable Heavy Features:**
1. Particles: Highest impact - disable if slow
2. Glassmorphism: Moderate impact
3. Gradients: Low impact
4. Animations: Very low impact

**Check Browser Performance:**
- Open DevTools (F12)
- Go to Performance tab
- Record while interacting
- Look for slow operations

## 📊 Feature Matrix

| Feature | Impact | Browser Support | Recommended |
|---------|--------|----------------|-------------|
| Dark Theme | None | All | ✅ Always On |
| Glassmorphism | Medium | Modern Browsers | ✅ Yes |
| Animations | Low | All | ✅ Yes |
| Gradients | Low | All | ✅ Yes |
| Particles | High | All | ⚠️ Optional |

## 🔄 Updates & Maintenance

### Checking for Updates
```bash
# In module directory
git pull origin main
# Then restart Odoo and upgrade module
```

### Backup Before Customization
```bash
# Backup original files
cp -r ai_tech_whitelabel ai_tech_whitelabel.backup
```

### Reset to Defaults
1. Settings → General Settings → AI Tech Theme
2. Click "Restore Defaults" (if available)
3. Or manually set default colors:
   - Primary: #0ea5e9
   - Secondary: #8b5cf6
   - Accent: #06b6d4

## 🎓 Best Practices

### 1. Test Before Production
- Install on staging/test instance first
- Test all main workflows
- Verify on different browsers
- Check mobile responsiveness

### 2. Gradual Rollout
- Start with default colors
- Customize one section at a time
- Get user feedback
- Adjust based on feedback

### 3. Performance Monitoring
- Monitor page load times
- Check memory usage
- Disable heavy features if needed
- Use browser DevTools

### 4. User Training
- Show users new interface
- Highlight key features
- Provide quick reference guide
- Collect feedback

## 📞 Support

**Documentation:** See README.md for full documentation

**Issues:** Report bugs via:
- Email: support@erposus.com
- Create issue in repository

**Community:** Join Odoo community forums

## ✅ Post-Installation Checklist

- [ ] Module installed successfully
- [ ] Theme applied (dark background visible)
- [ ] Colors customized for brand
- [ ] Branding configured (app name, tagline)
- [ ] Login page tested and styled
- [ ] Visual effects enabled/disabled as needed
- [ ] Tested on multiple browsers
- [ ] Mobile view checked
- [ ] Performance acceptable
- [ ] Users notified of new theme
- [ ] Backup created

---

**Congratulations! Your AI Tech Theme is now active.** 🎉

Enjoy your modern, futuristic Odoo experience!
