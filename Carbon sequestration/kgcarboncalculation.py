def calculate_carbon_sequestration_per_kg_food(
    forest_age: int,
    years_since_conversion: int,
    soil_type: str,
    conversion_type: str = "cropland_to_forest",
    co2_price_per_ton: float = 89.0,
    food_yield_ff: float = 3500,      # kg voedsel/ha/jaar in voedselbos
):
    """
    Estimate carbon sequestration and value per kg food for food forest vs. conventional.

    Parameters:
        forest_age (int): Age of the food forest in years.
        years_since_conversion (int): Years since conversion.
        soil_type (str): Soil type.
        conversion_type (str): Land use change.
        co2_price_per_ton (float): CO₂ credit price in €.
        food_yield_ff (float): Annual food yield in kg/ha for food forest.
        food_yield_conv (float): Annual food yield in kg/ha for conventional agriculture.

    Returns:
        dict: Overview of CO₂ sequestration and climate value per kg food.
    """

    age_to_carbon_co2 = {
        "0-5": 6.24, "6-15": 45.88, "16-25": 135.06, "25+": 243.69
    }

    soil_conversion_C = {
        "cropland_to_forest": {
            "brick": 0.3, "earth": 1.4, "sandy_with_lime": -1.1,
            "sandy_without_lime": -1.0, "loamy": 1.5, "old_clay": -1.1,
            "podzol": -0.8, "river_clay": 2.8, "marine_clay": 2.9,
            "not_determined": 0.3
        },
        "grassland_to_forest": {
            "brick": 0.2, "earth": 0.6, "sandy_with_lime": -1.3,
            "sandy_without_lime": -1.5, "loamy": 1.2, "old_clay": -1.0,
            "podzol": -1.2, "river_clay": 1.4, "marine_clay": 1.3,
            "not_determined": -0.9
        }
    }

    C_TO_CO2 = 3.67
    conventional_co2 = 23.35  # t CO₂/ha (netto)

    if forest_age <= 5:
        age_group = "0-5"
    elif forest_age <= 15:
        age_group = "6-15"
    elif forest_age <= 25:
        age_group = "16-25"
    else:
        age_group = "25+"

    # Berekeningen
    aboveground_co2 = age_to_carbon_co2[age_group]
    annual_soil_c = soil_conversion_C[conversion_type][soil_type]
    belowground_co2 = annual_soil_c * years_since_conversion * C_TO_CO2
    total_ff_co2 = aboveground_co2 + belowground_co2
    additional_co2 = total_ff_co2 - conventional_co2

    co2_per_kg_ff = additional_co2 / food_yield_ff if food_yield_ff > 0 else 0
    value_per_kg_ff = co2_per_kg_ff * co2_price_per_ton

    return {
        "CO2-opslag voedselbos (t/ha)": round(total_ff_co2, 2),
        "CO2-opslag conventioneel (t/ha)": round(conventional_co2, 2),
        "Extra CO2-opslag t.o.v. conventioneel (t/ha)": round(additional_co2, 2),
        "Extra CO2 per kg voedsel (ton)": round(co2_per_kg_ff, 5),
        "Waarde per kg voedsel (€)": round(value_per_kg_ff, 2)
    }

result = calculate_carbon_sequestration_per_kg_food(
    forest_age=15,
    years_since_conversion=15,
    soil_type="loamy",
    conversion_type="cropland_to_forest"
)

for key, value in result.items():
    print(f"{key}: {value}")
