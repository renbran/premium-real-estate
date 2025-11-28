# OSUS Properties - Embeddable Landing Page

## How to Embed in Your Odoo Website

### Option 1: As an Odoo Module (Recommended)

1. **Install the module:**
   - Place the `website_osus_properties` folder in your `custom/` directory
   - Install from Odoo Apps menu
   - The homepage will automatically be replaced with the OSUS landing page

2. **Module Structure:**
   ```
   custom/
   └── website_osus_properties/
       ├── __init__.py
       ├── __manifest__.py
       ├── templates/
       │   └── osus_homepage.xml
       └── static/
           └── src/
               └── css/
                   └── osus_landing.css
   ```

### Option 2: Direct Iframe Embed

Add this to your Odoo website's homepage or any page template:

```html
<section class="container">
    <div style="margin: 0; padding: 0; width: 100%;">
        <iframe 
            id="osus-properties-frame"
            src="/path/to/premium_real_estate.html" 
            style="width: 100%; height: auto; min-height: 100vh; border: none; margin: 0; padding: 0;"
            allow="autoplay; fullscreen; picture-in-picture; accelerometer; gyroscope; magnetometer">
        </iframe>
    </div>
</section>
```

### Option 3: Copy-Paste Integration

1. Copy the entire `premium_real_estate.html` file to your website's static files
2. Reference it in your Odoo template:
   ```qweb
   <t t-set="content" t-raw="read('/path/to/premium_real_estate.html')"/>
   ```

## Features

✅ **Smart Embed Detection** - Automatically detects when running inside Odoo
✅ **Navbar Preservation** - Odoo navbar remains functional and visible
✅ **Header Toggle** - Custom header hidden when embedded (uses Odoo navbar)
✅ **Responsive Design** - Works on desktop, tablet, and mobile
✅ **Full Functionality** - All animations, videos, and interactions preserved
✅ **No Conflicts** - CSS properly scoped to avoid Odoo conflicts
✅ **Autoplay Videos** - Videos play continuously in background
✅ **100% Audio** - Full volume audio for background videos

## Configuration

The embed mode is automatically detected. No manual configuration needed!

### Automatic Detection:
- **Standalone Mode**: Displays custom header + navbar + loading screen
- **Embedded Mode**: Uses Odoo navbar only, hides custom header

### Manual Override (if needed):

Add this before the page loads:
```javascript
window.OSUS_FORCE_EMBEDDED = true;  // Force embedded mode
window.OSUS_FORCE_STANDALONE = true; // Force standalone mode
```

## File Paths to Update

Replace these paths with your actual file locations:
- Video 1: `D:\Downloader\download (11).mp4`
- Video 2: `D:\Downloader\download (8).mp4`
- Logo: `D:\Downloader\osus-removebg-preview.png`
- Property Images: `D:\old downloads\Leonardo_Phoenix_*.jpg`
- Staff Images: `D:\old downloads\photo_*.png`

## JavaScript Integration

The page includes automatic iframe parent detection:
```javascript
const isEmbedded = window.self !== window.top;
const isOdoo = typeof Odoo !== 'undefined';
```

## CSS Classes

Use these classes for custom styling:
- `body.osus-embedded` - Applied when embedded in Odoo
- `#osuHeader` - Custom header element (hidden when embedded)
- `#loadingScreen` - Loading screen (hidden when embedded)

## Troubleshooting

**Videos not playing:**
- Check that file paths are correct
- Ensure autoplay permissions are granted
- Check browser console for errors

**Navbar not visible:**
- Ensure Odoo navbar is not hidden by parent CSS
- Check z-index conflicts in inspector

**Styles not applying:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)
- Check for CSS conflicts in developer tools

## Support

For issues or questions about embedding, check:
1. Browser console (F12) for JavaScript errors
2. Network tab for missing assets
3. Elements inspector for CSS conflicts
