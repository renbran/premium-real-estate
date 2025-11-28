# OSUS Properties Landing Page - Media Setup Guide

## Directory Structure

Create this folder structure in your Odoo server:

```
custom/
└── website_osus_properties/
    └── static/
        └── src/
            └── media/
                ├── videos/
                │   ├── hero-video-1.mp4
                │   └── hero-video-2.mp4
                ├── images/
                │   ├── osus-logo.png
                │   ├── properties/
                │   │   ├── property-1.jpg
                │   │   ├── property-2.jpg
                │   │   ├── property-3.jpg
                │   │   ├── property-4.jpg
                │   │   ├── property-5.jpg
                │   │   └── property-6.jpg
                │   └── staff/
                │       ├── staff-01.png through staff-19.png
```

## File Mapping

### Videos (2 files)
```
Videos needed: 2
Source files:
  - D:\Downloader\download (11).mp4 → hero-video-1.mp4
  - D:\Downloader\download (8).mp4  → hero-video-2.mp4

Destination:
  custom/website_osus_properties/static/src/media/videos/
```

### Logo (1 file)
```
Logo needed: 1
Source file:
  - D:\Downloader\osus-removebg-preview.png → osus-logo.png

Destination:
  custom/website_osus_properties/static/src/media/images/
```

### Property Images (6 files)
```
Images needed: 6
Source files:
  1. Leonardo_Phoenix_10_A_futuristic_and_luxurious_interior_design_2 (1).jpg → property-1.jpg
  2. Leonardo_Phoenix_10_A_futuristic_and_luxurious_interior_design_3 (2).jpg → property-2.jpg
  3. Leonardo_Phoenix_10_A_futuristic_and_luxurious_interior_design_0 (3).jpg → property-3.jpg
  4. Leonardo_Phoenix_10_A_futuristic_and_luxurious_interior_design_3 (1).jpg → property-4.jpg
  5. Leonardo_Phoenix_10_A_futuristic_and_luxurious_interior_design_0 (2).jpg → property-5.jpg
  6. propertu.jpg → property-6.jpg

Destination:
  custom/website_osus_properties/static/src/media/images/properties/
```

### Staff Images (19 files)
```
Images needed: 19
Source files: photo_2025-04-28_*.png
Destination: custom/website_osus_properties/static/src/media/images/staff/

Rename as:
  photo_2025-04-28_10-59-49-removebg-preview.png → staff-01.png
  photo_2025-04-28_10-58-34-removebg-preview.png → staff-02.png
  photo_2025-04-28_10-58-00-removebg-preview.png → staff-03.png
  photo_2025-04-28_10-57-34-removebg-preview.png → staff-04.png
  photo_2025-04-28_10-57-20-removebg-preview.png → staff-05.png
  photo_2025-04-28_10-57-04-removebg-preview.png → staff-06.png
  photo_2025-04-28_10-55-18-removebg-preview.png → staff-07.png
  photo_2025-04-28_10-55-05-removebg-preview.png → staff-08.png
  photo_2025-04-28_10-54-21-removebg-preview.png → staff-09.png
  photo_2025-04-28_10-46-44-removebg-preview.png → staff-10.png
  photo_2025-04-28_10-46-59-removebg-preview.png → staff-11.png
  photo_2025-04-28_10-47-49-removebg-preview.png → staff-12.png
  photo_2025-04-28_10-48-37-removebg-preview.png → staff-13.png
  photo_2025-04-28_10-50-09-removebg-preview.png → staff-14.png
  photo_2025-04-28_10-50-22-removebg-preview.png → staff-15.png
  photo_2025-04-28_10-54-41-removebg-preview.png → staff-16.png
  photo_2025-04-28_10-54-53-removebg-preview.png → staff-17.png
  photo_2025-04-28_10-57-34-removebg-preview (1).png → staff-18.png
  photo_2025-04-28_11-10-37-removebg-preview.png → staff-19.png
```

## Total Files Required

| Category | Count | Format |
|----------|-------|--------|
| Videos | 2 | MP4 |
| Logo | 1 | PNG |
| Properties | 6 | JPG |
| Staff | 19 | PNG |
| **TOTAL** | **28** | Mixed |

## Setup Steps

1. **Create directories:**
   ```powershell
   New-Item -ItemType Directory -Force -Path "d:\odoo-docker\scholarix\custom\website_osus_properties\static\src\media\videos"
   New-Item -ItemType Directory -Force -Path "d:\odoo-docker\scholarix\custom\website_osus_properties\static\src\media\images\properties"
   New-Item -ItemType Directory -Force -Path "d:\odoo-docker\scholarix\custom\website_osus_properties\static\src\media\images\staff"
   ```

2. **Copy video files:**
   ```powershell
   Copy-Item "D:\Downloader\download (11).mp4" "d:\odoo-docker\scholarix\custom\website_osus_properties\static\src\media\videos\hero-video-1.mp4"
   Copy-Item "D:\Downloader\download (8).mp4" "d:\odoo-docker\scholarix\custom\website_osus_properties\static\src\media\videos\hero-video-2.mp4"
   ```

3. **Copy logo:**
   ```powershell
   Copy-Item "D:\Downloader\osus-removebg-preview.png" "d:\odoo-docker\scholarix\custom\website_osus_properties\static\src\media\images\osus-logo.png"
   ```

4. **Copy property images:**
   ```powershell
   Copy-Item "D:\old downloads\Leonardo_Phoenix_10_A_futuristic_and_luxurious_interior_design_2 (1).jpg" "d:\odoo-docker\scholarix\custom\website_osus_properties\static\src\media\images\properties\property-1.jpg"
   # ... repeat for all 6 properties
   ```

5. **Copy and rename staff images:**
   ```powershell
   # Batch rename staff photos
   # From: photo_2025-04-28_10-59-49-removebg-preview.png
   # To: staff-01.png
   ```

6. **Restart Odoo:**
   ```powershell
   # Restart your Odoo service for static files to be served
   ```

## URL Paths (After Setup)

All media will be accessible at:

```
Videos:
  /static/media/videos/hero-video-1.mp4
  /static/media/videos/hero-video-2.mp4

Logo:
  /static/media/images/osus-logo.png

Properties:
  /static/media/images/properties/property-1.jpg
  /static/media/images/properties/property-2.jpg
  ... etc

Staff:
  /static/media/images/staff/staff-01.png
  /static/media/images/staff/staff-02.png
  ... etc
```

## Troubleshooting

**Files not showing:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Restart Odoo service
3. Check file permissions (chmod 644 for images/videos)
4. Verify paths in browser DevTools Network tab

**Videos not playing:**
- Ensure MP4 files are valid (can open in media player)
- Check file size is not too large
- Verify audio codec is compatible

**Images not loading:**
- Check PNG/JPG files are valid
- Verify file names match exactly (case-sensitive on Linux)
- Ensure file permissions allow reading

## Performance Notes

- Optimize video file size before uploading
- Consider compressing large JPG files
- Use PNG for logo (supports transparency)
- Keep staff images under 500KB each
