"""
Geocoding utilities for converting addresses to coordinates.
"""
import requests
import time
from typing import Optional, Tuple

def geocode_address(address: str, city: str = None, postal_code: str = None, country: str = "Netherlands") -> Optional[Tuple[float, float]]:
    """
    Geocode an address using OpenStreetMap Nominatim API.
    
    Args:
        address (str): Street address
        city (str): City name
        postal_code (str): Postal code
        country (str): Country name
        
    Returns:
        Tuple[float, float]: (latitude, longitude) or None if not found
    """
    # Build the full address string
    address_parts = []
    if address:
        address_parts.append(address)
    if city:
        address_parts.append(city)
    if postal_code:
        address_parts.append(postal_code)
    if country:
        address_parts.append(country)
    
    full_address = ", ".join(address_parts)
    
    if not full_address.strip():
        return None
    
    try:
        # Use OpenStreetMap Nominatim API (free, no API key required)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': full_address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'nl' if country.lower() in ['netherlands', 'nederland'] else None
        }
        
        headers = {
            'User-Agent': 'FoodForestApp/1.0'  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return (lat, lon)
        
        return None
        
    except Exception as e:
        print(f"Geocoding error for address '{full_address}': {e}")
        return None

def geocode_forest_location(user) -> Optional[Tuple[float, float]]:
    """
    Geocode a forest's location from user data.
    
    Args:
        user: User object with forest location data
        
    Returns:
        Tuple[float, float]: (latitude, longitude) or None if not found
    """
    # If coordinates already exist, return them
    if user.forest_latitude and user.forest_longitude:
        return (user.forest_latitude, user.forest_longitude)
    
    # Try to geocode from detailed address fields
    if user.forest_address or user.forest_city:
        coords = geocode_address(
            address=user.forest_address,
            city=user.forest_city,
            postal_code=user.forest_postal_code,
            country=user.forest_country or "Netherlands"
        )
        
        if coords:
            return coords
    
    # Fallback to forest_location field
    if user.forest_location:
        coords = geocode_address(user.forest_location)
        if coords:
            return coords
    
    return None

def update_forest_coordinates(user, db_session):
    """
    Update forest coordinates for a user and save to database.
    
    Args:
        user: User object
        db_session: Database session
    """
    coords = geocode_forest_location(user)
    
    if coords:
        user.forest_latitude = coords[0]
        user.forest_longitude = coords[1]
        db_session.commit()
        print(f"Updated coordinates for {user.forest_name}: {coords}")
        return coords
    else:
        print(f"Could not geocode location for {user.forest_name}")
        return None

def get_amsterdam_fallback_coordinates(index: int = 0) -> Tuple[float, float]:
    """
    Get fallback coordinates within Amsterdam for forests without exact locations.
    
    Args:
        index: Index to cycle through different Amsterdam locations
        
    Returns:
        Tuple[float, float]: (latitude, longitude)
    """
    amsterdam_locations = [
        (52.3676, 4.9041),   # Amsterdam Center
        (52.3702, 4.8952),   # Vondelpark area
        (52.3738, 4.8910),   # Jordaan area
        (52.3555, 4.9139),   # Oost area
        (52.3478, 4.9036),   # Zuid area
        (52.3890, 4.9200),   # Noord area
        (52.3420, 4.8700),   # Nieuw-West area
        (52.3600, 4.8500),   # West area
        (52.3800, 4.9300),   # Waterplein area
        (52.3400, 4.9200),   # Zuiderpark area
    ]
    
    return amsterdam_locations[index % len(amsterdam_locations)]
