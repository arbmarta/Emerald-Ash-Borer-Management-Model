import os

from config import (
    output_dir_fig, output_dir_csv,
    starting_ash_trees, starting_diameter, starting_diameter_new, growth_rate, growth_rate_new,
    ash_mortality_rate, injected_ash_mortality_rate, tree_planting_and_establishment_expense,
    ash_tree_injections_expense, removal_rate, removal_year, injection_years, planting_rate, planting_year,
    depreciation_ash, depreciation_non_ash, mortality_rates_by_age, background_mortality_rate,
    annual_inflation_rate, years, get_pruning_cost_by_dbh, get_removal_cost_by_dbh,
    warranty_period_ends, pruning_cycle_years,
    annual_discount_rate,
    years_to_report, output_csv_future_values, output_csv_present_values,
    plot_style, dpi,
)
from simulation_module import (
    run_simulations, report_year_20_future_values, report_year_20_counts,
    apply_discount_rate, report_year_20_present_values,
    report_years_future_values, report_years_present_values,
)
from simulation_plotter import plot_simulations, plot_simulations_standalone, plot_simulations_present_value


def main():
    # Make sure the output folders exist before anything tries to save into them
    os.makedirs(output_dir_fig, exist_ok=True)
    os.makedirs(output_dir_csv, exist_ok=True)

    simulation_results_future_value = run_simulations(
        starting_ash_trees, starting_diameter, starting_diameter_new, growth_rate,
        growth_rate_new, ash_mortality_rate, injected_ash_mortality_rate,
        tree_planting_and_establishment_expense, ash_tree_injections_expense,
        removal_rate, removal_year, injection_years, planting_rate, planting_year,
        depreciation_ash, depreciation_non_ash, mortality_rates_by_age,
        background_mortality_rate, annual_inflation_rate, years,
        get_pruning_cost_by_dbh, get_removal_cost_by_dbh,
        warranty_period_ends, pruning_cycle_years,
    )

    report_year_20_future_values(simulation_results_future_value)
    report_year_20_counts(simulation_results_future_value)
    plot_simulations(simulation_results_future_value, plot_style, dpi, output_dir_fig)
    plot_simulations_standalone(simulation_results_future_value, plot_style, dpi, output_dir_fig)

    simulation_results_present_value = apply_discount_rate(simulation_results_future_value, annual_discount_rate)

    report_year_20_present_values(simulation_results_present_value)
    plot_simulations_present_value(simulation_results_present_value, plot_style, dpi, output_dir_fig)

    report_years_future_values(simulation_results_future_value, years_to_report,
                                os.path.join(output_dir_csv, output_csv_future_values))
    report_years_present_values(simulation_results_present_value, years_to_report,
                                 os.path.join(output_dir_csv, output_csv_present_values))


if __name__ == "__main__":
    main()