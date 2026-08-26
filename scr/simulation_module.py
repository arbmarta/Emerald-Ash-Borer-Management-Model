import pandas as pd
from math import pi


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def calculate_basal_area(diameter, count):
    """Basal area for a tree population: (radius^2 * pi) * count."""
    return ((diameter / 2) ** 2) * pi * count


def calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                          inflation_factor, depreciation, basal_area):
    """CTLA Trunk Formula Technique value for a population with the given basal area."""
    return ((tree_planting_and_establishment_expense * inflation_factor) /
             ((starting_diameter_new / 2) ** 2)) * depreciation * basal_area


def age_and_thin_cohorts(cohorts, growth_rate_new, mortality_rates_by_age, background_mortality_rate,
                          tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
                          starting_diameter_new, warranty_period_ends):
    """
    Age every non-ash cohort by one year, apply age-based mortality, and calculate the
    removal/replanting costs triggered by that mortality.

    Cohorts that die before reaching warranty_period_ends are replanted at no cost
    under warranty (matches every scenario -- replanting is always free within warranty).

    Returns a dict with: surviving_cohorts, non_ash_tree_count, average_diameter_non_ash,
    removal_cost_non_ash, planting_cost_non_ash.
    """
    non_ash_tree_count = 0
    total_diameter_non_ash = 0
    removal_cost_non_ash = 0
    planting_cost_non_ash = 0
    surviving_cohorts = []

    for cohort in cohorts:
        cohort['age'] += 1
        cohort['diameter'] += growth_rate_new

        mortality_rate = mortality_rates_by_age.get(cohort['age'], background_mortality_rate)
        # round() rather than int()/truncation: truncating always rounds down, which
        # would make any cohort smaller than ~1/mortality_rate trees immortal (e.g. a
        # 5-tree cohort at a 0.0085 rate would never lose a tree). round() still can't
        # register less than half a tree dying in a single year, but it isn't biased
        # downward the way truncation is.
        dead_trees = round(cohort['count'] * mortality_rate)
        cohort['count'] -= dead_trees

        if cohort['age'] >= warranty_period_ends:
            removal_cost_non_ash += dead_trees * get_removal_cost_by_dbh(cohort['diameter']) * inflation_factor
            planting_cost_non_ash += dead_trees * tree_planting_and_establishment_expense * inflation_factor
        # else: still within warranty -- replanting is free, no cost added.

        non_ash_tree_count += cohort['count']
        total_diameter_non_ash += cohort['diameter'] * cohort['count']

        if cohort['count'] > 0:
            surviving_cohorts.append(cohort)

    if non_ash_tree_count > 0:
        average_diameter_non_ash = total_diameter_non_ash / non_ash_tree_count
    else:
        average_diameter_non_ash = starting_diameter_new

    return {
        'surviving_cohorts': surviving_cohorts,
        'non_ash_tree_count': non_ash_tree_count,
        'average_diameter_non_ash': average_diameter_non_ash,
        'removal_cost_non_ash': removal_cost_non_ash,
        'planting_cost_non_ash': planting_cost_non_ash,
    }


def build_year_result(year, ash_tree_count, non_ash_tree_count, total_tree_count,
                       ash_basal_area, non_ash_basal_area, total_basal_area,
                       planting_cost, pruning_cost, injection_cost, removal_cost, total_cost,
                       cumulative_planting_cost, cumulative_pruning_cost, cumulative_injection_cost,
                       cumulative_removal_cost, cumulative_costs,
                       ctla_ash, ctla_non_ash, ctla_all, net_value):
    """Build the standard per-year results row used by every scenario."""
    return {
        'Year': year,

        'Ash Tree Count': ash_tree_count,
        'Non-Ash Tree Count': non_ash_tree_count,
        'Total Tree Count': total_tree_count,

        'Ash Tree Basal Area': round(ash_basal_area, 2),
        'Non-Ash Tree Basal Area': round(non_ash_basal_area, 2),
        'Total Tree Basal Area': round(total_basal_area, 2),

        'Cost of Tree Planting and Establishment': round(planting_cost, 2),
        'Cost of Pruning': round(pruning_cost, 2),
        'Cost of Injection': round(injection_cost, 2),
        'Cost of Removal': round(removal_cost, 2),
        'Total Costs': round(total_cost, 2),

        'Cumulative Cost of Tree Planting and Establishment': round(cumulative_planting_cost, 2),
        'Cumulative Cost of Pruning': round(cumulative_pruning_cost, 2),
        'Cumulative Cost of Injection': round(cumulative_injection_cost, 2),
        'Cumulative Cost of Removal': round(cumulative_removal_cost, 2),
        'Cumulative Costs': round(cumulative_costs, 2),

        'CTLA Value of Ash': round(ctla_ash, 2),
        'CTLA Value of Non-Ash': round(ctla_non_ash, 2),
        'CTLA Value of All Trees': round(ctla_all, 2),

        'Net Value of All Trees': round(net_value, 2),
    }


