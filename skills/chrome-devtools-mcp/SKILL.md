---

name: chrome-devtools-mcp

description: Chrome DevTools pour agents AI. Contrôle Chrome en temps réel, inspection, debugging, performance, test E2E, accès aux comptes connectés.

humanName: devtools-bridge

autoInvoke: true

---

# Chrome DevTools MCP

## Vue d'ensemble

Chrome DevTools MCP donne le controle total sur Chrome via MCP. 41 outils DevTools. Mode perso (--autoConnect) pour acces aux comptes connectes. Lancement automatique par classification IA Novahiz.

## Outils principaux

Navigation: navigate_page, list_pages, select_page

Automation: click, fill, drag, hover, type_text, press_key

Debug: take_screenshot, take_snapshot, evaluate_script, list_console_messages, get_console_message

Performance: performance_start_trace, performance_stop_trace, performance_analyze_insight, lighthouse_audit

Network: list_network_requests, get_network_request

Memory: take_heapsnapshot, get_heapsnapshot_summary (experimental)

Extensions: install_extension, list_extensions (experimental)

## Pattern d'utilisation

Verifier → Agir → Confirmer.

Exemple:

navigate_page(url="https://example.com")

take_screenshot()

list_console_messages()

## Securite

--redactNetworkHeaders=true masque Authorization, Cookie, Set-Cookie, X-API-Key.

Logging d'audit dans ~/.opencode/logs/devtools-audit.log.

## Connexion

Config OpenCode: chrome-devtools-mcp@latest avec --autoConnect --browser-url=http://127.0.0.1:9222

Cela se connecte au Chrome existant de l'utilisateur (profils, cookies, comptes).

## Monitoring

Scoreboard: agents.ralph-browser.deliberations, successRate, toolsUsed

devtools.totalConnections, autoConnectSuccess, toolsInvocation counts

## References

https://github.com/ChromeDevTools/chrome-devtools-mcp

https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md

---

Intégration complète Novahiz OS. Acces total a votre Chrome perso. Lancement automatique par IA.