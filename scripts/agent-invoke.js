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

function loadAgent(agentId) {
  const agentPath = path.join(AGENTS_DIR, `${agentId}.yaml`);
  if (fs.existsSync(agentPath)) {
    return fs.readFileSync(agentPath, 'utf8');
  }
  return null;
}

function invokeSubagent(agentId, task) {
  const agentPath = path.join(AGENTS_DIR, `${agentId}.yaml`);
  if (!fs.existsSync(agentPath)) {
    return { error: `Agent ${agentId} not found` };
  }

  const agent = loadRegistry().agents.find(a => a.id === agentId);
  if (!agent) {
    return { error: `Agent ${agentId} not in registry` };
  }

  console.log(`\n╔════════════════════════════════════════════╗`);
  console.log(`║  INVOKING: ${agent.name.padEnd(25)}║`);
  console.log(`╠════════════════════════════════════════════╣`);
  console.log(`║  Domain:   ${agent.domain.padEnd(25)}║`);
  console.log(`║  Score:    ${String(agent.score).padEnd(25)}║`);
  console.log(`║  Type:     ${agent.type.padEnd(25)}║`);
  console.log(`╠════════════════════════════════════════════╣`);
  console.log(`║  Task: ${task.substring(0, 30).padEnd(30)}║`);
  console.log(`╚════════════════════════════════════════════╝\n`);

  return {
    agent: agent.name,
    domain: agent.domain,
    score: agent.score,
    type: agent.type,
    status: 'invoked',
    task: task
  };
}

function invokeSimulated(agentId, task) {
  const registry = loadRegistry();
  const agent = registry.agents.find(a => a.id === agentId);

  if (!agent || agent.type !== 'simulated') {
    return { error: `Simulated agent ${agentId} not found` };
  }

  console.log(`\n╔════════════════════════════════════════════╗`);
  console.log(`║  SIMULATING: ${agent.name.padEnd(23)}║`);
  console.log(`╠════════════════════════════════════════════╣`);
  console.log(`║  Domain:   ${agent.domain.padEnd(25)}║`);
  console.log(`║  Score:    ${String(agent.score).padEnd(25)}║`);
  console.log(`║  Origin:   ${(agent.origin || 'N/A').padEnd(25)}║`);
  console.log(`╠════════════════════════════════════════════╣`);
  console.log(`║  This agent is invoked via context.         ║`);
  console.log(`╚════════════════════════════════════════════╝\n`);

  return {
    agent: agent.name,
    domain: agent.domain,
    score: agent.score,
    type: 'simulated',
    status: 'simulated',
    task: task,
    message: `${agent.name} would provide: ${agent.description}`
  };
}

function listAgents() {
  const registry = loadRegistry();
  console.log(`\n╔════════════════════════════════════════════════════╗`);
  console.log(`║           NOVAHIZ AGENT REGISTRY (${registry.agents.length})         ║`);
  console.log(`╠════════════════════════════════════════════════════╣`);

  registry.agents.forEach(agent => {
    const type = agent.type.padEnd(10);
    const name = agent.name.padEnd(12);
    const domain = agent.domain.padEnd(12);
    const score = String(agent.score).padStart(3);
    const status = agent.status === 'active' ? '●' : agent.status === 'simulated' ? '○' : '◐';

    console.log(`║ ${status} ${name} ${type} ${domain} ${score}/100 ║`);
  });

  console.log(`╠════════════════════════════════════════════════════╣`);
  console.log(`║  ● Active (subagent)   ○ Simulated   ◐ Primary    ║`);
  console.log(`╚════════════════════════════════════════════════════╝\n`);
}

