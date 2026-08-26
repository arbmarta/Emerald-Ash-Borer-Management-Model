import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

# Formatter function to add commas
def format_with_commas(x, pos):
    return f"{int(x):,}"

# Scenario legend label overrides, shared by every plot function
CUSTOM_LABELS = {
    'Remove (Control)': 'Remove Dead Ash Only',
    'Control with Replanting': 'Remove Dead Ash then Replant',
    'Remove then Replant': 'Preemptive Removal then Replant',
    'Replant, Inject, then Remove': 'Replant, Inject, then Preemptive Removal',
    'Inject, Remove, and Replant': 'Inject, Preemptive Removal, and Replant',
    'Inject in Perpetuity': 'Injection in Perpetuity',
    'Inject in Perpetuity with Replanting': 'Injection in Perpetuity with Replanting',
}

# Colour palette (used when style == "colour") and linestyles (used when style == "monochrome")
PLOT_COLOURS = ['red', 'pink', 'blue', 'orange', 'green', 'purple', 'black']
PLOT_LINESTYLES = ['solid', 'dotted', 'dashed', 'dashdot', (0, (3, 5, 1, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (5, 5))]


def _style_settings(style, num_scenarios):
    """Return (colors, linestyles, legend_kwargs) for the requested plot style.

    Raises ValueError if there are more scenarios than defined colours/linestyles,
    instead of letting zip() silently drop the extra scenarios from the plot.
    """
    if style == "colour":
        colors, linestyles, legend_kwargs = PLOT_COLOURS, ['solid'] * len(PLOT_COLOURS), {}
    elif style == "monochrome":
        colors, linestyles, legend_kwargs = ['black'] * len(PLOT_LINESTYLES), PLOT_LINESTYLES, {'handlelength': 4, 'handletextpad': 1}
    else:
        raise ValueError(f"Unknown plot_style '{style}'. Expected 'colour' or 'monochrome'.")

    if num_scenarios > len(colors):
        raise ValueError(
            f"{num_scenarios} scenarios were passed in, but only {len(colors)} colours/linestyles "
            f"are defined in PLOT_COLOURS/PLOT_LINESTYLES. Add more entries there before adding "
            f"another scenario, or later scenarios will silently be left off every plot."
        )

    return colors, linestyles, legend_kwargs


def _plot_metric_grid(simulation_results, metrics, style, dpi, output_dir_fig, filename, show=True):
    """
    Shared implementation behind plot_simulations() and plot_simulations_present_value(),
    which were previously near-identical copies of each other. Draws a 3x2 grid of
    subplots, one per metric.

    metrics: list of (column_name, ylabel, title, scale_divisor) tuples. scale_divisor
    is None for metrics that shouldn't be rescaled, or a number (e.g. 1000) to divide by.
    """
    scenarios = list(simulation_results.keys())
    colors, linestyles, legend_kwargs = _style_settings(style, len(scenarios))

    plt.figure(figsize=(18, 12), dpi=dpi)

    for idx, (metric, ylabel, title, scale_divisor) in enumerate(metrics, start=1):
        ax = plt.subplot(3, 2, idx)
        for scenario, color, linestyle in zip(scenarios, colors, linestyles):
            data = simulation_results[scenario].copy()

            if scale_divisor is not None:
                data[metric] = data[metric] / scale_divisor

            ax.plot(data['Year'], data[metric], label=scenario, color=color, linestyle=linestyle, linewidth=2)
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()

        # Apply the formatter to add commas to y-axis numbers
        ax.yaxis.set_major_formatter(FuncFormatter(format_with_commas))

        # Add legend only to the first subplot in the second column
        if idx == 4:
            custom_handles = [
                Line2D([0], [0], color=color, linestyle=linestyle, linewidth=2)
                for color, linestyle in zip(colors, linestyles)
            ]
            renamed_labels = [CUSTOM_LABELS.get(scenario, scenario) for scenario in scenarios]

            ax.legend(custom_handles, renamed_labels, loc='center left', bbox_to_anchor=(1.1, 0.5),
                      title="Scenarios", fontsize=10, title_fontsize=14, **legend_kwargs)

    # Adjust layout for space around the legend
    plt.tight_layout(rect=[0, 0, 1, 1])  # Reserve space on the right for the legend
    plt.savefig(os.path.join(output_dir_fig, filename), format='jpeg')
    if show:
        plt.show()
    else:
        plt.close()


def plot_simulations(simulation_results_future_value, style, dpi, output_dir_fig, show=True):
    metrics = [
        ('Total Tree Count', 'Tree Count', 'Total Tree Count Over Time', None),
        ('Total Tree Basal Area', 'Basal Area (square meters)', 'Total Tree Basal Area Over Time', None),
        ('Total Costs', 'Cost (per $1k)', 'Annual Costs', 1000),
        ('Cumulative Costs', 'Cost (per $1k)', 'Cumulative Costs Over Time', 1000),
        ('CTLA Value of All Trees', 'CTLA Value (per $1k)', 'CTLA Value of All Trees Over Time', 1000),
        ('Net Value of All Trees', 'Net Value (per $1k)', 'Net Value of All Trees Over Time', 1000),
    ]
    suffix = "Colour" if style == "colour" else "B&W"
    _plot_metric_grid(simulation_results_future_value, metrics, style, dpi, output_dir_fig,
                       f"Figure 1 - {suffix}.jpeg", show=show)


def plot_simulations_present_value(simulation_results_present_value, style, dpi, output_dir_fig, show=True):
    metrics = [
        ('Total Tree Count', 'Tree Count', 'Total Tree Count Over Time', None),
        ('Total Tree Basal Area', 'Basal Area (square meters)', 'Total Tree Basal Area Over Time', None),
        ('Discounted Annual Costs', 'Cost (per $1k)', 'Discounted Annual Costs', 1000),
        ('Discounted Cumulative Costs', 'Cost (per $1k)', 'Discounted Cumulative Costs Over Time', 1000),
        ('Discounted CTLA Value', 'CTLA Value (per $1k)', 'Discounted CTLA Value of All Trees Over Time', 1000),
        ('Discounted Net Value', 'Net Value (per $1k)', 'Discounted Net Value of All Trees Over Time', 1000),
    ]
    suffix = "Colour" if style == "colour" else "B&W"
    _plot_metric_grid(simulation_results_present_value, metrics, style, dpi, output_dir_fig,
                       f"Figure 2 - {suffix}.jpeg", show=show)


def plot_simulations_standalone(simulation_results_future_value, style, dpi, output_dir_fig, show=True):
    scenarios = list(simulation_results_future_value.keys())
    colors, linestyles, legend_kwargs = _style_settings(style, len(scenarios))

    metrics = [
        ('Total Tree Count', 'Tree Count', 'Total Tree Count Over Time'),
        ('Total Tree Basal Area', 'Basal Area (square meters)', 'Total Tree Basal Area Over Time'),
        ('Total Costs', 'Cost (per $1k)', 'Inflation-Adjusted Annual Costs'),
        ('Cumulative Costs', 'Cost (per $1k)', 'Inflation-Adjusted Cumulative Costs Over Time'),
        ('CTLA Value of All Trees', 'CTLA Value (per $1k)', 'Inflation-Adjusted CTLA Value of All Trees Over Time'),
        ('Net Value of All Trees', 'Net Value (per $1k)', 'Inflation-Adjusted Net Value of All Trees Over Time'),
    ]

    filename_suffix = "Colour_standalone" if style == "colour" else "Black_and_White_standalone"

    for metric, ylabel, title in metrics:
        plt.figure(figsize=(10, 6), dpi=dpi)  # Create a new figure for each metric
        for scenario, color, linestyle in zip(scenarios, colors, linestyles):
            data = simulation_results_future_value[scenario].copy()

            # Scale to per $1,000 if applicable
            if metric in ['Total Costs', 'Cumulative Costs', 'CTLA Value of All Trees', 'Net Value of All Trees']:
                data[metric] = data[metric] / 1000

            plt.plot(data['Year'], data[metric], label=scenario, color=color, linestyle=linestyle, linewidth=2)

        plt.xlabel('Year')
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid()

        # Set x-axis ticks to start from 2 and increment by 2
        plt.xticks(range(2, int(data['Year'].max()) + 1, 2))

        # Apply a formatter to add commas to y-axis numbers
        plt.gca().yaxis.set_major_formatter(FuncFormatter(format_with_commas))

        # Add a legend on the left
        custom_handles = [
            Line2D([0], [0], color=color, linestyle=linestyle, linewidth=2)
            for color, linestyle in zip(colors, linestyles)
        ]
        renamed_labels = [CUSTOM_LABELS.get(scenario, scenario) for scenario in scenarios]

        plt.legend(custom_handles, renamed_labels, loc='center left', bbox_to_anchor=(1.02, 0.5),
                   fontsize=10, title="Scenarios", title_fontsize=14, **legend_kwargs)
        plt.tight_layout()

        # Save each figure separately
        filename = title.replace(' ', '_') + f'_{filename_suffix}.jpeg'
        plt.savefig(os.path.join(output_dir_fig, filename), format='jpeg')
        if show:
            plt.show()
        else:
            plt.close()