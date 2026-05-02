"""
Base Tools System - Reusable Tool Patterns with Caching

This module provides reusable patterns for creating tools that integrate
caching, local databases, and API fallbacks.

Use in your projects by:
1. Extend BaseCachedTool for your tools
2. Implement search() method with your logic
3. Tools automatically handle caching and stats

Example:
    from cost_optimization_framework.base_tools import BaseCachedTool
    
    class ProductSearchTool(BaseCachedTool):
        def __init__(self, cache, db):
            super().__init__(cache, "product_search", ttl_hours=48)
            self.db = db
        
        def search(self, query: str) -> str:
            # This method is called after cache check
            results = self.db.search(query)
            return self._format_results(results)
        
        def _format_results(self, items):
            return "\\n".join(f"• {item.name}: ${item.price}" for item in items)
    
    tool = ProductSearchTool(cache, db)
    result = tool.execute("laptop")  # Auto-cached!
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import json


class BaseCachedTool(ABC):
    """
    Base class for tools that use caching and fallback strategies.
    
    Features:
    - Automatic caching of results
    - Cache hit tracking
    - Fallback strategies
    - Execution statistics
    - Error handling
    
    Subclass this and implement search() method.
    """
    
    def __init__(self, cache, tool_name: str, ttl_hours: int = 48):
        """
        Initialize cached tool.
        
        Args:
            cache: CacheManager instance
            tool_name: Name of the tool (used for cache keys)
            ttl_hours: How long to cache results
        """
        self.cache = cache
        self.tool_name = tool_name
        self.ttl_hours = ttl_hours
        self.stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
        }
    
    def execute(self, query: str, use_cache: bool = True) -> str:
        """
        Execute tool with caching.
        
        Args:
            query: Query string
            use_cache: Whether to use cache
        
        Returns:
            Tool result
        """
        self.stats['total_calls'] += 1
        cache_key = f"{self.tool_name}:{query.lower()}"
        
        # Step 1: Check cache
        if use_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                self.stats['cache_hits'] += 1
                return cached.get('result', '')
        
        # Step 2: Execute search
        self.stats['cache_misses'] += 1
        try:
            result = self.search(query)
        except Exception as e:
            self.stats['errors'] += 1
            return self._handle_error(query, e)
        
        # Step 3: Cache result
        if self.cache:
            self.cache.set(
                cache_key,
                {'result': result},
                ttl_hours=self.ttl_hours,
                category=self.tool_name
            )
        
        return result
    
    @abstractmethod
    def search(self, query: str) -> str:
        """
        Perform search operation.
        This method is called after cache check fails.
        
        Args:
            query: Search query
        
        Returns:
            Formatted result string
        """
        pass
    
    def _handle_error(self, query: str, error: Exception) -> str:
        """Handle errors gracefully. Override for custom behavior."""
        return f"Error searching for '{query}': {str(error)}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        stats = self.stats.copy()
        total = stats['total_calls']
        if total > 0:
            stats['cache_hit_rate'] = f"{(stats['cache_hits'] / total * 100):.1f}%"
        return stats
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
        }


class ChainedSearchTool(BaseCachedTool):
    """
    Tool that chains multiple search strategies.
    
    Tries strategies in order until one returns results:
    1. Local database search
    2. Custom fallback function
    3. Error message
    
    Example:
        tool = ChainedSearchTool(
            cache,
            "product_search",
            search_strategies=[
                lambda q: db.search(q),  # Try local DB first
                lambda q: api.search(q),  # Fall back to API
            ],
            formatter=lambda items: "\\n".join(str(i) for i in items)
        )
        result = tool.execute("query")
    """
    
    def __init__(self, cache, tool_name: str, search_strategies: List[Callable],
                 formatter: Callable, ttl_hours: int = 48):
        """
        Initialize chained search tool.
        
        Args:
            cache: CacheManager instance
            tool_name: Tool name
            search_strategies: List of search functions (tried in order)
            formatter: Function to format results
            ttl_hours: Cache TTL
        """
        super().__init__(cache, tool_name, ttl_hours)
        self.search_strategies = search_strategies
        self.formatter = formatter
        self.strategy_stats = {f"strategy_{i}": 0 for i in range(len(search_strategies))}
    
    def search(self, query: str) -> str:
        """
        Try each search strategy until one returns results.
        
        Args:
            query: Search query
        
        Returns:
            Formatted results or error message
        """
        for i, strategy in enumerate(self.search_strategies):
            try:
                results = strategy(query)
                if results:
                    self.strategy_stats[f"strategy_{i}"] += 1
                    return self.formatter(results) if results else "No results found."
            except Exception as e:
                continue
        
        return f"No results found for '{query}'."


class SmartFallbackTool(BaseCachedTool):
    """
    Tool with intelligent fallback strategy.
    
    Uses local database for common queries, falls back to API for uncommon ones.
    
    Example:
        tool = SmartFallbackTool(
            cache,
            "destination_search",
            local_search=lambda q: destination_db.search(q),
            api_search=lambda q: google_api.search(q),
            formatter=lambda items: "\\n".join(format_item(i) for i in items),
            db_coverage=0.7,  # Use DB first 70% of the time
        )
    """
    
    def __init__(self, cache, tool_name: str,
                 local_search: Callable,
                 api_search: Callable = None,
                 formatter: Callable = None,
                 db_coverage: float = 0.7,
                 ttl_hours: int = 48):
        """
        Initialize smart fallback tool.
        
        Args:
            cache: CacheManager instance
            tool_name: Tool name
            local_search: Function to search local database
            api_search: Function to search API (fallback)
            formatter: Function to format results
            db_coverage: Fraction of queries to try local search first
            ttl_hours: Cache TTL
        """
        super().__init__(cache, tool_name, ttl_hours)
        self.local_search = local_search
        self.api_search = api_search
        self.formatter = formatter or (lambda x: str(x))
        self.db_coverage = db_coverage
        self.local_hits = 0
        self.api_hits = 0
    
    def search(self, query: str) -> str:
        """
        Smart search: try local DB first, fall back to API if needed.
        
        Args:
            query: Search query
        
        Returns:
            Formatted results
        """
        # Try local database first
        try:
            results = self.local_search(query)
            if results:
                self.local_hits += 1
                return self.formatter(results)
        except Exception:
            pass
        
        # Fall back to API if available
        if self.api_search:
            try:
                results = self.api_search(query)
                if results:
                    self.api_hits += 1
                    return self.formatter(results)
            except Exception:
                pass
        
        return f"No results found for '{query}'."
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics including fallback usage."""
        stats = super().get_stats()
        stats['local_hits'] = self.local_hits
        stats['api_hits'] = self.api_hits
        if (self.local_hits + self.api_hits) > 0:
            rate = self.local_hits / (self.local_hits + self.api_hits) * 100
            stats['local_db_usage_rate'] = f"{rate:.1f}%"
        return stats


