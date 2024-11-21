from math import pi
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from Consistent_Parameters import *

## ------------------------------------------------ SIMULATION SETTINGS ------------------------------------------------
set_removal_rate = [100, 250, 500, 1000] # Sets a number of ash trees to remove each year

# Store all results in a dictionary with injection years as keys
all_results = {}
legend_title = "Rate of Tree Removal per Year"

## ------------------------------------------------ SIMULATION SETTINGS ------------------------------------------------
def simulate_remove_then_replant(set_removal_rate):
    # List to store results
    results_remove_then_replant = []
    cohorts = []  # Track non-ash tree cohorts with ages

    # Initialize variables for the simulation
    ash_tree_count = starting_ash_trees
    average_diameter_ash = starting_diameter
    average_diameter_non_ash = starting_diameter_new  # Initial diameter for new trees

    # Cumulative cost trackers
    cumulative_removal_cost = 0
    cumulative_pruning_cost = 0
    cumulative_planting_cost = 0

    # Initialize inflation factor and set the annual inflation rate
    inflation_factor = 1

    # Simulation loop for each year
    for year in range(1, years + 1):
        # Update ash tree diameter based on growth rate
        average_diameter_ash += growth_rate

        # Remove up to set removal rate (e.g., 400 trees), or however many remain if less than set removal rate
        trees_to_remove = min(set_removal_rate, ash_tree_count)
        ash_tree_count -= trees_to_remove

        # Add removed ash trees as a new non-ash cohort (replanting) with initial diameter
        cohorts.append({'age': 0, 'count': trees_to_remove, 'diameter': starting_diameter_new})

        # Reset non-ash tree count, total diameter, and removal cost for non-ash trees each year
        non_ash_tree_count = 0
        total_diameter_non_ash = 0  # Reset this each year
        removal_cost_non_ash = 0

        # Apply age-based mortality to each cohort and update non-ash tree count
        surviving_cohorts = []
        for cohort in cohorts:
            cohort['age'] += 1  # Increment age for each cohort
            cohort['diameter'] += growth_rate_new  # Increment diameter for each cohort

            # Get mortality rate for the cohort's current age
            mortality_rate = mortality_rates_by_age.get(cohort['age'], background_mortality_rate)
            dead_trees = int(cohort['count'] * mortality_rate)
            cohort['count'] -= dead_trees

            # Conditional cost logic based on age
            if cohort['age'] >= 3:
                removal_cost_non_ash = get_removal_cost_by_dbh(cohort['diameter']) * dead_trees * inflation_factor
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

        # Calculate the average diameter for all non-ash trees
        if non_ash_tree_count > 0:
            average_diameter_non_ash = total_diameter_non_ash / non_ash_tree_count
        else:
            average_diameter_non_ash = starting_diameter_new

        # Calculate total tree count
        total_tree_count = ash_tree_count + non_ash_tree_count

        # Calculate costs with inflation applied
        removal_cost_ash = get_removal_cost_by_dbh(average_diameter_ash) * trees_to_remove * inflation_factor
        replanting_cost = trees_to_remove * tree_planting_and_establishment_expense * inflation_factor
        pruning_cost = get_pruning_cost_by_dbh(average_diameter_non_ash) * (non_ash_tree_count / 7) * inflation_factor
        total_removal_cost = removal_cost_ash + removal_cost_non_ash

        # Update cumulative costs
        cumulative_removal_cost += total_removal_cost
        cumulative_planting_cost += replanting_cost
        cumulative_pruning_cost += pruning_cost

        # Calculate basal areas
        ash_tree_basal_area = ((average_diameter_ash / 2) ** 2) * pi * ash_tree_count
        non_ash_tree_basal_area = ((average_diameter_non_ash / 2) ** 2) * pi * non_ash_tree_count
        total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

        # Calculate CTLA values for ash and non-ash trees
        ctla_value_ash = ((tree_planting_and_establishment_expense * inflation_factor) / (
            (starting_diameter_new / 2) ** 2)) * depreciation_ash * ash_tree_basal_area
        ctla_value_non_ash = ((tree_planting_and_establishment_expense * inflation_factor) / (
            (starting_diameter_new / 2) ** 2)) * depreciation_non_ash * non_ash_tree_basal_area
        ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

        # Store results for the year
        results_remove_then_replant.append({
            'Year': year,

            'Ash Tree Count': ash_tree_count,
            'Non-Ash Tree Count': non_ash_tree_count,
            'Total Tree Count': total_tree_count,

            'Ash Tree Basal Area': round(ash_tree_basal_area, 2),
            'Non-Ash Tree Basal Area': round(non_ash_tree_basal_area, 2),
            'Total Tree Basal Area': round(total_tree_basal_area, 2),

            'Cost of Tree Planting and Establishment': round(replanting_cost, 2),
            'Cost of Pruning': round(pruning_cost, 2),  # Pruning costs applied to non-ash trees
            'Cost of Injection': 0,  # No tree injection in this simulation
            'Cost of Removal': round(total_removal_cost, 2),
            'Total Costs': round((replanting_cost + pruning_cost + total_removal_cost), 2),

            'Cumulative Cost of Tree Planting and Establishment': round(cumulative_planting_cost, 2),
            'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
            'Cumulative Cost of Injection': 0,  # No tree injection in this simulation
            'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
            'Cumulative Costs': round((cumulative_planting_cost + cumulative_pruning_cost + cumulative_removal_cost), 2),

            'CTLA Value of Ash': round(ctla_value_ash, 2),
            'CTLA Value of Non-Ash': round(ctla_value_non_ash, 2),
            'CTLA Value of All Trees': round(ctla_value_all_trees, 2),

            'Net Value of All Trees': round((ctla_value_all_trees - (cumulative_planting_cost + cumulative_pruning_cost + cumulative_removal_cost)), 2)
        })

        # Update the inflation factor for the next year
        inflation_factor *= 1 + annual_inflation_rate

    return pd.DataFrame(results_remove_then_replant)

