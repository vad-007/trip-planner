# ADK Trip Planner - Project Architecture

## 📋 Project Overview
**ADK Trip Planner** is an intelligent travel planning assistant built using Google's ADK (AI Development Kit). It helps users discover dream vacation destinations and plan their trips through an agent-based system powered by Gemini 2.5 Flash LLM.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADK Trip Planner                             │
│                   (root_agent - Main Entry)                      │
│              "Exclusive Travel Concierge Agent"                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  travel_inspiration_agent          │
        │  "Travel Inspiration Provider"     │
        └────────┬─────────────────┬─────────┘
                 │                 │
        ┌────────▼────────┐  ┌─────▼──────────┐
        │  news_agent     │  │ places_agent   │
        │  (Events/News)  │  │ (Locations)    │
        └────────┬────────┘  └─────┬──────────┘
                 │                 │
        ┌────────▼────────┐  ┌─────▼──────────┐
        │ google_search   │  │ find_nearby_   │
        │   grounding     │  │ places_open    │
        └─────────────────┘  └────────────────┘
```

---

## 📁 Project Structure

```
ADK_Trip_Planner/
├── pyproject.toml              # Project metadata & dependencies
├── ARCHITECTURE.md             # This file - System design documentation
│
└── trip_planner/               # Main application package
    ├── __init__.py             # Package initialization
    ├── agent.py                # Main root agent definition
    ├── supporting_agent.py     # Sub-agents configuration
    ├── tools.py                # Tool implementations
    └── __pycache__/            # Python cache
```

---

## 🤖 Agent System Architecture

### 1. **Root Agent** (`agent.py`)
**Name:** `ADK_Trip_Planner_main`  
**Role:** Main entry point for user interactions  
**Model:** Gemini 2.5 Flash  

**Characteristics:**
- Acts as an exclusive travel concierge
- Cannot use tools directly
- Delegates requests to sub-agents
- Orchestrates the travel planning workflow

**Responsibilities:**
- Welcome and understand user requirements
- Route requests to appropriate sub-agents
- Provide recommendations based on sub-agent responses

---

### 2. **Travel Inspiration Agent** (`supporting_agent.py`)
**Name:** `travel_inspiration_agent`  
**Role:** Core intelligence for destination discovery  
**Model:** Gemini 2.5 Flash  

**Capabilities:**
- Helps users identify dream vacation destinations
- Suggests activities at chosen destinations
- Provides general knowledge about destinations
- Consults subordinate agents for detailed information

**Sub-agents It Uses:**
- `news_agent` - For travel events/news
- `places_agent` - For location/place suggestions

---

### 3. **News Agent** (Sub-agent)
**Name:** `news_agent`  
**Role:** Travel events and news provider  
**Model:** Gemini 2.5 Flash  

**Capabilities:**
- Searches for travel events and news
- Limits results to 10 recommendations
- Uses Google search grounding for current information

**Tools:**
- `google_search_grounding` - Web search via Google API

---

### 4. **Places Agent** (Sub-agent)
**Name:** `places_agent`  
**Role:** Location and place suggestions  
**Model:** Gemini 2.5 Flash  

**Capabilities:**
- Suggests specific places based on user preferences
- Provides name, location, and address for each place
- Limits results to 10 recommendations
- Can find nearby places (hotels, cafes, etc.)

**Tools:**
- `location_search_tool` - OpenStreetMap-based place finder

---

## 🛠️ Tools Layer

### Tool 1: Google Search Grounding
**File:** `tools.py`  
**Function:** `google_search_grounding`  
**Implementation:** Wrapped agent using Google Search Tool  

**Purpose:**
- Provides web search capability via Google ADK
- Returns current travel news and events
- Output format: Bullet points with actionable items

**Key Features:**
- Direct question answering
- Brief, concise responses
- Tourist/traveler perspective

---

### Tool 2: OpenStreetMap Place Finder
**File:** `tools.py`  
**Function:** `find_nearby_places_open()`  

**Signature:**
```python
find_nearby_places_open(
    query: str,          # What to search (e.g., "restaurant")
    location: str,       # City or area
    radius: int = 3000,  # Search radius in meters
    limit: int = 5       # Number of results
) -> str
```

**Process Flow:**
1. **Geocoding:** Converts location name to coordinates (Nominatim)
2. **Place Search:** Queries Overpass API (OpenStreetMap) within radius
3. **Result Formatting:** Returns matching places with addresses

**Capabilities:**
- Searches for: restaurants, hotels, gyms, bars, etc.
- No API key required (Free services only)
- Handles errors gracefully

---

## 📊 Data Flow

### Typical User Journey:
```
1. User → Root Agent
   "I want to plan a trip to Europe"
   
