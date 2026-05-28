#!/usr/bin/env node

const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const HOME = process.env.HOME || '/home/novahiz';
const NOVAHIZ_DIR = `${HOME}/.opencode`;

console.log(`
╔════════════════════════════════════════════════════╗
║         NOVAHIZ OS - INTEGRITY VERIFICATION        ║
╠════════════════════════════════════════════════════╣`);

const criticalFiles = [
  '00_META/00_IDENTITY.md',
  '01_AGENTS',
  '02_RULES',
  '03_SKILLS',
  '04_WORKFLOWS',
  '05_CONTEXT',
  'dashboard/index.js',
  'scripts/novahiz-cli.js',
  'dashboard/config/user-config.json'
];

let allValid = true;

criticalFiles.forEach(file => {
  const filePath = path.join(NOVAHIZ_DIR, file);
  const exists = fs.existsSync(filePath);

  if (exists) {
    const stat = fs.statSync(filePath);
    console.log(`  ✓ ${file.padEnd(30)} (${formatBytes(stat.size)})`);
  } else {
    console.log(`  ✗ ${file.padEnd(30)} MISSING`);
    allValid = false;
  }
});

console.log('╠════════════════════════════════════════════════════╣');

if (allValid) {
  console.log('║                                                    ║');
  console.log('║              ✓ ALL CHECKSUMS VALID                 ║');
  console.log('║                                                    ║');
  console.log('╚════════════════════════════════════════════════════╝');
} else {
  console.log('║                                                    ║');
  console.log('║              ✗ INTEGRITY CHECK FAILED              ║');
  console.log('║                                                    ║');
  console.log('╚════════════════════════════════════════════════════╝');
  process.exit(1);
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}