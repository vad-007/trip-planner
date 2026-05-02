"""
Base Database System - Reusable Abstract Database Pattern

This is a generic database implementation that can be reused across ANY project.
It provides core search and indexing functionality without domain-specific code.

Use this in your projects by:
1. Copy this file to your project
2. Extend BaseDatabase class for your domain
3. Implement _init_data() and format_item() methods

Example:
    from cost_optimization_framework.base_database import BaseDatabase
    
    @dataclass
    class Product:
        name: str
        category: str
        price: float
    
    class ProductDatabase(BaseDatabase):
        def _init_data(self):
            return {
                'product1': Product('Laptop', 'Electronics', 999.99),
                'product2': Product('Mouse', 'Electronics', 29.99),
            }
        
        def format_item(self, item: Product) -> str:
            return f"{item.name} (${item.price})"
    
    db = ProductDatabase()
    results = db.search("laptop")
"""

from typing import List, Dict, Any, Optional, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields


T = TypeVar('T')  # Generic type for items


class BaseDatabase(ABC, Generic[T]):
    """
    Abstract base class for domain-specific databases.
    
    Provides:
    - Generic search across items
    - Category-based filtering
    - Flexible indexing
    - Item formatting
    
    Subclass this and implement:
    - _init_data(): Return dict of items
    - format_item(): Format item as string
    """
    
    def __init__(self):
        """Initialize database and load data."""
        self.items = self._init_data()
    
    @abstractmethod
    def _init_data(self) -> Dict[str, T]:
        """
        Load all items into database.
        
        Returns:
            Dictionary of {item_id: item_object}
        
        Example:
            return {
                'user1': User(name='John', email='john@example.com'),
                'user2': User(name='Jane', email='jane@example.com'),
            }
        """
        pass
    
    @abstractmethod
    def format_item(self, item: T) -> str:
        """
        Format item as human-readable string.
        
        Args:
            item: Item object to format
        
        Returns:
            Formatted string representation
        
        Example:
            return f"{item.name} - {item.email}"
        """
        pass
    
    def search(self, query: str, search_fields: List[str] = None, 
               limit: int = 10) -> List[T]:
        """
        Search items by query string.
        
        Args:
            query: Search term (case-insensitive)
            search_fields: Fields to search in. If None, searches all string fields.
            limit: Maximum results to return
        
        Returns:
            List of matching items
        """
        query_lower = query.lower()
        results = []
        
        for item in self.items.values():
            if self._matches_query(item, query_lower, search_fields):
                results.append(item)
            
            if len(results) >= limit:
                break
        
        return results
    
    def search_by_field(self, field: str, value: str, limit: int = 10) -> List[T]:
        """
        Search items by specific field.
        
        Args:
            field: Field name to search in
            value: Value to search for (case-insensitive)
            limit: Maximum results
        
        Returns:
            List of matching items
        """
        results = []
        value_lower = value.lower()
        
        for item in self.items.values():
            item_value = getattr(item, field, None)
            if item_value and value_lower in str(item_value).lower():
                results.append(item)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_by_id(self, item_id: str) -> Optional[T]:
        """Get item by ID."""
        return self.items.get(item_id)
    
    def search_by_predicate(self, predicate: Callable[[T], bool], 
                           limit: int = 10) -> List[T]:
        """
        Search items using custom predicate function.
        
        Args:
            predicate: Function that returns True if item matches
            limit: Maximum results
        
        Returns:
            List of matching items
        
        Example:
            db.search_by_predicate(lambda item: item.price < 100, limit=5)
        """
        results = []
        
        for item in self.items.values():
            if predicate(item):
                results.append(item)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_all_values(self, field: str) -> List[Any]:
        """Get all unique values for a field."""
        return sorted(set(
            getattr(item, field)
            for item in self.items.values()
            if hasattr(item, field)
        ))
    
    def count(self) -> int:
        """Get total number of items."""
        return len(self.items)
    
    def _matches_query(self, item: T, query_lower: str, 
                      search_fields: List[str] = None) -> bool:
        """
        Check if item matches query.
        
        Default: searches all string-type fields
        Override for custom search logic.
        """
        if search_fields is None:
            # Auto-detect string fields
            search_fields = [
                f.name for f in fields(item)
                if f.type == str or 'str' in str(f.type)
            ]
        
        for field in search_fields:
            value = getattr(item, field, '')
            if query_lower in str(value).lower():
                return True
        
        return False


class SimpleDatabase(BaseDatabase[T]):
    """
    Minimal database implementation.
    Use this if you just need basic search functionality.
    
    Example:
        db = SimpleDatabase(items_dict, format_func)
        results = db.search("query")
    """
    
    def __init__(self, items: Dict[str, T], formatter: Callable[[T], str]):
        """
        Initialize with items and formatter function.
        
        Args:
            items: Dictionary of {item_id: item}
            formatter: Function to format items as strings
        """
        self._items_data = items
        self._formatter = formatter
        super().__init__()
    
    def _init_data(self) -> Dict[str, T]:
        """Return pre-provided items."""
        return self._items_data
    
    def format_item(self, item: T) -> str:
        """Format using provided formatter function."""
        return self._formatter(item)


# Example: Generic filterable database
class FilterableDatabase(BaseDatabase[T]):
    """
    Enhanced database with filtering capabilities.
    
    Example:
        class UserDB(FilterableDatabase):
            def _init_data(self):
                return {'u1': User(...), 'u2': User(...)}
            
            def format_item(self, item):
                return f"{item.name} ({item.email})"
        
        db = UserDB()
        # Search
        results = db.search("john")
        # Filter
        active_users = db.search_by_predicate(
            lambda u: u.is_active and u.age > 18
        )
"""
    pass


def create_indexed_database(items: Dict[str, Any], 
                          index_fields: List[str]) -> Dict[str, List[str]]:
    """
    Create indices for fast filtering.
    
    Args:
        items: Dictionary of items
        index_fields: Fields to create indices for
    
    Returns:
        Dictionary of {field: {value: [item_ids]}}
    
    Example:
        indices = create_indexed_database(
            {'u1': User(...), 'u2': User(...)},
            index_fields=['category', 'status']
        )
        # Fast lookup: indices['category']['Electronics'] -> ['u1', 'u3']
    """
    indices = {}
    
    for field in index_fields:
        indices[field] = {}
        
        for item_id, item in items.items():
            value = getattr(item, field, None)
            if value:
                value_str = str(value).lower()
                if value_str not in indices[field]:
                    indices[field][value_str] = []
                indices[field][value_str].append(item_id)
    
    return indices
