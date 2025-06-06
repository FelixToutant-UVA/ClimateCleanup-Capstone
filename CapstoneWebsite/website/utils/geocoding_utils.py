"""
Geocoding utilities for converting addresses to coordinates using geocode.maps.co API.
"""
import requests
import time
from typing import Optional, Tuple

# API configuration
GEOCODE_API_KEY = "683d7767b00d8744657247xzmc4b53e"
GEOCODE_BASE_URL = "https://geocode.maps.co/search"

def geocode_address(address: str, city: str = None, postal_code: str = None, country: str = "Netherlands") -> Optional[Tuple[float, float]]:
    """
    Geocode an address using geocode.maps.co API.
    
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
        # Use geocode.maps.co API
        params = {
            'q': full_address,
            'api_key': GEOCODE_API_KEY,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'nl' if country.lower() in ['netherlands', 'nederland'] else None
        }
        
        headers = {
            'User-Agent': 'FoodForestApp/1.0'
        }
        
        response = requests.get(GEOCODE_BASE_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            print(f"Successfully geocoded '{full_address}' to ({lat}, {lon})")
            return (lat, lon)
        
        print(f"No results found for address: '{full_address}'")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"API request error for address '{full_address}': {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Data parsing error for address '{full_address}': {e}")
        return None
    except Exception as e:
        print(f"Unexpected geocoding error for address '{full_address}': {e}")
        return None

def geocode_forest_location(user) -> Optional[Tuple[float, float]]:
    """
    Geocode a forest's location from user data with priority order.
    
    Args:
        user: User object with forest location data
        
    Returns:
        Tuple[float, float]: (latitude, longitude) or None if not found
    """
    # If coordinates already exist and seem valid, return them
    if user.forest_latitude and user.forest_longitude:
        # Basic validation - check if coordinates are in reasonable range
        if (-90 <= user.forest_latitude <= 90) and (-180 <= user.forest_longitude <= 180):
            print(f"Using existing coordinates for {user.forest_name}: ({user.forest_latitude}, {user.forest_longitude})")
            return (user.forest_latitude, user.forest_longitude)
    
    # Priority 1: Try detailed address fields (most precise)
    if user.forest_address or user.forest_city or user.forest_postal_code:
        coords = geocode_address(
            address=user.forest_address,
            city=user.forest_city,
            postal_code=user.forest_postal_code,
            country=user.forest_country or "Netherlands"
        )
        
        if coords:
            print(f"Geocoded from detailed address for {user.forest_name}")
            return coords
    
    # Priority 2: Fallback to forest_location field (less precise)
    if user.forest_location:
        coords = geocode_address(user.forest_location)
        if coords:
            print(f"Geocoded from forest_location field for {user.forest_name}")
            return coords
    
    print(f"Could not geocode any location data for {user.forest_name}")
    return None

def geocode_business_location(user) -> Optional[Tuple[float, float]]:
    """
    Geocode a business's location from user data with priority order.
    
    Args:
        user: User object with business location data
        
    Returns:
        Tuple[float, float]: (latitude, longitude) or None if not found
    """
    # If coordinates already exist and seem valid, return them
    if user.business_latitude and user.business_longitude:
        # Basic validation - check if coordinates are in reasonable range
        if (-90 <= user.business_latitude <= 90) and (-180 <= user.business_longitude <= 180):
            print(f"Using existing coordinates for {user.business_name}: ({user.business_latitude}, {user.business_longitude})")
            return (user.business_latitude, user.business_longitude)
    
    # Priority 1: Try detailed address fields (most precise)
    if user.business_address or user.business_city or user.business_postal_code:
        coords = geocode_address(
            address=user.business_address,
            city=user.business_city,
            postal_code=user.business_postal_code,
            country=user.business_country or "Netherlands"
        )
        
        if coords:
            print(f"Geocoded from detailed address for {user.business_name}")
            return coords
    
    # Priority 2: Fallback to business_location field (less precise)
    if user.business_location:
        coords = geocode_address(user.business_location)
        if coords:
            print(f"Geocoded from business_location field for {user.business_name}")
            return coords
    
    print(f"Could not geocode any location data for {user.business_name}")
    return None

def update_forest_coordinates(user, db_session):
    """
    Update forest coordinates for a user and save to database.
    
    Args:
        user: User object
        db_session: Database session
        
    Returns:
        Tuple[float, float] or None: Updated coordinates
    """
    coords = geocode_forest_location(user)
    
    if coords:
        user.forest_latitude = coords[0]
        user.forest_longitude = coords[1]
        try:
            db_session.commit()
            print(f"Updated coordinates for {user.forest_name}: {coords}")
            return coords
        except Exception as e:
            db_session.rollback()
            print(f"Database error updating coordinates for {user.forest_name}: {e}")
            return None
    else:
        print(f"Could not geocode location for {user.forest_name}")
        return None

def update_business_coordinates(user, db_session):
    """
    Update business coordinates for a user and save to database.
    
    Args:
        user: User object
        db_session: Database session
        
    Returns:
        Tuple[float, float] or None: Updated coordinates
    """
    coords = geocode_business_location(user)
    
    if coords:
        user.business_latitude = coords[0]
        user.business_longitude = coords[1]
        try:
            db_session.commit()
            print(f"Updated coordinates for {user.business_name}: {coords}")
            return coords
        except Exception as e:
            db_session.rollback()
            print(f"Database error updating coordinates for {user.business_name}: {e}")
            return None
    else:
        print(f"Could not geocode location for {user.business_name}")
        return None

def batch_update_coordinates(db_session):
    """
    Batch update coordinates for all users that don't have them yet.
    
    Args:
        db_session: Database session
    """
    from ..models import User
    
    # Update food forests without coordinates
    forests_without_coords = User.query.filter(
        User.account_type == 'food-forest',
        (User.forest_latitude.is_(None) | User.forest_longitude.is_(None))
    ).all()
    
    print(f"Found {len(forests_without_coords)} food forests without coordinates")
    
    for forest in forests_without_coords:
        print(f"Updating coordinates for forest: {forest.forest_name}")
        update_forest_coordinates(forest, db_session)
        time.sleep(0.5)  # Rate limiting - be nice to the API
    
    # Update businesses without coordinates
    businesses_without_coords = User.query.filter(
        User.account_type == 'business',
        (User.business_latitude.is_(None) | User.business_longitude.is_(None))
    ).all()
    
    print(f"Found {len(businesses_without_coords)} businesses without coordinates")
    
    for business in businesses_without_coords:
        print(f"Updating coordinates for business: {business.business_name}")
        update_business_coordinates(business, db_session)
        time.sleep(0.5)  # Rate limiting - be nice to the API

def get_distance_between_coordinates(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two coordinates using the Haversine formula.
    
    Args:
        lat1, lon1: First coordinate pair
        lat2, lon2: Second coordinate pair
        
    Returns:
        float: Distance in kilometers
    """
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def find_nearby_forests(business_user, max_distance_km: float = 50) -> list:
    """
    Find food forests within a certain distance of a business.
    
    Args:
        business_user: Business user object
        max_distance_km: Maximum distance in kilometers
        
    Returns:
        list: List of nearby forest users with distance information
    """
    from ..models import User
    
    if not (business_user.business_latitude and business_user.business_longitude):
        return []
    
    # Get all food forests with coordinates
    forests = User.query.filter(
        User.account_type == 'food-forest',
        User.forest_latitude.isnot(None),
        User.forest_longitude.isnot(None)
    ).all()
    
    nearby_forests = []
    
    for forest in forests:
        distance = get_distance_between_coordinates(
            business_user.business_latitude,
            business_user.business_longitude,
            forest.forest_latitude,
            forest.forest_longitude
        )
        
        if distance <= max_distance_km:
            nearby_forests.append({
                'forest': forest,
                'distance_km': round(distance, 2)
            })
    
    # Sort by distance
    nearby_forests.sort(key=lambda x: x['distance_km'])
    
    return nearby_forests

def get_amsterdam_fallback_coordinates(index: int = 0) -> Tuple[float, float]:
    """
    Get fallback coordinates within Amsterdam for entities without exact locations.
    
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
