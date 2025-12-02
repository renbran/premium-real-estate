const fs = require('fs');
const path = require('path');

console.log('🔍 Verifying build output...\n');

let errors = [];
let warnings = [];
let success = [];

// Check if dist directory exists
if (!fs.existsSync('dist')) {
  errors.push('dist directory does not exist. Run: npm run build');
} else {
  success.push('dist directory exists');
}

// Check required files
const requiredFiles = [
  'dist/index.html',
  'dist/_redirects'
];

requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    const stats = fs.statSync(file);
    success.push(`${file} (${(stats.size / 1024).toFixed(2)} KB)`);
  } else {
    errors.push(`Missing required file: ${file}`);
  }
});

// Check static assets
const staticDirs = [
  'dist/static',
  'dist/static/media',
  'dist/static/media/images',
  'dist/static/media/videos'
];

staticDirs.forEach(dir => {
  if (fs.existsSync(dir)) {
    success.push(`${dir} exists`);
  } else {
    warnings.push(`Optional directory missing: ${dir}`);
  }
});

// Count files by type
function getFileStats(dir) {
  const stats = {
    html: 0,
    images: 0,
    videos: 0,
    other: 0,
    totalSize: 0
  };

  if (!fs.existsSync(dir)) return stats;

  function traverse(currentDir) {
    const files = fs.readdirSync(currentDir);
    files.forEach(file => {
      const filePath = path.join(currentDir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        traverse(filePath);
      } else {
        stats.totalSize += stat.size;
        const ext = path.extname(file).toLowerCase();
        
        if (ext === '.html') stats.html++;
        else if (['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'].includes(ext)) stats.images++;
        else if (['.mp4', '.webm', '.mov'].includes(ext)) stats.videos++;
        else stats.other++;
      }
    });
  }

  traverse(dir);
  return stats;
}

if (fs.existsSync('dist')) {
  const stats = getFileStats('dist');
  
  console.log('📊 Build Statistics:');
  console.log(`   HTML files: ${stats.html}`);
  console.log(`   Images: ${stats.images}`);
  console.log(`   Videos: ${stats.videos}`);
  console.log(`   Other files: ${stats.other}`);
  console.log(`   Total size: ${(stats.totalSize / (1024 * 1024)).toFixed(2)} MB\n`);
}

// Print results
if (success.length > 0) {
  console.log('✅ Success:');
  success.forEach(msg => console.log(`   ✓ ${msg}`));
  console.log('');
}

if (warnings.length > 0) {
  console.log('⚠️  Warnings:');
  warnings.forEach(msg => console.log(`   ! ${msg}`));
  console.log('');
}

if (errors.length > 0) {
  console.log('❌ Errors:');
  errors.forEach(msg => console.log(`   ✗ ${msg}`));
  console.log('');
  console.log('Build verification failed. Please fix the errors above.\n');
  process.exit(1);
}

console.log('✨ Build verification passed! Ready for deployment.\n');
process.exit(0);
