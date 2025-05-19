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


# Example Usage
example = calculate_carbon_sequestration_simple(
    forest_age=18,
    years_since_conversion=10,
    soil_type="loamy"
)

for key, value in example.items():
    print(f"{key}: {value}")
