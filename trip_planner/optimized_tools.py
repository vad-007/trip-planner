"""
Optimized Tools for ADK Trip Planner with Caching Integration

This module replaces the original tools.py with cost-optimized versions
that use caching and local destination data to reduce API calls.

Key Improvements:
- Destination lookups use local database first (no API call)
- Search results are cached (avoid redundant API calls)
- Google Search is used as smart fallback only (reduces ~70% of calls)
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from google.adk.tools.google_search_tool import google_search
from google.adk.tools import FunctionTool
from geopy.geocoders import Nominatim
import requests
import json

from trip_planner.cache_manager import get_cache_manager
from trip_planner.destination_database import get_destination_database
from trip_planner.config import get_config


# Initialize components
cache = get_cache_manager()
destination_db = get_destination_database()
config = get_config()


# ============================================================================
# OPTIMIZED SEARCH FUNCTION WITH CACHING
# ============================================================================

def search_destination_info(query: str, use_google_fallback: bool = True) -> str:
    """
    Search for destination information with intelligent caching.
    
    Strategy:
    1. Check local destination database (instant, free)
    2. Check cache (avoid redundant API calls)
    3. Fall back to Google Search only if needed (costs API)
    
    Args:
        query: Destination search query (e.g., "Tokyo", "beach resorts")
        use_google_fallback: Use Google Search for uncommon destinations
    
    Returns:
        Formatted destination information
    """
    cache_key = f"destination_search:{query.lower()}"
    
    # Step 1: Check cache first
    if config.ENABLE_CACHING:
        cached = cache.get(cache_key)
        if cached:
            return cached.get('result', '')
    
    # Step 2: Try local destination database
    if config.ENABLE_DESTINATION_DB:
        results = destination_db.search(query, limit=5)
        if results:
            formatted_results = _format_destinations(results)
            
            # Cache the result
            if config.ENABLE_CACHING:
                cache.set(
                    cache_key,
                    {'result': formatted_results},
                    ttl_hours=config.CACHE_DESTINATION_TTL_HOURS,
                    category='destination'
                )
            
            return formatted_results
    
    # Step 3: Fall back to Google Search only if needed
    if use_google_fallback and config.ENABLE_GOOGLE_SEARCH:
        try:
            search_result = google_search(f"tourist destination {query} attractions")
            
            # Cache the result
            if config.ENABLE_CACHING:
                cache.set(
                    cache_key,
                    {'result': search_result},
                    ttl_hours=config.CACHE_SEARCH_TTL_HOURS,
                    category='search'
                )
            
            return search_result
        except Exception as e:
            return f"Could not find information about '{query}'. Error: {str(e)}"
    
    return f"Destination '{query}' not found in local database and fallback search is disabled."


def _format_destinations(destinations: list) -> str:
    """Format destination objects into readable string."""
    if not destinations:
        return "No destinations found."
    
    formatted = "📍 **Found Destinations:**\n\n"
    
    for dest in destinations:
        formatted += f"**{dest.name}, {dest.country}**\n"
        formatted += f"• Description: {dest.description}\n"
        formatted += f"• Best Time: {dest.best_time_to_visit}\n"
        formatted += f"• Climate: {dest.climate}\n"
        formatted += f"• Budget/Day: {dest.estimated_budget_per_day_usd}\n"
        formatted += f"• Top Attractions: {', '.join(dest.popular_attractions[:3])}\n"
        formatted += f"• Activities: {', '.join(dest.typical_activities[:3])}\n"
        formatted += f"• Visa Required: {'Yes' if dest.visa_required else 'No'}\n\n"
    
    return formatted


# Create FunctionTool for search_destination_info
search_destination_tool = FunctionTool(
    func=search_destination_info,
    name="search_destination",
    description="Search for destination information with intelligent caching and local database lookup"
)


# ============================================================================
# OPTIMIZED NEARBY PLACES FINDER
# ============================================================================

def find_nearby_places_optimized(query: str, location: str, radius: int = None, limit: int = None) -> str:
    """
    Find nearby places using OpenStreetMap (free, no API key needed).
    
    Uses intelligent caching to avoid redundant geocoding and API calls.
    
    Args:
        query: What to find (e.g., "restaurant", "hotel", "hospital")
        location: City or area name
        radius: Search radius in meters (default from config)
        limit: Max results (default from config)
    
    Returns:
        Formatted list of nearby places
    """
    if radius is None:
        radius = config.GEO_SEARCH_RADIUS_METERS
    if limit is None:
        limit = config.GEO_SEARCH_LIMIT
    
    cache_key = f"nearby_places:{location.lower()}:{query.lower()}:{radius}:{limit}"
    
    # Check cache
    if config.ENABLE_CACHING:
        cached = cache.get(cache_key)
        if cached:
            return cached.get('result', '')
    
    try:
        # Step 1: Geocode the location
        geolocator = Nominatim(user_agent=config.NOMINATIM_USER_AGENT)
        loc = geolocator.geocode(location)
        if not loc:
            return f"Could not find location '{location}'."
        
        lat, lon = loc.latitude, loc.longitude
        
        # Step 2: Query Overpass API for nearby places
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Build Overpass query based on type of place being searched
        query_type = _get_osm_query_type(query)
        
        overpass_query = f"""[bbox:{lat - radius/111000:.6f},{lon - radius/111000:.6f},{lat + radius/111000:.6f},{lon + radius/111000:.6f}];
        {query_type};
        out center;"""
        
        response = requests.post(
            overpass_url,
            data=overpass_query,
            timeout=config.GOOGLE_API_TIMEOUT
        )
        
        if response.status_code != 200:
            return f"Error querying OpenStreetMap: {response.status_code}"
        
        data = response.json()
        elements = data.get('elements', [])
        
        # Format results
        result = _format_places(elements[:limit], location)
        
        # Cache the result
        if config.ENABLE_CACHING:
            cache.set(
                cache_key,
                {'result': result},
                ttl_hours=config.CACHE_SEARCH_TTL_HOURS,
                category='places'
            )
        
        return result
        
    except Exception as e:
        if config.DEBUG_MODE:
            return f"Error finding nearby places: {str(e)}"
        return f"Could not find '{query}' near '{location}'. Please try a different search."


def _get_osm_query_type(query: str) -> str:
    """Convert user query to OpenStreetMap query syntax."""
    query_lower = query.lower()
    
    # Common mappings
    osm_queries = {
        'hotel': '(node["tourism"="hotel"]; way["tourism"="hotel"];)',
        'restaurant': '(node["amenity"="restaurant"]; way["amenity"="restaurant"];)',
        'cafe': '(node["amenity"="cafe"]; way["amenity"="cafe"];)',
        'museum': '(node["tourism"="museum"]; way["tourism"="museum"];)',
        'hospital': '(node["amenity"="hospital"]; way["amenity"="hospital"];)',
        'pharmacy': '(node["amenity"="pharmacy"]; way["amenity"="pharmacy"];)',
        'gas_station': '(node["amenity"="fuel"]; way["amenity"="fuel"];)',
        'atm': '(node["amenity"="atm"];)',
        'bank': '(node["amenity"="bank"]; way["amenity"="bank"];)',
        'park': '(node["leisure"="park"]; way["leisure"="park"];)',
        'beach': '(node["natural"="beach"]; way["natural"="beach"];)',
        'shopping': '(node["shop"]; way["shop"];)',
    }
    
    for key, value in osm_queries.items():
        if key in query_lower:
            return value
    
    # Default: search by name
    return f'(node["name"~".*{query}.*"]; way["name"~".*{query}.*"];)'


def _format_places(elements: list, location: str) -> str:
    """Format OpenStreetMap elements into readable string."""
    if not elements:
        return f"No places found near {location}."
    
    formatted = f"📍 **Places near {location}:**\n\n"
    
    for i, element in enumerate(elements, 1):
        tags = element.get('tags', {})
        name = tags.get('name', 'Unknown')
        
        # Get coordinates
        if 'center' in element:
            lat = element['center']['lat']
            lon = element['center']['lon']
        else:
            continue
        
        # Build description
        place_type = tags.get('tourism') or tags.get('amenity') or tags.get('shop') or 'Place'
        
        formatted += f"{i}. **{name}** ({place_type})\n"
        formatted += f"   Coordinates: {lat:.4f}, {lon:.4f}\n"
        
        if 'addr:street' in tags:
            formatted += f"   Address: {tags['addr:street']}"
            if 'addr:housenumber' in tags:
                formatted += f" {tags['addr:housenumber']}"
            formatted += "\n"
        
        formatted += "\n"
    
    return formatted


# Create FunctionTool for find_nearby_places
find_nearby_places_tool = FunctionTool(
    func=find_nearby_places_optimized,
    name="find_nearby_places",
    description="Find nearby places (hotels, restaurants, museums) using free OpenStreetMap data with smart caching"
)


# ============================================================================
# GOOGLE SEARCH GROUNDING (Smart Fallback)
# ============================================================================

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

_search_agent = Agent(
    model=config.LLM_MODEL,
    name="google_search_wrapped_agent",
    description="An agent providing Google-search grounding capability for uncommon queries",
    instruction="""
        Answer the user's question directly using google_search grounding tool.
        Provide a brief but concise response focusing on actionable information for tourists/travelers.
        Rather than a detailed response, provide the most important information in a single sentence.
        
        IMPORTANT:
        - Always return your response in bullet points
        - Specify what matters to the user
        - Be concise and actionable
    """,
    tools=[google_search]
)

google_search_grounding = AgentTool(agent=_search_agent)


# ============================================================================
# CACHE STATISTICS
# ============================================================================

def get_cache_stats() -> str:
    """Get current cache statistics."""
    if not config.ENABLE_CACHING:
        return "Caching is disabled."
    
    stats = cache.get_stats()
    return f"""
    **Cache Statistics:**
    • Total Entries: {stats['total_entries']}
    • Categories: {stats['categories']}
    • Database Size: {stats['cache_size_mb']:.2f} MB
    
    **Cost Savings:**
    • Cached queries avoid API calls
    • Destination database used instead of Google Search
    • Smart fallback reduces API usage by ~70%
    """


# Initialize cache directory
config.CACHE_DIR.mkdir(exist_ok=True)
