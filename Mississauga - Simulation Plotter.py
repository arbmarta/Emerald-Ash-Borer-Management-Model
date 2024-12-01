import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

# Formatter function to add commas
def format_with_commas(x, pos):
    return f"{int(x):,}"

def plot_simulations_colour(simulation_results):
    scenarios = simulation_results.keys()
    colors = ['red', 'pink', 'blue', 'orange', 'green', 'purple', 'black']

    metrics = [
        ('Total Tree Count', 'Tree Count', 'Total Tree Count Over Time'),
        ('Total Tree Basal Area', 'Basal Area (cubic meters)', 'Total Tree Basal Area Over Time'),
        ('Total Costs', 'Cost (per $1k)', 'Annual Costs'),
        ('Cumulative Costs', 'Cost (per $1k)', 'Cumulative Costs Over Time'),
        ('CTLA Value of All Trees', 'CTLA Value (per $1k)', 'CTLA Value of All Trees Over Time'),
        ('Net Value of All Trees', 'Net Value (per $1k)', 'Net Value of All Trees Over Time'),
    ]

    # Create figure for plots
    plt.figure(figsize=(18, 12), dpi=400)

    # Loop over each metric to create subplots
    for idx, (metric, ylabel, title) in enumerate(metrics, start=1):
        ax = plt.subplot(3, 2, idx)  # Get axis handle
        for scenario, color in zip(scenarios, colors):
            data = simulation_results[scenario]

            # Scale Cumulative Costs to per $1,000
            if metric == 'Total Costs':
                data[metric] = data[metric] / 1000  # Scale to per $1,000

            # Scale Cumulative Costs to per $1,000
            if metric == 'Cumulative Costs':
                data[metric] = data[metric] / 1000  # Scale to per $1,000

            # Scale Cumulative Costs to per $1,000
            if metric == 'CTLA Value of All Trees':
                data[metric] = data[metric] / 1000  # Scale to per $1,000

            # Scale Cumulative Costs to per $1,000
            if metric == 'Net Value of All Trees':
                data[metric] = data[metric] / 1000  # Scale to per $1,000


            ax.plot(data['Year'], data[metric], label=scenario, color=color, linewidth = 2)
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()

        # Apply the formatter to add commas to y-axis numbers
        ax.yaxis.set_major_formatter(FuncFormatter(format_with_commas))

        # Add legend only to the first subplot in the second column
        if idx == 4:
            custom_labels = {
                'Control and Remove': 'Remove Dead Ash Only',
                'Control, Remove, then Replant': 'Remove Dead Ash then Replant',
                'Remove then Replant': 'Preemptive Removal then Replant',
                'Replant, Inject, then Remove': 'Replant, Inject, then Preemptive Removal',
                'Inject, Remove, and Replant': 'Inject, Preemptive Removal, and Replant',
                'Inject in Perpetuity': 'Injection in Perpetuity',
                'Inject in Perpetuity with Replanting': 'Injection in Perpetuity with Replanting',
            }

            # Create custom legend handles with Line2D objects
            custom_handles = [
                Line2D([0], [0], color=color, linewidth=2)
                for color in colors
            ]
            renamed_labels = [custom_labels.get(scenario, scenario) for scenario in scenarios]

            # Add legend with custom handles
            ax.legend(custom_handles, renamed_labels, loc='center left', bbox_to_anchor=(1.1, 0.5),
                      title="Scenarios", fontsize=10, title_fontsize=14,)

    # Adjust layout for space around the legend
    plt.tight_layout(rect=[0, 0, 1, 1])  # Reserve space on the right for the legend
    plt.savefig("Figure 1 - Colour.jpeg", format='jpeg')
    plt.show()

def plot_simulations_black_and_white(simulation_results):
    scenarios = simulation_results.keys()
    colors = ['black', 'black', 'black', 'black', 'black', 'black', 'black']
    lines = ['solid', 'dotted', 'dashed', 'dashdot', (0, (3, 5, 1, 5, 1, 5)), (0, (3, 10, 1, 10)), (0, (5, 5))]

    metrics = [
        ('Total Tree Count', 'Tree Count', 'Total Tree Count Over Time'),
        ('Total Tree Basal Area', 'Basal Area (cubic meters)', 'Total Tree Basal Area Over Time'),
        ('Total Costs', 'Cost (per $1k)', 'Annual Costs'),
        ('Cumulative Costs', 'Cost (per $1k)', 'Cumulative Costs Over Time'),
        ('CTLA Value of All Trees', 'CTLA Value (per $1k)', 'CTLA Value of All Trees Over Time'),
        ('Net Value of All Trees', 'Net Value (per $1k)', 'Net Value of All Trees Over Time'),
    ]

    # Create figure for plots
    plt.figure(figsize=(18, 12), dpi=400)

    # Loop over each metric to create subplots
    for idx, (metric, ylabel, title) in enumerate(metrics, start=1):
        ax = plt.subplot(3, 2, idx)  # Get axis handle
        for scenario, color, line in zip(scenarios, colors, lines):
            data = simulation_results[scenario]

            # Scale Cumulative Costs to per $1,000
            if metric == 'Total Costs':
                data[metric] = data[metric] / 1000  # Scale to per $1,000

            # Scale Cumulative Costs to per $1,000
            if metric == 'Cumulative Costs':
                data[metric] = data[metric] / 1000  # Scale to per $1,000

            # Scale Cumulative Costs to per $1,000
            if metric == 'CTLA Value of All Trees':
                data[metric] = data[metric] / 1000  # Scale to per $1,000

            # Scale Cumulative Costs to per $1,000
            if metric == 'Net Value of All Trees':
                data[metric] = data[metric] / 1000  # Scale to per $1,000


            ax.plot(data['Year'], data[metric], label=scenario, color=color, linestyle = line, linewidth = 2)
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()

        # Apply the formatter to add commas to y-axis numbers
        ax.yaxis.set_major_formatter(FuncFormatter(format_with_commas))

        # Add legend only to the first subplot in the second column
        if idx == 4:
            custom_labels = {
                'Control and Remove': 'Remove Dead Ash Only',
                'Control, Remove, then Replant': 'Remove Dead Ash then Replant',
                'Remove then Replant': 'Preemptive Removal then Replant',
                'Replant, Inject, then Remove': 'Replant, Inject, then Preemptive Removal',
                'Inject, Remove, and Replant': 'Inject, Preemptive Removal, and Replant',
                'Inject in Perpetuity': 'Injection in Perpetuity',
                'Inject in Perpetuity with Replanting': 'Injection in Perpetuity with Replanting',
            }

            # Create custom legend handles with Line2D objects
            custom_handles = [
                Line2D([0], [0], color=color, linestyle=line, linewidth=2)
                for color, line in zip(colors, lines)
            ]
            renamed_labels = [custom_labels.get(scenario, scenario) for scenario in scenarios]

            # Add legend with custom handles
            ax.legend(custom_handles, renamed_labels, loc='center left', bbox_to_anchor=(1.1, 0.5),
                      title="Scenarios", fontsize=10, title_fontsize=14, handlelength = 4, handletextpad=1)

    # Adjust layout for space around the legend
    plt.tight_layout(rect=[0, 0, 1, 1])  # Reserve space on the right for the legend
    plt.savefig("Figure 1 - B&W.jpeg", format='jpeg')
    plt.show()
