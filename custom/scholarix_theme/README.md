# Scholarix AI Theme

## Overview

The Scholarix AI Theme is a cutting-edge Odoo 18 website theme designed specifically for AI and technology companies. It embodies a futuristic aesthetic with advanced visual effects, modern animations, and a comprehensive design system that reflects innovation and technological excellence.

## Features

### 🎨 Design System
- **Futuristic Color Palette**: Electric Blue (#00E5FF), Deep Blue (#0D47A1), Neon Cyan (#40C4FF), Holographic Purple (#7C4DFF)
- **Modern Typography**: Orbitron for headings, Rajdhani for body text
- **Advanced Gradients**: Holographic and electric gradient effects
- **Responsive Grid System**: Bootstrap 5 based with custom enhancements

### ✨ Visual Effects
- **Particle Systems**: Interactive canvas-based particle animations
- **Neural Network Visualizations**: Animated AI brain and connection effects
- **Holographic Elements**: CSS-based holographic animations and glows
- **Matrix Rain Effects**: Classic matrix-style background animations
- **Smooth Scroll Animations**: GSAP-powered scroll-triggered animations

### 🚀 Interactive Components
- **Smart Navigation**: Auto-hiding navbar with active section highlighting
- **Animated Statistics**: Counting animations for key metrics
- **Interactive Service Cards**: Hover effects with gradient transitions
- **Tech Showcase**: Interactive technology demonstration circles
- **Dynamic Forms**: Floating labels and real-time validation

### 📱 Performance & Accessibility
- **Mobile Optimized**: Fully responsive design with touch gestures
- **Performance Optimized**: Lazy loading, debounced scroll handlers
- **SEO Ready**: Structured data and semantic HTML
- **Accessibility Compliant**: WCAG guidelines implementation
- **Cross-browser Compatible**: Modern browser support with fallbacks

## Installation

1. **Copy Theme Files**
   ```bash
   cp -r scholarix_theme /path/to/your/odoo/addons/
   ```

2. **Update Odoo Addons Path**
   Ensure your addons path includes the theme directory.

3. **Install Theme**
   - Go to Apps menu in Odoo
   - Search for "Scholarix AI Theme"
   - Click Install

4. **Activate Theme**
   - Go to Website → Configuration → Settings
   - Select "Scholarix AI Theme" from the theme dropdown
   - Click Apply

## Theme Structure

```
scholarix_theme/
├── __manifest__.py                 # Module manifest
├── models/                        # Python models
│   ├── __init__.py
│   └── theme_utils.py            # Theme utility functions
├── static/
│   ├── description/              # Theme description and screenshots
│   └── src/
│       ├── scss/                 # SCSS source files
│       │   ├── primary_variables.scss
│       │   ├── bootstrap_overrides.scss
│       │   ├── scholarix_animations.scss
│       │   └── scholarix_main.scss
│       ├── js/                   # JavaScript files
│       │   ├── scholarix_animations.js
│       │   ├── scholarix_particles.js
│       │   └── scholarix_main.js
│       └── img/                  # Image assets
└── views/                        # XML template files
    ├── layout_templates.xml      # Base layout templates
    ├── homepage_sections.xml     # Homepage sections
    └── snippets.xml              # Drag-and-drop snippets
```

## Customization

### Color Scheme
The theme uses CSS custom properties for easy color customization:

```css
:root {
  --scholarix-electric-blue: #00E5FF;
  --scholarix-deep-blue: #0D47A1;
  --scholarix-neon-cyan: #40C4FF;
  --scholarix-holographic-purple: #7C4DFF;
}
```

### Typography
Customize fonts by updating the font variables:

```css
:root {
  --scholarix-font-primary: 'Orbitron', monospace;
  --scholarix-font-secondary: 'Rajdhani', sans-serif;
}
```

### Animations
Control animation settings through SCSS variables:

```scss
$scholarix-transition-fast: 0.2s ease-out;
$scholarix-transition-normal: 0.3s ease-out;
$scholarix-transition-slow: 0.5s ease-out;
```

## Available Snippets

### AI Services Cards
Pre-built service cards with icons and hover effects for showcasing AI capabilities.

### Technology Showcase
Interactive circular display of different technologies with connecting lines.

### Statistics Counter
Animated counters for displaying key business metrics and achievements.

### Hero Banner
Full-width hero section with particle effects and call-to-action buttons.

### Team Member Cards
Professional team member cards with social media links and hover effects.

### Process Steps
Step-by-step process visualization with numbered indicators.

### Client Testimonials
Rotating testimonial slider with client photos and quotes.

## Browser Support

- **Chrome**: 88+
- **Firefox**: 85+
- **Safari**: 14+
- **Edge**: 88+
- **Mobile Safari**: 14+
- **Chrome Mobile**: 88+

## Dependencies

### Required Odoo Modules
- `base`: Core Odoo functionality
- `website`: Website builder functionality
- `website_sale`: E-commerce features (optional)
- `website_blog`: Blog functionality (optional)

### External Libraries
- **Bootstrap 5.3**: CSS framework
- **Font Awesome 6**: Icon library
- **Google Fonts**: Orbitron & Rajdhani fonts
- **GSAP**: Animation library (optional, loaded via CDN)
- **AOS**: Animate On Scroll library (optional)

## Performance Considerations

### Optimization Features
- **Lazy Loading**: Images and heavy content load on demand
- **Debounced Events**: Scroll and resize events are optimized
- **Critical CSS**: Above-the-fold styles are prioritized
- **Asset Minification**: CSS and JS are compressed in production
- **Caching**: Static assets have appropriate cache headers

### Best Practices
1. **Image Optimization**: Use WebP format where possible
2. **Font Loading**: Fonts are preloaded for better performance
3. **Script Loading**: Non-critical scripts load asynchronously
4. **Animation Performance**: CSS transforms are preferred over position changes

## Troubleshooting

### Common Issues

**Theme not appearing in theme selector**
- Ensure the module is installed and activated
- Check that all dependencies are satisfied
- Verify the `__manifest__.py` file is correct

**Animations not working**
- Check browser compatibility for CSS animations
- Ensure JavaScript is enabled
- Verify GSAP library is loading correctly

**Styling issues**
- Clear browser cache and Odoo asset cache
- Check for CSS conflicts with other modules
- Ensure SCSS files are compiling correctly

**Performance problems**
- Disable particle effects on lower-end devices
- Optimize image assets
- Review JavaScript console for errors

## Support and Documentation

For technical support and detailed documentation:
- Review the code comments in each file
- Check the Odoo logs for any errors
- Test in a development environment first

## Version History

- **v1.0.0**: Initial release with core AI theme features
- **v1.1.0**: Added particle systems and advanced animations
- **v1.2.0**: Enhanced mobile responsiveness and performance
- **v2.0.0**: Full Odoo 18 compatibility and new snippets

## License

This theme is licensed under the LGPL-3.0 license. See the LICENSE file for details.

---

**Developed by Scholarix Global Consultants**
*Pioneering the future of AI technology and digital transformation*
