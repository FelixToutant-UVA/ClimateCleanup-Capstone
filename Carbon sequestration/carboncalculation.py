def calculate_carbon_sequestration_simple(
    forest_age: int,
    years_since_conversion: int,
    soil_type: str,
    conversion_type: str = "cropland_to_forest",  # of "grassland_to_forest"
    co2_price_per_ton: float = 89.0
):
    """
    Estimate carbon sequestration and climate value of a food forest vs conventional agriculture.

    Parameters:
        forest_age (int): Age of the food forest in years.
        years_since_conversion (int): Years since land was converted.
        soil_type (str): Soil type (e.g., 'loamy', 'marine_clay', 'sandy').
        conversion_type (str): 'cropland_to_forest' or 'grassland_to_forest'.
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

    # Conversion rates (t C/ha/year) from table
    soil_conversion_C = {
        "cropland_to_forest": {
            "brick": 0.3,
            "earth": 1.4,
            "sandy_with_lime": -1.1,
            "sandy_without_lime": -1.0,
            "loamy": 1.5,
            "old_clay": -1.1,
            "podzol": -0.8,
            "river_clay": 2.8,
            "marine_clay": 2.9,
            "not_determined": 0.3
        },
        "grassland_to_forest": {
            "brick": 0.2,
            "earth": 0.6,
            "sandy_with_lime": -1.3,
            "sandy_without_lime": -1.5,
            "loamy": 1.2,
            "old_clay": -1.0,
            "podzol": -1.2,
            "river_clay": 1.4,
            "marine_clay": 1.3,
            "not_determined": -0.9
        }
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

    # Belowground carbon based on soil type and conversion type
    conversion_dict = soil_conversion_C.get(conversion_type, {})
    annual_soil_c = conversion_dict.get(soil_type, 0)
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


# Example usage:
example = calculate_carbon_sequestration_simple(
    forest_age=18,
    years_since_conversion=10,
    soil_type="loamy",
    conversion_type="cropland_to_forest"
)

for key, value in example.items():
    print(f"{key}: {value}")
