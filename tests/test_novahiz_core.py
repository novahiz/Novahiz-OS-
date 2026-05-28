#!/usr/bin/env python3
"""
Novahiz OS — Unit Tests
Test suite for core components

Run: python3 tests/test_novahiz_core.py
"""

import unittest
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
_RUNTIME = str(ROOT / "runtime")
if _RUNTIME not in sys.path:
    sys.path.insert(0, _RUNTIME)

# =============================================================================
# TESTS: RATE LIMITER
# =============================================================================

class TestRateLimiter:
    """Tests for rate_limiter.py"""
    
    def test_import_rate_limiter(self):
        """Test that rate_limiter can be imported"""
        try:
            from rate_limiter import get_rate_limiter, RateLimiter, TokenBucket
            assert True
        except ImportError as e:
            self.fail(f"Failed to import rate_limiter: {e}")
    
    def test_token_bucket_creation(self):
        """Test TokenBucket initialization"""
        from rate_limiter import TokenBucket
        
        bucket = TokenBucket(10, 100, 1000)
        assert bucket.rate_per_minute == 10
        assert bucket.rate_per_hour == 100
        assert bucket.rate_per_day == 1000
        assert bucket.minute_tokens == 10
    
    def test_token_bucket_consume(self):
        """Test TokenBucket consume method"""
        from rate_limiter import TokenBucket
        
        bucket = TokenBucket(5, 50, 500)
        
        # Should allow first 5 requests
        for i in range(5):
            allowed, msg = bucket.consume()
            assert allowed, f"Request {i+1} should be allowed"
        
        # 6th request should be denied
        allowed, msg = bucket.consume()
        assert not allowed
        assert "limit" in msg.lower()
    
    def test_rate_limiter_singleton(self):
        """Test get_rate_limiter returns singleton"""
        from rate_limiter import get_rate_limiter
        
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        
        assert limiter1 is limiter2


# =============================================================================
# TESTS: IMMUTABLE STATE
# =============================================================================

class TestImmutableState:
    """Tests for immutable_state.py"""
    
    def test_import_immutable_state(self):
        """Test that immutable_state can be imported"""
        try:
            from immutable_state import ImmutableState, StateManager
            assert True
        except ImportError as e:
            self.fail(f"Failed to import immutable_state: {e}")
    
    def test_state_creation(self):
        """Test ImmutableState creation"""
        from immutable_state import ImmutableState
        
        state = ImmutableState("test_state")
        assert state.name == "test_state"
        assert isinstance(state.get(), dict)
    
    def test_state_update(self):
        """Test ImmutableState update method"""
        from immutable_state import ImmutableState
        
        state = ImmutableState("test_state")
        
        # Create update
        new_state = state.update({"key": "value", "number": 42})
        
        # Original should be unchanged
        assert state.get("key") is None
        
        # New state should have changes
        assert new_state["key"] == "value"
        assert new_state["number"] == 42
        assert "_version" in new_state
    
    def test_state_manager_singleton(self):
        """Test StateManager returns same instance"""
        from immutable_state import StateManager
        
        manager1 = StateManager()
        manager2 = StateManager()
        
        assert manager1 is manager2


# =============================================================================
# TESTS: BUDGET GUARD
# =============================================================================

class TestBudgetGuard:
    """Tests for premium budget guard in novahiz-unified.py"""
    
    def test_import_unified(self):
        """Test that novahiz-unified can be imported"""
        try:
            # Import specific functions
            import novahiz_unified as unified
            assert hasattr(unified, 'check_premium_budget')
            assert hasattr(unified, 'increment_premium_usage')
        except ImportError as e:
            self.fail(f"Failed to import novahiz_unified: {e}")
    
    def test_budget_check_returns_tuple(self):
        """Test that check_premium_budget returns (bool, str)"""
        import novahiz_unified as unified
        
        allowed, message = unified.check_premium_budget()
        
        assert isinstance(allowed, bool)
        assert isinstance(message, str)


