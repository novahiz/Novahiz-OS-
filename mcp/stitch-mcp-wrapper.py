#!/usr/bin/env python3
"""
Stitch MCP STDIO Wrapper — v4 (synchrone + cache fichier)
- Cache fichier pour tools/list (~295KB)
- 1er lancement: appel API synchrone (4-5s) puis mis en cache
- Lancements suivants: < 50ms
- Aucun thread, aucun risque de race condition
"""
import json
import os
import sys
import urllib.request
import urllib.error

API_URL = "https://stitch.googleapis.com/mcp"
CACHE_FILE = os.path.expanduser("~/.opencode/cache/stitch-tools.json")
ENV_FILE = os.path.expanduser("~/.novahiz/.env")

# Cherche la clé API: d'abord env var, puis fichier .env
API_KEY = os.environ.get("STITCH_API_KEY", "")
if not API_KEY:
    try:
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("STITCH_API_KEY="):
                    API_KEY = line.split("=", 1)[1].strip().strip("\"'")
                    break
    except (FileNotFoundError, IOError):
        pass

# Cache mémoire
_tools_cache = None


def _load_cache():
    """Charge le cache fichier en mémoire. Retourne True si OK."""
    global _tools_cache
    try:
        with open(CACHE_FILE, "rb") as f:
            _tools_cache = f.read()
        return True
    except (FileNotFoundError, IOError):
        return False


def _save_cache(data: bytes):
    """Sauvegarde sur disque."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    try:
        with open(CACHE_FILE, "wb") as f:
            f.write(data)
    except IOError:
        pass


def _fetch_tools_list():
    """Appel API Stitch pour tools/list, met en cache."""
    global _tools_cache
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/list"
    })
    data = _forward(body)
    try:
        resp = json.loads(data)
        if "result" in resp:
            _tools_cache = data
            _save_cache(data)
            return True
    except json.JSONDecodeError:
        pass
    return False


def _forward(body: str, timeout: int = 120) -> bytes:
    """Forward JSON-RPC vers Stitch HTTP API."""
    req = urllib.request.Request(
        API_URL,
        data=body.encode("utf-8"),
        headers={"X-Goog-Api-Key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        return json.dumps({
            "jsonrpc": "2.0", "id": None,
            "error": {"code": e.code, "message": str(e.reason)},
        }).encode("utf-8")
    except urllib.error.URLError as e:
        return json.dumps({
            "jsonrpc": "2.0", "id": None,
            "error": {"code": 0, "message": f"URLError: {e.reason}"},
        }).encode("utf-8")


def _respond(data: bytes, req_id):
    """Écrit réponse JSON-RPC sur stdout, avec le bon ID de requête."""
    try:
        resp = json.loads(data)
        resp["id"] = req_id  # Toujours utiliser l'ID de la requête
        sys.stdout.write(json.dumps(resp) + "\n")
    except (json.JSONDecodeError, KeyError):
        sys.stdout.write(data.decode("utf-8") + "\n")
    sys.stdout.flush()


def main():
    # Ne JAMAIS exit — même sans API key, on reste en vie et on répond erreur
    cache_loaded = False
    no_key = not API_KEY

    if no_key:
        sys.stderr.write("[stitch-wrapper] STITCH_API_KEY not set\n")
        sys.stderr.flush()
    else:
        sys.stderr.write("[stitch-wrapper] OK: STITCH_API_KEY set\n")
        sys.stderr.flush()
        cache_loaded = _load_cache()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            _respond(
                json.dumps({
                    "jsonrpc": "2.0", "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }).encode("utf-8"),
                None,
            )
            continue

        method = req.get("method", "")
        req_id = req.get("id")

        # Notifications → ignorer (Stitch stateless)
        if req_id is None:
            continue

        # Si pas de clé API, répondre erreur sur chaque requête
        if no_key:
            _respond(
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": "STITCH_API_KEY not set. Configure dans ~/.novahiz/.env ou opencode.jsonc"
                    },
                }).encode("utf-8"),
                req_id,
            )
            continue

        # tools/list → cache si dispo, sinon API
        if method == "tools/list":
            if not cache_loaded:
                # 1ère fois: fetch synchrone depuis Stitch
                cache_loaded = _fetch_tools_list()
            if _tools_cache:
                _respond(_tools_cache, req_id)
            else:
                # Fallback: forward direct
                data = _forward(line)
                _respond(data, req_id)
            continue

        # Tout le reste → forward direct vers Stitch
        data = _forward(line)
        _respond(data, req_id)


if __name__ == "__main__":
    main()
