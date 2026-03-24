# 🌍 ADK Trip Planner

An intelligent travel planning assistant powered by Google's ADK (AI Development Kit) and Gemini LLM. Discover dream vacation destinations, get travel inspiration, find local attractions, and plan your perfect trip.

---

## ✨ Features

- 🎯 **Destination Discovery** - Find your dream vacation destinations based on preferences
- 📰 **Travel News & Events** - Get current travel events and recommendations
- 📍 **Local Place Finder** - Search for hotels, restaurants, attractions, and more
- 🤖 **AI-Powered Agents** - Multi-agent system for intelligent travel planning
- 🗺️ **OpenStreetMap Integration** - Free, open-source location data (no API keys needed)
- 💬 **Natural Language** - Chat naturally with your travel concierge

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- `pip`, `uv`, or similar package manager
- Google ADK API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ADK_Trip_Planner.git
   cd ADK_Trip_Planner
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   uv sync
   # or
   pip install -e .
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Add your Google API credentials and other configs
   GOOGLE_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   uv run adk web
   # or
   python -m trip_planner.agent
   ```

---

## 📖 Usage Guide

### Basic Trip Planning
```
User: "Help me plan a trip to Japan"

ADK Trip Planner:
1. Suggests popular destinations (Tokyo, Kyoto, Osaka, etc.)
2. Shows current travel events and news in Japan
3. Recommends activities and nearby attractions
4. Provides hotel, restaurant, and landmark information
```

### Finding Nearby Places
```
User: "Find hotels near Mount Fuji"

System:
- Locates Mount Fuji coordinates
- Searches OpenStreetMap for nearby hotels
- Returns hotel names, addresses, and locations
```

### Travel News
```
User: "What's happening in Paris this month?"

System:
- Searches for current events and news
- Provides travel-relevant information
- Recommends best times to visit
```

---

## 🏗️ Project Structure

```
ADK_Trip_Planner/
├── pyproject.toml                    # Project configuration & dependencies
├── README.md                         # This file
├── ARCHITECTURE.md                   # Detailed system architecture
├── .env.example                      # Environment variables template
│
└── trip_planner/                     # Main application package
    ├── __init__.py                   # Package initialization
    ├── agent.py                      # Root agent (main entry point)
    ├── supporting_agent.py           # Sub-agents configuration
    ├── tools.py                      # Tool implementations
    └── __pycache__/                  # Python cache (auto-generated)
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration
LLM_MODEL=gemini-2.5-flash

# Optional: Geolocation Settings
DEFAULT_RADIUS=3000  # meters
MAX_RESULTS=10
```

### Agent Configuration
Agents are configured in `trip_planner/supporting_agent.py`:

```python
LLM = "gemini-2.5-flash"  # Change LLM model here

# Modify agent instructions for different behavior
travel_inspiration_agent = Agent(
    model=LLM,
    name="travel_inspiration_agent",
    instruction="Your custom instructions here",
    tools=[...]
)
```

---

## 📚 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| google-adk | Agent framework | >=1.15.1 |
| geopy | Geocoding (Nominatim) | >=2.4.1 |
| python-dotenv | Environment management | >=1.1.1 |

### External Services
- **Google Search API** - Travel news and events
- **Nominatim (OpenStreetMap)** - Address geocoding
- **Overpass API (OpenStreetMap)** - Place discovery

---

## 🤖 Architecture Overview

The system uses a **multi-agent architecture**:

```
┌─────────────────────────────────┐
│    Root Agent (Concierge)       │ ← User Interface
└────────────────┬────────────────┘
                 │
        ┌────────▼─────────────┐
        │ Travel Inspiration   │
        │     Agent             │
        └────┬──────────┬──────┘
             │          │
        ┌────▼─┐    ┌───▼──┐
        │ News │    │Places│
        │Agent │    │Agent │
        └──────┘    └──────┘
