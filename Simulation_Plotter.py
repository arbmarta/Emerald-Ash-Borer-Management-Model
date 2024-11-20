import matplotlib.pyplot as plt

def plot_simulations(simulation_results):

    # Define scenarios and corresponding colors for plotting
    scenarios = simulation_results.keys()
    colors = ['red', 'pink', 'blue', 'orange', 'green', 'purple', 'black']

    # Metrics to plot
    metrics = [
        ('Total Tree Count', 'Count', 'Total Tree Count Over Time'),
        ('Total Tree Basal Area', 'Basal Area', 'Total Tree Basal Area Over Time'),
        ('Total Costs', 'Cost ($)', 'Annual Costs'),
        ('Cumulative Costs', 'Cost ($)', 'Cumulative Costs Over Time'),
        ('CTLA Value of All Trees', 'CTLA Value ($)', 'CTLA Value of All Trees Over Time'),
        ('Net Value of All Trees', 'Net Value ($)', 'Net Value of All Trees Over Time'),
    ]

    # Create figure for plots
    plt.figure(figsize=(18, 12))

    # Loop over each metric to create subplots
    for idx, (metric, ylabel, title) in enumerate(metrics, start=1):
        ax = plt.subplot(3, 2, idx)  # Get axis handle
        for scenario, color in zip(scenarios, colors):
            data = simulation_results[scenario]
            ax.plot(data['Year'], data[metric], label=scenario, color=color)
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()

        # Add legend only to the first subplot in the second column
        if idx == 4:
            ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), title="Scenarios", fontsize=10, title_fontsize=14)

    # Adjust layout for space around the legend
    plt.tight_layout(rect=[0, 0, 1, 1])  # Reserve space on the right for the legend
    plt.show()
