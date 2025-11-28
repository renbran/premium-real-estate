# OSUS Properties - Project Structure Guide

## 📊 Overview

Your project is now organized into **two main sections**:

1. **`website_automation/`** - Standalone website tools & utilities
2. **`custom/website_osus_properties/`** - Odoo module

---

## 📂 Folder Structure

```
d:\odoo-docker\scholarix/
│
├── 📁 website_automation/              ← WEBSITE UTILITIES (New!)
│   ├── 📄 README.md
│   ├── 📄 ANIMATION_GENERATION_GUIDE.md
│   ├── 📄 MEDIA_SETUP.md
│   ├── 🐍 generate_osus_animation.py
│   ├── 🪟 generate_animation.bat
│   ├── 🐧 generate_animation.sh
│   └── 📄 copy-media.ps1
│
└── 📁 custom/
    └── 📁 website_osus_properties/     ← ODOO MODULE
        ├── 🐍 __init__.py
        ├── 📋 __manifest__.py
        ├── 📄 README.md
        ├── 📁 templates/
        │   └── 📄 osus_homepage.xml
        └── 📁 static/
            └── src/
                ├── css/
                └── media/
                    ├── videos/
                    └── images/

```

---

## 🎯 When to Use Each Folder

### `website_automation/` folder (FOR WEBSITE CONTENT CREATORS)

Use this folder for:

✅ **Generating 4K animations**
```bash
cd d:\odoo-docker\scholarix\website_automation
.\generate_animation.bat              # Windows
# OR
./generate_animation.sh              # macOS/Linux
```

✅ **Copying media files**
```powershell
cd d:\odoo-docker\scholarix\website_automation
.\copy-media.ps1
```

✅ **Reading documentation**
- `ANIMATION_GENERATION_GUIDE.md` - How to create 4K videos
- `MEDIA_SETUP.md` - How to deploy media files
- `README.md` - Overview of all tools

**Files in this folder:**
- `generate_osus_animation.py` - Python animation generator
- `generate_animation.bat` - Windows automation script
- `generate_animation.sh` - macOS/Linux automation script
- `copy-media.ps1` - PowerShell media copying utility

---

### `custom/website_osus_properties/` folder (FOR ODOO DEVELOPERS)

Use this folder for:

✅ **Odoo module management**
```bash
cd d:\odoo-docker\scholarix\custom\website_osus_properties
```

✅ **Modifying website templates**
- Edit `templates/osus_homepage.xml` to change layout
- Edit `static/src/css/osus_landing.css` for styling

✅ **Installing/upgrading the module**
- Odoo reads `__manifest__.py` for module info
- Odoo loads templates from `templates/` folder

**Files in this folder:**
- `__init__.py` - Python package initialization
- `__manifest__.py` - Module configuration for Odoo
- `templates/osus_homepage.xml` - Website page template
- `static/` - CSS and media directories

---

## 🚀 Typical Workflows

### Workflow 1: Generate a New 4K Animation
```bash
1. Open PowerShell
2. cd d:\odoo-docker\scholarix\website_automation
3. .\generate_animation.bat
4. Wait 4-8 hours for rendering ⏳
5. Copy output to Odoo media folder (automatic in upcoming steps)
```

### Workflow 2: Copy Media Files
```bash
1. Open PowerShell
2. cd d:\odoo-docker\scholarix\website_automation
3. .\copy-media.ps1
4. Verify all 28 files copied ✓
5. Restart Odoo service
```

### Workflow 3: Modify Website Layout
```bash
1. Navigate to custom/website_osus_properties/
2. Edit templates/osus_homepage.xml
3. Save changes
4. Refresh browser to see updates
```

### Workflow 4: Update Website Styling
```bash
1. Navigate to custom/website_osus_properties/static/src/css/
2. Edit osus_landing.css
3. Save and refresh browser
4. Clear cache if needed (Ctrl+Shift+Delete)
```

---

## 📊 File Purposes at a Glance

