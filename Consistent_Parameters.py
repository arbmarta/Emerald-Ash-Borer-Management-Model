## ---------------------------------------------- MISSISSAUGA PARAMETERS ----------------------------------------------
# Tree Inventory Parameters
years = 20
starting_ash_trees = 1490
starting_diameter = 27.18
growth_rate = 0.30 # Growth rate of ash in cm

# Mortality and Growth data
background_mortality_rate = 0.0085  # Natural (“background”) mortality rate across all tree species
injected_ash_mortality_rate = 0.028 # Mortality rate of ash tree population while being injected
ash_mortality_rate = 0.20 # Mortality rate of ash tree population without injection

# Replanting Data
starting_diameter_new = 6  # Starting diameter of replanted trees in cm
growth_rate_new = 0.47  # Growth rate of replanted trees in cm
warranty_period_ends = 3 # Warranty period ends at 3_year_post_planting

# Mortality rate data for new plantings
mortality_1_year_post_planting_overall = 0.085
mortality_2_year_post_planting_overall = 0.117
mortality_3_year_post_planting_overall = 0.042
mortality_4_year_post_planting_overall = 0.061

# Define mortality rates by age with default for age >= 5
mortality_rates_by_age = {
    age: globals()[f"mortality_{age}_year_post_planting_overall"] if age <= 4 else background_mortality_rate
    for age in range(1, years + 1)
}

# Management expenses
tree_planting_and_establishment_expense = 849.91 # Cost ($) to plant and establish a 6 cm caliper tree.
ash_tree_injections_expense = 3.325 # Cost ($) to inject tree per cm DBH

# Define cost ranges for removal
removal_cost_ranges = [
    (0, 20, 105), # (Min DBH, Max DBH, pruning cost)
    (20, 40, 305),
    (40, 60, 855),
    (60, 80, 1450),
    (80, 100, 2950),
    (100, 120, 2950),
    (120, float('inf'), 5700)
]

def get_removal_cost_by_dbh(dbh):
    """Get removal cost based on DBH, with error if out of range."""
    for min_dbh, max_dbh, removal_cost in removal_cost_ranges:
        if min_dbh < dbh <= max_dbh:
            return removal_cost
    raise ValueError(f"DBH value {dbh} falls outside defined cost ranges.")

# Define cost ranges for pruning
pruning_cost_ranges = [
    (0, 20, 60), # (Min DBH, Max DBH, pruning cost)
    (20, 40, 118),
    (40, 60, 268),
    (60, 80, 460),
    (80, 100, 610),
    (100, 120, 710),
    (120, float('inf'), 862)
]

def get_pruning_cost_by_dbh(dbh):
    """Get pruning cost based on DBH, with error if out of range."""
    for min_dbh, max_dbh, pruning_cost in pruning_cost_ranges:
        if min_dbh < dbh <= max_dbh:
            return pruning_cost
    raise ValueError(f"DBH value {dbh} falls outside defined cost ranges.")

annual_inflation_rate = 0.02
#endregion

# CTLA Trunk Formula Technique
condition_rating_ash = 0.50
functional_limitations_ash = 0.10
external_limitations_ash = 0.80
depreciation_ash = condition_rating_ash * functional_limitations_ash * external_limitations_ash

condition_rating_nonash = 0.75
functional_limitations_nonash = 0.70
external_limitations_nonash = 0.90
depreciation_non_ash = condition_rating_nonash * functional_limitations_nonash * external_limitations_nonash