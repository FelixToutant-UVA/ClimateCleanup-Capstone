
# defining the function, calling in the values according to data
def calculate_water_cleaning_costs(pesticide_usage_kg_per_ha = 8.38,  # this amounts for the average usage of pesticides in kilograms per hectar of land
                                   pesticide_leakage_ratio = 0.07,    # this is how many percent of those pesticides leak into water sources according to data
                                   pesticide_removal_cost_per_kg = 7.40,  # how much it costs to remove 1 kg of pesticides from water 
                                   fertilizer_usage_kg_per_ha = 246.6,  # this amounts to the average usage of fertilizers in kilograms per hectar of land
                                   fertilizer_leakage_ratio = 0.65,   # this is how many percent of those fertilizers leak into water sources according to data
                                   fertilizer_removal_cost_per_kg = 3.05,  # how much it costs to remove 1 kg of fertilizers from water 
                                   food_production_kg_per_ha = 9177,  # average amount of food produced in the netherlands per hectare for 2022/23
                                   food_consumption_kg_per_person_per_year = 200):  # this value is just for to better imagine the values - for if a person purchases 200 kg of fruits and vegetables per year...
    # PESTICIDES:
    pesticide_leakage_kg_per_ha = pesticide_usage_kg_per_ha * pesticide_leakage_ratio  # calculating the amount of pesticides that leak into water in kg
    pesticide_cleaning_cost_per_ha = pesticide_leakage_kg_per_ha * pesticide_removal_cost_per_kg  # calculating how much it costs to remove that amount in kg
    pesticide_cost_per_kg_food = pesticide_cleaning_cost_per_ha / food_production_kg_per_ha   # calculating how much costs would it equal to for an average person who buys lets say 200 kg of fruits and vegetables per year

    # FERTILIZERS:
    fertilizer_leakage_kg_per_ha = fertilizer_usage_kg_per_ha * fertilizer_leakage_ratio  # calculating the amount of fertilizers that leak into water in kg
    fertilizer_cleaning_cost_per_ha = fertilizer_leakage_kg_per_ha * fertilizer_removal_cost_per_kg  # calculating how much it costs to remove that amount in kg
    fertilizer_cost_per_kg_food = fertilizer_cleaning_cost_per_ha / food_production_kg_per_ha   # calculating how much costs would it equal to for an average person who buys lets say 200 kg of fruits and vegetables per year

    # combining the costs (both pesticide and fertilizer removal costs) per kg of food
    total_cost_per_kg_food = pesticide_cost_per_kg_food + fertilizer_cost_per_kg_food

    # calculating the annual cost per person (with the chosen food consumption value)
    annual_cost_per_person = total_cost_per_kg_food * food_consumption_kg_per_person_per_year

    return {
        "pesticide_cost_per_kg_food": round(pesticide_cost_per_kg_food, 6),
        "fertilizer_cost_per_kg_food": round(fertilizer_cost_per_kg_food, 6),
        "total_cost_per_kg_food": round(total_cost_per_kg_food, 6),
        "annual_cost_per_person": round(annual_cost_per_person, 2)
    }


# results:
results = calculate_water_cleaning_costs()

for key, value in results.items():
    print(f"{key}: {value}")

