from math import pi
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from Consistent_Parameters import *

## ------------------------------------------------ SIMULATION SETTINGS ------------------------------------------------
set_injection_years = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
set_removal_rate = [100, 250, 500, 1000] # Sets a number of ash trees to remove each year

# Store all results in a dictionary with injection years as keys
all_results = {}
legend_title = "Year that Injections End & Rate of Tree Removal per Year"

## ------------------------------------------------ SIMULATION SETTINGS ------------------------------------------------
def simulate_inject_remove_and_replant(injection_year, removal_rate):
    # List to store results
    results_inject_remove_and_replant = []
    cohorts = []  # Track non-ash tree cohorts with ages

    # Initialize variables for the simulation
    ash_tree_count = starting_ash_trees
    average_diameter_ash = starting_diameter
    average_diameter_non_ash = starting_diameter_new  # Initial DBH of replanted trees

    # Cumulative cost trackers
    cumulative_removal_cost = 0
    cumulative_planting_cost = 0
    cumulative_injection_cost = 0
    cumulative_pruning_cost = 0

    # Initialize inflation factor
    inflation_factor = 1

    # Simulation loop for each year
    for year in range(1, years + 1):
        # Update ash diameter based on growth rate
        average_diameter_ash += growth_rate

        # Phase 1: Injection Period with Mortality
        if year <= injection_year:
            # Inject all ash trees each year during the injection period
            injection_cost = (ash_tree_count / 2) * average_diameter_ash * ash_tree_injections_expense * inflation_factor
            cumulative_injection_cost += injection_cost

            # Apply mortality rate to ash trees
            trees_died = int(ash_tree_count * injected_ash_mortality_rate)
            ash_tree_count -= trees_died

            # Calculate removal cost for naturally dead ash trees using cost lookup
            removal_cost = trees_died * get_removal_cost_by_dbh(average_diameter_ash) * inflation_factor
            cumulative_removal_cost += removal_cost

            # Replant dead ash trees as non-ash trees in a new cohort
            cohorts.append({'age': 0, 'count': trees_died, 'diameter': starting_diameter_new})

            # Calculate replanting cost for new non-ash trees
            replanting_cost = trees_died * tree_planting_and_establishment_expense * inflation_factor
            cumulative_planting_cost += replanting_cost

        # Phase 2: Planned Removal and Replanting Period (after injection period)
        else:
            # Remove a set number of ash trees each year
            trees_to_remove = min(removal_rate, ash_tree_count)
            ash_tree_count -= trees_to_remove

            # Calculate removal cost for removed ash trees using cost lookup
            removal_cost = trees_to_remove * get_removal_cost_by_dbh(average_diameter_ash) * inflation_factor
            cumulative_removal_cost += removal_cost

            # Replant the removed ash trees with non-ash trees in a new cohort
            cohorts.append({'age': 0, 'count': trees_to_remove, 'diameter': starting_diameter_new})

            # Calculate replanting cost for new non-ash trees
            replanting_cost = trees_to_remove * tree_planting_and_establishment_expense * inflation_factor
            cumulative_planting_cost += replanting_cost

            # Set injection cost to zero after the injection period
            injection_cost = 0

        # Reset non-ash tree count, total diameter, and removal cost each year
        non_ash_tree_count = 0
        total_diameter_non_ash = 0
        removal_cost_non_ash = 0
        surviving_cohorts = []
        for cohort in cohorts:
            cohort['age'] += 1
            cohort['diameter'] += growth_rate_new

            # Mortality for each cohort
            mortality_rate = mortality_rates_by_age.get(cohort['age'], background_mortality_rate)
            dead_trees = int(cohort['count'] * mortality_rate)
            cohort['count'] -= dead_trees

            # Conditional cost logic based on age
            if cohort['age'] >= 3:
                # Calculate removal cost for dead non-ash trees using cost lookup
                removal_cost_non_ash = dead_trees * get_removal_cost_by_dbh(cohort['diameter']) * inflation_factor
                cumulative_removal_cost += removal_cost_non_ash
                replanting_cost_non_ash = dead_trees * tree_planting_and_establishment_expense * inflation_factor
                cumulative_planting_cost += replanting_cost_non_ash
            else:
                replanting_cost_non_ash = 0
                cumulative_planting_cost += replanting_cost_non_ash

            # Update non-ash tree count and diameter
            non_ash_tree_count += cohort['count']
            total_diameter_non_ash += cohort['diameter'] * cohort['count']

            if cohort['count'] > 0:
                surviving_cohorts.append(cohort)

        # Update cohorts with surviving trees
        cohorts = surviving_cohorts

        # Calculate average diameter for non-ash trees
        if non_ash_tree_count > 0:
            average_diameter_non_ash = total_diameter_non_ash / non_ash_tree_count
        else:
            average_diameter_non_ash = starting_diameter_new

        # Total tree count
        total_tree_count = ash_tree_count + non_ash_tree_count

        # Calculate pruning costs for ash and non-ash trees using cost lookup
        pruning_cost_ash = (ash_tree_count / 7) * get_pruning_cost_by_dbh(average_diameter_ash) * inflation_factor
        pruning_cost_non_ash = (non_ash_tree_count / 7) * get_pruning_cost_by_dbh(average_diameter_non_ash) * inflation_factor
        total_pruning_cost = pruning_cost_ash + pruning_cost_non_ash
        cumulative_pruning_cost += total_pruning_cost

        # Basal areas
        ash_tree_basal_area = ((average_diameter_ash / 2) ** 2) * pi * ash_tree_count
        non_ash_tree_basal_area = ((average_diameter_non_ash / 2) ** 2) * pi * non_ash_tree_count
        total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

        # CTLA values
        ctla_value_ash = ((tree_planting_and_establishment_expense * inflation_factor) / ((starting_diameter_new / 2) ** 2)) * depreciation_ash * ash_tree_basal_area
        ctla_value_non_ash = ((tree_planting_and_establishment_expense * inflation_factor) / ((starting_diameter_new / 2) ** 2)) * depreciation_non_ash * non_ash_tree_basal_area
        ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

        # Store results
        results_inject_remove_and_replant.append({
            'Year': year,

            'Ash Tree Count': ash_tree_count,
            'Non-Ash Tree Count': non_ash_tree_count,
            'Total Tree Count': total_tree_count,

            'Ash Tree Basal Area': round(ash_tree_basal_area, 2),
            'Non-Ash Tree Basal Area': round(non_ash_tree_basal_area, 2),
            'Total Tree Basal Area': round(total_tree_basal_area, 2),

            'Cost of Tree Planting and Establishment': round(replanting_cost, 2),
            'Cost of Pruning': round(total_pruning_cost, 2),
            'Cost of Injection': round(injection_cost, 2),
            'Cost of Removal': round(removal_cost + removal_cost_non_ash, 2),
            'Total Costs': round(replanting_cost + total_pruning_cost + injection_cost + removal_cost + removal_cost_non_ash, 2),

            'Cumulative Cost of Tree Planting and Establishment': round(cumulative_planting_cost, 2),
            'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
            'Cumulative Cost of Injection': round(cumulative_injection_cost, 2),
            'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
            'Cumulative Costs': round(cumulative_planting_cost + cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost, 2),

            'CTLA Value of Ash': round(ctla_value_ash, 2),
            'CTLA Value of Non-Ash': round(ctla_value_non_ash, 2),
            'CTLA Value of All Trees': round(ctla_value_all_trees, 2),

            'Net Value of All Trees': round(
                ctla_value_all_trees - (cumulative_planting_cost + cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost), 2)
        })

        # Update the inflation factor for the next year
        inflation_factor *= 1 + annual_inflation_rate

    return pd.DataFrame(results_inject_remove_and_replant)

