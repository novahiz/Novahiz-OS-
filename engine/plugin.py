"""
Plugin System — Auto-découverte, chargement et cycle de vie des plugins.
Plugins = modules Python dans ~/.opencode/plugins/<nom>/plugin.py
Chaque plugin expose: info(), setup(engine), teardown()
"""
import importlib.util
import json
import os
import sys
from typing import Any

PLUGINS_DIR = os.path.expanduser("~/.opencode/plugins")
PLUGIN_MANIFEST = "plugin.json"


class PluginInfo:
    """Métadonnées d'un plugin."""

    def __init__(self, name: str, path: str, manifest: dict):
        self.name = name
        self.path = path
        self.manifest = manifest
        self.module = None
        self.active = False

    @property
    def version(self) -> str:
        return self.manifest.get("version", "0.0.0")

    @property
    def description(self) -> str:
        return self.manifest.get("description", "")

    @property
    def author(self) -> str:
        return self.manifest.get("author", "")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "path": self.path,
            "active": self.active,
        }


class PluginManager:
    """Gère la découverte, le chargement et l'exécution des plugins."""

    def __init__(self, plugins_dir: str = PLUGINS_DIR):
        self.plugins_dir = plugins_dir
        self._plugins: dict[str, PluginInfo] = {}
        os.makedirs(plugins_dir, exist_ok=True)

    def discover(self) -> list[PluginInfo]:
        """Découvre tous les plugins installés."""
        self._plugins = {}
        if not os.path.isdir(self.plugins_dir):
            return []

        for entry in sorted(os.listdir(self.plugins_dir)):
            plugin_path = os.path.join(self.plugins_dir, entry)
            if not os.path.isdir(plugin_path):
                continue
            manifest_path = os.path.join(plugin_path, PLUGIN_MANIFEST)
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, encoding="utf-8") as f:
                        manifest = json.load(f)
                    info = PluginInfo(entry, plugin_path, manifest)
                    self._plugins[entry] = info
                except (json.JSONDecodeError, IOError):
                    continue
        return list(self._plugins.values())

    def load(self, name: str) -> bool:
        """Charge un plugin spécifique."""
        if name not in self._plugins:
            return False

        info = self._plugins[name]
        module_path = os.path.join(info.path, "plugin.py")
        if not os.path.isfile(module_path):
            return False

        try:
            spec = importlib.util.spec_from_file_location(f"novahiz_plugin_{name}", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                info.module = module
                info.active = True
                return True
        except Exception:
            return False
        return False

    def load_all(self) -> list[str]:
        """Découvre et charge tous les plugins."""
        loaded = []
        for info in self.discover():
            if self.load(info.name):
                loaded.append(info.name)
        return loaded

    def setup_all(self, engine_ref: Any = None):
        """Appelle setup() sur tous les plugins chargés."""
        results = {}
        for name, info in self._plugins.items():
            if info.active and info.module and hasattr(info.module, "setup"):
                try:
                    result = info.module.setup(engine_ref)
                    results[name] = {"success": True, "result": result}
                except Exception as e:
                    results[name] = {"success": False, "error": str(e)}
            else:
                results[name] = {"success": False, "error": "not loaded or no setup()"}
        return results

    def teardown_all(self):
        """Appelle teardown() sur tous les plugins actifs."""
        for info in self._plugins.values():
            if info.active and info.module and hasattr(info.module, "teardown"):
                try:
                    info.module.teardown()
                except Exception:
                    pass

    def list_active(self) -> list[PluginInfo]:
        return [p for p in self._plugins.values() if p.active]

    def list_all(self) -> list[PluginInfo]:
        return list(self._plugins.values())

    def get(self, name: str) -> PluginInfo | None:
        return self._plugins.get(name)
