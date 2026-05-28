#!/usr/bin/env python3
"""
Novahiz CLI v5.2 — Multi-Provider LLM Configuration
Configure providers, models, and fallbacks for Novahiz OS
"""
import os
import sys
import json
import urllib.request

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
RUNTIME_DIR = os.path.join(NOVAHIZ_DIR, "runtime")
CONFIG_FILE = os.path.join(RUNTIME_DIR, "config.json")
DOCS_DIR = os.path.join(NOVAHIZ_DIR, "documentation")

# Colors
CYAN = '\033[0;36m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

def log(msg, color=CYAN):
    print(f"{color}{msg}{NC}")

def load_config():
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(config):
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    log(f"✅ Configuration sauvegardée: {CONFIG_FILE}", GREEN)

# =============================================================================
# PROVIDER MANAGEMENT
# =============================================================================
def list_providers():
    """List configured providers"""
    config = load_config()
    if not config:
        log("❌ Configuration non trouvée. Exécutez: nv config init", RED)
        return
    
    log("\n═══════════════════════════════════════════════════════", CYAN)
    log("  NOVAHIZ OS — PROVIDERS CONFIGURÉS", CYAN)
    log("═══════════════════════════════════════════════════════", CYAN)
    
    providers = config.get("providers", {})
    for provider_id, provider in providers.items():
        enabled = provider.get("enabled", False)
        status = "✅" if enabled else "❌"
        api_key_set = "✅" if provider.get("api_key") else "❌"
        
        log(f"\n{status} {provider_id.upper()}", GREEN if enabled else YELLOW)
        log(f"   Name: {provider.get('name', 'N/A')}")
        log(f"   API Key: {api_key_set}")
        log(f"   Base URL: {provider.get('base_url', 'N/A')}")
        log(f"   Timeout: {provider.get('timeout', 60)}s")
        log(f"   Priority: {provider.get('priority', 99)}")
    
    log("\n═══════════════════════════════════════════════════════", CYAN)

def add_provider(provider_id, name, api_key, base_url, priority=1):
    """Add a new provider"""
    config = load_config()
    if not config:
        config = {"providers": {}, "models": {"flash": {}, "smart": {}, "premium": {}}}
    
    config["providers"][provider_id] = {
        "enabled": True,
        "name": name,
        "api_key_env": f"{provider_id.upper().replace('-', '_')}_API_KEY",
        "api_key": api_key,
        "base_url": base_url,
        "timeout": 60,
        "max_tokens": 8192,
        "priority": priority
    }
    
    save_config(config)
    log(f"✅ Provider '{provider_id}' ajouté avec succès", GREEN)

def enable_provider(provider_id):
    """Enable/disable provider"""
    config = load_config()
    if not config:
        log("❌ Configuration non trouvée", RED)
        return
    
    if provider_id in config.get("providers", {}):
        config["providers"][provider_id]["enabled"] = True
        save_config(config)
        log(f"✅ Provider '{provider_id}' activé", GREEN)
    else:
        log(f"❌ Provider '{provider_id}' non trouvé", RED)

def disable_provider(provider_id):
    """Disable provider"""
    config = load_config()
    if not config:
        log("❌ Configuration non trouvée", RED)
        return
    
    if provider_id in config.get("providers", {}):
        config["providers"][provider_id]["enabled"] = False
        save_config(config)
        log(f"✅ Provider '{provider_id}' désactivé", GREEN)
    else:
        log(f"❌ Provider '{provider_id}' non trouvé", RED)

# =============================================================================
# MODEL MANAGEMENT
# =============================================================================
def list_models():
    """List configured models by tier"""
    config = load_config()
    if not config:
        log("❌ Configuration non trouvée", RED)
        return
    
    log("\n═══════════════════════════════════════════════════════", CYAN)
    log("  NOVAHIZ OS — MODÈLES CONFIGURÉS PAR TIER", CYAN)
    log("═══════════════════════════════════════════════════════", CYAN)
    
    models = config.get("models", {})
    
    for tier in ["flash", "smart", "premium"]:
        tier_config = models.get(tier, {})
        log(f"\n📊 TIER {tier.upper()}", GREEN)
        
        # Default model
        default = tier_config.get("default", {})
        log(f"   Default: {default.get('provider', 'N/A')} → {default.get('model', 'N/A')}", CYAN)
        
        # Fallbacks
        fallbacks = tier_config.get("fallbacks", [])
        if fallbacks:
            log(f"   Fallbacks:", YELLOW)
            for i, fb in enumerate(fallbacks, 1):
                log(f"     {i}. {fb.get('provider', 'N/A')} → {fb.get('model', 'N/A')}", YELLOW)
        else:
            log(f"   Fallbacks: Aucun", YELLOW)
    
    log("\n═══════════════════════════════════════════════════════", CYAN)