## ------------------------------------------------- PLOTTING FUNCTION -------------------------------------------------
# Formatter function to add commas
def format_with_commas(x, pos):
    return f"{int(x):,}"

def plot_simulations(simulation_results, legend_title):
    # Define scenarios and corresponding colors for plotting
    scenarios = simulation_results.keys()
    colors = ['red', 'blue', 'green', 'black']

    # Metrics to plot
    metrics = [
        ('Total Tree Count', 'Count', 'Total Tree Count Over Time'),
        ('Total Tree Basal Area', 'Basal Area (cubic meters)', 'Total Tree Basal Area Over Time'),
        ('Total Costs', 'Cost (per $1k)', 'Annual Costs'),
        ('Cumulative Costs', 'Cost (per $1k)', 'Cumulative Costs Over Time'),
        ('CTLA Value of All Trees', 'CTLA Value (per $1k)', 'CTLA Value of All Trees Over Time'),
        ('Net Value of All Trees', 'Net Value (per $1k)', 'Net Value of All Trees Over Time'),
    ]

    # Create figure for plots
    fig, axs = plt.subplots(3, 2, figsize=(18, 12), dpi=900)  # Create a 3x2 grid for subplots

    # Flatten axes for easier iteration
    axs = axs.flatten()

    # Loop over each metric to create subplots
    for idx, (metric, ylabel, title) in enumerate(metrics):
        ax = axs[idx]  # Get the axis for the current subplot
        lines = []  # Store plot lines for legend

        for scenario, color in zip(scenarios, colors):
            data = simulation_results[scenario]

            # Scale Cumulative Costs to per $1,000
            data_copy = data.copy()
            if metric in ['Total Costs', 'Cumulative Costs', 'CTLA Value of All Trees', 'Net Value of All Trees']:
                data_copy[metric] = data_copy[metric] / 1000  # Scale to per $1,000

            line, = ax.plot(data['Year'], data_copy[metric], label=scenario, color=color, linewidth = 2)
            lines.append(line)  # Save line for legend
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(False)

        # Apply the formatter to add commas to y-axis numbers
        ax.yaxis.set_major_formatter(FuncFormatter(format_with_commas))

        # Add legend only to the last subplot
        if idx == 3:
            ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), title=legend_title, fontsize=12, title_fontsize=14, ncol=1)

    # Adjust layout to avoid overlap and reserve space for the legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Reserve space on the right for the legend
    plt.savefig(f"{legend_title}.jpeg", format='jpeg', dpi=900)