# ---------------------------------------------------------------------------
# TreePopulation: bundles the state that evolves year-by-year (ash count/
# diameter, non-ash cohorts, cumulative costs) so scenario functions don't
# have to thread 6-7 loose variables through the loop themselves. The actual
# math is unchanged -- this wraps the same helpers used above.
# ---------------------------------------------------------------------------

class TreePopulation:
    def __init__(self, ash_count, ash_diameter, starting_diameter_new):
        self.ash_count = ash_count
        self.ash_diameter = ash_diameter
        self.starting_diameter_new = starting_diameter_new

        self.cohorts = []
        self.non_ash_count = 0
        self.average_diameter_non_ash = starting_diameter_new

        self.cumulative_planting_cost = 0
        self.cumulative_pruning_cost = 0
        self.cumulative_injection_cost = 0
        self.cumulative_removal_cost = 0

    def grow(self, growth_rate):
        """Advance ash diameter by one year's growth."""
        self.ash_diameter += growth_rate

    def apply_ash_mortality(self, rate):
        """Kill off a fraction of the ash population. Returns the count that died."""
        # round(), not int()/truncation -- see the matching note in age_and_thin_cohorts.
        dead = round(self.ash_count * rate)
        self.ash_count -= dead
        return dead

    def remove_ash(self, n):
        """Remove up to n ash trees (or however many remain). Returns the count removed."""
        removed = min(n, self.ash_count)
        self.ash_count -= removed
        return removed

    def add_cohort(self, count, diameter=None):
        """Plant a new non-ash cohort at age 0."""
        self.cohorts.append({
            'age': 0,
            'count': count,
            'diameter': self.starting_diameter_new if diameter is None else diameter,
        })

    def age_cohorts(self, growth_rate_new, mortality_rates_by_age, background_mortality_rate,
                     tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
                     warranty_period_ends):
        """
        Age every non-ash cohort by one year and apply mortality; updates
        non_ash_count and average_diameter_non_ash in place. Returns the same
        dict as the age_and_thin_cohorts() helper (removal_cost_non_ash,
        planting_cost_non_ash) so the calling scenario can fold the costs in.
        """
        aged = age_and_thin_cohorts(
            self.cohorts, growth_rate_new, mortality_rates_by_age, background_mortality_rate,
            tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
            self.starting_diameter_new, warranty_period_ends
        )
        self.cohorts = aged['surviving_cohorts']
        self.non_ash_count = aged['non_ash_tree_count']
        self.average_diameter_non_ash = aged['average_diameter_non_ash']
        return aged

    @property
    def total_count(self):
        return self.ash_count + self.non_ash_count

    def ash_basal_area(self):
        return calculate_basal_area(self.ash_diameter, self.ash_count)

    def non_ash_basal_area(self):
        return calculate_basal_area(self.average_diameter_non_ash, self.non_ash_count)


