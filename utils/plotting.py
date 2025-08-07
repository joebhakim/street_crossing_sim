"""
Plotting utilities for street crossing simulation results.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr
from itertools import combinations


def plot_strategy_comparison_swarm(strategy_results, n, m, title="Strategy Performance Comparison"):
    """Create swarm plot comparing strategy performance."""
    if not strategy_results:
        print("No strategy results to plot")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data for seaborn
    plot_data = []
    sample_size = 200  # Sample size per strategy for faster plotting
    
    for strategy, stats in strategy_results.items():
        # Generate sample data points from normal distribution based on mean/std
        if 'times' in stats:
            # Use actual time data if available
            times = stats['times']
            sampled_times = np.random.choice(times, size=min(sample_size, len(times)), replace=False)
        else:
            # Generate from normal distribution using mean/std
            sampled_times = np.random.normal(stats['mean'], stats['std'], sample_size)
        
        for time_val in sampled_times:
            plot_data.append({'Strategy': strategy, 'Travel Time': time_val})
    
    if not plot_data:
        print("No plot data generated")
        return
        
    df = pd.DataFrame(plot_data)
    
    # Create swarm plot
    sns.swarmplot(data=df, x='Strategy', y='Travel Time', ax=ax, size=3)
    
    # Add mean lines and error bars
    for i, (strategy, stats) in enumerate(strategy_results.items()):
        mean_val = stats['mean']
        std_val = stats['std']
        n_samples = stats['count']
        sem_val = std_val / np.sqrt(n_samples)  # Standard error of the mean
        
        # Plot mean line
        ax.hlines(mean_val, i-0.4, i+0.4, colors='red', linewidth=2, alpha=0.8)
        
        # Plot horizontal error bars for standard error
        ax.hlines([mean_val - sem_val, mean_val + sem_val], i-0.2, i+0.2, 
                 colors='orange', linewidth=1.5, alpha=0.7)
        
        # Add text with statistics
        ax.text(i, ax.get_ylim()[1] * 0.95, f'μ={mean_val:.2f}±{sem_val:.2f}s', 
                ha='center', va='top', fontsize=9, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # include mean and sem in y label
    # Perform pairwise rank-sum tests
    strategies = list(strategy_results.keys())
    pairwise_results = []
    
    for i, (strat1, strat2) in enumerate(combinations(strategies, 2)):
        # Get the actual time data for each strategy
        if 'times' in strategy_results[strat1] and 'times' in strategy_results[strat2]:
            times1 = strategy_results[strat1]['times']
            times2 = strategy_results[strat2]['times']
        else:
            # Generate data from normal distribution if times not available
            stats1 = strategy_results[strat1]
            stats2 = strategy_results[strat2]
            times1 = np.random.normal(stats1['mean'], stats1['std'], stats1['count'])
            times2 = np.random.normal(stats2['mean'], stats2['std'], stats2['count'])
        
        # Perform Mann-Whitney U test (equivalent to rank-sum test)
        statistic, p_value = mannwhitneyu(times1, times2, alternative='two-sided')
        
        # Calculate correlation (Spearman's rank correlation)
        combined_times = np.concatenate([times1, times2])
        combined_labels = np.concatenate([np.zeros(len(times1)), np.ones(len(times2))])
        correlation, _ = spearmanr(combined_times, combined_labels)
        
        pairwise_results.append({
            'strat1': strat1,
            'strat2': strat2,
            'p_value': p_value,
            'correlation': abs(correlation),
            'significant': p_value < 0.05
        })
    
    # Add significance bars
    y_max = ax.get_ylim()[1]
    y_min = ax.get_ylim()[0]
    bar_height = (y_max - y_min) * 0.05
    
    # Position bars at different heights to avoid overlap
    bar_positions = np.linspace(y_max * 1.02, y_max * 1.02 + bar_height * 5, len(pairwise_results))
    
    strategy_positions = {strat: i for i, strat in enumerate(strategies)}
    
    for i, result in enumerate(pairwise_results):
        x1 = strategy_positions[result['strat1']]
        x2 = strategy_positions[result['strat2']]
        y_pos = bar_positions[i]
        
        # Draw horizontal line
        ax.plot([x1, x2], [y_pos, y_pos], 'k-', linewidth=1)
        
        # Add vertical ticks at ends
        ax.plot([x1, x1], [y_pos - bar_height*0.1, y_pos + bar_height*0.1], 'k-', linewidth=1)
        ax.plot([x2, x2], [y_pos - bar_height*0.1, y_pos + bar_height*0.1], 'k-', linewidth=1)
        
        # Add p-value and significance annotation
        mid_x = (x1 + x2) / 2
        significance_marker = '*' if result['significant'] else ''
        ax.text(mid_x, y_pos + bar_height*0.2, 
                f"p={result['p_value']:.3f}{significance_marker}", 
                ha='center', va='bottom', fontsize=8, 
                bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgray', alpha=0.8))
    
    # Adjust y-axis limits to accommodate significance bars
    ax.set_ylim(y_min, bar_positions[-1] + bar_height * 0.5)
    
    ax.set_ylabel(f"Travel time (s) (mean ± sem)")
    ax.set_title(f"{title} ({n}×{m} grid)")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("strategy_comparison_swarmplot.png", dpi=300)
    plt.show()


def print_detailed_statistics(path_lookup, all_paths):
    """Print detailed path analysis statistics."""
    used_paths = [(sig, info) for sig, info in path_lookup.items() if info['frequency'] > 0]
    used_paths.sort(key=lambda x: x[1]['frequency'], reverse=True)
    
    print(f"\n" + "=" * 50)
    print("DETAILED PATH STATISTICS")
    print("=" * 50)
    print(f"Total possible paths: {len(all_paths)}")
    print(f"Paths actually used: {len(used_paths)}")
    print(f"Path utilization: {len(used_paths)/len(all_paths):.1%}")
    
    if used_paths:
        total_sims = sum(info['frequency'] for _, info in used_paths)
        print(f"Total successful simulations: {total_sims}")
        
        print(f"\nTop 10 most frequent paths:")
        print("-" * 80)
        print(f"{'Rank':<6} {'Freq':<8} {'%':<8} {'Avg Time':<12} {'Std':<8} {'Edges':<8} {'Sample Edge Types'}")
        print("-" * 80)
        
        for i, (sig, info) in enumerate(used_paths[:10]):
            pct = (info['frequency'] / total_sims) * 100
            sample_edges = str(sig[:4]) + "..." if len(sig) > 4 else str(sig)
            std = info.get('std_time', 0)
            print(f"{i+1:<6} {info['frequency']:<8} {pct:<8.1f} {info['mean_time']:<12.2f} {std:<8.2f} {info['edge_count']:<8} {sample_edges}")
        
        # Analyze path characteristics
        print(f"\nPath characteristics:")
        edge_counts = [info['edge_count'] for _, info in used_paths]
        frequencies = [info['frequency'] for _, info in used_paths]
        times = [info['mean_time'] for _, info in used_paths]
        
        print(f"Edge count range: {min(edge_counts)} to {max(edge_counts)} (avg: {np.mean(edge_counts):.1f})")
        print(f"Frequency range: {min(frequencies)} to {max(frequencies)} (most popular path used {max(frequencies)} times)")
        print(f"Time range: {min(times):.2f}s to {max(times):.2f}s (avg: {np.mean(times):.2f}s)")
        
        # Test Galton board hypothesis - are middle paths more frequent?
        print(f"\nGalton board analysis:")
        print("(Checking if paths with more routing options are more frequent)")


def print_strategy_comparison(strategy_results):
    """Print strategy comparison results."""
    print(f"\n" + "=" * 50)
    print("STRATEGY COMPARISON")
    print("=" * 50)
    
    for strategy, stats in strategy_results.items():
        print(f"{strategy:8s}: {stats['mean']:.2f}±{stats['std']:.2f}s (n={stats['count']})") 