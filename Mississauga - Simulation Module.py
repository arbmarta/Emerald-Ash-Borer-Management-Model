import pandas as pd
from math import pi

def run_simulations(
    starting_ash_trees, starting_diameter, starting_diameter_new, growth_rate,
    growth_rate_new, ash_mortality_rate, injected_ash_mortality_rate, tree_planting_and_establishment_expense,
    ash_tree_injections_expense, set_removal_rate, set_removal_year, set_injection_years, set_planting_rate, set_planting_year,
    depreciation_ash, depreciation_non_ash, mortality_rates_by_age, background_mortality_rate, annual_inflation_rate,
    years, get_pruning_cost_by_dbh, get_removal_cost_by_dbh
):
    # Initialize results containers
    all_results = {}

    def simulate_control_and_remove():
        results_control_and_remove = []

        # Initialize variables for the simulation
        ash_tree_count = starting_ash_trees
        average_diameter_ash = starting_diameter

        # Cumulative cost trackers
        cumulative_planting_cost = 0
        cumulative_pruning_cost = 0
        cumulative_removal_cost = 0

        # Initialize inflation factor
        inflation_factor = 1

        # Simulation loop for each year
        for year in range(1, years + 1):
            # Update diameter based on growth rate
            average_diameter_ash += growth_rate

            # Apply mortality and update tree counts
            dead_ash_tree_count = int(ash_tree_count * ash_mortality_rate)
            ash_tree_count -= dead_ash_tree_count
            total_tree_count = ash_tree_count

            # Calculate basal areas
            ash_tree_basal_area = ((average_diameter_ash / 2) ** 2) * pi * ash_tree_count
            total_tree_basal_area = ash_tree_basal_area

            # Calculate individual expenses using lookup functions
            pruning_cost = get_pruning_cost_by_dbh(average_diameter_ash) * (ash_tree_count / 7) * inflation_factor
            removal_cost = get_removal_cost_by_dbh(average_diameter_ash) * dead_ash_tree_count * inflation_factor

            # Update cumulative costs
            cumulative_pruning_cost += pruning_cost
            cumulative_removal_cost += removal_cost

            # Calculate CTLA values (placeholder logic as needed)
            ctla_value_ash = (ash_tree_basal_area * ((tree_planting_and_establishment_expense * inflation_factor) / ((starting_diameter_new / 2) ** 2))) * depreciation_ash

            # Store results for the year in the list directly
            results_control_and_remove.append({
                'Year': year,
                'Ash Tree Count': ash_tree_count,
                'Non-Ash Tree Count': 0,
                'Total Tree Count': total_tree_count,
                'Ash Tree Basal Area': round(ash_tree_basal_area, 2),
                'Non-Ash Tree Basal Area': 0,
                'Total Tree Basal Area': round(total_tree_basal_area, 2),
                'Cost of Tree Planting and Establishment': 0,  # No tree planting in control simulation
                'Cost of Pruning': round(pruning_cost, 2),
                'Cost of Injection': 0,  # No tree injection in control simulation
                'Cost of Removal': round(removal_cost, 2),
                'Total Costs': round((pruning_cost + removal_cost), 2),
                'Cumulative Cost of Tree Planting and Establishment': 0,  # No tree planting in control simulation
                'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
                'Cumulative Cost of Injection': 0,  # No tree injection in control simulation
                'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
                'Cumulative Costs': round((cumulative_pruning_cost + cumulative_removal_cost), 2),
                'CTLA Value of Ash': round(ctla_value_ash, 2),
                'CTLA Value of Non-Ash': 0,
                'CTLA Value of All Trees': round(ctla_value_ash, 2),
                'Net Value of All Trees': round((ctla_value_ash - (cumulative_pruning_cost + cumulative_removal_cost)), 2)
            })

            # Update the inflation factor for the next year
            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results_control_and_remove)

    def simulate_control_and_remove_and_replant():
        # List to store results
        results_control_and_remove_and_replant = []
        cohorts = []  # Track non-ash tree cohorts with ages and diameters

        # Initialize variables for the simulation
        ash_tree_count = starting_ash_trees
        average_diameter_ash = starting_diameter

        # Initialize inflation factor and cumulative cost trackers
        inflation_factor = 1
        cumulative_planting_cost = 0
        cumulative_pruning_cost = 0
        cumulative_removal_cost = 0

        # Simulation loop for each year
        for year in range(1, years + 1):
            # Update diameter based on growth rate for ash trees
            average_diameter_ash += growth_rate

            # Apply mortality and update ash tree counts
            dead_ash_tree_count = int(ash_tree_count * ash_mortality_rate)
            ash_tree_count -= dead_ash_tree_count
            removal_cost_ash = get_removal_cost_by_dbh(average_diameter_ash) * dead_ash_tree_count * inflation_factor

            # Reset non-ash tree count, total diameter, and removal cost for non-ash trees each year
            non_ash_tree_count = 0
            total_diameter_non_ash = 0  # Reset total diameter for averaging
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

                # Apply conditional cost logic
                if cohort['age'] >= 3:
                    # Removal and replanting costs for trees older than 3 years
                    removal_cost_non_ash = get_removal_cost_by_dbh(cohort['diameter']) * dead_trees * inflation_factor
                    cumulative_removal_cost += removal_cost_non_ash
                    replanting_cost_non_ash = dead_trees * tree_planting_and_establishment_expense * inflation_factor
                    cumulative_planting_cost += replanting_cost_non_ash
                else:
                    # Free replanting for younger trees
                    replanting_cost_non_ash = 0
                    cumulative_planting_cost += replanting_cost_non_ash

                # Update non-ash tree count and diameter
                non_ash_tree_count += cohort['count']
                total_diameter_non_ash += cohort['diameter'] * cohort['count']

                # Retain surviving cohorts
                if cohort['count'] > 0:
                    surviving_cohorts.append(cohort)

            # Replace cohorts with the updated list
            cohorts = surviving_cohorts

            # Add a new cohort for the replanted trees (from dead ash trees)
            cohorts.append({'age': 0, 'count': dead_ash_tree_count, 'diameter': starting_diameter_new})

            # Calculate the average diameter for all non-ash trees
            if non_ash_tree_count > 0:
                average_diameter_non_ash = total_diameter_non_ash / non_ash_tree_count
            else:
                average_diameter_non_ash = starting_diameter_new

            # Calculate total tree count
            total_tree_count = ash_tree_count + non_ash_tree_count

            # Calculate costs with inflation applied
            replanting_cost = dead_ash_tree_count * tree_planting_and_establishment_expense * inflation_factor
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
            results_control_and_remove_and_replant.append({
                'Year': year,

                'Ash Tree Count': ash_tree_count,
                'Non-Ash Tree Count': non_ash_tree_count,
                'Total Tree Count': total_tree_count,

                'Ash Tree Basal Area': round(ash_tree_basal_area, 2),
                'Non-Ash Tree Basal Area': round(non_ash_tree_basal_area, 2),
                'Total Tree Basal Area': round(total_tree_basal_area, 2),

                'Cost of Tree Planting and Establishment': round(replanting_cost, 2),
                'Cost of Pruning': round(pruning_cost, 2),
                'Cost of Injection': 0,  # No tree injection in control simulation
                'Cost of Removal': round(total_removal_cost, 2),
                'Total Costs': round((replanting_cost + pruning_cost + total_removal_cost), 2),

                'Cumulative Cost of Tree Planting and Establishment': round(cumulative_planting_cost, 2),
                'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
                'Cumulative Cost of Injection': 0,  # No tree injection in control simulation
                'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
                'Cumulative Costs': round((cumulative_planting_cost + cumulative_pruning_cost + cumulative_removal_cost), 2),

                'CTLA Value of Ash': round(ctla_value_ash, 2),
                'CTLA Value of Non-Ash': round(ctla_value_non_ash, 2),
                'CTLA Value of All Trees': round(ctla_value_all_trees, 2),

                'Net Value of All Trees': round((ctla_value_all_trees - (cumulative_planting_cost + cumulative_pruning_cost + cumulative_removal_cost)), 2)
            })

            # Update the inflation factor for the next year
            inflation_factor *= 1 + annual_inflation_rate

        # After the loop, convert to DataFrame
        return pd.DataFrame(results_control_and_remove_and_replant)

    def simulate_remove_then_replant():
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

    def simulate_replant_inject_then_remove():
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

            if year <= set_removal_year:
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
                trees_to_remove = min(set_removal_rate, ash_tree_count)
                ash_tree_count -= trees_to_remove

                # Calculate removal cost for manually removed ash trees with cost lookup and inflation
                removal_cost = trees_to_remove * get_removal_cost_by_dbh(average_diameter_ash) * inflation_factor
                cumulative_removal_cost += removal_cost

                # No injection cost beyond the set removal year
                injection_cost = 0

            if year >= set_planting_year:
                remaining_trees_to_replace = max(0, starting_ash_trees - non_ash_tree_count)
                planting_rate = min(set_planting_rate, remaining_trees_to_replace)
                non_ash_tree_count += planting_rate
                cohorts.append({'age': 0, 'count': planting_rate, 'diameter': starting_diameter_new})

            # Calculate replanting cost with inflation (only for newly planted trees during replanting years)
            if year >= set_removal_year:
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
            pruning_cost_non_ash = (non_ash_tree_count / 7) * get_pruning_cost_by_dbh(average_diameter_non_ash) * inflation_factor
            total_pruning_cost = pruning_cost_ash + pruning_cost_non_ash
            cumulative_pruning_cost += total_pruning_cost

            # Basal areas
            ash_tree_basal_area = ((average_diameter_ash / 2) ** 2) * pi * ash_tree_count
            non_ash_tree_basal_area = ((average_diameter_non_ash / 2) ** 2) * pi * non_ash_tree_count
            total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

            # CTLA values
            ctla_value_ash = (tree_planting_and_establishment_cost / ((starting_diameter_new / 2) ** 2)) * depreciation_ash * ash_tree_basal_area
            ctla_value_non_ash = (tree_planting_and_establishment_cost / ((starting_diameter_new / 2) ** 2)) * depreciation_non_ash * non_ash_tree_basal_area
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
                'Total Costs': round(replanting_cost + total_pruning_cost + injection_cost + removal_cost + removal_cost_non_ash, 2),

                'Cumulative Cost of Tree Planting and Establishment': round(cumulative_planting_cost, 2),
                'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
                'Cumulative Cost of Injection': round(cumulative_injection_cost, 2),
                'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
                'Cumulative Costs': round(cumulative_planting_cost + cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost, 2),

                'CTLA Value of Ash': round(ctla_value_ash, 2),
                'CTLA Value of Non-Ash': round(ctla_value_non_ash, 2),
                'CTLA Value of All Trees': round(ctla_value_all_trees, 2),

                'Net Value of All Trees': round(ctla_value_all_trees - cumulative_planting_cost - cumulative_pruning_cost - cumulative_injection_cost - cumulative_removal_cost, 2)
            })

            # Update the inflation factor for the next year
            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results_replant_inject_then_remove)

    def simulate_inject_remove_and_replant():
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
            if year <= set_injection_years:
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
                trees_to_remove = min(set_removal_rate, ash_tree_count)
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

    def simulate_inject_in_perpetuity():
        # List to store results
        results_inject_in_perpetuity = []

        # Initialize variables for the simulation
        ash_tree_count = starting_ash_trees
        average_diameter_ash = starting_diameter

        # Cumulative cost trackers
        cumulative_removal_cost = 0
        cumulative_injection_cost = 0
        cumulative_pruning_cost = 0

        # Initialize inflation factor
        inflation_factor = 1

        # Simulation loop for each year
        for year in range(1, years + 1):
            # Update ash diameter based on growth rate
            average_diameter_ash += growth_rate

            # Annual injection cost for all ash trees with inflation
            annual_injection_cost = (ash_tree_count / 2) * average_diameter_ash * ash_tree_injections_expense * inflation_factor
            cumulative_injection_cost += annual_injection_cost

            # Apply mortality rate for injected ash trees
            trees_died = int(ash_tree_count * injected_ash_mortality_rate)
            ash_tree_count -= trees_died

            # Calculate removal cost for dead ash trees using cost lookup with inflation
            annual_removal_cost = trees_died * get_removal_cost_by_dbh(average_diameter_ash) * inflation_factor
            cumulative_removal_cost += annual_removal_cost

            # Calculate pruning costs for ash trees using cost lookup with inflation
            pruning_cost_ash = (ash_tree_count / 7) * get_pruning_cost_by_dbh(average_diameter_ash) * inflation_factor
            cumulative_pruning_cost += pruning_cost_ash

            # Basal area calculation for ash trees only
            ash_tree_basal_area = ((average_diameter_ash / 2) ** 2) * pi * ash_tree_count
            total_tree_basal_area = ash_tree_basal_area
            total_tree_count = ash_tree_count

            # CTLA value calculation for ash trees
            ctla_value_ash = ((tree_planting_and_establishment_expense * inflation_factor) / ((starting_diameter_new / 2) ** 2)) * depreciation_ash * ash_tree_basal_area

            # Store results for the year
            results_inject_in_perpetuity.append({
                'Year': year,

                'Ash Tree Count': ash_tree_count,
                'Non-Ash Tree Count': 0,
                'Total Tree Count': total_tree_count,

                'Ash Tree Basal Area': round(ash_tree_basal_area, 2),
                'Non-Ash Tree Basal Area': 0,
                'Total Tree Basal Area': round(total_tree_basal_area, 2),

                'Cost of Tree Planting and Establishment': 0,
                'Cost of Pruning': round(pruning_cost_ash, 2),
                'Cost of Injection': round(annual_injection_cost, 2),
                'Cost of Removal': round(annual_removal_cost, 2),
                'Total Costs': round((pruning_cost_ash + annual_injection_cost + annual_removal_cost), 2),

                'Cumulative Cost of Tree Planting and Establishment': 0,
                'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
                'Cumulative Cost of Injection': round(cumulative_injection_cost, 2),
                'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
                'Cumulative Costs': round((cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost), 2),

                'CTLA Value of Ash': round(ctla_value_ash, 2),
                'CTLA Value of Non-Ash': 0,
                'CTLA Value of All Trees': round(ctla_value_ash, 2),

                'Net Value of All Trees': round(
                    (ctla_value_ash - (cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost)), 2)
            })

            # Update the inflation factor for the next year
            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results_inject_in_perpetuity)

    def simulate_inject_in_perpetuity_and_replant():
        # List to store results
        results_inject_in_perpetuity_and_replant = []

        # Initialize variables for the simulation
        ash_tree_count = starting_ash_trees
        average_diameter_ash = starting_diameter
        cohorts = []  # Track non-ash tree cohorts with their age and diameter

        # Cumulative cost trackers
        cumulative_removal_cost = 0
        cumulative_planting_cost = 0
        cumulative_injection_cost = 0
        cumulative_pruning_cost = 0

        # Initialize inflation factor
        inflation_factor = 1

        # Simulation loop for each year
        for year in range(1, years + 1):
            # Update ash tree diameter based on growth rate
            average_diameter_ash += growth_rate

            # Annual injection cost for all ash trees with inflation
            annual_injection_cost = (ash_tree_count / 2) * average_diameter_ash * ash_tree_injections_expense * inflation_factor
            cumulative_injection_cost += annual_injection_cost

            # Apply mortality rate for injected ash trees
            trees_died = int(ash_tree_count * injected_ash_mortality_rate)
            ash_tree_count -= trees_died

            # Calculate removal cost for dead ash trees with inflation
            annual_removal_cost = trees_died * get_removal_cost_by_dbh(average_diameter_ash) * inflation_factor
            cumulative_removal_cost += annual_removal_cost

            # Replant dead ash trees as new non-ash trees in a cohort with initial diameter
            cohorts.append({'age': 0, 'count': trees_died, 'diameter': starting_diameter_new})

            # Calculate replanting cost for new non-ash trees with inflation
            annual_replanting_cost = trees_died * tree_planting_and_establishment_expense * inflation_factor
            cumulative_planting_cost += annual_replanting_cost

            # Track non-ash tree count and reset for calculation each year
            non_ash_tree_count = 0
            total_diameter_non_ash = 0  # To calculate the average diameter of non-ash trees

            # Update each cohort's age and diameter, apply mortality, and calculate removal costs
            surviving_cohorts = []
            for cohort in cohorts:
                cohort['age'] += 1
                cohort['diameter'] += growth_rate_new

                # Apply mortality to the cohort based on age
                mortality_rate = mortality_rates_by_age.get(cohort['age'], background_mortality_rate)
                dead_trees = int(cohort['count'] * mortality_rate)
                cohort['count'] -= dead_trees

                # Check age to determine costs
                if cohort['age'] >= 3:
                    # Removal and replanting costs for trees older than 3 years
                    removal_cost_non_ash = dead_trees * get_removal_cost_by_dbh(cohort['diameter']) * inflation_factor
                    cumulative_removal_cost += removal_cost_non_ash
                    replanting_cost_non_ash = dead_trees * tree_planting_and_establishment_expense * inflation_factor
                    cumulative_planting_cost += replanting_cost_non_ash
                else:
                    # Free replanting for younger trees
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

            # Calculate pruning costs with inflation for both ash and non-ash trees
            pruning_cost_ash = (ash_tree_count / 7) * get_pruning_cost_by_dbh(average_diameter_ash) * inflation_factor
            pruning_cost_non_ash = (non_ash_tree_count / 7) * get_pruning_cost_by_dbh(average_diameter_non_ash) * inflation_factor
            total_pruning_cost = pruning_cost_ash + pruning_cost_non_ash
            cumulative_pruning_cost += total_pruning_cost

            # Calculate basal areas
            ash_tree_basal_area = ((average_diameter_ash / 2) ** 2) * pi * ash_tree_count
            non_ash_tree_basal_area = ((average_diameter_non_ash / 2) ** 2) * pi * non_ash_tree_count
            total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area
            total_tree_count = ash_tree_count + non_ash_tree_count

            # Calculate CTLA values for ash and non-ash trees
            ctla_value_ash = ((tree_planting_and_establishment_expense * inflation_factor) / ((starting_diameter_new / 2) ** 2)) * depreciation_ash * ash_tree_basal_area
            ctla_value_non_ash = ((tree_planting_and_establishment_expense * inflation_factor) / ((starting_diameter_new / 2) ** 2)) * depreciation_non_ash * non_ash_tree_basal_area
            ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

            # Store results for the year
            results_inject_in_perpetuity_and_replant.append({
                'Year': year,
                'Ash Tree Count': ash_tree_count,
                'Non-Ash Tree Count': non_ash_tree_count,
                'Total Tree Count': total_tree_count,
                'Ash Tree Basal Area': round(ash_tree_basal_area, 2),
                'Non-Ash Tree Basal Area': round(non_ash_tree_basal_area, 2),
                'Total Tree Basal Area': round(total_tree_basal_area, 2),
                'Cost of Tree Planting and Establishment': round(annual_replanting_cost, 2),
                'Cost of Pruning': round(total_pruning_cost, 2),
                'Cost of Injection': round(annual_injection_cost, 2),
                'Cost of Removal': round(annual_removal_cost, 2),
                'Total Costs': round((annual_replanting_cost + total_pruning_cost + annual_injection_cost + annual_removal_cost), 2),
                'Cumulative Cost of Tree Planting and Establishment': round(cumulative_planting_cost, 2),
                'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
                'Cumulative Cost of Injection': round(cumulative_injection_cost, 2),
                'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
                'Cumulative Costs': round((cumulative_planting_cost + cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost), 2),
                'CTLA Value of Ash': round(ctla_value_ash, 2),
                'CTLA Value of Non-Ash': round(ctla_value_non_ash, 2),
                'CTLA Value of All Trees': round(ctla_value_all_trees, 2),
                'Net Value of All Trees': round((ctla_value_all_trees - (cumulative_planting_cost + cumulative_pruning_cost + cumulative_injection_cost + cumulative_removal_cost)), 2)
            })

            # Update the inflation factor for the next year
            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results_inject_in_perpetuity_and_replant)

    # Run simulations and store results
    all_results['Control and Remove'] = simulate_control_and_remove()
    all_results['Control, Remove, then Replant'] = simulate_control_and_remove_and_replant()
    all_results['Remove then Replant'] = simulate_remove_then_replant()
    all_results['Replant, Inject, then Remove'] = simulate_replant_inject_then_remove()
    all_results['Inject, Remove, and Replant'] = simulate_inject_remove_and_replant()
    all_results['Inject in Perpetuity'] = simulate_inject_in_perpetuity()
    all_results['Inject in Perpetuity with Replanting'] = simulate_inject_in_perpetuity_and_replant()

    # Add other simulations similarly...
    return all_results