def run_simulations(
    starting_ash_trees, starting_diameter, starting_diameter_new, growth_rate,
    growth_rate_new, ash_mortality_rate, injected_ash_mortality_rate, tree_planting_and_establishment_expense,
    ash_tree_injections_expense, set_removal_rate, set_removal_year, set_injection_years, set_planting_rate, set_planting_year,
    depreciation_ash, depreciation_non_ash, mortality_rates_by_age, background_mortality_rate, annual_inflation_rate,
    years, get_pruning_cost_by_dbh, get_removal_cost_by_dbh, warranty_period_ends, pruning_cycle_years
):
    all_results = {}

    def simulate_control():
        results = []
        pop = TreePopulation(starting_ash_trees, starting_diameter, starting_diameter_new)
        inflation_factor = 1

        for year in range(1, years + 1):
            pop.grow(growth_rate)

            dead_ash_tree_count = pop.apply_ash_mortality(ash_mortality_rate)
            total_tree_count = pop.ash_count

            ash_tree_basal_area = pop.ash_basal_area()

            pruning_cost = get_pruning_cost_by_dbh(pop.ash_diameter) * (pop.ash_count / pruning_cycle_years) * inflation_factor
            removal_cost = get_removal_cost_by_dbh(pop.ash_diameter) * dead_ash_tree_count * inflation_factor

            pop.cumulative_pruning_cost += pruning_cost
            pop.cumulative_removal_cost += removal_cost

            ctla_value_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                   inflation_factor, depreciation_ash, ash_tree_basal_area)

            results.append(build_year_result(
                year, pop.ash_count, 0, total_tree_count,
                ash_tree_basal_area, 0, ash_tree_basal_area,
                0, pruning_cost, 0, removal_cost, pruning_cost + removal_cost,
                0, pop.cumulative_pruning_cost, 0, pop.cumulative_removal_cost,
                pop.cumulative_pruning_cost + pop.cumulative_removal_cost,
                ctla_value_ash, 0, ctla_value_ash,
                ctla_value_ash - (pop.cumulative_pruning_cost + pop.cumulative_removal_cost)
            ))

            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results)

    def simulate_control_and_replant():
        results = []
        pop = TreePopulation(starting_ash_trees, starting_diameter, starting_diameter_new)
        inflation_factor = 1

        for year in range(1, years + 1):
            pop.grow(growth_rate)

            dead_ash_tree_count = pop.apply_ash_mortality(ash_mortality_rate)
            removal_cost_ash = get_removal_cost_by_dbh(pop.ash_diameter) * dead_ash_tree_count * inflation_factor

            # New cohort is appended AFTER aging below, so it stays at age 0 this year
            # (ages starting next year).
            aged = pop.age_cohorts(
                growth_rate_new, mortality_rates_by_age, background_mortality_rate,
                tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
                warranty_period_ends
            )
            pop.cumulative_planting_cost += aged['planting_cost_non_ash']

            pop.add_cohort(dead_ash_tree_count)

            total_tree_count = pop.total_count

            replanting_cost = dead_ash_tree_count * tree_planting_and_establishment_expense * inflation_factor
            pruning_cost = get_pruning_cost_by_dbh(pop.average_diameter_non_ash) * (pop.non_ash_count / pruning_cycle_years) * inflation_factor
            total_removal_cost = removal_cost_ash + aged['removal_cost_non_ash']
            total_planting_cost = replanting_cost + aged['planting_cost_non_ash']

            pop.cumulative_removal_cost += total_removal_cost
            pop.cumulative_planting_cost += replanting_cost
            pop.cumulative_pruning_cost += pruning_cost

            ash_tree_basal_area = pop.ash_basal_area()
            non_ash_tree_basal_area = pop.non_ash_basal_area()
            total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

            ctla_value_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                   inflation_factor, depreciation_ash, ash_tree_basal_area)
            ctla_value_non_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                       inflation_factor, depreciation_non_ash, non_ash_tree_basal_area)
            ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

            results.append(build_year_result(
                year, pop.ash_count, pop.non_ash_count, total_tree_count,
                ash_tree_basal_area, non_ash_tree_basal_area, total_tree_basal_area,
                total_planting_cost, pruning_cost, 0, total_removal_cost,
                total_planting_cost + pruning_cost + total_removal_cost,
                pop.cumulative_planting_cost, pop.cumulative_pruning_cost, 0, pop.cumulative_removal_cost,
                pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_removal_cost,
                ctla_value_ash, ctla_value_non_ash, ctla_value_all_trees,
                ctla_value_all_trees - (pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_removal_cost)
            ))

            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results)

    def simulate_remove_then_replant():
        results = []
        pop = TreePopulation(starting_ash_trees, starting_diameter, starting_diameter_new)
        inflation_factor = 1

        for year in range(1, years + 1):
            pop.grow(growth_rate)

            trees_to_remove = pop.remove_ash(set_removal_rate)

            # New cohort appended BEFORE aging below, so it gets aged to age 1
            # immediately, in the same year it's created.
            pop.add_cohort(trees_to_remove)

            aged = pop.age_cohorts(
                growth_rate_new, mortality_rates_by_age, background_mortality_rate,
                tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
                warranty_period_ends
            )
            pop.cumulative_planting_cost += aged['planting_cost_non_ash']

            total_tree_count = pop.total_count

            removal_cost_ash = get_removal_cost_by_dbh(pop.ash_diameter) * trees_to_remove * inflation_factor
            replanting_cost = trees_to_remove * tree_planting_and_establishment_expense * inflation_factor
            pruning_cost = get_pruning_cost_by_dbh(pop.average_diameter_non_ash) * (pop.non_ash_count / pruning_cycle_years) * inflation_factor
            total_removal_cost = removal_cost_ash + aged['removal_cost_non_ash']
            total_planting_cost = replanting_cost + aged['planting_cost_non_ash']

            pop.cumulative_removal_cost += total_removal_cost
            pop.cumulative_planting_cost += replanting_cost
            pop.cumulative_pruning_cost += pruning_cost

            ash_tree_basal_area = pop.ash_basal_area()
            non_ash_tree_basal_area = pop.non_ash_basal_area()
            total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

            ctla_value_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                   inflation_factor, depreciation_ash, ash_tree_basal_area)
            ctla_value_non_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                       inflation_factor, depreciation_non_ash, non_ash_tree_basal_area)
            ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

            results.append(build_year_result(
                year, pop.ash_count, pop.non_ash_count, total_tree_count,
                ash_tree_basal_area, non_ash_tree_basal_area, total_tree_basal_area,
                total_planting_cost, pruning_cost, 0, total_removal_cost,
                total_planting_cost + pruning_cost + total_removal_cost,
                pop.cumulative_planting_cost, pop.cumulative_pruning_cost, 0, pop.cumulative_removal_cost,
                pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_removal_cost,
                ctla_value_ash, ctla_value_non_ash, ctla_value_all_trees,
                ctla_value_all_trees - (pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_removal_cost)
            ))

            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results)

    def simulate_replant_inject_then_remove():
        results = []
        pop = TreePopulation(starting_ash_trees, starting_diameter, starting_diameter_new)
        inflation_factor = 1
        planting_rate = 0

        for year in range(1, years + 1):
            pop.grow(growth_rate)

            tree_planting_and_establishment_cost = tree_planting_and_establishment_expense * inflation_factor
            ash_tree_injections_cost = ash_tree_injections_expense * inflation_factor

            if year <= set_removal_year:
                # Injection happens in spring (May), before this year's EAB-driven
                # mortality has played out -- so cost is based on the population
                # going into treatment, not the smaller population left after
                # some of those already-injected trees die anyway.
                injection_cost = (pop.ash_count / 2) * pop.ash_diameter * ash_tree_injections_cost
                pop.cumulative_injection_cost += injection_cost

                trees_died = pop.apply_ash_mortality(injected_ash_mortality_rate)

                removal_cost = trees_died * get_removal_cost_by_dbh(pop.ash_diameter) * inflation_factor
                pop.cumulative_removal_cost += removal_cost
            else:
                trees_to_remove = pop.remove_ash(set_removal_rate)

                removal_cost = trees_to_remove * get_removal_cost_by_dbh(pop.ash_diameter) * inflation_factor
                pop.cumulative_removal_cost += removal_cost

                injection_cost = 0

            if year >= set_planting_year:
                remaining_trees_to_replace = max(0, starting_ash_trees - pop.non_ash_count)
                planting_rate = min(set_planting_rate, remaining_trees_to_replace)
                pop.add_cohort(planting_rate)
                replanting_cost = planting_rate * tree_planting_and_establishment_cost
                pop.cumulative_planting_cost += replanting_cost
            else:
                replanting_cost = 0

            aged = pop.age_cohorts(
                growth_rate_new, mortality_rates_by_age, background_mortality_rate,
                tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
                warranty_period_ends
            )
            pop.cumulative_removal_cost += aged['removal_cost_non_ash']
            pop.cumulative_planting_cost += aged['planting_cost_non_ash']

            total_tree_count = pop.total_count

            pruning_cost_ash = (pop.ash_count / pruning_cycle_years) * get_pruning_cost_by_dbh(pop.ash_diameter) * inflation_factor
            pruning_cost_non_ash = (pop.non_ash_count / pruning_cycle_years) * get_pruning_cost_by_dbh(pop.average_diameter_non_ash) * inflation_factor
            total_pruning_cost = pruning_cost_ash + pruning_cost_non_ash
            pop.cumulative_pruning_cost += total_pruning_cost

            ash_tree_basal_area = pop.ash_basal_area()
            non_ash_tree_basal_area = pop.non_ash_basal_area()
            total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

            ctla_value_ash = calculate_ctla_value(tree_planting_and_establishment_cost, starting_diameter_new,
                                                   1, depreciation_ash, ash_tree_basal_area)
            ctla_value_non_ash = calculate_ctla_value(tree_planting_and_establishment_cost, starting_diameter_new,
                                                       1, depreciation_non_ash, non_ash_tree_basal_area)
            ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

            removal_cost_non_ash = aged['removal_cost_non_ash']
            total_planting_cost = replanting_cost + aged['planting_cost_non_ash']

            results.append(build_year_result(
                year, pop.ash_count, pop.non_ash_count, total_tree_count,
                ash_tree_basal_area, non_ash_tree_basal_area, total_tree_basal_area,
                total_planting_cost, total_pruning_cost, injection_cost, removal_cost + removal_cost_non_ash,
                total_planting_cost + total_pruning_cost + injection_cost + removal_cost + removal_cost_non_ash,
                pop.cumulative_planting_cost, pop.cumulative_pruning_cost, pop.cumulative_injection_cost, pop.cumulative_removal_cost,
                pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_injection_cost + pop.cumulative_removal_cost,
                ctla_value_ash, ctla_value_non_ash, ctla_value_all_trees,
                ctla_value_all_trees - pop.cumulative_planting_cost - pop.cumulative_pruning_cost - pop.cumulative_injection_cost - pop.cumulative_removal_cost
            ))

            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results)

    def simulate_inject_remove_and_replant():
        results = []
        pop = TreePopulation(starting_ash_trees, starting_diameter, starting_diameter_new)
        inflation_factor = 1

        for year in range(1, years + 1):
            pop.grow(growth_rate)

            if year <= set_injection_years:
                # Injection happens in spring (May), before this year's EAB-driven
                # mortality has played out -- cost is based on the population going
                # into treatment, not the smaller post-mortality population.
                injection_cost = (pop.ash_count / 2) * pop.ash_diameter * ash_tree_injections_expense * inflation_factor
                pop.cumulative_injection_cost += injection_cost

                trees_died = pop.apply_ash_mortality(injected_ash_mortality_rate)

                removal_cost = trees_died * get_removal_cost_by_dbh(pop.ash_diameter) * inflation_factor
                pop.cumulative_removal_cost += removal_cost

                pop.add_cohort(trees_died)

                replanting_cost = trees_died * tree_planting_and_establishment_expense * inflation_factor
                pop.cumulative_planting_cost += replanting_cost
            else:
                trees_to_remove = pop.remove_ash(set_removal_rate)

                removal_cost = trees_to_remove * get_removal_cost_by_dbh(pop.ash_diameter) * inflation_factor
                pop.cumulative_removal_cost += removal_cost

                pop.add_cohort(trees_to_remove)

                replanting_cost = trees_to_remove * tree_planting_and_establishment_expense * inflation_factor
                pop.cumulative_planting_cost += replanting_cost

                injection_cost = 0

            # New cohort appended BEFORE aging below; free replanting under warranty.
            aged = pop.age_cohorts(
                growth_rate_new, mortality_rates_by_age, background_mortality_rate,
                tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
                warranty_period_ends
            )
            pop.cumulative_removal_cost += aged['removal_cost_non_ash']
            pop.cumulative_planting_cost += aged['planting_cost_non_ash']

            total_tree_count = pop.total_count

            pruning_cost_ash = (pop.ash_count / pruning_cycle_years) * get_pruning_cost_by_dbh(pop.ash_diameter) * inflation_factor
            pruning_cost_non_ash = (pop.non_ash_count / pruning_cycle_years) * get_pruning_cost_by_dbh(pop.average_diameter_non_ash) * inflation_factor
            total_pruning_cost = pruning_cost_ash + pruning_cost_non_ash
            pop.cumulative_pruning_cost += total_pruning_cost

            ash_tree_basal_area = pop.ash_basal_area()
            non_ash_tree_basal_area = pop.non_ash_basal_area()
            total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area

            ctla_value_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                   inflation_factor, depreciation_ash, ash_tree_basal_area)
            ctla_value_non_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                       inflation_factor, depreciation_non_ash, non_ash_tree_basal_area)
            ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

            removal_cost_non_ash = aged['removal_cost_non_ash']
            total_planting_cost = replanting_cost + aged['planting_cost_non_ash']

            results.append(build_year_result(
                year, pop.ash_count, pop.non_ash_count, total_tree_count,
                ash_tree_basal_area, non_ash_tree_basal_area, total_tree_basal_area,
                total_planting_cost, total_pruning_cost, injection_cost, removal_cost + removal_cost_non_ash,
                total_planting_cost + total_pruning_cost + injection_cost + removal_cost + removal_cost_non_ash,
                pop.cumulative_planting_cost, pop.cumulative_pruning_cost, pop.cumulative_injection_cost, pop.cumulative_removal_cost,
                pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_injection_cost + pop.cumulative_removal_cost,
                ctla_value_ash, ctla_value_non_ash, ctla_value_all_trees,
                ctla_value_all_trees - (pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_injection_cost + pop.cumulative_removal_cost)
            ))

            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results)

    def simulate_inject_in_perpetuity():
        results = []
        pop = TreePopulation(starting_ash_trees, starting_diameter, starting_diameter_new)
        inflation_factor = 1

        for year in range(1, years + 1):
            pop.grow(growth_rate)

            # Injection happens in spring (May), before this year's EAB-driven
            # mortality has played out -- cost is based on the population going
            # into treatment, not the smaller post-mortality population.
            annual_injection_cost = (pop.ash_count / 2) * pop.ash_diameter * ash_tree_injections_expense * inflation_factor
            pop.cumulative_injection_cost += annual_injection_cost

            trees_died = pop.apply_ash_mortality(injected_ash_mortality_rate)

            annual_removal_cost = trees_died * get_removal_cost_by_dbh(pop.ash_diameter) * inflation_factor
            pop.cumulative_removal_cost += annual_removal_cost

            pruning_cost_ash = (pop.ash_count / pruning_cycle_years) * get_pruning_cost_by_dbh(pop.ash_diameter) * inflation_factor
            pop.cumulative_pruning_cost += pruning_cost_ash

            ash_tree_basal_area = pop.ash_basal_area()
            total_tree_count = pop.ash_count

            ctla_value_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                   inflation_factor, depreciation_ash, ash_tree_basal_area)

            results.append(build_year_result(
                year, pop.ash_count, 0, total_tree_count,
                ash_tree_basal_area, 0, ash_tree_basal_area,
                0, pruning_cost_ash, annual_injection_cost, annual_removal_cost,
                pruning_cost_ash + annual_injection_cost + annual_removal_cost,
                0, pop.cumulative_pruning_cost, pop.cumulative_injection_cost, pop.cumulative_removal_cost,
                pop.cumulative_pruning_cost + pop.cumulative_injection_cost + pop.cumulative_removal_cost,
                ctla_value_ash, 0, ctla_value_ash,
                ctla_value_ash - (pop.cumulative_pruning_cost + pop.cumulative_injection_cost + pop.cumulative_removal_cost)
            ))

            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results)

    def simulate_inject_in_perpetuity_and_replant():
        results = []
        pop = TreePopulation(starting_ash_trees, starting_diameter, starting_diameter_new)
        inflation_factor = 1

        for year in range(1, years + 1):
            pop.grow(growth_rate)

            # Injection happens in spring (May), before this year's EAB-driven
            # mortality has played out -- cost is based on the population going
            # into treatment, not the smaller post-mortality population.
            annual_injection_cost = (pop.ash_count / 2) * pop.ash_diameter * ash_tree_injections_expense * inflation_factor
            pop.cumulative_injection_cost += annual_injection_cost

            trees_died = pop.apply_ash_mortality(injected_ash_mortality_rate)

            annual_removal_cost = trees_died * get_removal_cost_by_dbh(pop.ash_diameter) * inflation_factor
            pop.cumulative_removal_cost += annual_removal_cost

            pop.add_cohort(trees_died)

            annual_replanting_cost = trees_died * tree_planting_and_establishment_expense * inflation_factor
            pop.cumulative_planting_cost += annual_replanting_cost

            # New cohort appended BEFORE aging below; free replanting under warranty.
            aged = pop.age_cohorts(
                growth_rate_new, mortality_rates_by_age, background_mortality_rate,
                tree_planting_and_establishment_expense, get_removal_cost_by_dbh, inflation_factor,
                warranty_period_ends
            )
            pop.cumulative_removal_cost += aged['removal_cost_non_ash']
            pop.cumulative_planting_cost += aged['planting_cost_non_ash']

            pruning_cost_ash = (pop.ash_count / pruning_cycle_years) * get_pruning_cost_by_dbh(pop.ash_diameter) * inflation_factor
            pruning_cost_non_ash = (pop.non_ash_count / pruning_cycle_years) * get_pruning_cost_by_dbh(pop.average_diameter_non_ash) * inflation_factor
            total_pruning_cost = pruning_cost_ash + pruning_cost_non_ash
            pop.cumulative_pruning_cost += total_pruning_cost

            ash_tree_basal_area = pop.ash_basal_area()
            non_ash_tree_basal_area = pop.non_ash_basal_area()
            total_tree_basal_area = ash_tree_basal_area + non_ash_tree_basal_area
            total_tree_count = pop.total_count

            ctla_value_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                   inflation_factor, depreciation_ash, ash_tree_basal_area)
            ctla_value_non_ash = calculate_ctla_value(tree_planting_and_establishment_expense, starting_diameter_new,
                                                       inflation_factor, depreciation_non_ash, non_ash_tree_basal_area)
            ctla_value_all_trees = ctla_value_ash + ctla_value_non_ash

            removal_cost_non_ash = aged['removal_cost_non_ash']
            total_planting_cost = annual_replanting_cost + aged['planting_cost_non_ash']
            results.append(build_year_result(
                year, pop.ash_count, pop.non_ash_count, total_tree_count,
                ash_tree_basal_area, non_ash_tree_basal_area, total_tree_basal_area,
                total_planting_cost, total_pruning_cost, annual_injection_cost, annual_removal_cost + removal_cost_non_ash,
                total_planting_cost + total_pruning_cost + annual_injection_cost + annual_removal_cost + removal_cost_non_ash,
                pop.cumulative_planting_cost, pop.cumulative_pruning_cost, pop.cumulative_injection_cost, pop.cumulative_removal_cost,
                pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_injection_cost + pop.cumulative_removal_cost,
                ctla_value_ash, ctla_value_non_ash, ctla_value_all_trees,
                ctla_value_all_trees - (pop.cumulative_planting_cost + pop.cumulative_pruning_cost + pop.cumulative_injection_cost + pop.cumulative_removal_cost)
            ))

            inflation_factor *= 1 + annual_inflation_rate

        return pd.DataFrame(results)

    # Run simulations and store results
    all_results['Remove (Control)'] = simulate_control()
    all_results['Control with Replanting'] = simulate_control_and_replant()
    all_results['Remove then Replant'] = simulate_remove_then_replant()
    all_results['Replant, Inject, then Remove'] = simulate_replant_inject_then_remove()
    all_results['Inject, Remove, and Replant'] = simulate_inject_remove_and_replant()
    all_results['Inject in Perpetuity'] = simulate_inject_in_perpetuity()
    all_results['Inject in Perpetuity with Replanting'] = simulate_inject_in_perpetuity_and_replant()

    return all_results


