# AI Tech White-Label Backend Theme

## 🚀 Overview

A world-class, production-ready Odoo 17 backend theme inspired by AI and modern technology. Features cutting-edge design with glassmorphism effects, smooth animations, and a futuristic aesthetic perfect for tech-forward organizations.

## ✨ Key Features

### 🎨 Modern Design Elements
- **Glassmorphism UI**: Frosted glass effects with backdrop blur
- **Gradient Accents**: Dynamic cyan/purple color schemes
- **Smooth Animations**: Polished transitions and micro-interactions
- **Neon Glow Effects**: Subtle lighting effects on interactive elements
- **Particle System**: Optional animated particles for login and dashboards
- **Dark Mode Optimized**: Built for dark theme with high contrast

### ⚙️ Fully Configurable
- **Color Customization**: Primary, secondary, accent, and background colors
- **Typography**: 5 font family options (Inter, Roboto, Poppins, Montserrat, IBM Plex Sans)
- **Branding**: Custom app name, tagline, logos, and favicons
- **Feature Toggles**: Enable/disable glassmorphism, animations, gradients, particles

### 🛠️ Technical Excellence
- **Odoo 17 Compliant**: Modern syntax and best practices
- **Responsive Design**: Mobile-first, works on all screen sizes
- **Performance Optimized**: Efficient CSS with minimal repaints
- **CloudPepper Compatible**: Tested for production deployment
- **Accessibility**: WCAG guidelines with proper contrast ratios

## 📦 Installation

### Requirements
- Odoo 17.0+
- Modern web browser with CSS backdrop-filter support

### Installation Steps

1. **Copy Module to Addons**
   ```bash
   cp -r ai_tech_whitelabel /path/to/odoo/addons/
   ```

2. **Update Apps List**
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "AI Tech White-Label System"

3. **Install Module**
   - Click "Install"
   - Wait for installation to complete

4. **Configure Theme**
   - Go to Settings → General Settings
   - Scroll to "AI Tech Theme Configuration"
   - Customize colors, fonts, and branding
   - Save changes

## ⚙️ Configuration

### Color Scheme

Navigate to **Settings → General Settings → AI Tech Theme Configuration**

| Setting | Default | Description |
|---------|---------|-------------|
| Primary Color | #0ea5e9 (Cyan) | Main brand color for buttons, headers |
| Secondary Color | #8b5cf6 (Purple) | Accent color for highlights |
| Accent Color | #06b6d4 (Bright Cyan) | Interactive elements |
| Dark Background | #0f172a | Main background color |
| Sidebar Background | #1e293b | Navigation sidebar color |

### Typography

Choose from 5 professional font families:
- **Inter** (Default) - Modern, clean sans-serif
- **Roboto** - Google's versatile typeface
- **Poppins** - Geometric sans-serif
- **Montserrat** - Urban elegance
- **IBM Plex Sans** - Tech-inspired design

### Branding

- **Application Name**: Custom name displayed in login and header
- **Tagline**: Subtitle for login page
- **Login Background**: Custom image for login screen
- **Favicon**: Custom browser icon

### Visual Effects

Toggle features on/off:
- ✅ **Glassmorphism**: Frosted glass UI elements
- ✅ **Animations**: Smooth transitions and effects
- ✅ **Gradients**: Colorful gradient backgrounds
- ⚪ **Particle Effects**: Animated particles (performance impact)

## 🎨 Design System

### Color Variables

```css
--ai-primary: #0ea5e9
--ai-secondary: #8b5cf6
--ai-accent: #06b6d4
--ai-dark-bg: #0f172a
--ai-dark-surface: #1e293b
--ai-text-primary: #f8fafc
--ai-text-secondary: #cbd5e1
```

### Spacing Scale

```css
--ai-spacing-xs: 4px
--ai-spacing-sm: 8px
--ai-spacing-md: 16px
--ai-spacing-lg: 24px
--ai-spacing-xl: 32px
--ai-spacing-2xl: 48px
```