function showAgent(agentId) {
  const registry = loadRegistry();
  const agent = registry.agents.find(a => a.id === agentId);

  if (!agent) {
    console.log(`Agent ${agentId} not found`);
    return;
  }

  console.log(`\n╔════════════════════════════════════════════════════╗`);
  console.log(`║  AGENT: ${agent.name.padEnd(35)}║`);
  console.log(`╠════════════════════════════════════════════════════╣`);
  console.log(`║  ID:       ${agent.id.padEnd(35)}║`);
  console.log(`║  Type:     ${agent.type.padEnd(35)}║`);
  console.log(`║  Domain:   ${agent.domain.padEnd(35)}║`);
  console.log(`║  Score:    ${String(agent.score).padEnd(35)}║`);
  console.log(`║  Status:   ${agent.status.padEnd(35)}║`);
  console.log(`╠════════════════════════════════════════════════════╣`);
  console.log(`║  Description:                                    ║`);
  const descLines = agent.description.match(/.{1,42}/g) || [agent.description];
  descLines.forEach(line => {
    console.log(`║  ${line.padEnd(42)}║`);
  });

  if (agent.specialty) {
    console.log(`╠════════════════════════════════════════════════════╣`);
    console.log(`║  Specialties:                                     ║`);
    agent.specialty.forEach(s => {
      console.log(`║    • ${s.padEnd(38)}║`);
    });
  }

  console.log(`╚════════════════════════════════════════════════════╝\n`);
}

function searchByDomain(domain) {
  const registry = loadRegistry();
  const matches = registry.agents.filter(a => a.domain.includes(domain));

  console.log(`\n╔════════════════════════════════════════════════════╗`);
  console.log(`║  DOMAIN: ${domain.padEnd(36)}║`);
  console.log(`║  Results: ${matches.length} agent(s)`.padEnd(44) + '║');
  console.log(`╠════════════════════════════════════════════════════╣`);

  matches.forEach(agent => {
    const status = agent.status === 'active' ? '●' : '○';
    console.log(`║ ${status} ${agent.name.padEnd(20)} (Score: ${agent.score})`.padEnd(44) + '║');
  });

  console.log(`╚════════════════════════════════════════════════════╝\n`);
}

function showHelp() {
  console.log(`
╔════════════════════════════════════════════════════╗
║         NOVAHIZ AGENT INVOKE - HELP                ║
╠════════════════════════════════════════════════════╣
║                                                     ║
║  Usage: agent-invoke.js [command] [args]            ║
║                                                     ║
║  Commands:                                          ║
║    list                      List all agents         ║
║    show <agent-id>           Show agent details     ║
║    invoke <agent-id> <task>  Invoke agent           ║
║    simulate <agent-id> <task> Invoke simulated      ║
║    domain <domain>           Search by domain       ║
║    help                      Show this help         ║
║                                                     ║
║  Examples:                                          ║
║    agent-invoke.js list                             ║
║    agent-invoke.js show luna-design                 ║
║    agent-invoke.js invoke kenzo-performance "..."   ║
║    agent-invoke.js domain security                   ║
║                                                     ║
╚════════════════════════════════════════════════════╝
  `);
}

if (args.length === 0) {
  showHelp();
} else {
  const cmd = args[0];

  switch (cmd) {
    case 'list':
      listAgents();
      break;
    case 'show':
      if (args[1]) showAgent(args[1]);
      else console.log('Usage: agent-invoke.js show <agent-id>');
      break;
    case 'invoke':
      if (args[1] && args[2]) {
        const registry = loadRegistry();
        const agent = registry.agents.find(a => a.id === args[1]);
        if (agent && agent.type === 'subagent') {
          console.log(JSON.stringify(invokeSubagent(args[1], args.slice(2).join(' ')), null, 2));
        } else if (agent && agent.type === 'simulated') {
          console.log(JSON.stringify(invokeSimulated(args[1], args.slice(2).join(' ')), null, 2));
        } else {
          console.log(`Agent ${args[1]} not found or invalid type`);
        }
      } else {
        console.log('Usage: agent-invoke.js invoke <agent-id> <task>');
      }
      break;
    case 'simulate':
      if (args[1]) {
        console.log(JSON.stringify(invokeSimulated(args[1], args.slice(2).join(' ')), null, 2));
      } else {
        console.log('Usage: agent-invoke.js simulate <agent-id> <task>');
      }
      break;
    case 'domain':
      if (args[1]) searchByDomain(args[1]);
      else console.log('Usage: agent-invoke.js domain <domain>');
      break;
    case 'help':
    default:
      showHelp();
  }
}