const fs = require('fs');
const path = require('path');

console.log('🚀 Starting build process...\n');

// Create dist directory if it doesn't exist
if (fs.existsSync('dist')) {
  console.log('🗑️  Cleaning existing dist directory...');
  fs.rmSync('dist', { recursive: true, force: true });
}

fs.mkdirSync('dist', { recursive: true });
console.log('✓ Created fresh dist directory');

// Copy index.html
if (!fs.existsSync('index.html')) {
  console.error('❌ Error: index.html not found!');
  process.exit(1);
}
fs.copyFileSync('index.html', 'dist/index.html');
console.log('✓ Copied index.html');

// Copy _redirects
if (fs.existsSync('_redirects')) {
  fs.copyFileSync('_redirects', 'dist/_redirects');
  console.log('✓ Copied _redirects');
} else {
  console.log('⚠️  Warning: _redirects file not found (optional)');
}

// Recursive copy function
function copyDir(src, dest) {
  if (!fs.existsSync(src)) {
    console.error(`❌ Error: Source directory ${src} not found!`);
    return false;
  }

  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  const files = fs.readdirSync(src);
  let fileCount = 0;
  
  files.forEach(file => {
    const srcFile = path.join(src, file);
    const destFile = path.join(dest, file);
    
    if (fs.statSync(srcFile).isDirectory()) {
      copyDir(srcFile, destFile);
    } else {
      fs.copyFileSync(srcFile, destFile);
      fileCount++;
    }
  });
  
  return true;
}

// Copy static directory (preserving structure)
if (fs.existsSync('static')) {
  console.log('📦 Copying static assets...');
  copyDir('static', 'dist/static');
  console.log('✓ Copied static directory');
} else {
  console.log('⚠️  Warning: static directory not found');
}

// Count files
function countFiles(dir) {
  let count = 0;
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      count += countFiles(filePath);
    } else {
      count++;
    }
  });
  return count;
}

const totalFiles = countFiles('dist');

console.log('\n✨ Build complete!');
console.log(`📊 Total files in dist: ${totalFiles}`);
console.log('📁 Build output directory: dist/');
console.log('\n🚀 Ready for deployment!');
console.log('Run: npm run deploy\n');
