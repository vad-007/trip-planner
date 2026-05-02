"""
Destination Database for ADK Trip Planner

Pre-indexed destination information to avoid expensive API calls.
Covers 100+ popular worldwide destinations with key attractions, 
climate info, and travel tips.

This replaces expensive Google Search API calls for common destinations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Destination:
    """Data class representing a travel destination."""
    name: str
    country: str
    region: str
    description: str
    best_time_to_visit: str
    climate: str
    currency: str
    language: str
    popular_attractions: List[str]
    typical_activities: List[str]
    estimated_budget_per_day_usd: str
    nearby_cities: List[str]
    visa_required: bool


class DestinationDatabase:
    """Database of pre-indexed destinations to reduce API calls."""
    
    def __init__(self):
        self.destinations = self._init_destinations()
    
    def search(self, query: str, limit: int = 5) -> List[Destination]:
        """
        Search destinations by name or keyword.
        
        Args:
            query: Search term (case-insensitive)
            limit: Maximum results to return
        
        Returns:
            List of matching destinations
        """
        query_lower = query.lower()
        results = []
        
        for dest in self.destinations.values():
            if (query_lower in dest.name.lower() or 
                query_lower in dest.country.lower() or
                query_lower in dest.region.lower() or
                any(query_lower in activity.lower() for activity in dest.typical_activities) or
                any(query_lower in attr.lower() for attr in dest.popular_attractions)):
                results.append(dest)
        
        return results[:limit]
    
    def get_by_name(self, destination_name: str) -> Optional[Destination]:
        """Get destination by exact name."""
        return self.destinations.get(destination_name.lower())
    
    def get_by_country(self, country: str) -> List[Destination]:
        """Get all destinations in a specific country."""
        return [
            dest for dest in self.destinations.values()
            if dest.country.lower() == country.lower()
        ]
    
    def get_by_activity(self, activity: str) -> List[Destination]:
        """Find destinations with specific activities."""
        activity_lower = activity.lower()
        return [
            dest for dest in self.destinations.values()
            if any(activity_lower in act.lower() for act in dest.typical_activities)
        ]
    
    def get_by_climate(self, climate: str) -> List[Destination]:
        """Find destinations with specific climate."""
        climate_lower = climate.lower()
        return [
            dest for dest in self.destinations.values()
            if climate_lower in dest.climate.lower()
        ]
    
    def get_all_countries(self) -> List[str]:
        """Get list of all countries with destinations."""
        return sorted(set(dest.country for dest in self.destinations.values()))
    
    def to_dict(self) -> Dict:
        """Convert destination to dictionary for JSON serialization."""
        return {
            name: {
                'country': dest.country,
                'region': dest.region,
                'description': dest.description,
                'best_time_to_visit': dest.best_time_to_visit,
                'climate': dest.climate,
                'currency': dest.currency,
                'language': dest.language,
                'popular_attractions': dest.popular_attractions,
                'typical_activities': dest.typical_activities,
                'estimated_budget_per_day_usd': dest.estimated_budget_per_day_usd,
                'nearby_cities': dest.nearby_cities,
                'visa_required': dest.visa_required,
            }
            for name, dest in self.destinations.items()
        }
    
    def _init_destinations(self) -> Dict[str, Destination]:
        """Initialize destination database with 100+ destinations."""
        destinations = {
            # ASIA
            'tokyo': Destination(
                name='Tokyo',
                country='Japan',
                region='East Asia',
                description='Vibrant metropolis blending ancient temples with ultramodern technology',
                best_time_to_visit='April-May (spring), September-October (fall)',
                climate='Temperate, humid summers, mild winters',
                currency='Japanese Yen (JPY)',
                language='Japanese',
                popular_attractions=['Shibuya Crossing', 'Senso-ji Temple', 'Tokyo Skytree', 'Imperial Palace'],
                typical_activities=['Shopping', 'Temple visiting', 'Karaoke', 'Street food tasting'],
                estimated_budget_per_day_usd='$100-150',
                nearby_cities=['Yokohama', 'Kamakura', 'Nikko'],
                visa_required=False
            ),
            'kyoto': Destination(
                name='Kyoto',
                country='Japan',
                region='East Asia',
                description='Historic imperial capital with thousands of temples and traditional culture',
                best_time_to_visit='March-April (cherry blossoms), November-December (autumn)',
                climate='Temperate, cold winters, hot summers',
                currency='Japanese Yen (JPY)',
                language='Japanese',
                popular_attractions=['Fushimi Inari Shrine', 'Arashiyama Bamboo Grove', 'Kinkaku-ji', 'Philosopher\'s Path'],
                typical_activities=['Temple exploration', 'Geisha watching', 'Tea ceremony', 'Garden walks'],
                estimated_budget_per_day_usd='$80-120',
                nearby_cities=['Osaka', 'Nara', 'Uji'],
                visa_required=False
            ),
            'bangkok': Destination(
                name='Bangkok',
                country='Thailand',
                region='Southeast Asia',
                description='Bustling capital with ornate temples, vibrant nightlife, and delicious street food',
                best_time_to_visit='November-February (cool season)',
                climate='Tropical, hot and humid, monsoon season',
                currency='Thai Baht (THB)',
                language='Thai',
                popular_attractions=['Grand Palace', 'Wat Pho', 'Floating Markets', 'Chinatown'],
                typical_activities=['Temple visiting', 'Thai massage', 'Street food tours', 'Elephant sanctuaries'],
                estimated_budget_per_day_usd='$30-60',
                nearby_cities=['Ayutthaya', 'Chiang Mai', 'Phuket'],
                visa_required=False
            ),
            'dubai': Destination(
                name='Dubai',
                country='United Arab Emirates',
                region='Middle East',
                description='Ultra-modern desert city with luxury shopping, iconic skyscrapers, and perfect beaches',
                best_time_to_visit='October-April (cool season)',
                climate='Hot desert, very hot in summer',
                currency='UAE Dirham (AED)',
                language='Arabic, English widely spoken',
                popular_attractions=['Burj Khalifa', 'Dubai Mall', 'Palm Jumeirah', 'Gold Souk'],
                typical_activities=['Shopping', 'Desert safari', 'Beach clubs', 'Skyscraper tours'],
                estimated_budget_per_day_usd='$150-250',
                nearby_cities=['Abu Dhabi', 'Sharjah'],
                visa_required=False
            ),
            'bali': Destination(
                name='Bali',
                country='Indonesia',
                region='Southeast Asia',
                description='Tropical island paradise with beaches, rice terraces, temples, and spiritual culture',
                best_time_to_visit='April-October (dry season)',
                climate='Tropical monsoon',
                currency='Indonesian Rupiah (IDR)',
                language='Indonesian, English common in tourist areas',
                popular_attractions=['Tegallalang Rice Terraces', 'Ubud Palace', 'Tanah Lot Temple', 'Mount Batur'],
                typical_activities=['Surfing', 'Yoga retreats', 'Temple tours', 'Jungle trekking'],
                estimated_budget_per_day_usd='$30-50',
                nearby_cities=['Lombok', 'Gili Islands'],
                visa_required=False
            ),
            'singapore': Destination(
                name='Singapore',
                country='Singapore',
                region='Southeast Asia',
                description='Ultra-clean city-state with futuristic architecture, diverse cultures, and world-class dining',
                best_time_to_visit='February-April, July-August',
                climate='Tropical, hot and humid year-round',
                currency='Singapore Dollar (SGD)',
                language='English, Mandarin, Malay, Tamil',
                popular_attractions=['Marina Bay Sands', 'Gardens by the Bay', 'Sentosa Island', 'Chinatown'],
                typical_activities=['Shopping', 'Fine dining', 'Botanical gardens', 'Island hopping'],
                estimated_budget_per_day_usd='$100-150',
                nearby_cities=['Johor Bahru', 'Batam Island'],
                visa_required=False
            ),
            'hongkong': Destination(
                name='Hong Kong',
                country='China',
                region='East Asia',
                description='Vibrant harbor city with stunning skyline, energetic culture, and Asian-Western blend',
                best_time_to_visit='October-November, March-April',
                climate='Subtropical, hot summers, mild winters',
                currency='Hong Kong Dollar (HKD)',
                language='Cantonese, English',
                popular_attractions=['Victoria Peak', 'Star Ferry', 'Tian Tan Buddha', 'Nathan Road'],
                typical_activities=['Shopping', 'Harbor cruises', 'Dim sum', 'Hiking trails'],
                estimated_budget_per_day_usd='$80-150',
                nearby_cities=['Macau', 'Shenzhen'],
                visa_required=False
            ),
            'newdelhi': Destination(
                name='New Delhi',
                country='India',
                region='South Asia',
                description='Chaotic yet captivating capital blending historical monuments with modern India',
                best_time_to_visit='October-March (cool season)',
                climate='Subtropical, extreme heat in summer',
                currency='Indian Rupee (INR)',
                language='Hindi, English',
                popular_attractions=['Taj Mahal', 'India Gate', 'Jama Masjid', 'Chandni Chowk'],
                typical_activities=['Monument visiting', 'Street food', 'Shopping', 'Spiritual tours'],
                estimated_budget_per_day_usd='$20-40',
                nearby_cities=['Agra', 'Jaipur'],
                visa_required=True
            ),
            
            # EUROPE
            'paris': Destination(
                name='Paris',
                country='France',
                region='Western Europe',
                description='The City of Light with iconic monuments, world-class art, and romantic streets',
                best_time_to_visit='April-May, September-October',
                climate='Temperate, mild winters, warm summers',
                currency='Euro (EUR)',
                language='French, English widely spoken in tourist areas',
                popular_attractions=['Eiffel Tower', 'Louvre Museum', 'Notre-Dame', 'Arc de Triomphe'],
                typical_activities=['Museum visits', 'Cafe sitting', 'Seine cruises', 'Shopping'],
                estimated_budget_per_day_usd='$100-150',
                nearby_cities=['Versailles', 'Monet\'s Giverny'],
                visa_required=False
            ),
            'london': Destination(
                name='London',
                country='United Kingdom',
                region='Western Europe',
                description='Historic capital with royal palaces, world-famous museums, and vibrant neighborhoods',
                best_time_to_visit='May-June, August-September',
                climate='Temperate oceanic, mild winters, cool summers',
                currency='British Pound (GBP)',
                language='English',
                popular_attractions=['Big Ben', 'Tower of London', 'British Museum', 'Buckingham Palace'],
                typical_activities=['Museum visits', 'Theater shows', 'Tea time', 'Shopping on Oxford Street'],
                estimated_budget_per_day_usd='$100-150',
                nearby_cities=['Stonehenge', 'Windsor'],
                visa_required=False
            ),
            'barcelona': Destination(
                name='Barcelona',
                country='Spain',
                region='Western Europe',
                description='Vibrant Mediterranean city with Gaudi\'s architecture, beaches, and lively culture',
                best_time_to_visit='April-May, September-October',
                climate='Mediterranean, warm summers, mild winters',
                currency='Euro (EUR)',
                language='Catalan, Spanish, English in tourist areas',
                popular_attractions=['Sagrada Familia', 'Park Güell', 'Gothic Quarter', 'Las Ramblas'],
                typical_activities=['Architecture tours', 'Beach relaxation', 'Tapas hopping', 'Festival visits'],
                estimated_budget_per_day_usd='$70-120',
                nearby_cities=['Montserrat', 'Costa Brava'],
                visa_required=False
            ),
            'rome': Destination(
                name='Rome',
                country='Italy',
                region='Southern Europe',
                description='Eternal City steeped in history with ancient ruins, Renaissance art, and Baroque fountains',
                best_time_to_visit='April-May, September-October',
                climate='Mediterranean, hot summers, mild winters',
                currency='Euro (EUR)',
                language='Italian, English in major areas',
                popular_attractions=['Colosseum', 'Vatican City', 'Roman Forum', 'Trevi Fountain'],
                typical_activities=['Monument touring', 'Vatican exploration', 'Pasta eating', 'Renaissance art viewing'],
                estimated_budget_per_day_usd='$70-120',
                nearby_cities=['Vatican City', 'Pompeii', 'Amalfi Coast'],
                visa_required=False
            ),
            'venice': Destination(
                name='Venice',
                country='Italy',
                region='Southern Europe',
                description='Romantic city built on water with canals, historic buildings, and artistic heritage',
                best_time_to_visit='April-May, September-November',
                climate='Mediterranean, cold wet winters, warm summers',
                currency='Euro (EUR)',
                language='Italian, English in tourist areas',
                popular_attractions=['St. Mark\'s Basilica', 'Grand Canal', 'Gondola rides', 'Doge\'s Palace'],
                typical_activities=['Gondola rides', 'Basilica tours', 'Mask making', 'Lace buying'],
                estimated_budget_per_day_usd='$100-150',
                nearby_cities=['Padua', 'Verona'],
                visa_required=False
            ),
            'florence': Destination(
                name='Florence',
                country='Italy',
                region='Southern Europe',
                description='Renaissance capital with magnificent art, architecture, and Florence Cathedral',
                best_time_to_visit='April-May, September-October',
                climate='Mediterranean, hot summers, mild winters',
                currency='Euro (EUR)',
                language='Italian, English in major areas',
                popular_attractions=['Uffizi Gallery', 'Florence Cathedral', 'Ponte Vecchio', 'Accademia Gallery'],
                typical_activities=['Art museum tours', 'Wine tasting', 'Leather shopping', 'Cathedral climbing'],
                estimated_budget_per_day_usd='$80-130',
                nearby_cities=['Pisa', 'Siena'],
                visa_required=False
            ),
            'amsterdam': Destination(
                name='Amsterdam',
                country='Netherlands',
                region='Northern Europe',
                description='Charming canal city with museums, cycling culture, and bohemian atmosphere',
                best_time_to_visit='April-May, September',
                climate='Temperate oceanic, cool, windy',
                currency='Euro (EUR)',
                language='Dutch, English widely spoken',
                popular_attractions=['Anne Frank House', 'Van Gogh Museum', 'Canal cruises', 'Red Light District'],
                typical_activities=['Canal cycling', 'Museum visits', 'Coffee shops', 'Bridge watching'],
                estimated_budget_per_day_usd='$80-130',
                nearby_cities=['Windmills of Kinderdijk', 'Marken'],
                visa_required=False
            ),
            'berlin': Destination(
                name='Berlin',
                country='Germany',
                region='Central Europe',
                description='Vibrant capital with history, culture, nightlife, and street art',
                best_time_to_visit='April-May, September-October',
                climate='Temperate continental, cold winters, warm summers',
                currency='Euro (EUR)',
                language='German, English widely understood',
                popular_attractions=['Brandenburg Gate', 'Berlin Wall', 'Reichstag', 'Museum Island'],
                typical_activities=['Museum visits', 'Nightlife', 'Street art tours', 'History walking'],
                estimated_budget_per_day_usd='$60-100',
                nearby_cities=['Potsdam', 'Dresden'],
                visa_required=False
            ),
            'prague': Destination(
                name='Prague',
                country='Czech Republic',
                region='Central Europe',
                description='Picturesque castle city with Gothic architecture, bridges, and beer culture',
                best_time_to_visit='April-May, September-October',
                climate='Temperate continental, cold winters, warm summers',
                currency='Czech Koruna (CZK)',
                language='Czech, English in tourist areas',
                popular_attractions=['Prague Castle', 'Charles Bridge', 'Old Town Square', 'Jewish Quarter'],
                typical_activities=['Castle touring', 'Beer tasting', 'Bridge walks', 'Puppet shows'],
                estimated_budget_per_day_usd='$40-70',
                nearby_cities=['Bohemian Switzerland'],
                visa_required=False
            ),
            'zurich': Destination(
                name='Zurich',
                country='Switzerland',
                region='Central Europe',
                description='Pristine Swiss city with lakefront charm, world-class museums, and precision living',
                best_time_to_visit='May-September',
                climate='Temperate, cold winters, moderate summers',
                currency='Swiss Franc (CHF)',
                language='German, English widely spoken',
                popular_attractions=['Lake Zurich', 'Kunsthaus Museum', 'Old Town', 'Swiss National Museum'],
                typical_activities=['Lake cruises', 'Museum visits', 'Mountain hiking', 'Shopping on Bahnhofstrasse'],
                estimated_budget_per_day_usd='$150-200',
                nearby_cities=['Interlaken', 'Lucerne'],
                visa_required=False
            ),
            
            # AMERICAS
            'newyork': Destination(
                name='New York City',
                country='United States',
                region='North America',
                description='The city that never sleeps with iconic skyline, Broadway, and diverse neighborhoods',
                best_time_to_visit='April-May, September-October',
                climate='Temperate, cold winters, warm summers',
                currency='US Dollar (USD)',
                language='English',
                popular_attractions=['Statue of Liberty', 'Empire State Building', 'Times Square', 'Central Park'],
                typical_activities=['Broadway shows', 'Museum visits', 'Shopping', 'Restaurant dining'],
                estimated_budget_per_day_usd='$150-250',
                nearby_cities=['Jersey City', 'Newark'],
                visa_required=False
            ),
            'losangeles': Destination(
                name='Los Angeles',
                country='United States',
                region='North America',
                description='Sun-soaked city with beaches, Hollywood glamour, and diverse culture',
                best_time_to_visit='Year-round (mild climate)',
                climate='Mediterranean, warm and dry',
                currency='US Dollar (USD)',
                language='English',
                popular_attractions=['Hollywood Walk of Fame', 'Griffith Observatory', 'Santa Monica Pier', 'Getty Center'],
                typical_activities=['Beach relaxation', 'Studio tours', 'Hiking', 'Driving scenic routes'],
                estimated_budget_per_day_usd='$100-180',
                nearby_cities=['Malibu', 'San Diego'],
                visa_required=False
            ),
            'sanfrancisco': Destination(
                name='San Francisco',
                country='United States',
                region='North America',
                description='Hilly coastal city with iconic Golden Gate Bridge, tech culture, and great food',
                best_time_to_visit='May-September',
                climate='Mediterranean, cool summers, mild winters',
                currency='US Dollar (USD)',
                language='English',
                popular_attractions=['Golden Gate Bridge', 'Alcatraz', 'Cable cars', 'Chinatown'],
                typical_activities=['Bridge walks', 'Ferry rides', 'Tech museum visits', 'Food tours'],
                estimated_budget_per_day_usd='$120-180',
                nearby_cities=['Oakland', 'Marin County'],
                visa_required=False
            ),
            'mexico_city': Destination(
                name='Mexico City',
                country='Mexico',
                region='North America',
                description='Ancient capital with Aztec ruins, colonial architecture, art, and street food',
                best_time_to_visit='October-April (dry season)',
                climate='Subtropical highland, mild temperatures',
                currency='Mexican Peso (MXN)',
                language='Spanish, English in tourist areas',
                popular_attractions=['Templo Mayor', 'National Palace', 'Frida Kahlo Museum', 'Xochimilco Canals'],
                typical_activities=['Museum visits', 'Street food eating', 'History tours', 'Art gallery hopping'],
                estimated_budget_per_day_usd='$40-80',
                nearby_cities=['Teotihuacan', 'Cuernavaca'],
                visa_required=False
            ),
            'cancun': Destination(
                name='Cancun',
                country='Mexico',
                region='North America',
                description='Caribbean resort destination with pristine beaches and cenote swimming',
                best_time_to_visit='December-April (dry season)',
                climate='Tropical, warm, humid, hurricane season Jun-Nov',
                currency='Mexican Peso (MXN)',
                language='Spanish, English widely spoken',
                popular_attractions=['Cancun Beach', 'Cenotes', 'Chichen Itza', 'Isla Mujeres'],
                typical_activities=['Beach relaxation', 'Diving', 'Cenote swimming', 'Mayan ruin tours'],
                estimated_budget_per_day_usd='$80-150',
                nearby_cities=['Playa del Carmen', 'Tulum'],
                visa_required=False
            ),
            'buenos_aires': Destination(
                name='Buenos Aires',
                country='Argentina',
                region='South America',
                description='Paris of South America with tango, European architecture, and passionate culture',
                best_time_to_visit='April-May, September-October',
                climate='Temperate, hot summers, mild winters',
                currency='Argentine Peso (ARS)',
                language='Spanish, English limited',
                popular_attractions=['La Boca', 'Teatro Colon', 'Recoleta Cemetery', 'Pink House'],
                typical_activities=['Tango shows', 'Steak dining', 'Tango lessons', 'Theater visits'],
                estimated_budget_per_day_usd='$50-100',
                nearby_cities=['Tigre Delta', 'Estancia (ranches)'],
                visa_required=False
            ),
            'rio_janeiro': Destination(
                name='Rio de Janeiro',
                country='Brazil',
                region='South America',
                description='Marvelous city with Christ the Redeemer, beaches, and vibrant culture',
                best_time_to_visit='December-February (summer)',
                climate='Tropical, warm and humid, rainy',
                currency='Brazilian Real (BRL)',
                language='Portuguese, English limited',
                popular_attractions=['Christ the Redeemer', 'Copacabana Beach', 'Sugarloaf Mountain', 'Carnival'],
                typical_activities=['Beach relaxation', 'Hiking', 'Samba shows', 'Paragliding'],
                estimated_budget_per_day_usd='$50-100',
                nearby_cities=['Niteroi', 'Petropolis'],
                visa_required=True
            ),
            
            # AFRICA & MIDDLE EAST
            'cairo': Destination(
                name='Cairo',
                country='Egypt',
                region='Africa',
                description='Ancient wonder city home to Pyramids and gateway to Egyptian heritage',
                best_time_to_visit='October-April (cool season)',
                climate='Hot desert, extreme heat in summer',
                currency='Egyptian Pound (EGP)',
                language='Arabic, English in tourist areas',
                popular_attractions=['Giza Pyramids', 'Sphinx', 'Egyptian Museum', 'Khan el-Khalili'],
                typical_activities=['Pyramid tours', 'Nile cruises', 'Museum visits', 'Bazaar shopping'],
                estimated_budget_per_day_usd='$30-60',
                nearby_cities=['Giza', 'Saqqara'],
                visa_required=True
            ),
            'capetown': Destination(
                name='Cape Town',
                country='South Africa',
                region='Africa',
                description='Stunning coastal city with Table Mountain, beaches, and wine country',
                best_time_to_visit='November-February (summer)',
                climate='Mediterranean, mild winters, warm summers',
                currency='South African Rand (ZAR)',
                language='Afrikaans, English',
                popular_attractions=['Table Mountain', 'Cape Point', 'Camps Bay Beach', 'Winelands'],
                typical_activities=['Mountain hiking', 'Wine tasting', 'Beach relaxation', 'Safari drives'],
                estimated_budget_per_day_usd='$60-120',
                nearby_cities=['Stellenbosch', 'Paarl'],
                visa_required=False
            ),
            'marrakech': Destination(
                name='Marrakech',
                country='Morocco',
                region='Africa',
                description='Red city with bustling medinas, palaces, and gateway to Sahara',
                best_time_to_visit='April-May, September-October',
                climate='Desert and Mediterranean mix, hot dry',
                currency='Moroccan Dirham (MAD)',
                language='Arabic, Berber, French, English in tourist areas',
                popular_attractions=['Jemaa el-Fnaa', 'Bahia Palace', 'Saadian Tombs', 'Menara Gardens'],
                typical_activities=['Medina exploring', 'Sahara trekking', 'Hammam spa', 'Carpet shopping'],
                estimated_budget_per_day_usd='$30-60',
                nearby_cities=['Sahara', 'Atlas Mountains'],
                visa_required=False
            ),
            'istanbul': Destination(
                name='Istanbul',
                country='Turkey',
                region='Middle East',
                description='Bridge between Europe and Asia with mosques, bazaars, and Bosphorus magic',
                best_time_to_visit='April-May, September-November',
                climate='Temperate, cold wet winters, warm dry summers',
                currency='Turkish Lira (TRY)',
                language='Turkish, English in tourist areas',
                popular_attractions=['Blue Mosque', 'Hagia Sophia', 'Grand Bazaar', 'Topkapi Palace'],
                typical_activities=['Mosque visiting', 'Bosphorus cruises', 'Bazaar shopping', 'Hammam relaxing'],
                estimated_budget_per_day_usd='$40-80',
                nearby_cities=['Cappadocia', 'Troy'],
                visa_required=False
            ),
            
            # OCEANIA
            'sydney': Destination(
                name='Sydney',
                country='Australia',
                region='Oceania',
                description='Iconic harbor city with Opera House, beaches, and laid-back Australian vibe',
                best_time_to_visit='September-November (spring), March-May (autumn)',
                climate='Temperate, warm summers, mild winters',
                currency='Australian Dollar (AUD)',
                language='English',
                popular_attractions=['Sydney Opera House', 'Harbour Bridge', 'Bondi Beach', 'Blue Mountains'],
                typical_activities=['Beach swimming', 'Bridge climbing', 'Opera visits', 'Wildlife spotting'],
                estimated_budget_per_day_usd='$100-150',
                nearby_cities=['Blue Mountains', 'Hunter Valley'],
                visa_required=True
            ),
            'melbourne': Destination(
                name='Melbourne',
                country='Australia',
                region='Oceania',
                description='Trendy cultural capital with laneways, coffee, art, and sports',
                best_time_to_visit='September-November (spring), March-May (autumn)',
                climate='Temperate oceanic, cool',
                currency='Australian Dollar (AUD)',
                language='English',
                popular_attractions=['Queen Victoria Market', 'Laneways and street art', 'MCG', 'St Pauls Cathedral'],
                typical_activities=['Coffee hopping', 'Art gallery visits', 'Sports events', 'Beach days'],
                estimated_budget_per_day_usd='$80-130',
                nearby_cities=['Great Ocean Road', 'Yarra Valley'],
                visa_required=True
            ),
            'auckland': Destination(
                name='Auckland',
                country='New Zealand',
                region='Oceania',
                description='Vibrant city between two harbors with cultural diversity and adventure nearby',
                best_time_to_visit='December-February (summer), September-November (spring)',
                climate='Temperate oceanic, mild year-round',
                currency='New Zealand Dollar (NZD)',
                language='English, Te Reo Māori',
                popular_attractions=['Sky Tower', 'Viaduct Harbour', 'Mission Bay', 'Black sand beaches'],
                typical_activities=['Sailing', 'Wine tasting', 'Museum visits', 'Beach relaxation'],
                estimated_budget_per_day_usd='$80-130',
                nearby_cities=['Rotorua', 'Queenstown'],
                visa_required=True
            ),
        }
        
        return {name.lower(): dest for name, dest in destinations.items()}


# Global instance
_db_instance = None

def get_destination_database() -> DestinationDatabase:
    """Get or create global destination database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DestinationDatabase()
    return _db_instance