def set_model(tier, provider, model, fallback_index=None):
    """Set model for a tier"""
    config = load_config()
    if not config:
        log("❌ Configuration non trouvée", RED)
        return
    
    if tier not in ["flash", "smart", "premium"]:
        log(f"❌ Tier invalide. Utilisez: flash, smart, premium", RED)
        return
    
    if "models" not in config:
        config["models"] = {"flash": {}, "smart": {}, "premium": {}}
    
    if tier not in config["models"]:
        config["models"][tier] = {"default": {}, "fallbacks": []}
    
    if fallback_index is None:
        # Set default model
        config["models"][tier]["default"] = {
            "provider": provider,
            "model": model
        }
        log(f"✅ Modèle {tier} défini: {provider} → {model}", GREEN)
    else:
        # Set fallback
        if "fallbacks" not in config["models"][tier]:
            config["models"][tier]["fallbacks"] = []
        
        # Extend fallbacks list if needed
        while len(config["models"][tier]["fallbacks"]) < fallback_index:
            config["models"][tier]["fallbacks"].append({})
        
        config["models"][tier]["fallbacks"][fallback_index - 1] = {
            "provider": provider,
            "model": model
        }
        log(f"✅ Fallback {fallback_index} pour {tier} défini: {provider} → {model}", GREEN)
    
    save_config(config)

# =============================================================================
# MODEL LISTING FROM PROVIDERS
# =============================================================================
def fetch_models_openrouter(api_key):
    """Fetch available models from OpenRouter"""
    log("\n📡 Récupération modèles OpenRouter...", CYAN)
    
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            models = data.get("data", [])
            
            log(f"✅ {len(models)} modèles trouvés", GREEN)
            
            # Group by provider
            by_provider = {}
            for model in models:
                model_id = model.get("id", "")
                if "/" in model_id:
                    provider = model_id.split("/")[0]
                    if provider not in by_provider:
                        by_provider[provider] = []
                    by_provider[provider].append(model_id)
            
            return by_provider
            
    except Exception as e:
        log(f"❌ Erreur: {e}", RED)
        return {}

