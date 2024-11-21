import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

# Formatter function to add commas
def format_with_commas(x, pos):
    return f"{int(x):,}"

def plot_simulations(simulation_results):
    scenarios = simulation_results.keys()
    colors = ['red', 'pink', 'blue', 'orange', 'green', 'purple', 'black']

    metrics = [
        ('Total Tree Count', 'Count', 'Total Tree Count Over Time'),
        ('Total Tree Basal Area', 'Basal Area (cubic meters)', 'Total Tree Basal Area Over Time'),
        ('Total Costs', 'Cost (per $1k)', 'Annual Costs'),
        ('Cumulative Costs', 'Cost (per $1k)', 'Cumulative Costs Over Time'),
        ('CTLA Value of All Trees', 'CTLA Value (per $1k)', 'CTLA Value of All Trees Over Time'),
        ('Net Value of All Trees', 'Net Value (per $1k)', 'Net Value of All Trees Over Time'),
    ]

    # Create figure for plots
    plt.figure(figsize=(18, 12), dpi=900)

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
            # Customize the legend labels as needed
            custom_labels = {
                'Control and Remove': 'Remove Dead Ash Only',
                'Control, Remove, then Replant': 'Remove Dead Ash then Replant',
                'Remove then Replant': 'Preemptive Removal then Replant',
                'Replant, Inject, then Remove': 'Replant, Inject, then Preemptive Removal',
                'Inject, Remove, and Replant': 'Inject, Preemptive Removal, and Replant',
                'Inject in Perpetuity': 'Injection in Perpetuity',
                'Inject in Perpetuity with Replanting': 'Injection in Perpetuity with Replanting',
            }
            handles, labels = ax.get_legend_handles_labels()
            renamed_labels = [custom_labels.get(label, label) for label in labels]
            ax.legend(handles, renamed_labels, loc='center left', bbox_to_anchor=(1.05, 0.5),
                      title="Scenarios", fontsize=10, title_fontsize=14)

    # Adjust layout for space around the legend
    plt.tight_layout(rect=[0, 0, 1, 1])  # Reserve space on the right for the legend
    plt.savefig("Mississauga Simulations.jpeg", format='jpeg')
    plt.show()
