"""
Carbon sequestration calculation utilities for food forests.
This module provides functions to estimate carbon sequestration and climate value
of food forests compared to conventional agriculture.
"""

def calculate_carbon_sequestration(
    size_m2: float,
    forest_age: int,
    soil_type: str,
    biodiversity_index: float = 0.75
):
    """
    Calculate carbon sequestration based on food forest parameters.
    
    Args:
        size_m2 (float): Size of the food forest in square meters
        forest_age (int): Age of the food forest in years
        soil_type (str): Type of soil (e.g., "Zandgrond", "Kleigrond", etc.)
        biodiversity_index (float): Biodiversity index (0-1)
        
    Returns:
        dict: Carbon sequestration estimates
    """
    # Soil sequestration rates: tons CO2e per hectare per year
    SEQUESTRATION_RATES = {
        "Zandgrond": (3.74, 9.84),
        "Kleigrond": (14.5, 14.5),
        "Veengrond": (25, 30),
        "Loess": (10, 20)
    }
    
    # Convert to hectares
    area_ha = size_m2 / 10000
    
    # Get sequestration rate based on soil type
    if soil_type in SEQUESTRATION_RATES:
        rate_min, rate_max = SEQUESTRATION_RATES[soil_type]
        min_seq = round(area_ha * rate_min * forest_age, 2)
        max_seq = round(area_ha * rate_max * forest_age, 2)
        
        # Apply biodiversity multiplier (higher biodiversity = more efficient carbon capture)
        biodiversity_multiplier = 1 + (biodiversity_index * 0.3)  # Up to 30% boost
        min_seq = round(min_seq * biodiversity_multiplier, 2)
        max_seq = round(max_seq * biodiversity_multiplier, 2)
        
        return {
            "min": min_seq,
            "max": max_seq,
            "unit": "tons CO₂e",
            "annual_min": round(area_ha * rate_min, 2),
            "annual_max": round(area_ha * rate_max, 2),
            "annual_unit": "tons CO₂e/year"
        }
    
    return None

def calculate_carbon_sequestration_simple(
    forest_age: int,
    years_since_conversion: int,
    soil_type: str,
    co2_price_per_ton: float = 89.0
):
    """
    Estimate carbon sequestration and climate value of a food forest vs conventional agriculture.

    Parameters:
        forest_age (int): Age of the food forest in years.
        years_since_conversion (int): Years since conversion from cropland.
        soil_type (str): Soil type for soil organic carbon (SOC) estimation. E.g., 'loamy', 'marine_clay', 'sandy'.
        co2_price_per_ton (float): Price per ton of CO₂ credits in EUR. Default = €89.

    Returns:
        dict: Carbon sequestration stats and value estimate.
    """

    # Age-to-carbon mapping (aboveground CO2 in t/ha)
    age_to_carbon_co2 = {
        "0-5": 6.24,
        "6-15": 45.88,
        "16-25": 135.06,
        "25+": 243.69,
    }

    # Soil carbon gain rates in t C/ha/year
    soil_conversion_C = {
        "loamy": 1.5,
        "marine_clay": 2.9,
        "sandy": 1.0,
        "brick": 0.3,
        "earth": 1.4,
        "old_clay": 1.1,
        "podzol": 0.8,
        "river_clay": 2.8,
        "not_determined": 0.3
    }

    C_TO_CO2 = 3.67

    # Match forest age to category
    if forest_age <= 5:
        age_group = "0-5"
    elif forest_age <= 15:
        age_group = "6-15"
    elif forest_age <= 25:
        age_group = "16-25"
    else:
        age_group = "25+"

    # Aboveground carbon from age
    aboveground_co2 = age_to_carbon_co2.get(age_group, 0)

    # Belowground carbon from soil type and conversion duration
    annual_soil_c = soil_conversion_C.get(soil_type, 0)
    belowground_co2 = annual_soil_c * years_since_conversion * C_TO_CO2

    # Total carbon sequestration in food forest
    total_ff_co2 = aboveground_co2 + belowground_co2

    # Conventional cropland benchmark
    conventional_co2 = 18.35  # t CO₂/ha

    # Added value
    additional_co2 = total_ff_co2 - conventional_co2
    value_eur = additional_co2 * co2_price_per_ton

    return {
        "Aboveground CO2 (t/ha)": round(aboveground_co2, 2),
        "Belowground CO2 (t/ha)": round(belowground_co2, 2),
        "Total Food Forest CO2 (t/ha)": round(total_ff_co2, 2),
        "Conventional Agriculture CO2 (t/ha)": conventional_co2,
        "Difference (t/ha)": round(additional_co2, 2),
        "Carbon Credit Value (€)": round(value_eur, 2)
    }

def map_soil_types(soil_type):
    """
    Map the application soil types to the soil types used in the carbon calculation.
    
    Args:
        soil_type (str): Soil type from the application
        
    Returns:
        str: Corresponding soil type for carbon calculations
    """
    soil_mapping = {
        "Zandgrond": "sandy",
        "Kleigrond": "marine_clay",
        "Veengrond": "earth",
        "Loess": "loamy"
    }
    
    return soil_mapping.get(soil_type, "not_determined")

def calculate_water_savings(size_m2, forest_age, soil_type):
    """
    Estimate water savings compared to conventional agriculture.
    
    Args:
        size_m2 (float): Size of the food forest in square meters
        forest_age (int): Age of the food forest in years
        soil_type (str): Type of soil
        
    Returns:
        dict: Water savings estimates
    """
    # Convert to hectares
    area_ha = size_m2 / 10000
    
    # Base water usage in conventional agriculture (cubic meters per hectare per year)
    conventional_water = 5000
    
    # Water usage reduction factors by soil type
    water_reduction = {
        "Zandgrond": 0.4,  # 40% reduction
        "Kleigrond": 0.5,
        "Veengrond": 0.6,
        "Loess": 0.45
    }
    
    # Get reduction factor based on soil type
    reduction = water_reduction.get(soil_type, 0.4)
    
    # Age multiplier (older forests are more efficient)
    age_multiplier = min(1 + (forest_age * 0.05), 1.5)  # Up to 50% more efficient
    reduction = min(reduction * age_multiplier, 0.7)  # Cap at 70% reduction
    
    # Calculate water savings
    annual_savings = conventional_water * area_ha * reduction
    total_savings = annual_savings * forest_age
    
    return {
        "annual_savings": round(annual_savings, 2),
        "total_savings": round(total_savings, 2),
        "unit": "cubic meters",
        "reduction_percentage": round(reduction * 100, 1)
    }

def calculate_water_storage(size_m2, soil_type, age_years):
    """
    Calculate water storage capacity based on forest parameters.
    
    Args:
        size_m2 (float): Size of the food forest in square meters
        soil_type (str): Type of soil
        age_years (int): Age of the forest
        
    Returns:
        float: Water storage in cubic meters
    """
    # Base water storage per square meter by soil type (cubic meters)
    base_storage = {
        "Zandgrond": 0.15,  # Sandy soil - lower retention
        "Kleigrond": 0.25,  # Clay soil - higher retention
        "Veengrond": 0.35,  # Peat soil - highest retention
        "Loess": 0.20       # Loess - moderate retention
    }
    
    # Age multiplier (older forests store more water)
    age_multiplier = min(1 + (age_years * 0.1), 2.0)  # Cap at 2x
    
    # Calculate total storage
    storage_per_m2 = base_storage.get(soil_type, 0.20)
    total_storage = size_m2 * storage_per_m2 * age_multiplier
    
    return round(total_storage, 2)