# =============================================================================
# TESTS: CONFIG LOADING
# =============================================================================

class TestConfigLoading:
    """Tests for configuration loading"""
    
    def test_config_file_exists(self):
        """Test that config.json exists"""
        config_file = NOVAHIZ_DIR / "runtime" / "config.json"
        assert config_file.exists(), "config.json should exist"
    
    def test_config_is_valid_json(self):
        """Test that config.json is valid JSON"""
        config_file = NOVAHIZ_DIR / "runtime" / "config.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        assert isinstance(config, dict)
        assert "providers" in config
        assert "models" in config
    
    def test_config_has_required_sections(self):
        """Test that config has required sections"""
        config_file = NOVAHIZ_DIR / "runtime" / "config.json"
        
        with open(config_file) as f:
            config = json.load(f)
        
        # Check providers
        assert "openrouter" in config["providers"]
        
        # Check models
        assert "flash" in config["models"]
        assert "smart" in config["models"]
        assert "premium" in config["models"]
        
        # Check budget
        assert "budget" in config
        assert "premium" in config["budget"]


# =============================================================================
# TESTS: METRICS
# =============================================================================

class TestMetrics:
    """Tests for metrics system"""
    
    def test_metrics_file_exists(self):
        """Test that metrics.json exists"""
        metrics_file = NOVAHIZ_DIR / "memory" / "00_Core" / "metrics.json"
        assert metrics_file.exists(), "metrics.json should exist"
    
    def test_metrics_is_valid_json(self):
        """Test that metrics.json is valid JSON"""
        metrics_file = NOVAHIZ_DIR / "memory" / "00_Core" / "metrics.json"
        
        with open(metrics_file) as f:
            metrics = json.load(f)
        
        assert isinstance(metrics, dict)
    
    def test_metrics_has_budget_section(self):
        """Test that metrics has premiumBudget section"""
        metrics_file = NOVAHIZ_DIR / "memory" / "00_Core" / "metrics.json"
        
        with open(metrics_file) as f:
            metrics = json.load(f)
        
        assert "premiumBudget" in metrics
        budget = metrics["premiumBudget"]
        assert "daily_limit" in budget or "used_today" in budget


# =============================================================================
# TESTS: DOCUMENTATION
# =============================================================================

class TestDocumentation:
    """Tests for documentation completeness"""
    
    def test_api_doc_exists(self):
        """Test that API.md exists"""
        api_doc = NOVAHIZ_DIR / "docs" / "API.md"
        assert api_doc.exists(), "API.md should exist"
    
    def test_architecture_doc_exists(self):
        """Test that ARCHITECTURE.md exists"""
        arch_doc = NOVAHIZ_DIR / "docs" / "ARCHITECTURE.md"
        assert arch_doc.exists(), "ARCHITECTURE.md should exist"
    
    def test_legal_docs_exist(self):
        """Test that legal docs exist"""
        legal_dir = NOVAHIZ_DIR / "docs" / "legal"
        
        assert (legal_dir / "PRIVACY_POLICY.md").exists()
        assert (legal_dir / "TERMS_OF_SERVICE.md").exists()
        assert (legal_dir / "TRADEMARK.md").exists()


# =============================================================================
# TESTS: SCRIPTS
# =============================================================================

class TestScripts:
    """Tests for script existence and executability"""
    
    def test_backup_script_exists(self):
        """Test that backup.sh exists and is executable"""
        backup_script = NOVAHIZ_DIR / "scripts" / "backup.sh"
        assert backup_script.exists()
        assert os.access(backup_script, os.X_OK)
    
    def test_secret_scanner_exists(self):
        """Test that scan-secrets.sh exists"""
        scanner = NOVAHIZ_DIR / "scripts" / "scan-secrets.sh"
        assert scanner.exists()
    
    def test_performance_audit_exists(self):
        """Test that performance-audit.py exists"""
        audit = NOVAHIZ_DIR / "scripts" / "performance-audit.py"
        assert audit.exists()


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
