"""
Main script for street crossing simulation.
"""
from enum import Enum
import numpy as np
from utils.graph_utils import build_city_graph, plot_city_graph, visualize_paths_on_graph
from utils.simulation import (
    simulate_graph_many, analyze_specific_strategy_paths
)
from utils.plotting import print_detailed_statistics, print_strategy_comparison, plot_strategy_comparison_swarm
from utils.strategies import Strategies

def main():
    """Run the complete street crossing simulation analysis."""
    # Use smaller grid for manageable path enumeration
    n, m, Nsim = 3, 4, 5000  # Smaller for path analysis
    
    s_lengths = {'vertical': 0.5, 'horizontal': 1.0}
    b_lengths = {'vertical': 4.0, 'horizontal': 3.0}

    print("=" * 70)
    print("STREET CROSSING SIMULATION WITH PATH ANALYSIS")
    print("=" * 70)
    
    # Build graph and define start/end points
    G, pos = build_city_graph(n, m, s_lengths, b_lengths)
    start_node = (0, 0, 0, 0)  # Top-left of first intersection
    end_node = (n-1, m-1, 1, 1)  # Bottom-right of last intersection
    
    print(f"Grid size: {n}×{m} big blocks")
    print(f"Graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
    print(f"Journey: {start_node} → {end_node}")
    
    # 1. Draw base city graph
    plot_city_graph(n, m, s_lengths, b_lengths)
    
    # 2. Run path analysis for random strategy
    print("\n" + "=" * 50)
    print("PATH FREQUENCY ANALYSIS")
    print("=" * 50)
    
    specific_path_data_random, all_paths_analyzed_random = analyze_specific_strategy_paths(G, start_node, end_node, Strategies.random, Nsim)
    
    # 3. Create path overlay visualization
    print("\nGenerating path overlay visualization...")
    visualize_paths_on_graph(G, pos, specific_path_data_random, n, m, s_lengths, b_lengths, max_paths_to_show=1500, title=f"Strategy: {Strategies.random.name} path overlay")
    
    # 4. Print detailed statistics
    print_detailed_statistics(specific_path_data_random, all_paths_analyzed_random)
    
    # 5. Strategy comparison with swarm plot
    strategies = [Strategies.random, Strategies.oracular, Strategies.signal_observer, Strategies.edge]
    strategy_results = {}
    
    for strategy in strategies:
        results = simulate_graph_many(G, start_node, end_node, strategy, min(Nsim, 200))
        if results:
            times = [r['time'] for r in results]
            strategy_results[strategy.name] = {
                'mean': np.mean(times),
                'std': np.std(times),
                'count': len(results),
                'times': times  # Include raw times for swarm plot
            }
    
    print_strategy_comparison(strategy_results)
    
    # Generate swarm plot for strategy comparison
    print(f"\nGenerating strategy comparison swarm plot...")
    plot_strategy_comparison_swarm(strategy_results, n, m, title="Strategy Performance Comparison")
    
    print("\n" + "=" * 70)
    print("Analysis complete! Check generated PNG files for visualizations.")
    print("=" * 70)


if __name__ == "__main__":
    main()