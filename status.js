const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('');
console.log('═══════════════════════════════════════════════');
console.log('   OSUS Properties - Deployment Status');
console.log('═══════════════════════════════════════════════');
console.log('');

let issues = [];
let warnings = [];
let success = [];

// Check Node.js and npm
try {
  const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
  const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
  success.push(`Node.js ${nodeVersion}, npm v${npmVersion}`);
} catch (error) {
  issues.push('Node.js or npm not found');
}

// Check project files
const requiredFiles = [
  'index.html',
  'package.json',
  'build.js',
  'wrangler.toml',
  '_redirects'
];

requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    success.push(`${file} exists`);
  } else {
    issues.push(`Missing: ${file}`);
  }
});

// Check static directory
if (fs.existsSync('static/media')) {
  const images = fs.existsSync('static/media/images');
  const videos = fs.existsSync('static/media/videos');
  const logo = fs.existsSync('static/media/images/osus-logo.png');
  
  if (images) success.push('static/media/images/ exists');
  else warnings.push('static/media/images/ not found');
  
  if (videos) success.push('static/media/videos/ exists');
  else warnings.push('static/media/videos/ not found');
  
  if (logo) success.push('Logo file exists');
  else warnings.push('Logo file not found');
  
  // Count files
  try {
    const imageFiles = fs.readdirSync('static/media/images/properties').length;
    const staffFiles = fs.readdirSync('static/media/images/staff').length;
    const videoFiles = fs.readdirSync('static/media/videos').length;
    
    success.push(`Properties: ${imageFiles} images`);
    success.push(`Staff: ${staffFiles} photos`);
    success.push(`Videos: ${videoFiles} files`);
  } catch (e) {
    warnings.push('Could not count media files');
  }
} else {
  issues.push('static/media directory not found');
}

// Check dist directory
if (fs.existsSync('dist')) {
  const distFiles = fs.readdirSync('dist');
  success.push(`dist/ directory exists (${distFiles.length} items)`);
  
  if (fs.existsSync('dist/index.html')) {
    success.push('dist/index.html exists');
  } else {
    warnings.push('dist/index.html not found (run: npm run build)');
  }
} else {
  warnings.push('dist/ directory not found (run: npm run build)');
}

// Check Wrangler
try {
  const wranglerVersion = execSync('npx wrangler --version', { encoding: 'utf8' }).trim();
  success.push(`Wrangler installed: ${wranglerVersion.split('\n')[0]}`);
  
  // Check auth
  try {
    execSync('npx wrangler whoami', { encoding: 'utf8', stdio: 'pipe' });
    success.push('Wrangler authenticated ✓');
  } catch (error) {
    warnings.push('Not logged in to Wrangler (run: npx wrangler login)');
  }
} catch (error) {
  warnings.push('Wrangler not accessible');
}

// Check node_modules (optional since we only use built-in modules)
if (fs.existsSync('node_modules')) {
  success.push('Dependencies installed');
} else {
  warnings.push('node_modules not found (optional - only needed for additional packages)');
}

// Display results
console.log('🟢 SUCCESS:');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
success.forEach(msg => console.log(`  ✓ ${msg}`));

if (warnings.length > 0) {
  console.log('');
  console.log('🟡 WARNINGS:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  warnings.forEach(msg => console.log(`  ⚠ ${msg}`));
}

if (issues.length > 0) {
  console.log('');
  console.log('🔴 ISSUES:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  issues.forEach(msg => console.log(`  ✗ ${msg}`));
}

console.log('');
console.log('═══════════════════════════════════════════════');

// Overall status
if (issues.length === 0 && warnings.length === 0) {
  console.log('✅ All systems ready for deployment!');
  console.log('');
  console.log('Run: npm run deploy');
} else if (issues.length === 0) {
  console.log('⚠️  Ready with warnings');
  console.log('');
  console.log('You can deploy, but review warnings above.');
} else {
  console.log('❌ Issues found - please fix before deploying');
  console.log('');
  console.log('Fix the issues above, then try again.');
}

console.log('═══════════════════════════════════════════════');
console.log('');

process.exit(issues.length > 0 ? 1 : 0);
