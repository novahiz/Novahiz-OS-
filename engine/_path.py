"""
Centralise l'ajout de la racine du projet dans sys.path.
Évite la duplication du même hack dans 7 fichiers.
"""
import sys
import os

_ROOT: str | None = None


def ensure() -> str:
    global _ROOT
    if _ROOT is not None:
        return _ROOT
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root not in sys.path:
        sys.path.insert(0, root)
    _ROOT = root
    return root