### Border Radius

```css
--ai-border-radius-sm: 6px
--ai-border-radius-md: 10px
--ai-border-radius-lg: 14px
--ai-border-radius-xl: 20px
```

## 🖼️ Screenshots

### Login Page
- Glassmorphism card with animated gradient background
- Icon-enhanced input fields
- Smooth hover effects on buttons
- Optional particle animation

### Backend Interface
- Dark themed with cyan/purple accents
- Glassmorphism sidebar and navbar
- Enhanced control panel with gradient buttons
- Neon glow effects on active elements
- Modern kanban cards with hover animations

### Form Views
- Styled input fields with focus effects
- Enhanced checkboxes and radio buttons
- Custom dropdown menus
- Glassmorphism modals and dialogs

## 🔧 Customization

### CSS Variables

Override any variable in your custom CSS:

```css
:root {
    --ai-primary: #your-color;
    --ai-font-family: 'Your Font', sans-serif;
}
```

### JavaScript Events

Listen for theme updates:

```javascript
document.addEventListener('ai_theme_updated', (event) => {
    console.log('Theme updated:', event.detail);
});
```

### Custom Animations

Add your own animations:

```css
@keyframes custom-animation {
    from { transform: scale(1); }
    to { transform: scale(1.05); }
}

.your-element {
    animation: custom-animation 0.3s ease;
}
```

## 📱 Responsive Design

- **Desktop**: Full glassmorphism effects and animations
- **Tablet**: Optimized layout with touch-friendly controls
- **Mobile**: Simplified UI with essential features

## 🚀 Performance

### Optimizations
- CSS variables for dynamic theming (no page reload)
- GPU-accelerated animations
- Efficient backdrop-filter usage
- Lazy-loaded particle effects
- Minimal JavaScript footprint

### Browser Support
- Chrome/Edge 76+ (full support)
- Firefox 103+ (full support)
- Safari 15.4+ (full support with -webkit prefix)
- Mobile browsers (iOS 15.4+, Android Chrome 76+)

## 🐛 Troubleshooting

### Theme Not Applying

1. Clear browser cache (Ctrl+Shift+Delete)
2. Restart Odoo server
3. Check module is installed and active
4. Verify `web` dependency is loaded

### Glassmorphism Not Working

- Update to a modern browser (Chrome 76+, Firefox 103+, Safari 15.4+)
- Check backdrop-filter support: https://caniuse.com/css-backdrop-filter
- Disable if browser doesn't support (fallback to solid backgrounds)

### Performance Issues

- Disable particle effects in settings
- Reduce animation speed in animations.scss
- Check browser console for errors

## 🔐 Security

- No external dependencies or CDN calls
- All assets served locally
- Follows Odoo security best practices
- CSRF protection maintained

## 📄 License

LGPL-3 - See LICENSE file for details

## 👨‍💻 Author

**OSUS Tech**  
Website: https://erposus.com  
Support: support@erposus.com

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow Odoo coding standards
4. Submit a pull request

## 📝 Changelog

### Version 17.0.1.0.0 (Initial Release)
- ✨ Complete glassmorphism UI
- 🎨 Cyan/purple gradient theme
- ⚡ Smooth animations and transitions
- 🎯 Particle effects system
- ⚙️ Full backend configuration
- 📱 Responsive design
- 🔧 Dynamic color management
- 🎭 Custom login page
- 🌐 CloudPepper compatible

## 📚 Resources

- [Odoo 17 Documentation](https://www.odoo.com/documentation/17.0/)
- [Glassmorphism Design](https://glassmorphism.com/)
- [CSS Variables Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)

## 🎯 Roadmap

- [ ] Additional color presets (dark mode variants)
- [ ] More font options
- [ ] Theme import/export
- [ ] Advanced particle customization
- [ ] Real-time preview in settings
- [ ] Light mode support
- [ ] Multi-company theme switching

---

**Made with ❤️ for the Odoo community**