2. Root Agent → Travel Inspiration Agent
   "Help the user find destinations in Europe"
   
3. Travel Inspiration Agent → Parallel Calls:
   a) News Agent → Google Search
      "What are trending travel destinations in Europe?"
      
   b) Places Agent → Overpass API
      "Find popular attractions in Europe"
   
4. Results Aggregated → Travel Inspiration Agent
   
5. Response → Root Agent → User
   "Here are the best destinations with activities and events..."
```

---

## 🔧 Technologies & Dependencies

| Component | Purpose | Version |
|-----------|---------|---------|
| **google-adk** | Agent framework | >=1.15.1 |
| **geopy** | Geocoding service | >=2.4.1 |
| **python-dotenv** | Environment variables | >=1.1.1 |
| **Python** | Runtime | >=3.11 |

### External APIs Used:
- **Google Search API** - Via ADK integration
- **Nominatim (OpenStreetMap)** - Geocoding
- **Overpass API (OpenStreetMap)** - Place search

---

## 🚀 Execution Flow

### Startup Process:
1. `pyproject.toml` defines dependencies
2. `trip_planner/__init__.py` marks it as a package
3. `agent.py` instantiates `root_agent`
4. `supporting_agent.py` creates sub-agents
5. `tools.py` provides tool implementations
6. Agent system is ready for requests

### Request Handling:
- User query enters root agent
- Root agent coordinates with travel_inspiration_agent
- Sub-agents perform parallel searches
- Results are compiled and formatted
- Response returned to user

---

## 🔐 Key Design Patterns

### 1. **Agent Hierarchy**
- Single root agent manages user interaction
- Specialized sub-agents handle specific domains
- Clear separation of concerns

### 2. **Tool Abstraction**
- Generic tools wrapped as agent tools
- Agents can defer to other agents (AgentTool)
- Consistent interface across different tool types

### 3. **No Direct Tool Access**
- Root agent cannot call tools directly
- Ensures proper workflow and context passing
- Maintains abstraction layers

### 4. **Free/Open APIs**
- Uses Nominatim and Overpass (OpenStreetMap) for locations
- No proprietary API keys needed (except Google services)
- Scalable and maintainable

---

## ⚙️ Configuration

### LLM Model
All agents use: **`gemini-2.5-flash`**
- Fast inference
- Optimized for travel domain
- Consistent across all agents

### Search Parameters
- **Place Search Radius:** Default 3000m (customizable)
- **Result Limits:** 10 items for news/places
- **Timeout:** 25 seconds for API calls

---

## 🔄 Interaction Patterns

### Sequential Flow (Root → Travel → News/Places)
```
User speaks to Root Agent
    ↓
Root Agent delegates to Travel Inspiration Agent
    ↓
Travel Inspiration Agent consults News Agent
    ↓
News Agent performs Google Search
    ↓
Results bubble back up through agents
```

### Parallel Flow (News + Places simultaneously)
```
Travel Inspiration Agent
    ├→ News Agent (queries Google)
    └→ Places Agent (queries Overpass)
           ↓
       Results combined
```

---

## 📝 Notes for Developers

### Adding New Agents:
1. Create in `supporting_agent.py`
2. Define tools required
3. Set model and instructions
4. Register with parent agent using `AgentTool`

### Adding New Tools:
1. Implement function in `tools.py`
2. Wrap with `FunctionTool()` or agent wrapper
3. Register with respective agent via `tools=[]`

### Customizing Responses:
- Modify `instruction` field in agent definitions
- Update output format in tool implementations
- Adjust search parameters (radius, limits)

---

## 🐛 Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Agent not responding | Sub-agent failure | Check sub-agent instructions and tools |
| No places found | Spelling or unsupported location | Verify location name with Nominatim |
| API errors | Network or timeout | Check internet, increase timeout |
| Slow responses | Parallel queries overloaded | Reduce result limits temporarily |

---

## 📈 Future Enhancements

- [ ] Add booking integration (flights, hotels)
- [ ] Implement user preference persistence
- [ ] Add real-time flight pricing
- [ ] Weather integration for destinations
- [ ] User reviews/ratings aggregation
- [ ] Multi-language support

---

**Last Updated:** March 2026  
**Project:** ADK Trip Planner  
**Version:** 0.1.0
