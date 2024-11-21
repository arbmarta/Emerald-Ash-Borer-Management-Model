from math import pi
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from Consistent_Parameters import *

## ------------------------------------------------ SIMULATION SETTINGS ------------------------------------------------
set_removal_year = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
set_removal_rate = [100, 250, 500, 1000] # Sets a number of ash trees to remove each year
set_planting_rate = [10, 332, 333, 334, 400, 1000] # Sets a number of non-ash trees to plant each year
set_planting_year = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

# Store all results in a dictionary with injection years as keys
all_results = {}
legend_title = "Replant, Inject, then Preemptive Removal"

## ------------------------------------------------ SIMULATION SETTINGS ------------------------------------------------
def simulate_replant_inject_then_remove(removal_year, removal_rate, planting_rate, planting_year):
    # List to store results
    results_replant_inject_then_remove = []
    cohorts = []  # Track non-ash tree cohorts with ages

    # Initialize variables for the simulation
    ash_tree_count = starting_ash_trees
    average_diameter_ash = starting_diameter
    non_ash_tree_count = 0
    average_diameter_non_ash = starting_diameter_new  # Initial DBH of new trees

    # Cumulative cost trackers
    cumulative_planting_cost = 0
    cumulative_pruning_cost = 0
    cumulative_injection_cost = 0
    cumulative_removal_cost = 0

    # Initialize inflation factor and set the annual inflation rate
    inflation_factor = 1

    # Simulation loop for each year
    for year in range(1, years + 1):
        # Update ash and non-ash diameters based on growth rates
        average_diameter_ash += growth_rate

        # Update management expenses with inflation factor
        tree_planting_and_establishment_cost = tree_planting_and_establishment_expense * inflation_factor
        ash_tree_injections_cost = ash_tree_injections_expense * inflation_factor

        if year <= removal_year:
            # Apply mortality rate to ash trees
            trees_died = int(ash_tree_count * injected_ash_mortality_rate)
            ash_tree_count -= trees_died

            # Calculate injection cost for all living ash trees with inflation
            injection_cost = (ash_tree_count / 2) * average_diameter_ash * ash_tree_injections_cost
            cumulative_injection_cost += injection_cost

            # Calculate removal cost for naturally dead ash trees with cost lookup and inflation
            removal_cost = trees_died * get_removal_cost_by_dbh(average_diameter_ash) * inflation_factor
            cumulative_removal_cost += removal_cost
        else:
            # From set removal year onwards, start removing ash trees at the specified rate
            trees_to_remove = min(removal_rate, ash_tree_count)
            ash_tree_count -= trees_to_remove

            # Calculate removal cost for manually removed ash trees with cost lookup and inflation
            removal_cost = trees_to_remove * get_removal_cost_by_dbh(average_diameter_ash) * inflation_factor
            cumulative_removal_cost += removal_cost

            # No injection cost beyond the set removal year
            injection_cost = 0

        if year >= planting_year:
            remaining_trees_to_replace = max(0, starting_ash_trees - non_ash_tree_count)
            planting_rate = min(planting_rate, remaining_trees_to_replace)
            non_ash_tree_count += planting_rate
            cohorts.append({'age': 0, 'count': planting_rate, 'diameter': starting_diameter_new})

        # Calculate replanting cost with inflation (only for newly planted trees during replanting years)
        if year >= removal_year:
            replanting_cost = planting_rate * tree_planting_and_establishment_cost
            cumulative_planting_cost += replanting_cost
        else:
            replanting_cost = 0

        # Reset non-ash tree count and total diameter each year
        non_ash_tree_count = 0
        total_diameter_non_ash = 0
        removal_cost_non_ash = 0

        # Age-based mortality and diameter growth for each non-ash cohort
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
                # Apply both removal and replanting costs for trees older than 3 years
                removal_cost_non_ash = dead_trees * get_removal_cost_by_dbh(cohort['diameter']) * inflation_factor
                cumulative_removal_cost += removal_cost_non_ash
                replanting_cost_non_ash = dead_trees * tree_planting_and_establishment_expense * inflation_factor
                cumulative_planting_cost += replanting_cost_non_ash
            else:
                # Free replanting cost without removal for trees younger than 3 years
                replanting_cost_non_ash = dead_trees * tree_planting_and_establishment_expense * inflation_factor
                cumulative_planting_cost += replanting_cost_non_ash

            # Update non-ash tree count and total diameter
            non_ash_tree_count += cohort['count']
            total_diameter_non_ash += cohort['diameter'] * cohort['count']

            # Keep cohorts with surviving trees
            if cohort['count'] > 0:
                surviving_cohorts.append(cohort)

        # Update cohorts with surviving trees
        cohorts = surviving_cohorts

        # Average diameter for non-ash trees
        if non_ash_tree_count > 0:
            average_diameter_non_ash = total_diameter_non_ash / non_ash_tree_count
        else:
            average_diameter_non_ash = starting_diameter_new

        # Total tree count
        total_tree_count = ash_tree_count + non_ash_tree_count

        # Pruning costs with cost lookup and inflation for ash and non-ash trees
        pruning_cost_ash = (ash_tree_count / 7) * get_pruning_cost_by_dbh(average_diameter_ash) * inflation_factor
        pruning_cost_non_ash = (non_ash_tree_count / 7) * get_pruning_cost_by_dbh(
            average_diameter_non_ash) * inflation_factor
        total_pruning_cost = pruning_cost_ash + pruning_cost_non_ash
        cumulative_pruning_cost += total_pruning_cost

        # Basal areas
        ash_tree_basal_area = ((average_diameter_ash / 2) ** 2) * pi * ash_tree_count
        non_ash_tree_basal_area = ((average_diameter_non_ash / 2) ** 2) * pi * non_ash_tree_count
        total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

        # CTLA values
        ctla_value_ash = (tree_planting_and_establishment_cost / (
                    (starting_diameter_new / 2) ** 2)) * depreciation_ash * ash_tree_basal_area
        ctla_value_non_ash = (tree_planting_and_establishment_cost / (
                    (starting_diameter_new / 2) ** 2)) * depreciation_non_ash * non_ash_tree_basal_area
        ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

        # Store results
        results_replant_inject_then_remove.append({
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
            'Total Costs': round(
                replanting_cost + total_pruning_cost + injection_cost + removal_cost + removal_cost_non_ash, 2),

            'Cumulative Cost of Tree Planting and Establishment': round(cumulative_planting_cost, 2),
            'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
            'Cumulative Cost of Injection': round(cumulative_injection_cost, 2),
            'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
            'Cumulative Costs': round(
                cumulative_planting_cost + cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost,
                2),

            'CTLA Value of Ash': round(ctla_value_ash, 2),
            'CTLA Value of Non-Ash': round(ctla_value_non_ash, 2),
            'CTLA Value of All Trees': round(ctla_value_all_trees, 2),

            'Net Value of All Trees': round(
                ctla_value_all_trees - cumulative_planting_cost - cumulative_pruning_cost - cumulative_injection_cost - cumulative_removal_cost,
                2)
        })

        # Update the inflation factor for the next year
        inflation_factor *= 1 + annual_inflation_rate

    return pd.DataFrame(results_replant_inject_then_remove)

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
# Loop through all combinations of removal year, removal rate, planting rate, and planting year
for removal_year in set_removal_year:
    for removal_rate in set_removal_rate:
        for planting_rate in set_planting_rate:
            for planting_year in set_planting_year:
                # Ensure removal year is greater than planting year
                if removal_year > planting_year:
                    print(f"Simulating: Removal Year = {removal_year}, Removal Rate = {removal_rate}, "
                          f"Planting Rate = {planting_rate}, Planting Year = {planting_year}")

                    # Run the simulation with the current combination of parameters
                    results = simulate_replant_inject_then_remove(
                        removal_year, removal_rate, planting_rate, planting_year
                    )

                    # Store the results with a unique key
                    key = (f'Removal Year: {removal_year}, Removal Rate: {removal_rate}, '
                           f'Planting Rate: {planting_rate}, Planting Year: {planting_year}')
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