### Animation & Media Tools (website_automation/)
| File | Purpose | Run On |
|------|---------|--------|
| generate_osus_animation.py | Main animation generator | All OS |
| generate_animation.bat | Windows automation wrapper | Windows |
| generate_animation.sh | Unix automation wrapper | macOS/Linux |
| copy-media.ps1 | Automated media copy script | PowerShell |
| ANIMATION_GENERATION_GUIDE.md | 4K animation documentation | All |
| MEDIA_SETUP.md | Media deployment guide | All |
| README.md | Tools overview | All |

### Odoo Module (custom/website_osus_properties/)
| File | Purpose |
|------|---------|
| __init__.py | Makes folder a Python package |
| __manifest__.py | Tells Odoo about this module |
| __pycache__/ | Python compiled files |
| templates/osus_homepage.xml | Website page template |
| static/src/css/*.css | Website styling |
| static/src/media/* | Images, videos, logos |
| README.md | Module documentation |

---

## 💡 Key Concepts

### Separation of Concerns
- **website_automation/** = Content creation tools
- **website_osus_properties/** = Odoo integration

### No Dependencies
- Tools in `website_automation/` don't depend on Odoo
- Can be run on any computer with Python, Blender, FFmpeg
- Odoo module works independently

### File Organization Benefits

✅ **Clarity** - Know which files do what
✅ **Maintenance** - Update tools without affecting module
✅ **Reusability** - Use tools for other projects
✅ **Scalability** - Add more utilities easily
✅ **Version Control** - Better git history tracking

---

## 📋 Common Tasks

### "I need to generate a 4K animation"
→ Use `website_automation/ANIMATION_GENERATION_GUIDE.md`

### "I need to copy media files"
→ Use `website_automation/copy-media.ps1`

### "I need to change the landing page layout"
→ Edit `custom/website_osus_properties/templates/osus_homepage.xml`

### "I need to change colors/styling"
→ Edit `custom/website_osus_properties/static/src/css/osus_landing.css`

### "I need to troubleshoot the module"
→ Check `custom/website_osus_properties/README.md`

### "I need to install the module in Odoo"
→ Odoo automatically sees modules in `custom/` folder

---

## ⚙️ System Requirements

### For website_automation/ tools:
- Python 3.10+
- Blender 4.0+ (for animation)
- FFmpeg (for video compilation)
- GPU: RTX 2080+ (optional, for faster rendering)
- RAM: 32GB minimum
- Storage: 150GB free for rendering

### For website_osus_properties/ module:
- Odoo 17+
- Web browser to view website
- No special requirements

---

## 🔗 Related Documentation

**In this folder:**
- `FOLDER_ORGANIZATION.md` - Migration details

**In website_automation/ folder:**
- `README.md` - Tools overview
- `ANIMATION_GENERATION_GUIDE.md` - Animation guide
- `MEDIA_SETUP.md` - Media deployment

**In custom/website_osus_properties/ folder:**
- `README.md` - Module documentation

---

## ✅ Checklist for Success

Getting started with the new structure:

- [ ] Navigate to `website_automation/` folder
- [ ] Read `README.md` for tools overview
- [ ] Check `ANIMATION_GENERATION_GUIDE.md` for animation steps
- [ ] Run `copy-media.ps1` to copy media files
- [ ] Verify Odoo module in `custom/website_osus_properties/`
- [ ] Restart Odoo service
- [ ] View website in browser ✨

---

## 🆘 Troubleshooting

**Q: Files are in wrong folder?**
A: Check `FOLDER_ORGANIZATION.md` for current structure

**Q: Animation won't run?**
A: See `website_automation/ANIMATION_GENERATION_GUIDE.md`

**Q: Media files not showing?**
A: See `website_automation/MEDIA_SETUP.md`

**Q: Odoo module not working?**
A: Check `custom/website_osus_properties/README.md`

---

## 📞 Quick Links

| Need | Location |
|------|----------|
| Animation help | `website_automation/ANIMATION_GENERATION_GUIDE.md` |
| Media help | `website_automation/MEDIA_SETUP.md` |
| Tools overview | `website_automation/README.md` |
| Module info | `custom/website_osus_properties/README.md` |
| Organization | `FOLDER_ORGANIZATION.md` (this folder) |

---

**Ready to go!** 🚀 Your project structure is now clean and organized.