def report_year_20_future_values(simulation_results):
    for scenario, df in simulation_results.items():
        year_20_data = df[df['Year'] == 20]
        if not year_20_data.empty:
            cumulative_costs = round(year_20_data['Cumulative Costs'].values[0] / 1000, 1)
            ctla_value_all_trees = round(year_20_data['CTLA Value of All Trees'].values[0] / 1000, 1)
            net_value_all_trees = round(year_20_data['Net Value of All Trees'].values[0] / 1000, 1)

            print(f"Scenario: {scenario}")
            print(f"  Cumulative Costs: ${cumulative_costs}k")
            print(f"  CTLA Value of All Trees: ${ctla_value_all_trees}k")
            print(f"  Net Value of All Trees: ${net_value_all_trees}k")
            print()


def report_year_20_counts(simulation_results):
    for scenario, df in simulation_results.items():
        year_20_data = df[df['Year'] == 20]
        if not year_20_data.empty:
            ash_tree_count = year_20_data['Ash Tree Count'].values[0]
            non_ash_tree_count = year_20_data['Non-Ash Tree Count'].values[0]
            total_tree_count = year_20_data['Total Tree Count'].values[0]
            ash_tree_basal_area = year_20_data['Ash Tree Basal Area'].values[0]
            non_ash_tree_basal_area = year_20_data['Non-Ash Tree Basal Area'].values[0]
            total_tree_basal_area = year_20_data['Total Tree Basal Area'].values[0]

            print(f"Scenario: {scenario}")
            print(f"  Ash Tree Count: {ash_tree_count}")
            print(f"  Non-Ash Tree Count: {non_ash_tree_count}")
            print(f"  Total Tree Count: {total_tree_count}")
            print(f"  Ash Tree Basal Area: {ash_tree_basal_area}")
            print(f"  Non-Ash Tree Basal Area: {non_ash_tree_basal_area}")
            print(f"  Total Tree Basal Area: {total_tree_basal_area}")
            print()


