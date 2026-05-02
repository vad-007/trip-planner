"""
Cost Optimization Framework

A production-ready framework for adding cost optimization to ANY Python project.

Components:
- base_cache_system.py: SQLite-based caching with TTL and statistics
- base_database.py: Generic searchable database with indexing
- base_tools.py: Tools with intelligent fallback strategies

Usage:
    from cost_optimization_framework.base_cache_system import CacheManager
    from cost_optimization_framework.base_database import BaseDatabase
    from cost_optimization_framework.base_tools import SmartFallbackTool
    
    # Create your domain-specific implementations
    # See REUSE_GUIDE.md for detailed examples

For detailed documentation, see: REUSE_GUIDE.md
"""

__version__ = "1.0.0"
__author__ = "Cost Optimization Framework"

from .base_cache_system import CacheManager, get_cache
from .base_database import BaseDatabase, SimpleDatabase, FilterableDatabase
from .base_tools import (
    BaseCachedTool,
    ChainedSearchTool,
    SmartFallbackTool,
    CachedAPITool,
    create_cached_tool,
)

__all__ = [
    # Cache
    'CacheManager',
    'get_cache',
    # Database
    'BaseDatabase',
    'SimpleDatabase',
    'FilterableDatabase',
    # Tools
    'BaseCachedTool',
    'ChainedSearchTool',
    'SmartFallbackTool',
    'CachedAPITool',
    'create_cached_tool',
]
