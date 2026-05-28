#!/usr/bin/env python3
"""
Novahiz OS — Rate Limiter
Token bucket algorithm for LLM API rate limiting
"""

import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

HOME = Path.home()
NOVAHIZ_DIR = HOME / ".opencode"
RATE_STATE_FILE = NOVAHIZ_DIR / "memory" / "00_Core" / "rate_limits.json"


class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, rate_per_minute, rate_per_hour, rate_per_day):
        self.rate_per_minute = rate_per_minute
        self.rate_per_hour = rate_per_hour
        self.rate_per_day = rate_per_day
        
        # Buckets
        self.minute_tokens = rate_per_minute
        self.hour_tokens = rate_per_hour
        self.day_tokens = rate_per_day
        
        # Last refill times
        self.last_minute = time.time()
        self.last_hour = time.time()
        self.last_day = time.time()
        
        self.lock = threading.Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        
        # Refill minute bucket
        if now - self.last_minute >= 60:
            elapsed_minutes = (now - self.last_minute) / 60
            self.minute_tokens = min(
                self.rate_per_minute,
                self.minute_tokens + int(elapsed_minutes * self.rate_per_minute)
            )
            self.last_minute = now
        
        # Refill hour bucket
        if now - self.last_hour >= 3600:
            elapsed_hours = (now - self.last_hour) / 3600
            self.hour_tokens = min(
                self.rate_per_hour,
                self.hour_tokens + int(elapsed_hours * self.rate_per_hour)
            )
            self.last_hour = now
        
        # Refill day bucket
        if now - self.last_day >= 86400:
            elapsed_days = (now - self.last_day) / 86400
            self.day_tokens = min(
                self.rate_per_day,
                self.day_tokens + int(elapsed_days * self.rate_per_day)
            )
            self.last_day = now
    
    def consume(self) -> tuple[bool, str]:
        """
        Try to consume a token.
        Returns (allowed: bool, message: str)
        """
        with self.lock:
            self._refill()
            
            if self.day_tokens <= 0:
                return (False, f"Daily limit reached ({self.rate_per_day}/day)")
            
            if self.hour_tokens <= 0:
                return (False, f"Hourly limit reached ({self.rate_per_hour}/hour)")
            
            if self.minute_tokens <= 0:
                return (False, f"Per-minute limit reached ({self.rate_per_minute}/min)")
            
            # Consume tokens
            self.minute_tokens -= 1
            self.hour_tokens -= 1
            self.day_tokens -= 1
            
            return (True, "OK")
    
    def get_status(self) -> dict:
        """Get current bucket status"""
        with self.lock:
            self._refill()
            return {
                "minute": f"{self.minute_tokens}/{self.rate_per_minute}",
                "hour": f"{self.hour_tokens}/{self.rate_per_hour}",
                "day": f"{self.day_tokens}/{self.rate_per_day}"
            }


class RateLimiter:
    """Global rate limiter for all tiers"""
    
    def __init__(self, config=None):
        self.config = config or self._load_config()
        self.buckets = {}
        self.usage = defaultdict(lambda: {"minute": 0, "hour": 0, "day": 0})
        self.lock = threading.Lock()
        
        # Initialize buckets for each tier
        rate_config = self.config.get("rate_limit", {})
        if rate_config.get("enabled", True):
            for tier in ["flash", "smart", "premium"]:
                limits = rate_config.get(tier, {})
                self.buckets[tier] = TokenBucket(
                    limits.get("per_minute", 60),
                    limits.get("per_hour", 600),
                    limits.get("per_day", 3000)
                )
        
        # Load persisted usage
        self._load_usage()
    
    def _load_config(self):
        """Load config from file"""
        config_file = NOVAHIZ_DIR / "runtime" / "config.json"
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _load_usage(self):
        """Load usage from file"""
        try:
            with open(RATE_STATE_FILE) as f:
                data = json.load(f)
                for tier, counts in data.get("usage", {}).items():
                    self.usage[tier]["minute"] = counts.get("minute", 0)
                    self.usage[tier]["hour"] = counts.get("hour", 0)
                    self.usage[tier]["day"] = counts.get("day", 0)
        except Exception:
            pass
    
    def _save_usage(self):
        """Save usage to file"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "usage": dict(self.usage)
            }
            temp_file = RATE_STATE_FILE.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(data, f, indent=2)
            temp_file.replace(RATE_STATE_FILE)
        except Exception as e:
            print(f"Failed to save usage: {e}")
    
    def check(self, tier: str = "smart") -> tuple[bool, str]:
        """
        Check if request is allowed for given tier.
        Returns (allowed: bool, message: str)
        """
        # Check if rate limiting is enabled
        rate_config = self.config.get("rate_limit", {})
        if not rate_config.get("enabled", True):
            return (True, "Rate limiting disabled")
        
        # Get bucket for tier
        if tier not in self.buckets:
            # Default bucket
            self.buckets[tier] = TokenBucket(50, 500, 2000)
        
        bucket = self.buckets[tier]
        allowed, message = bucket.consume()
        
        if allowed:
            # Track usage
            with self.lock:
                self.usage[tier]["minute"] += 1
                self.usage[tier]["hour"] += 1
                self.usage[tier]["day"] += 1
                self._save_usage()
        
        return (allowed, message)
    
    def get_status(self, tier: str = None) -> dict:
        """Get rate limit status"""
        if tier:
            if tier in self.buckets:
                return {
                    "tier": tier,
                    "limits": self.buckets[tier].get_status(),
                    "usage": self.usage[tier]
                }
            return {"tier": tier, "error": "Unknown tier"}
        
        # All tiers
        return {
            "tiers": {
                tier: {
                    "limits": bucket.get_status(),
                    "usage": self.usage[tier]
                }
                for tier, bucket in self.buckets.items()
            }
        }
    
    def reset(self, tier: str = None):
        """Reset rate limits"""
        if tier:
            if tier in self.buckets:
                bucket = self.buckets[tier]
                bucket.minute_tokens = bucket.rate_per_minute
                bucket.hour_tokens = bucket.rate_per_hour
                bucket.day_tokens = bucket.rate_per_day
                self.usage[tier] = {"minute": 0, "hour": 0, "day": 0}
        else:
            for bucket in self.buckets.values():
                bucket.minute_tokens = bucket.rate_per_minute
                bucket.hour_tokens = bucket.rate_per_hour
                bucket.day_tokens = bucket.rate_per_day
            self.usage.clear()
        
        self._save_usage()


# Singleton instance
_rate_limiter = None

def get_rate_limiter(config=None):
    """Get or create rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(config)
    return _rate_limiter


if __name__ == "__main__":
    # Test rate limiter
    limiter = get_rate_limiter()
    
    print("Rate Limiter Test")
    print("=" * 50)
    
    # Test flash tier
    for i in range(5):
        allowed, msg = limiter.check("flash")
        print(f"Request {i+1}: {'✅' if allowed else '❌'} {msg}")
    
    print()
    print("Status:")
    print(json.dumps(limiter.get_status(), indent=2))
