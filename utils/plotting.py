"""
Plotting utilities for street crossing simulation results.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


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
    
    # Add mean lines and statistics
    for i, (strategy, stats) in enumerate(strategy_results.items()):
        mean_val = stats['mean']
        std_val = stats['std']
        
        # Plot mean line
        ax.hlines(mean_val, i-0.4, i+0.4, colors='red', linewidth=2, alpha=0.8)
        
        # Add text with statistics
        ax.text(i, ax.get_ylim()[1] * 0.95, f'μ={mean_val:.2f}±{std_val:.2f}s', 
                ha='center', va='top', fontsize=9, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_ylabel("Travel time (s)")
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