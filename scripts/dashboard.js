#!/usr/bin/env node

const path = require('path');
const HOME = process.env.HOME || '/home/novahiz';
const NOVAHIZ_DIR = `${HOME}/.opencode`;
const DASHBOARD_PATH = path.join(NOVAHIZ_DIR, 'dashboard', 'index.js');

console.log('🚀 Launching Novahiz OS Dashboard...');
console.log('   Location:', DASHBOARD_PATH);

if (!require('fs').existsSync(DASHBOARD_PATH)) {
  console.error('✗ Dashboard not found at:', DASHBOARD_PATH);
  console.log('\nAvailable dashboards in ~/.opencode/dashboard/:');
  const dashboardDir = path.join(NOVAHIZ_DIR, 'dashboard');
  if (require('fs').existsSync(dashboardDir)) {
    require('fs').readdirSync(dashboardDir).forEach(f => {
      console.log('  -', f);
    });
  }
  process.exit(1);
}

console.log('  ✓ Dashboard found');

try {
  require(DASHBOARD_PATH);
} catch (error) {
  console.error('✗ Failed to launch dashboard:', error.message);
  console.log('\nMake sure you have installed the required dependencies:');
  console.log('  npm install -g blessed blessed-contrib');
  process.exit(1);
}

console.log('  ✓ Dashboard found');
console.log('  ✓ Loading configuration...');
console.log('  ✓ Initializing TUI...\n');

try {
  require(DASHBOARD_PATH);
} catch (error) {
  console.error('✗ Failed to launch dashboard:', error.message);
  console.log('\nMake sure you have installed the required dependencies:');
  console.log('  npm install -g blessed blessed-contrib');
  process.exit(1);
}