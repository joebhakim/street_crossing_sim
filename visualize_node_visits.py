#!/usr/bin/env python3
"""
Visualize node visit frequencies overlaid on the graph to check for structural asymmetries.
"""

from utils.graph_utils import build_city_graph, visualize_paths_on_graph
from utils.simulation import analyze_specific_strategy_paths
from utils.strategies import Strategies
import matplotlib.pyplot as plt
import networkx as nx

def visualize_node_visits():
    """Create a focused visualization showing node visit frequencies."""
    print("=" * 60)
    print("NODE VISIT FREQUENCY VISUALIZATION")
    print("=" * 60)
    
    # Use small symmetric grid to easily spot asymmetries  
    n, m = 3, 3  # 3x3 grid should be perfectly symmetric
    s_lengths = {'vertical': 0.5, 'horizontal': 1.0}
    b_lengths = {'vertical': 4.0, 'horizontal': 3.0}
    
    G, pos = build_city_graph(n, m, s_lengths, b_lengths)
    start_node = (0, 0, 0, 0)
    end_node = (n-1, m-1, 1, 1)
    
    print(f"Testing {n}×{m} grid with {len(G.nodes)} nodes")
    print(f"Path: {start_node} → {end_node}")
    
    # Run analysis
    N_sims = 1000
    print(f"Running {N_sims} random strategy simulations...")
    
    path_data, all_paths = analyze_specific_strategy_paths(G, start_node, end_node, Strategies.random, N_sims)
    
    # Create visualization with node visit counts
    print("Generating node visit visualization...")
    visualize_paths_on_graph(G, pos, path_data, n, m, s_lengths, b_lengths, 
                            max_paths_to_show=None, 
                            title=f"Node Visit Frequencies - {Strategies.random.name} strategy ({N_sims} runs)")
    
    # Also create a clean graph with just node labels for clarity
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Calculate node visit frequencies
    node_visits = {}
    for node in G.nodes():
        node_visits[node] = 0
    
    for path_sig, path_info in path_data.items():
        if path_info['frequency'] > 0:
            for node in path_info['nodes']:
                node_visits[node] += path_info['frequency']
    
    # Draw clean graph
    nx.draw_networkx_nodes(G, pos=pos, node_size=800, node_color='lightblue', ax=ax, alpha=0.7)
    nx.draw_networkx_edges(G, pos=pos, edge_color='gray', width=1, alpha=0.5, ax=ax)
    
    # Add visit count labels
    node_labels = {}
    for node in G.nodes():
        visits = node_visits.get(node, 0)
        r, c, dx, dy = node
        node_labels[node] = f"{visits}\n({r},{c},{dx},{dy})"
    
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, ax=ax)
    
    ax.set_aspect('equal')
    ax.set_title(f"Node Visit Frequencies with Coordinates\n{n}×{m} grid, {N_sims} random walks")
    
    plt.tight_layout()
    plt.savefig("node_visit_frequencies.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print some key statistics
    print(f"\nNode visit statistics:")
    print("-" * 40)
    total_visits = sum(node_visits.values())
    print(f"Total node visits: {total_visits}")
    print(f"Average visits per node: {total_visits / len(G.nodes()):.1f}")
    
    # Show most and least visited nodes
    sorted_visits = sorted(node_visits.items(), key=lambda x: x[1], reverse=True)
    print(f"\nMost visited nodes:")
    for node, visits in sorted_visits[:5]:
        r, c, dx, dy = node
        print(f"  ({r},{c},{dx},{dy}): {visits} visits")
    
    print(f"\nLeast visited nodes:")
    for node, visits in sorted_visits[-5:]:
        if visits > 0:  # Only show nodes that were visited
            r, c, dx, dy = node
            print(f"  ({r},{c},{dx},{dy}): {visits} visits")

if __name__ == "__main__":
    visualize_node_visits()