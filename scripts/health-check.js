#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/home/novahiz';
const NOVAHIZ_DIR = `${HOME}/.opencode`;

console.log('\n🔍 Novahiz OS Health Check\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const checks = [
  { name: 'Core Identity', path: `${NOVAHIZ_DIR}/00_META/00_IDENTITY.md`, critical: true },
  { name: 'Agent Profiles', path: `${NOVAHIZ_DIR}/01_AGENTS`, critical: true },
  { name: 'Rule Files', path: `${NOVAHIZ_DIR}/02_RULES`, critical: true },
  { name: 'Skills Directory', path: `${NOVAHIZ_DIR}/03_SKILLS`, critical: true },
  { name: 'Workflows', path: `${NOVAHIZ_DIR}/04_WORKFLOWS`, critical: false },
  { name: 'Context Templates', path: `${NOVAHIZ_DIR}/05_CONTEXT`, critical: false },
  { name: 'Dashboard', path: `${NOVAHIZ_DIR}/dashboard/index.js`, critical: false },
  { name: 'Scripts', path: `${NOVAHIZ_DIR}/scripts`, critical: false },
  { name: 'Cache', path: `${NOVAHIZ_DIR}/cache`, critical: false },
  { name: 'Logs', path: `${NOVAHIZ_DIR}/logs`, critical: false },
  { name: 'Backups', path: `${NOVAHIZ_DIR}/backups`, critical: false },
  { name: 'OpenCode Config', path: `${HOME}/.config/opencode/opencode.jsonc`, critical: true }
];

let passed = 0;
let warnings = 0;
let errors = 0;

checks.forEach(({ name, path: checkPath, critical }) => {
  const exists = fs.existsSync(checkPath);
  const icon = exists ? '✓' : '✗';
  const type = critical ? 'CRITICAL' : 'INFO';

  console.log(`  ${icon} [${type}] ${name.padEnd(20)}`);

  if (exists) {
    passed++;
  } else {
    if (critical) {
      errors++;
      console.log(`       └─ Missing! This may cause system issues.`);
    } else {
      warnings++;
      console.log(`       └─ Optional component not found.`);
    }
  }
});

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
console.log(`  Results: ${passed} passed, ${warnings} warnings, ${errors} errors\n`);

const status = errors === 0 ? '✓ HEALTHY' : warnings === 0 ? '⚠ CAUTION' : '✗ UNHEALTHY';
console.log(`  Overall Status: ${status}\n`);

if (errors === 0) {
  console.log('  All critical components are operational.\n');
} else {
  console.log('  Please address critical issues before continuing.\n');
}

process.exit(errors > 0 ? 1 : 0);