def fetch_models_opencode_zen(api_key):
    """Fetch available models from OpenCode Zen"""
    log("\n📡 Récupération modèles OpenCode Zen...", CYAN)
    
    try:
        req = urllib.request.Request(
            "https://api.opencode.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            models = data.get("data", [])
            
            log(f"✅ {len(models)} modèles trouvés", GREEN)
            
            # Simple list
            model_list = [m.get("id", "") for m in models]
            return {"opencode-zen": model_list}
            
    except Exception as e:
        log(f"❌ Erreur: {e}", RED)
        return {}

def list_available_models():
    """List all available models from configured providers"""
    config = load_config()
    if not config:
        log("❌ Configuration non trouvée", RED)
        return
    
    log("\n═══════════════════════════════════════════════════════", CYAN)
    log("  MODÈLES DISPONIBLES PAR FOURNISSEUR", CYAN)
    log("═══════════════════════════════════════════════════════", CYAN)
    
    providers = config.get("providers", {})
    all_models = {}
    
    for provider_id, provider in providers.items():
        if not provider.get("enabled", False):
            continue
        
        api_key = provider.get("api_key", "")
        
        if provider_id == "openrouter":
            models = fetch_models_openrouter(api_key)
        elif provider_id == "opencode-zen":
            models = fetch_models_opencode_zen(api_key)
        else:
            log(f"⚠️  Provider '{provider_id}' non supporté pour listing", YELLOW)
            continue
        
        all_models.update(models)
    
    # Display
    log("\n📊 RÉSULTATS", GREEN)
    for provider_id, model_list in all_models.items():
        log(f"\n{provider_id.upper()}:", CYAN)
        if isinstance(model_list, dict):
            for sub_provider, models in model_list.items():
                log(f"  {sub_provider}:", YELLOW)
                for model in models[:20]:  # Show first 20
                    log(f"    - {model}")
                if len(models) > 20:
                    log(f"    ... et {len(models) - 20} autres", YELLOW)
        else:
            for model in model_list[:20]:  # Show first 20
                log(f"    - {model}")
            if len(model_list) > 20:
                log(f"    ... et {len(model_list) - 20} autres", YELLOW)
    
    log("\n═══════════════════════════════════════════════════════", CYAN)
    log("💡 Astuce: Utilisez 'nv config set-model' pour configurer", CYAN)
    log("═══════════════════════════════════════════════════════", CYAN)

# =============================================================================
# INITIALIZATION
# =============================================================================
def init_config():
    """Initialize default configuration"""
    config = {
        "version": "5.2.0",
        "description": "Novahiz OS Multi-Provider LLM Configuration",
        "providers": {
            "openrouter": {
                "enabled": True,
                "name": "OpenRouter",
                "api_key_env": "OPENROUTER_API_KEY",
                "api_key": "sk-or-v1-your-openrouter-api-key-here",
                "base_url": "https://openrouter.ai/api/v1",
                "timeout": 60,
                "max_tokens": 8192,
                "priority": 1
            },
            "opencode-zen": {
                "enabled": False,
                "name": "OpenCode Zen",
                "api_key_env": "OPENCODE_ZEN_API_KEY",
                "base_url": "https://api.opencode.ai/v1",
                "timeout": 60,
                "max_tokens": 8192,
                "priority": 2,
                "note": "Disabled - set api_key or env var to enable"
            }
        },
        "models": {
            "flash": {
                "default": {"provider": "openrouter", "model": "qwen/qwen3.5-9b"},
                "fallbacks": [
                    {"provider": "openrouter", "model": "qwen/qwen3.5-flash-02-23"},
                    {"provider": "openrouter", "model": "stepfun/step-3.5-flash"},
                    {"provider": "openrouter", "model": "z-ai/glm-4.7-flash"}
                ]
            },
            "smart": {
                "default": {"provider": "opencode-zen", "model": "Qwen3.5 plus"},
                "fallbacks": [
                    {"provider": "openrouter", "model": "qwen/qwen3.6-flash"},
                    {"provider": "openrouter", "model": "qwen/qwen3.5-plus-20260420"},
                    {"provider": "openrouter", "model": "moonshotai/kimi-k2.5"}
                ]
            },
            "premium": {
                "default": {"provider": "openrouter", "model": "qwen/qwen3.6-plus"},
                "fallbacks": [
                    {"provider": "openrouter", "model": "moonshotai/kimi-k2.5"},
                    {"provider": "openrouter", "model": "z-ai/glm-5"}
                ]
            }
        },
        "runtime": {
            "retry_count": 3,
            "retry_delay": 2,
            "poll_interval": 2,
            "auto_fallback": True,
            "max_fallbacks": 3
        }
    }
    
    save_config(config)
    log("\n✅ Configuration initialisée avec:", GREEN)
    log("   • 2 providers: openrouter, opencode-zen", CYAN)
    log("   • 3 tiers: flash, smart, premium", CYAN)
    log("   • Fallbacks configurés automatiquement", CYAN)

# =============================================================================
# CLI MAIN
# =============================================================================
def usage():
    log("\n═══════════════════════════════════════════════════════", CYAN)
    log("  NOVAHIZ CLI v5.2 — Multi-Provider Configuration", CYAN)
    log("═══════════════════════════════════════════════════════", CYAN)
    log("\nUsage: nv config <command> [options]", CYAN)
    log("\nCommands:", YELLOW)
    log("  init                          Initialiser configuration", GREEN)
    log("  providers                     Lister providers", GREEN)
    log("  providers enable <id>         Activer provider", GREEN)
    log("  providers disable <id>        Désactiver provider", GREEN)
    log("  models                        Lister modèles par tier", GREEN)
    log("  set-model <tier> <provider> <model> [fallback]", GREEN)
    log("                                Définir modèle pour tier", GREEN)
    log("  list-available                Voir modèles disponibles", GREEN)
    log("\nExamples:", YELLOW)
    log("  nv config init", GREEN)
    log("  nv config providers", GREEN)
    log("  nv config models", GREEN)
    log("  nv config set-model flash openrouter qwen/qwen3.5-9b", GREEN)
    log("  nv config set-model smart openrouter qwen/qwen3.6-flash 1", GREEN)
    log("  nv config list-available", GREEN)
    log("\n═══════════════════════════════════════════════════════", CYAN)

def main():
    if len(sys.argv) < 2:
        usage()
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_config()
    elif command == "providers":
        if len(sys.argv) > 2:
            subcmd = sys.argv[2]
            if subcmd == "enable" and len(sys.argv) > 3:
                enable_provider(sys.argv[3])
            elif subcmd == "disable" and len(sys.argv) > 3:
                disable_provider(sys.argv[3])
        else:
            list_providers()
    elif command == "models":
        list_models()
    elif command == "set-model":
        if len(sys.argv) < 4:
            log("❌ Usage: novahiz-config set-model <tier> <provider> <model> [fallback_index]", RED)
            return
        tier = sys.argv[2]
        provider = sys.argv[3]
        model = sys.argv[4]
        fallback = int(sys.argv[5]) if len(sys.argv) > 5 else None
        set_model(tier, provider, model, fallback)
    elif command == "list-available":
        list_available_models()
    else:
        usage()

if __name__ == "__main__":
    main()
