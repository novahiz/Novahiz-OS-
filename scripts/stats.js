#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/home/novahiz';
const NOVAHIZ_DIR = `${HOME}/.opencode`;

console.log(`
╔════════════════════════════════════════════════════╗
║           NOVAHIZ STATISTICS                       ║
╠════════════════════════════════════════════════════╣`);

const stats = {
  'Agents': countFiles(`${NOVAHIZ_DIR}/01_AGENTS`),
  'Rules': countFiles(`${NOVAHIZ_DIR}/02_RULES`),
  'Skills': countFiles(`${NOVAHIZ_DIR}/03_SKILLS`),
  'Workflows': countFiles(`${NOVAHIZ_DIR}/04_WORKFLOWS`),
  'Context': countFiles(`${NOVAHIZ_DIR}/05_CONTEXT`),
  'Themes': countFiles(`${NOVAHIZ_DIR}/dashboard/config/themes`),
  'Backgrounds': countFiles(`${NOVAHIZ_DIR}/dashboard/config/backgrounds`),
  'Layouts': countFiles(`${NOVAHIZ_DIR}/dashboard/config/layouts`),
  'Scripts': countFiles(`${NOVAHIZ_DIR}/scripts`)
};

Object.entries(stats).forEach(([key, value]) => {
  console.log(`║  ${key.padEnd(12)}: ${String(value).padEnd(5)}`.padEnd(45) + '║');
});

const logsCount = fs.existsSync(`${NOVAHIZ_DIR}/logs`) ? fs.readdirSync(`${NOVAHIZ_DIR}/logs`).length : 0;
const cacheSize = calculateDirSize(`${NOVAHIZ_DIR}/cache`);

console.log(`╠════════════════════════════════════════════════════╣`);
console.log(`║  Activity Log Entries: ${String(logsCount).padEnd(22)}║`);
console.log(`║  Cache Size: ${(cacheSize / 1024).toFixed(2)} KB`.padEnd(45) + '║');
console.log('╚════════════════════════════════════════════════════╝\n');

function countFiles(dir) {
  if (!fs.existsSync(dir)) return 0;
  return fs.readdirSync(dir).filter(f => !f.startsWith('.')).length;
}

function calculateDirSize(dir) {
  if (!fs.existsSync(dir)) return 0;
  let size = 0;
  fs.readdirSync(dir).forEach(file => {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      size += calculateDirSize(filePath);
    } else {
      size += fs.statSync(filePath).size;
    }
  });
  return size;
}