class CachedAPITool(BaseCachedTool):
    """
    Simple cached API tool.
    
    Wraps an API call with caching for cost optimization.
    
    Example:
        tool = CachedAPITool(
            cache,
            "weather_api",
            api_func=lambda city: weather_api.get(city),
            ttl_hours=1,
        )
        result = tool.execute("London")  # First call hits API, 2nd uses cache
    """
    
    def __init__(self, cache, tool_name: str, api_func: Callable, ttl_hours: int = 48):
        """
        Initialize cached API tool.
        
        Args:
            cache: CacheManager instance
            tool_name: Tool name
            api_func: Function to call API
            ttl_hours: Cache TTL
        """
        super().__init__(cache, tool_name, ttl_hours)
        self.api_func = api_func
    
    def search(self, query: str) -> str:
        """
        Call API (only when cache misses).
        
        Args:
            query: Query for API
        
        Returns:
            API response formatted as string
        """
        result = self.api_func(query)
        return str(result) if result else "No results."


# Utility function to create tools with common patterns
def create_cached_tool(
    cache,
    tool_name: str,
    search_func: Callable,
    formatter: Callable = None,
    ttl_hours: int = 48,
    enable_fallback: bool = False,
    fallback_func: Callable = None
) -> BaseCachedTool:
    """
    Factory function to create a cached tool quickly.
    
    Args:
        cache: CacheManager instance
        tool_name: Tool name
        search_func: Main search function
        formatter: Optional formatter function
        ttl_hours: Cache TTL
        enable_fallback: Use fallback function
        fallback_func: Fallback search function
    
    Returns:
        Configured BaseCachedTool instance
    
    Example:
        tool = create_cached_tool(
            cache,
            "products",
            search_func=db.search,
            formatter=lambda items: "\\n".join(str(i) for i in items),
            ttl_hours=48,
        )
    """
    if not enable_fallback:
        # Simple tool
        class SimpleTool(BaseCachedTool):
            def search(self, query: str) -> str:
                results = search_func(query)
                if formatter:
                    return formatter(results)
                return str(results) if results else "No results."
        
        return SimpleTool(cache, tool_name, ttl_hours)
    else:
        # Tool with fallback
        return SmartFallbackTool(
            cache,
            tool_name,
            local_search=search_func,
            api_search=fallback_func,
            formatter=formatter,
            ttl_hours=ttl_hours
        )
