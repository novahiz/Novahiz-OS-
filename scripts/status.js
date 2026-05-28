#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/home/novahiz';
const NOVAHIZ_DIR = `${HOME}/.opencode`;

console.log(`
╔════════════════════════════════════════════════════╗
║           NOVAHIZ OS v1.7 - STATUS                  ║
╠════════════════════════════════════════════════════╣
║  Mode:        OpenCode-Exclusive                   ║
║  Version:     1.7                                  ║
║  Location:    ${NOVAHIZ_DIR.padEnd(27)}║
║  Status:      Running                              ║
╚════════════════════════════════════════════════════╝

Core Components:
`);

const components = [
  { name: 'Identity', path: '00_META/00_IDENTITY.md', icon: '✓' },
  { name: 'Agents', path: '01_AGENTS', icon: '✓' },
  { name: 'Rules', path: '02_RULES', icon: '✓' },
  { name: 'Skills', path: '03_SKILLS', icon: '✓' },
  { name: 'Workflows', path: '04_WORKFLOWS', icon: '✓' },
  { name: 'Context', path: '05_CONTEXT', icon: '✓' },
  { name: 'Dashboard', path: 'dashboard/index.js', icon: '✓' },
  { name: 'Scripts', path: 'scripts', icon: '✓' }
];

components.forEach(comp => {
  const fullPath = path.join(NOVAHIZ_DIR, comp.path);
  const exists = fs.existsSync(fullPath);
  const status = exists ? '✓' : '✗';
  console.log(`  ${status} ${comp.name.padEnd(12)} - ${fullPath}`);
});

const configPath = path.join(HOME, '.config/opencode/opencode.jsonc');
const configExists = fs.existsSync(configPath);
console.log(`
Configuration:
  ${configExists ? '✓' : '✗'} opencode.jsonc

Dashboard:
  ${fs.existsSync(path.join(NOVAHIZ_DIR, 'dashboard/index.js')) ? '✓' : '✗'} TUI Available
`);