#!/usr/bin/env python3
"""
NovaHiz OS - Interactive REPL Mode
Interactive command-line interface for NovaHiz OS
"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from novahiz_cli import NovahizCLI, Colors

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")

class REPL:
    def __init__(self):
        self.cli = NovahizCLI(json_output=False, quiet=False, verbose=False)
        self.running = True
        self.history = []
        
        self.commands = {
            'help': self.cmd_help,
            'h': self.cmd_help,
            '?': self.cmd_help,
            'status': lambda: self.cli.cmd_status(),
            'health': lambda: self.cli.cmd_health(),
            'agents': lambda: self.cli.cmd_agents(),
            'skills': lambda: self.cli.cmd_skills(),
            'stats': lambda: self.cli.cmd_stats(),
            'sync': lambda: self.cli.cmd_sync(),
            'link': lambda: self.cli.cmd_link(),
            'backup': lambda: self.cli.cmd_backup(),
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'q': self.cmd_exit,
            'clear': self.cmd_clear,
        }
    
    def cmd_help(self):
        print(f"""
{Colors.BRIGHT_CYAN}╔════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}         NOVAHIZ OS REPL - HELP                 {Colors.BRIGHT_CYAN}║{Colors.RESET}
{Colors.BRIGHT_CYAN}╚════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.BOLD}Commands:{Colors.RESET}
  status, agents, skills, stats  → System info
  health                         → Health check
  sync, link, backup             → System commands
  route <task>                   → Route task to agent
  invoke <agent>                 → Invoke agent
  search <query>                 → Search agents/skills
  council <task>                 → Council deliberation
  monitor, api                   → Management
  clear                          → Clear screen
  help, h, ?                     → This help
  exit, quit, q, Ctrl+D          → Exit REPL

{Colors.BOLD}Examples:{Colors.RESET}
  > route "Design a landing page"
  > invoke luna-design
  > search design
  > council "Build auth system"
""")
    
    def cmd_exit(self):
        self.running = False
        print(f"\n{Colors.BRIGHT_GREEN}✓ Goodbye!{Colors.RESET}\n")
    
    def cmd_clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        self.print_banner()
    
    def print_banner(self):
        print(f"""
{Colors.BRIGHT_MAGENTA}╔════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BRIGHT_MAGENTA}║{Colors.RESET}     {Colors.BOLD}🚀 NOVAHIZ OS v1.7 - INTERACTIVE MODE{Colors.RESET}       {Colors.BRIGHT_MAGENTA}║{Colors.RESET}
{Colors.BRIGHT_MAGENTA}║{Colors.RESET}         Type {Colors.BRIGHT_CYAN}'help'{Colors.RESET} for commands               {Colors.BRIGHT_MAGENTA}║{Colors.RESET}
{Colors.BRIGHT_MAGENTA}║{Colors.RESET}         Type {Colors.BRIGHT_YELLOW}'exit'{Colors.RESET} to quit                    {Colors.BRIGHT_MAGENTA}║{Colors.RESET}
{Colors.BRIGHT_MAGENTA}╚════════════════════════════════════════════════════╝{Colors.RESET}
""")
    
    def parse_command(self, line):
        """Parse command line into command and arguments"""
        parts = line.strip().split(None, 1)
        if not parts:
            return None, None
        
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None
        return cmd, args
    
    def execute_command(self, line):
        """Execute a command"""
        if not line.strip():
            return
        
        self.history.append(line)
        cmd, args = self.parse_command(line)
        
        if not cmd:
            return
        
        # Handle commands with arguments
        if cmd == 'route' and args:
            self.cli.cmd_route(args)
        elif cmd == 'invoke':
            if args:
                # Check for --task flag
                if '--task' in args:
                    parts = args.split('--task')
                    agent = parts[0].strip()
                    task = parts[1].strip() if len(parts) > 1 else None
                    self.cli.cmd_invoke(agent, task)
                else:
                    self.cli.cmd_invoke(args)
            else:
                self.cli.cmd_invoke()
        elif cmd == 'search' and args:
            self.cli.cmd_search(args)
        elif cmd == 'council' and args:
            self.cli.cmd_council(args)
        elif cmd in self.commands:
            self.commands[cmd]()
        else:
            print(f"{Colors.RED}✗ Unknown command: {cmd}{Colors.RESET}")
            print(f"{Colors.DIM}Type 'help' for available commands{Colors.RESET}")
    
    def run(self):
        """Main REPL loop"""
        self.print_banner()
        
        try:
            while self.running:
                try:
                    line = input(f"{Colors.BRIGHT_CYAN}novahiz>{Colors.RESET} ")
                    self.execute_command(line)
                except KeyboardInterrupt:
                    print(f"\n{Colors.DIM}Use 'exit' to quit{Colors.RESET}")
                except EOFError:
                    self.cmd_exit()
        finally:
            self.cli.close()


def main():
    print(f"{Colors.BRIGHT_CYAN}Starting NovaHiz OS REPL...{Colors.RESET}\n")
    repl = REPL()
    repl.run()


if __name__ == "__main__":
    main()
