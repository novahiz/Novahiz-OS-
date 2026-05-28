#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || '/home/novahiz';
const REGISTRY_PATH = `${HOME}/.opencode/registry/novahiz-registry.json`;
const AGENTS_DIR = `${HOME}/.opencode/agents`;

const args = process.argv.slice(2);

function loadRegistry() {
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
}

function loadAgentFile(agentId) {
  const agentPath = path.join(AGENTS_DIR, `${agentId}.yaml`);
  if (fs.existsSync(agentPath)) {
    return fs.readFileSync(agentPath, 'utf8');
  }
  return null;
}

function classifyTask(task) {
  const taskLower = task.toLowerCase();
  
  const simpleKeywords = ['read', 'simple', 'quick', 'check', 'list', 'show', 'get'];
  const complexKeywords = ['design', 'architecture', 'refactor', 'create', 'build', 'implement', 'system', 'complete'];
  
  let score = 0;
  simpleKeywords.forEach(k => { if (taskLower.includes(k)) score--; });
  complexKeywords.forEach(k => { if (taskLower.includes(k)) score++; });
  
  if (score <= -1) return 'SIMPLE';
  if (score >= 1) return 'COMPLEX';
  return 'MEDIUM';
}

function selectAgents(task, count = 3) {
  const registry = loadRegistry();
  const activeAgents = registry.agents.filter(a => a.status === 'active');
  
  const domainKeywords = {
    design: ['design', 'ui', 'ux', 'frontend', 'visual', 'interface'],
    performance: ['performance', 'speed', 'optimize', 'load', 'core web vitals'],
    database: ['database', 'sql', 'query', 'data', 'schema', 'mongodb'],
    architecture: ['architecture', 'system', 'microservice', 'api', 'pattern'],
    security: ['security', 'auth', 'crypt', 'vulnerability', 'owasp'],
    quality: ['test', 'quality', 'review', 'lint', 'debug'],
    marketing: ['marketing', 'copy', 'content', 'seo', 'growth'],
    strategy: ['strategy', 'planning', 'roadmap', 'decision'],
    execution: ['build', 'deploy', 'devops', 'ci', 'cd'],
    memory: ['memory', 'context', 'retrieve', 'knowledge']
  };
  
  const taskLower = task.toLowerCase();
  const relevantDomains = [];
  
  Object.entries(domainKeywords).forEach(([domain, keywords]) => {
    if (keywords.some(k => taskLower.includes(k))) {
      relevantDomains.push(domain);
    }
  });
  
  const ranked = activeAgents.map(agent => {
    let relevance = 0;
    if (relevantDomains.includes(agent.domain)) relevance += 10;
    relevance += agent.score / 10;
    return { ...agent, relevance };
  });
  
  ranked.sort((a, b) => b.relevance - a.relevance);
  return ranked.slice(0, Math.min(count, ranked.length));
}

function showCouncilHeader(task, classification, agents) {
  console.log(`\n`);
  console.log(`╔══════════════════════════════════════════════════════════════╗`);
  console.log(`║            NOVAHIZ COUNCIL - DELIBERATION                     ║`);
  console.log(`╠══════════════════════════════════════════════════════════════╣`);
  console.log(`║  Task: ${task.substring(0, 55).padEnd(55)}║`);
  console.log(`╠══════════════════════════════════════════════════════════════╣`);
  console.log(`║  Classification: ${classification.padEnd(43)}║`);
  console.log(`║  Deliberating Agents: ${agents.length}`.padEnd(44) + '║');
  console.log(`╠══════════════════════════════════════════════════════════════╣`);
  
  agents.forEach((agent, i) => {
    const name = agent.name.padEnd(12);
    const domain = agent.domain.padEnd(12);
    const score = String(agent.score).padStart(3);
    console.log(`║  ${i + 1}. ${name} | ${domain} | Score: ${score}/100`.padEnd(58) + '║');
  });
  
  console.log(`╚══════════════════════════════════════════════════════════════╝\n`);
}