## ------------------------------------------------- PLOTTING FUNCTION -------------------------------------------------
# Formatter function to add commas
def format_with_commas(x, pos):
    return f"{int(x):,}"

def plot_simulations(simulation_results, legend_title):
    # Define scenarios and corresponding colors for plotting
    scenarios = simulation_results.keys()
    colors = ['red', 'blue', 'green', 'orange']

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
            ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), title="Legend", fontsize=12, title_fontsize=14, ncol=1)

    # Adjust layout to avoid overlap and reserve space for the legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Reserve space on the right for the legend
    plt.savefig(f"{legend_title}.jpeg", format='jpeg', dpi=900)

## ------------------------------------------------- LOOP THE FUNCTION -------------------------------------------------
# Loop through each injection year
for removal_rate in set_removal_rate:
    # Set the current injection year
    set_removal_rate = removal_rate

    # Run the simulation
    results = simulate_remove_then_replant(set_removal_rate)

    # Store the results with the injection year as the key
    all_results[f'Rate of Tree Removals per Year: {removal_rate}'] = results

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

# Initialize dictionary to store the best removal rates for each metric
best_removal_rate_per_metric = {}

for metric in metrics:
    # Initialize the best removal rate and its corresponding value
    best_removal_rate = None
    best_value = float('-inf') if metric != 'Cumulative Costs' else float('inf')

    for removal_rate, results in all_results.items():
        # Ensure both 'Year' and the current metric exist in the results DataFrame
        if 'Year' not in results.columns or metric not in results.columns:
            print(f"Metric '{metric}' or 'Year' not found in results for {removal_rate}")
            continue

        # Filter the value for Year 20
        year_20_value = results.loc[results['Year'] == 20, metric]
        if not year_20_value.empty:
            year_20_value = year_20_value.values[0]
        else:
            print(f"No data for Year 20 in {removal_rate}")
            continue

        # Update the best removal rate based on the value at Year 20
        if metric == 'Cumulative Costs':
            # For Cumulative Costs, find the lowest value
            if year_20_value < best_value:
                best_value = year_20_value
                best_removal_rate = removal_rate
        else:
            # For all other metrics, find the highest value
            if year_20_value > best_value:
                best_value = year_20_value
                best_removal_rate = removal_rate

    # Store the best removal rate and its value for the current metric
    best_removal_rate_per_metric[metric] = (best_removal_rate, best_value)

# Print the results
print("Best Removal Rates for Each Metric (Evaluated at Year 20):")
for metric, (removal_rate, value) in best_removal_rate_per_metric.items():
    if metric == 'Cumulative Costs':
        print(f"{metric} {removal_rate}, Value = {value:.2f}")
    else:
        print(f"{metric}: {removal_rate}, Highest Value = {value:.2f}")