def apply_discount_rate(simulation_results, annual_discount_rate):
    discounted_results = {}
    for scenario, df in simulation_results.items():
        df = df.copy()
        df['Discount Factor'] = df['Year'].apply(lambda x: 1 if x == 1 else (1 / (1 + annual_discount_rate)) ** (x - 1))
        df['Discounted Annual Costs'] = df['Total Costs'] * df['Discount Factor']
        df['Discounted Cumulative Costs'] = df['Cumulative Costs'] * df['Discount Factor']
        df['Discounted CTLA Value'] = df['CTLA Value of All Trees'] * df['Discount Factor']
        df['Discounted Net Value'] = df['Net Value of All Trees'] * df['Discount Factor']

        discounted_results[scenario] = df

    return discounted_results


def report_year_20_present_values(simulation_results_present_value):
    for scenario, df in simulation_results_present_value.items():
        year_20_data = df[df['Year'] == 20]
        if not year_20_data.empty:
            cumulative_costs_present = round(year_20_data['Discounted Cumulative Costs'].values[0] / 1000, 1)
            ctla_value_all_trees_present = round(year_20_data['Discounted CTLA Value'].values[0] / 1000, 1)
            net_value_all_trees_present = round(year_20_data['Discounted Net Value'].values[0] / 1000, 1)

            print(f"Scenario: {scenario}")
            print(f"  Discounted Cumulative Costs: ${cumulative_costs_present}k")
            print(f"  Discounted CTLA Value of All Trees: ${ctla_value_all_trees_present}k")
            print(f"  Discounted Net Value of All Trees: ${net_value_all_trees_present}k")
            print()