## ------------------------------------------------- LOOP THE FUNCTION -------------------------------------------------
# Loop through each combination of removal rate and injection year
for removal_rate in set_removal_rate:
    for injection_year in set_injection_years:
        print(f"Running simulation for Removal Rate: {removal_rate}, Injection Year: {injection_year}")

        # Update the current removal rate and injection year
        current_removal_rate = removal_rate
        current_injection_year = injection_year

        # Run the simulation with the current parameters
        results = simulate_inject_remove_and_replant(current_injection_year, current_removal_rate)

        # Store the results with both parameters as the key
        key = f'Removal Rate: {removal_rate}, Injection Year: {injection_year}'
        all_results[key] = results

# Plot the simulation results
plot_simulations(all_results, legend_title)

## ----------------------------------------------- OPTIMIZATION FUNCTION -----------------------------------------------
# Extract and print the removal rate achieving the highest value for each metric at Year 20
metrics = [
    'Total Tree Count',
    'Total Tree Basal Area',
    'Cumulative Costs',
    'CTLA Value of All Trees',
    'Net Value of All Trees',
]

# Initialize dictionary to store the optimization for each metric
best_combinations = {}

for metric in metrics:
    best_combination = None
    best_value = float('-inf') if metric != 'Cumulative Costs' else float('inf')

    for key, results in all_results.items():
        removal_rate, injection_year = key.split(", ")
        removal_rate = removal_rate.split(": ")[1]
        injection_year = injection_year.split(": ")[1]

        if 'Year' not in results.columns or metric not in results.columns:
            print(f"Metric '{metric}' or 'Year' not found in results for {key}")
            continue

        # Get value for Year 20
        year_20_value = results.loc[results['Year'] == 20, metric]
        if not year_20_value.empty:
            year_20_value = year_20_value.values[0]
        else:
            print(f"No data for Year 20 in {key}")
            continue

        # Update the best combination based on the value
        if metric == 'Cumulative Costs':
            if year_20_value < best_value:
                best_value = year_20_value
                best_combination = (removal_rate, injection_year)
        else:
            if year_20_value > best_value:
                best_value = year_20_value
                best_combination = (removal_rate, injection_year)

    best_combinations[metric] = (best_combination, best_value)

# Print the results
print("Best Removal Rates and Injection Years for Each Metric (Evaluated at Year 20):")
for metric, ((removal_rate, injection_year), value) in best_combinations.items():
    if metric == 'Cumulative Costs':
        print(f"{metric}: Removal Rate = {removal_rate}, Injection Year = {injection_year}, Lowest Value = {value:.2f}")
    else:
        print(f"{metric}: Removal Rate = {removal_rate}, Injection Year = {injection_year}, Highest Value = {value:.2f}")