```

- **Root Agent**: Main user interface, coordinates requests
- **Travel Inspiration Agent**: Core intelligence for recommendations
- **News Agent**: Searches travel events and news
- **Places Agent**: Finds locations and nearby places

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system design.

---

## 💡 Usage Examples

### Example 1: European Adventure
```
Input: "I want to explore Europe. Show me destinations with cultural events."

Output:
- Destinations: Paris, Rome, Barcelona, Berlin...
- Current Events: Festivals, exhibitions, concerts...
- Nearby Places: Museums, restaurants, historical sites...
- Accommodation: Hotels in each city
```

### Example 2: Beach Vacation
```
Input: "Find me the best beaches with water sports facilities nearby."

Output:
- Beach Destinations: Bali, Maldives, Greece...
- Activities: Surfing, diving, snorkeling...
- Nearby: Resorts, restaurants, equipment rentals...
```

### Example 3: Adventure Travel
```
Input: "I love hiking. Where should I go? What's happening there?"

Output:
- Destinations: Switzerland, Nepal, Patagonia...
- Events: Hiking festivals, mountain events...
- Nearby: Guides, equipment shops, lodges...
```

---

## 🛠️ Development

### Running Tests
```bash
# Run pytest
pytest

# With coverage
pytest --cov=trip_planner
```

### Adding New Agents
1. Create agent in `trip_planner/supporting_agent.py`
2. Define tools and instructions
3. Register with parent agent
4. Test with `uv run adk web`

### Adding New Tools
1. Implement function in `trip_planner/tools.py`
2. Wrap with `FunctionTool()` or `AgentTool()`
3. Assign to appropriate agent
4. Update documentation

### Code Style
```bash
# Format code
black trip_planner/

# Lint
ruff check trip_planner/

# Type checking
mypy trip_planner/
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Could not find location"**
- Verify location spelling
- Try broader location names (e.g., "UK" instead of exact town)
- Use Nominatim web interface to test: https://nominatim.openstreetmap.org/

**Issue: "No results found"**
- Check internet connection
- Increase search radius in configuration
- Try different search keywords

**Issue: API Error 429**
- Rate limit exceeded
- Wait a few seconds before retrying
- Consider caching results

**Issue: Agent not responding**
- Check `.env` file for API keys
- Verify Google ADK installation
- Check agent instructions in `supporting_agent.py`

For detailed troubleshooting, see [ARCHITECTURE.md](ARCHITECTURE.md#-troubleshooting).

---

## 📋 Requirements

- Python 3.11 or higher
- Internet connection (for API calls)
- Google API credentials
- 50MB+ free disk space

---

## 🔐 Security & Privacy

- No personal data is stored
- API calls go to Google, OpenStreetMap, and Nominatim only
- Environment variables stored in local `.env` (not in version control)
- Add `.env` to `.gitignore`

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Update ARCHITECTURE.md if adding new agents/tools
- Test your changes before submitting

---

## 📞 Support & Contact

- 📧 Email: support@adktripplanner.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/ADK_Trip_Planner/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/ADK_Trip_Planner/discussions)

---

## 🎯 Roadmap

- [x] Core agent system
- [x] Location-based search
- [x] Travel news integration
- [ ] Flight booking integration
- [ ] Hotel booking system
- [ ] Real-time pricing
- [ ] Weather forecasts
- [ ] User preferences persistence
- [ ] Multi-language support
- [ ] Mobile app

---

## 📚 Additional Resources

- [Google ADK Documentation](https://ai.google.dev/adk)
- [Gemini API Reference](https://ai.google.dev/api)
- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/)
- [Architecture Documentation](ARCHITECTURE.md)

---

## 🙏 Acknowledgments

- Built with [Google ADK](https://ai.google.dev/adk)
- Uses [OpenStreetMap](https://www.openstreetmap.org/) data
- Powered by [Gemini](https://ai.google.dev/) LLM
- Inspired by modern travel planning needs

---

## 📊 Project Status

**Current Version:** 0.1.0  
**Status:** Active Development  
**Last Updated:** March 2026

---

**Happy Travels! 🌍✈️**