# Count/area metrics are named identically in both the future-value and
# present-value dataframes, so they need no column-name mapping below.
_COUNT_AND_AREA_METRICS = [
    'Ash Tree Count', 'Non-Ash Tree Count', 'Total Tree Count',
    'Ash Tree Basal Area', 'Non-Ash Tree Basal Area', 'Total Tree Basal Area',
]


def _build_years_report(simulation_results, years_to_report, value_columns):
    """
    Build one row per (Metric, Scenario), with one column per reported year --
    e.g. Metric, Scenario, Year 1, Year 5, Year 10, Year 15, Year 20 -- all
    filled in on the same row.

    value_columns: dict mapping the label shown in the "Metric" column to the
    dataframe column it should be read from (e.g. {"Cumulative Costs":
    "Discounted Cumulative Costs"} for the present-value report).
    """
    metrics = {**value_columns, **{m: m for m in _COUNT_AND_AREA_METRICS}}

    rows = []
    for scenario, df in simulation_results.items():
        for metric_label, source_column in metrics.items():
            row = {"Metric": metric_label, "Scenario": scenario}
            for year in years_to_report:
                year_data = df[df['Year'] == year]
                if not year_data.empty:
                    row[f"Year {year}"] = round(year_data[source_column].values[0], 2)
            rows.append(row)

    return pd.DataFrame(rows)


def report_years_future_values(simulation_results_future_value, years_to_report, output_csv):
    results_df = _build_years_report(
        simulation_results_future_value, years_to_report,
        value_columns={
            "Cumulative Costs": "Cumulative Costs",
            "CTLA Value of All Trees": "CTLA Value of All Trees",
            "Net Value of All Trees": "Net Value of All Trees",
        }
    )
    results_df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")


def report_years_present_values(simulation_results_present_value, years_to_report, output_csv):
    # Reads the Discounted columns (previously this read the plain future-value
    # columns, so the CSV contained undiscounted figures mislabeled as present values).
    results_df = _build_years_report(
        simulation_results_present_value, years_to_report,
        value_columns={
            "Cumulative Costs": "Discounted Cumulative Costs",
            "CTLA Value of All Trees": "Discounted CTLA Value",
            "Net Value of All Trees": "Discounted Net Value",
        }
    )
    results_df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")