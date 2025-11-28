const fs = require('fs');
const path = require('path');

// Create dist directory if it doesn't exist
if (!fs.existsSync('dist')) {
  fs.mkdirSync('dist', { recursive: true });
}

// Copy index.html
fs.copyFileSync('index.html', 'dist/index.html');
console.log('✓ Copied index.html');

// Copy _redirects
fs.copyFileSync('_redirects', 'dist/_redirects');
console.log('✓ Copied _redirects');

// Recursive copy function
function copyDir(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  const files = fs.readdirSync(src);
  files.forEach(file => {
    const srcFile = path.join(src, file);
    const destFile = path.join(dest, file);
    
    if (fs.statSync(srcFile).isDirectory()) {
      copyDir(srcFile, destFile);
    } else {
      fs.copyFileSync(srcFile, destFile);
    }
  });
}

// Copy static/media directory
copyDir('static/media', 'dist/media');
console.log('✓ Copied static/media');

console.log('\n✨ Build complete! All files ready in dist/');
