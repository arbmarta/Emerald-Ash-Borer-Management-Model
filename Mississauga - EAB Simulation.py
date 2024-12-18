## ------------------------------------------------ SIMULATION SETTINGS ------------------------------------------------
set_removal_rate = 400 # Sets a number of ash trees to remove each year
set_planting_rate = 400 # Sets a number of new trees to plant each year
set_removal_year = 5 # Select year in which ash trees begin to be removed
set_injection_years = 5 # Number of years to inject ash
set_planting_year = 1 # Year where tree planting starts

from Simulation_Parameters import *
from Simulation_Module import run_simulations, report_year_20_values, report_year_20_counts
from Simulation_Plotter import plot_simulations

simulation_results = run_simulations(starting_ash_trees, starting_diameter, starting_diameter_new, growth_rate,
                                    growth_rate_new, ash_mortality_rate, injected_ash_mortality_rate,
                                    tree_planting_and_establishment_expense, ash_tree_injections_expense,
                                    set_removal_rate, set_removal_year, set_injection_years, set_planting_rate, set_planting_year,
                                    depreciation_ash, depreciation_non_ash, mortality_rates_by_age,
                                    background_mortality_rate, annual_inflation_rate, years,
                                    get_pruning_cost_by_dbh, get_removal_cost_by_dbh)

report_year_20_values(simulation_results)
report_year_20_counts(simulation_results)
plot_simulations(simulation_results)
