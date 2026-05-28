#!/usr/bin/env node
/**
 * Novahiz OS Plugin for OpenCode Desktop
 * Provides UI integration for multi-agent orchestration
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const NOVAHIZ_DIR = path.join(process.env.HOME, '.opencode');
const SCRIPTS_DIR = path.join(NOVAHIZ_DIR, 'scripts');

class NovahizPlugin {
    constructor() {
        this.name = 'Novahiz OS';
        this.version = '5.2.0';
        this.services = [];
    }

    /**
     * Activate plugin
     */
    async activate() {
        console.log(`[${this.name}] Activating v${this.version}...`);
        
        // Check if services are running
        const running = await this.checkServices();
        
        if (!running) {
            console.log(`[${this.name}] Services not running, auto-starting...`);
            await this.startServices();
        }
        
        // Register commands
        this.registerCommands();
        
        console.log(`[${this.name}] Activated successfully`);
    }

    /**
     * Check if Novahiz services are running
     */
    async checkServices() {
        return new Promise((resolve) => {
            const check = spawn('pgrep', ['-f', 'novahiz-runtime.py']);
            
            check.on('close', (code) => {
                resolve(code === 0);
            });
            
            check.on('error', () => {
                resolve(false);
            });
        });
    }

    /**
     * Start Novahiz services
     */
    async startServices() {
        return new Promise((resolve) => {
            const autostart = spawn('bash', [
                path.join(SCRIPTS_DIR, 'novahiz-autostart.sh')
            ], {
                detached: true,
                stdio: 'ignore'
            });
            
            autostart.unref();
            
            setTimeout(() => {
                resolve(true);
            }, 3000);
        });
    }

    /**
     * Register OpenCode commands
     */
    registerCommands() {
        const commands = [
            { name: 'novahiz.route', handler: this.route.bind(this) },
            { name: 'novahiz.auto', handler: this.auto.bind(this) },
            { name: 'novahiz.execute', handler: this.execute.bind(this) },
            { name: 'novahiz.agents', handler: this.agents.bind(this) },
            { name: 'novahiz.search', handler: this.search.bind(this) },
            { name: 'novahiz.health', handler: this.health.bind(this) },
            { name: 'novahiz.status', handler: this.status.bind(this) }
        ];

        commands.forEach(cmd => {
            // In real OpenCode environment, this would register with the API
            console.log(`[${this.name}] Registered command: ${cmd.name}`);
        });
    }

    /**
     * Route task to optimal agent
     */
    async route(task) {
        return this.runCommand('novahiz-cli.py', ['route', task]);
    }

    /**
     * Auto-route and execute
     */
    async auto(task) {
        return this.runCommand('novahiz-mcp.py', ['auto', task]);
    }

    /**
     * Execute with specific agent
     */
    async execute(agent, task) {
        return this.runCommand('novahiz-mcp.py', ['execute', agent, task]);
    }

    /**
     * List all agents
     */
    async agents() {
        return this.runCommand('novahiz-cli.py', ['agents']);
    }

    /**
     * Search agents
     */
    async search(query) {
        return this.runCommand('novahiz-cli.py', ['search', query]);
    }

    /**
     * Health check
     */
    async health() {
        return this.runCommand('novahiz-mcp.py', ['health']);
    }

    /**
     * Show status
     */
    async status() {
        return this.runCommand('novahiz-runtime.py', ['status']);
    }

    /**
     * Run a Python command
     */
    runCommand(script, args) {
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(SCRIPTS_DIR, script);
            const proc = spawn('python3', [scriptPath, ...args]);
            
            let output = '';
            let error = '';
            
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });
            
            proc.stderr.on('data', (data) => {
                error += data.toString();
            });
            
            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(error || `Exit code: ${code}`));
                }
            });
        });
    }

    /**
     * Deactivate plugin
     */
    async deactivate() {
        console.log(`[${this.name}] Deactivated`);
    }
}

module.exports = new NovahizPlugin();