function simulateDeliberation(task, agents) {
  const votes = [];
  const consensusThreshold = 60;
  
  console.log(`╔══════════════════════════════════════════════════════════════╗`);
  console.log(`║                    DELIBERATION PHASE                          ║`);
  console.log(`╠══════════════════════════════════════════════════════════════╣`);
  
  agents.forEach((agent, i) => {
    const voteStrength = Math.min(100, agent.score + Math.random() * 10);
    const vote = Math.floor(voteStrength);
    const approved = vote >= consensusThreshold;
    
    const status = approved ? '✓' : '✗';
    const opinion = approved 
      ? `Approves (Vote: ${vote}%)` 
      : `Suggests refinement (Vote: ${vote}%)`;
    
    console.log(`║  ${agent.name}:`);
    console.log(`║    ${status} ${opinion}`.padEnd(57) + '║');
    
    votes.push({
      agent: agent.name,
      domain: agent.domain,
      vote: vote,
      approved: approved
    });
  });
  
  console.log(`╚══════════════════════════════════════════════════════════════╝\n`);
  
  const approvedVotes = votes.filter(v => v.approved).length;
  const totalVotes = votes.length;
  const consensus = (approvedVotes / totalVotes) * 100;
  const passed = consensus >= consensusThreshold;
  
  console.log(`╔══════════════════════════════════════════════════════════════╗`);
  console.log(`║                    RESULTS PHASE                              ║`);
  console.log(`╠══════════════════════════════════════════════════════════════╣`);
  console.log(`║  Approved: ${approvedVotes}/${totalVotes}`.padEnd(57) + '║');
  console.log(`║  Consensus: ${consensus.toFixed(1)}%`.padEnd(57) + '║');
  console.log(`║  Threshold: ${consensusThreshold}%`.padEnd(57) + '║');
  console.log(`╠══════════════════════════════════════════════════════════════╣`);
  
  if (passed) {
    console.log(`║  ✓ DECISION: APPROVED`.padEnd(57) + '║');
    console.log(`║    Proceeding with execution...`.padEnd(57) + '║');
  } else {
    console.log(`║  ✗ DECISION: BLOCKED`.padEnd(57) + '║');
    console.log(`║    Requires refinement before proceeding.`.padEnd(57) + '║');
  }
  
  console.log(`╚══════════════════════════════════════════════════════════════╝\n`);
  
  return {
    task: task,
    classification: classifyTask(task),
    agents: agents.map(a => a.name),
    votes: votes,
    consensus: consensus,
    threshold: consensusThreshold,
    decision: passed ? 'APPROVED' : 'BLOCKED'
  };
}

function showHelp() {
  console.log(`
╔════════════════════════════════════════════════════╗
║      NOVAHIZ COUNCIL DELIBERATION - HELP           ║
╠════════════════════════════════════════════════════╣
║                                                     ║
║  Usage: council-deliberate.js [task]               ║
║                                                     ║
║  Examples:                                         ║
║    council-deliberate.js "Design a new API"        ║
║    council-deliberate.js "Refactor the frontend"    ║
║    council-deliberate.js "Create a database schema"║
║                                                     ║
║  The script will:                                  ║
║    1. Classify the task (SIMPLE/MEDIUM/COMPLEX)   ║
║    2. Select 3-5 relevant agents                   ║
║    3. Simulate deliberation with votes             ║
║    4. Calculate consensus (60% threshold)          ║
║    5. Return decision (APPROVED/BLOCKED)           ║
║                                                     ║
╚════════════════════════════════════════════════════╝
  `);
}

if (args.length === 0 || args[0] === 'help') {
  showHelp();
} else {
  const task = args.join(' ');
  const classification = classifyTask(task);
  const agents = selectAgents(task, 5);
  
  showCouncilHeader(task, classification, agents);
  const result = simulateDeliberation(task, agents);
  
  console.log('Council Result:', JSON.stringify(result, null, 2));
}