# Function to extract and report year 20 values
def report_year_20_values(simulation_results):
    # Iterate through each simulation scenario
    for scenario, df in simulation_results.items():
        # Filter data for year 20
        year_20_data = df[df['Year'] == 20]
        if not year_20_data.empty:
            # Extract relevant values and convert to thousands of dollars, rounded to 1 decimal place
            cumulative_costs = round(year_20_data['Cumulative Costs'].values[0] / 1000, 1)
            ctla_value_all_trees = round(year_20_data['CTLA Value of All Trees'].values[0] / 1000, 1)
            net_value_all_trees = round(year_20_data['Net Value of All Trees'].values[0] / 1000, 1)

            # Print the results
            print(f"Scenario: {scenario}")
            print(f"  Cumulative Costs: ${cumulative_costs}k")
            print(f"  CTLA Value of All Trees: ${ctla_value_all_trees}k")
            print(f"  Net Value of All Trees: ${net_value_all_trees}k")
            print()

# Function to extract and report year 20 counts
def report_year_20_counts(simulation_results):
    # Iterate through each simulation scenario
    for scenario, df in simulation_results.items():
        # Filter data for year 20
        year_20_data = df[df['Year'] == 20]
        if not year_20_data.empty:
            # Extract relevant values and convert to thousands of dollars, rounded to 1 decimal place
            ash_tree_basal_count = year_20_data['Ash Tree Count'].values[0]
            non_ash_tree_count = year_20_data['Non-Ash Tree Count'].values[0]
            total_tree_basal_count = year_20_data['Total Tree Count'].values[0]

            ash_tree_basal_area = year_20_data['Ash Tree Basal Area'].values[0]
            non_ash_tree_basal_area = year_20_data['Non-Ash Tree Basal Area'].values[0]
            total_tree_basal_area = year_20_data['Total Tree Basal Area'].values[0]

            # Print the results
            print(f"Scenario: {scenario}")
            print(f"  Ash Tree Count: {ash_tree_basal_count}")
            print(f"  Non-Ash Tree Count: {non_ash_tree_count}")
            print(f"  Total Tree Count: {total_tree_basal_count}")
            print(f"  Ash Tree Basal Area: {ash_tree_basal_area}")
            print(f"  Non-Ash Tree Basal Area: {non_ash_tree_basal_area}")
            print(f"  Total Tree Basal Area: {total_tree_basal_area}")
            print()
