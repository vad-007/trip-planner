"""
Base Cache System - Reusable Abstract Cache Manager

This is a generic cache implementation that can be reused across ANY project.
It provides the core caching functionality without domain-specific code.

Use this in your projects by:
1. Copy this file to your project
2. Use CacheManager directly, or
3. Subclass CacheManager for custom behavior

Example:
    from cost_optimization_framework.base_cache_system import CacheManager
    cache = CacheManager(db_path="my_app_cache.db")
    cache.set("user:123", {"name": "John", "age": 30})
    cached = cache.get("user:123")
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import threading
from abc import ABC, abstractmethod


class BaseCacheManager(ABC):
    """
    Abstract base class for cache managers.
    Implement this if you need custom cache behavior.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached value by key."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Dict[str, Any], ttl_hours: int = None, 
            category: str = 'general') -> bool:
        """Store value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete specific cache entry."""
        pass
    
    @abstractmethod
    def clear(self, category: str = None) -> bool:
        """Clear cache entries."""
        pass


class CacheManager(BaseCacheManager):
    """
    Production-ready SQLite-based cache manager.
    
    Features:
    - TTL-based expiration
    - Thread-safe operations
    - Automatic cleanup
    - Category-based organization
    - Statistics tracking
    
    Usage:
        cache = CacheManager(db_path="cache.db", default_ttl_hours=48)
        cache.set("key", {"data": "value"}, ttl_hours=24, category="api_response")
        data = cache.get("key")
        cache.cleanup_expired()
    """
    
    def __init__(self, db_path: str = None, default_ttl_hours: int = 48):
        """
        Initialize cache manager.
        
        Args:
            db_path: Path to SQLite database
            default_ttl_hours: Default time-to-live for cached items
        """
        if db_path is None:
            cache_dir = Path.cwd() / ".cache"
            cache_dir.mkdir(exist_ok=True)
            db_path = str(cache_dir / "app_cache.db")
        
        self.db_path = db_path
        self.default_ttl_hours = default_ttl_hours
        self._lock = threading.Lock()
        
        self._init_db()
    
    def _init_db(self):
        """Create cache table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    ttl_hours INTEGER NOT NULL,
                    category TEXT DEFAULT 'general'
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_key ON cache(cache_key)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON cache(category)
            """)
            conn.commit()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached value by key.
        
        Args:
            key: Cache key
        
        Returns:
            Cached data or None if not found or expired
        """
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT cache_value, created_at, ttl_hours FROM cache WHERE cache_key = ?",
                    (key,)
                )
                row = cursor.fetchone()
        
        if row is None:
            return None
        
        cache_value, created_at, ttl_hours = row
        
        # Check if expired
        if self._is_expired(created_at, ttl_hours):
            self.delete(key)
            return None
        
        try:
            return json.loads(cache_value)
        except json.JSONDecodeError:
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl_hours: int = None, 
            category: str = 'general') -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key (e.g., 'user:123', 'api:response:weather')
            value: Data to cache (must be JSON-serializable)
            ttl_hours: Time-to-live in hours
            category: Cache category for organization
        
        Returns:
            True if successful, False otherwise
        """
        if ttl_hours is None:
            ttl_hours = self.default_ttl_hours
        
        try:
            cache_value = json.dumps(value)
        except (TypeError, ValueError):
            return False
        
        created_at = time.time()
        
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache 
                        (cache_key, cache_value, created_at, ttl_hours, category)
                        VALUES (?, ?, ?, ?, ?)
                    """, (key, cache_value, created_at, ttl_hours, category))
                    conn.commit()
                return True
            except sqlite3.Error:
                return False
    
    def delete(self, key: str) -> bool:
        """Delete specific cache entry."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache WHERE cache_key = ?", (key,))
                    conn.commit()
                return True
            except sqlite3.Error:
                return False
    
    def clear(self, category: str = None) -> bool:
        """
        Clear cache entries.
        
        Args:
            category: If specified, only clear entries of this category
        
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    if category:
                        conn.execute("DELETE FROM cache WHERE category = ?", (category,))
                    else:
                        conn.execute("DELETE FROM cache")
                    conn.commit()
                return True
            except sqlite3.Error:
                return False
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of entries deleted
        """
        current_time = time.time()
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id, created_at, ttl_hours FROM cache"
                )
                expired_ids = [
                    row[0] for row in cursor.fetchall()
                    if self._is_expired(row[1], row[2])
                ]
                
                for expired_id in expired_ids:
                    conn.execute("DELETE FROM cache WHERE id = ?", (expired_id,))
                
                conn.commit()
                return len(expired_ids)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                total_entries = cursor.fetchone()[0]
                
                cursor = conn.execute(
                    "SELECT category, COUNT(*) FROM cache GROUP BY category"
                )
                categories = dict(cursor.fetchall())
        
        return {
            'total_entries': total_entries,
            'categories': categories,
            'cache_size_mb': Path(self.db_path).stat().st_size / (1024 * 1024)
        }
    
    def set_multiple(self, items: List[tuple], category: str = 'general') -> int:
        """
        Set multiple cache items at once.
        
        Args:
            items: List of (key, value, ttl_hours) tuples
            category: Category for all items
        
        Returns:
            Number of items successfully set
        """
        count = 0
        for item in items:
            if len(item) == 2:
                key, value = item
                ttl_hours = None
            else:
                key, value, ttl_hours = item
            
            if self.set(key, value, ttl_hours, category):
                count += 1
        
        return count
    
    def get_by_category(self, category: str) -> Dict[str, Any]:
        """Get all non-expired items in a category."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT cache_key, cache_value, created_at, ttl_hours FROM cache WHERE category = ?",
                    (category,)
                )
                rows = cursor.fetchall()
        
        result = {}
        for cache_key, cache_value, created_at, ttl_hours in rows:
            if not self._is_expired(created_at, ttl_hours):
                try:
                    result[cache_key] = json.loads(cache_value)
                except json.JSONDecodeError:
                    pass
        
        return result
    
    @staticmethod
    def _is_expired(created_at: float, ttl_hours: int) -> bool:
        """Check if cache entry is expired."""
        return time.time() - created_at > (ttl_hours * 3600)


# Global instance (optional, for convenience)
_cache_instance = None

def get_cache(db_path: str = None) -> CacheManager:
    """Get or create global cache instance (singleton pattern)."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager(db_path)
    return _cache_instance
