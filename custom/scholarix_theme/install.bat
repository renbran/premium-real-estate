@echo off
REM Scholarix AI Theme Installation Script for Windows
echo 🚀 Installing Scholarix AI Theme with Enhanced Features...

REM Check if we're in the right directory
if not exist "__manifest__.py" (
    echo ❌ Error: Please run this script from the scholarix_theme directory
    pause
    exit /b 1
)

REM Check if logo exists
if not exist "static\src\img\logo.png" (
    echo ⚠️  Warning: Logo file not found at static\src\img\logo.png
    echo    Please place the Scholarix logo in this location for full functionality
)

REM Create necessary directories
echo 📁 Creating directory structure...
if not exist "static\src\img\portfolio" mkdir static\src\img\portfolio
if not exist "static\src\img\team" mkdir static\src\img\team
if not exist "static\src\img\testimonials" mkdir static\src\img\testimonials
if not exist "static\src\img\icons" mkdir static\src\img\icons
if not exist "static\src\css" mkdir static\src\css
if not exist "static\description" mkdir static\description
if not exist "views\about" mkdir views\about
if not exist "views\services" mkdir views\services
if not exist "views\portfolio" mkdir views\portfolio
if not exist "views\blog" mkdir views\blog
if not exist "views\contact" mkdir views\contact
if not exist "views\snippets" mkdir views\snippets
if not exist "views\index" mkdir views\index

echo 🔍 Checking dependencies...

REM Check JavaScript files
echo 🔧 Validating JavaScript files...
set js_files=scholarix_loader.js scholarix_cursor.js scholarix_3d_hero.js scholarix_animations.js scholarix_particles.js scholarix_main.js

for %%f in (%js_files%) do (
    if exist "static\src\js\%%f" (
        echo    ✅ static\src\js\%%f
    ) else (
        echo    ❌ Missing: static\src\js\%%f
    )
)

REM Check SCSS files
echo 🎨 Validating SCSS files...
set scss_files=primary_variables.scss bootstrap_overrides.scss scholarix_loading.scss scholarix_cursor.scss scholarix_animations.scss scholarix_main.scss

for %%f in (%scss_files%) do (
    if exist "static\src\scss\%%f" (
        echo    ✅ static\src\scss\%%f
    ) else (
        echo    ❌ Missing: static\src\scss\%%f
    )
)

REM Check XML template files
echo 📄 Validating XML template files...
set xml_files=layout_templates.xml homepage_sections.xml snippets.xml

for %%f in (%xml_files%) do (
    if exist "views\%%f" (
        echo    ✅ views\%%f
    ) else (
        echo    ❌ Missing: views\%%f
    )
)

REM Performance recommendations
echo.
echo ⚡ Performance Recommendations:
echo    • Enable gzip compression on your web server
echo    • Use CDN for external libraries (already configured)
echo    • Optimize images using WebP format when possible
echo    • Test on mobile devices for optimal performance

REM Installation instructions
echo.
echo 📋 Next Steps:
echo    1. Place your Scholarix logo at: static\src\img\logo.png
echo    2. Copy this theme directory to your Odoo addons path
echo    3. Update your Odoo addons path to include this directory
echo    4. Restart your Odoo server
echo    5. Go to Apps ^> Search 'Scholarix AI Theme' ^> Install
echo    6. Go to Website ^> Settings ^> Select 'Scholarix AI Theme'

REM Feature highlights
echo.
echo ✨ Enhanced Features Available:
echo    🔄 Advanced Loading Screen with animated logo
echo    🖱️  Custom Mouse Cursor with interactive effects
echo    🎯 3D Hero Section with parallax effects
echo    🎨 Futuristic AI design with holographic elements
echo    📱 Fully responsive with mobile optimizations
echo    ♿ Accessibility features and reduced motion support

echo.
echo 🎉 Installation preparation complete!
echo    Read ENHANCED_FEATURES.md for detailed feature documentation
echo.
pause
