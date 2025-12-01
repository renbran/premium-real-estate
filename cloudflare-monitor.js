// OSUS Properties - Cloudflare Monitoring Script
// Real-time website monitoring with alerts

const https = require('https');
const fs = require('fs');

const CONFIG = {
  siteUrl: 'https://properties.erposus.com',
  checkInterval: 30000, // 30 seconds
  alertThresholds: {
    responseTime: 3000, // 3 seconds
    uptime: 99.9, // 99.9%
  }
};

let stats = {
  totalChecks: 0,
  successfulChecks: 0,
  failedChecks: 0,
  averageResponseTime: 0,
  responseTimes: [],
  lastCheck: null,
  uptime: 100,
  status: 'Unknown'
};

function checkWebsite() {
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    https.get(CONFIG.siteUrl, (res) => {
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      stats.totalChecks++;
      stats.lastCheck = new Date().toISOString();
      
      if (res.statusCode === 200) {
        stats.successfulChecks++;
        stats.status = 'ONLINE';
        stats.responseTimes.push(responseTime);
        
        // Keep only last 100 response times
        if (stats.responseTimes.length > 100) {
          stats.responseTimes.shift();
        }
        
        // Calculate average
        stats.averageResponseTime = 
          stats.responseTimes.reduce((a, b) => a + b, 0) / stats.responseTimes.length;
        
        // Calculate uptime
        stats.uptime = (stats.successfulChecks / stats.totalChecks) * 100;
        
        console.log(`✅ [${new Date().toLocaleTimeString()}] ONLINE - ${responseTime}ms`);
        
        // Alert if response time is slow
        if (responseTime > CONFIG.alertThresholds.responseTime) {
          console.warn(`⚠️  SLOW RESPONSE: ${responseTime}ms (threshold: ${CONFIG.alertThresholds.responseTime}ms)`);
        }
        
        resolve({ success: true, responseTime, statusCode: res.statusCode });
      } else {
        stats.failedChecks++;
        stats.status = `ERROR ${res.statusCode}`;
        console.error(`❌ [${new Date().toLocaleTimeString()}] ERROR - Status: ${res.statusCode}`);
        resolve({ success: false, statusCode: res.statusCode });
      }
    }).on('error', (err) => {
      stats.totalChecks++;
      stats.failedChecks++;
      stats.status = 'OFFLINE';
      stats.lastCheck = new Date().toISOString();
      stats.uptime = (stats.successfulChecks / stats.totalChecks) * 100;
      
      console.error(`❌ [${new Date().toLocaleTimeString()}] OFFLINE - ${err.message}`);
      reject(err);
    });
  });
}

function displayStats() {
  console.clear();
  console.log('═══════════════════════════════════════════════════');
  console.log('🚀 OSUS Properties - Real-Time Monitoring');
  console.log('═══════════════════════════════════════════════════');
  console.log(`📊 Status: ${stats.status}`);
  console.log(`🌐 URL: ${CONFIG.siteUrl}`);
  console.log(`⏱️  Last Check: ${stats.lastCheck || 'Never'}`);
  console.log('───────────────────────────────────────────────────');
  console.log(`✓ Total Checks: ${stats.totalChecks}`);
  console.log(`✓ Successful: ${stats.successfulChecks}`);
  console.log(`✗ Failed: ${stats.failedChecks}`);
  console.log(`📈 Uptime: ${stats.uptime.toFixed(2)}%`);
  console.log(`⚡ Avg Response: ${Math.round(stats.averageResponseTime)}ms`);
  console.log('═══════════════════════════════════════════════════');
  
  // Alert if uptime is below threshold
  if (stats.uptime < CONFIG.alertThresholds.uptime) {
    console.warn(`🚨 UPTIME ALERT: ${stats.uptime.toFixed(2)}% (threshold: ${CONFIG.alertThresholds.uptime}%)`);
  }
  
  console.log('Press Ctrl+C to stop monitoring\n');
}

function saveStats() {
  const report = {
    timestamp: new Date().toISOString(),
    stats,
    config: CONFIG
  };
  
  fs.writeFileSync('monitoring-report.json', JSON.stringify(report, null, 2));
}

async function monitor() {
  console.log('🚀 Starting website monitoring...');
  console.log(`📍 Target: ${CONFIG.siteUrl}`);
  console.log(`⏱️  Interval: ${CONFIG.checkInterval / 1000} seconds\n`);
  
  // Initial check
  await checkWebsite().catch(() => {});
  displayStats();
  
  // Regular checks
  setInterval(async () => {
    await checkWebsite().catch(() => {});
    displayStats();
    saveStats();
  }, CONFIG.checkInterval);
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Stopping monitoring...');
  saveStats();
  console.log('📊 Final report saved to monitoring-report.json');
  process.exit(0);
});

// Start monitoring
monitor();
