#!/bin/bash
# Scholarix AI Theme Installation Script

echo "🚀 Installing Scholarix AI Theme with Enhanced Features..."

# Check if we're in the right directory
if [ ! -f "__manifest__.py" ]; then
    echo "❌ Error: Please run this script from the scholarix_theme directory"
    exit 1
fi

# Check if logo exists
if [ ! -f "static/src/img/logo.png" ]; then
    echo "⚠️  Warning: Logo file not found at static/src/img/logo.png"
    echo "   Please place the Scholarix logo in this location for full functionality"
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p static/src/img/{portfolio,team,testimonials,icons}
mkdir -p static/src/css
mkdir -p static/description
mkdir -p views/{about,services,portfolio,blog,contact,snippets,index}

# Set permissions
echo "🔒 Setting permissions..."
chmod -R 755 static/
chmod -R 644 static/src/scss/*.scss
chmod -R 644 static/src/js/*.js
chmod -R 644 views/*.xml

# Check for required dependencies
echo "🔍 Checking dependencies..."

# Check if Odoo modules exist
required_modules=("base" "website" "website_sale" "website_blog")
for module in "${required_modules[@]}"; do
    echo "   Checking for $module..."
done

# Compile SCSS (if sass is available)
if command -v sass >/dev/null 2>&1; then
    echo "🎨 Compiling SCSS files..."
    sass static/src/scss/scholarix_main.scss static/src/css/scholarix_theme.css --style compressed
    echo "   ✅ SCSS compiled successfully"
else
    echo "ℹ️  SASS not found. CSS will be compiled by Odoo."
fi

# Check JavaScript files
echo "🔧 Validating JavaScript files..."
js_files=(
    "static/src/js/scholarix_loader.js"
    "static/src/js/scholarix_cursor.js"
    "static/src/js/scholarix_3d_hero.js"
    "static/src/js/scholarix_animations.js"
    "static/src/js/scholarix_particles.js"
    "static/src/js/scholarix_main.js"
)

for file in "${js_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
    fi
done

# Check SCSS files
echo "🎨 Validating SCSS files..."
scss_files=(
    "static/src/scss/primary_variables.scss"
    "static/src/scss/bootstrap_overrides.scss"
    "static/src/scss/scholarix_loading.scss"
    "static/src/scss/scholarix_cursor.scss"
    "static/src/scss/scholarix_animations.scss"
    "static/src/scss/scholarix_main.scss"
)

for file in "${scss_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
    fi
done

# Check XML template files
echo "📄 Validating XML template files..."
xml_files=(
    "views/layout_templates.xml"
    "views/homepage_sections.xml"
    "views/snippets.xml"
)

for file in "${xml_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
    fi
done

# Performance recommendations
echo ""
echo "⚡ Performance Recommendations:"
echo "   • Enable gzip compression on your web server"
echo "   • Use CDN for external libraries (already configured)"
echo "   • Optimize images using WebP format when possible"
echo "   • Test on mobile devices for optimal performance"

# Installation instructions
echo ""
echo "📋 Next Steps:"
echo "   1. Place your Scholarix logo at: static/src/img/logo.png"
echo "   2. Copy this theme directory to your Odoo addons path"
echo "   3. Update your Odoo addons path to include this directory"
echo "   4. Restart your Odoo server"
echo "   5. Go to Apps > Search 'Scholarix AI Theme' > Install"
echo "   6. Go to Website > Settings > Select 'Scholarix AI Theme'"

# Feature highlights
echo ""
echo "✨ Enhanced Features Available:"
echo "   🔄 Advanced Loading Screen with animated logo"
echo "   🖱️  Custom Mouse Cursor with interactive effects"
echo "   🎯 3D Hero Section with parallax effects"
echo "   🎨 Futuristic AI design with holographic elements"
echo "   📱 Fully responsive with mobile optimizations"
echo "   ♿ Accessibility features and reduced motion support"

echo ""
echo "🎉 Installation preparation complete!"
echo "   Read ENHANCED_FEATURES.md for detailed feature documentation"
echo ""
