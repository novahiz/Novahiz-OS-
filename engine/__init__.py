"""
Novahiz Engine — Main Package
"""
from .registry import AgentRegistry
from .router import Router
from .scoring import Scoreboard
from .executor import Executor
from .plugin import PluginManager
from .database_manager import DatabaseManager, get_db, init_db
from .detectors import ErrorDetector, LogAnalyzer
from .correction import AutoCorrectEngine, CorrectionValidator
from .learning import BehaviorTracker, LearningEngine, SuggestionGenerator

__all__ = [
    'AgentRegistry',
    'Router',
    'Scoreboard',
    'Executor',
    'PluginManager',
    'DatabaseManager',
    'get_db',
    'init_db',
    'ErrorDetector',
    'LogAnalyzer',
    'AutoCorrectEngine',
    'CorrectionValidator',
    'BehaviorTracker',
    'LearningEngine',
    'SuggestionGenerator'
]
