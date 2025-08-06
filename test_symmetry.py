#!/usr/bin/env python3
"""
Test script to verify symmetry in random strategy path selection.
For a truly random strategy, visits to coordinate (x,y) should approximately equal visits to (y,x).
"""

from utils.graph_utils import build_city_graph
from utils.simulation import analyze_specific_strategy_paths
from utils.strategies import Strategies
import numpy as np
from collections import defaultdict

def test_coordinate_symmetry():
    """Test if random strategy shows coordinate symmetry in path selection."""
    print("=" * 60)
    print("COORDINATE SYMMETRY TEST")
    print("=" * 60)
    
    # Use a symmetric grid
    n, m = 4, 4  # 4x4 grid should be perfectly symmetric
    s_lengths = {'vertical': 0.5, 'horizontal': 1.0}
    b_lengths = {'vertical': 4.0, 'horizontal': 3.0}
    
    G, pos = build_city_graph(n, m, s_lengths, b_lengths)
    start_node = (0, 0, 0, 0)
    end_node = (n-1, m-1, 1, 1)
    
    print(f"Testing {n}×{m} grid with {len(G.nodes)} nodes")
    print(f"Path: {start_node} → {end_node}")
    
    # Run many simulations using the same function as main analysis
    N_sims = 2000
    print(f"Running {N_sims} random strategy simulations...")
    
    path_data, all_paths = analyze_specific_strategy_paths(G, start_node, end_node, Strategies.random, N_sims)
    
    # Count node visits from path data
    node_visits = defaultdict(int)
    total_runs = 0
    
    for path_sig, path_info in path_data.items():
        if path_info['frequency'] > 0:
            total_runs += path_info['frequency']
            # Count visits for each node in this path
            for node in path_info['nodes']:
                node_visits[node] += path_info['frequency']
    
    print(f"Successful runs: {total_runs}")
    
    print(f"\nNode visit frequencies (sample):")
    print("-" * 40)
    
    # Test specific symmetric pairs
    symmetric_pairs = [
        ((1, 1, 0, 0), (1, 1, 0, 0)),  # Self-symmetric (should be same)
        ((0, 1, 0, 0), (1, 0, 0, 0)),  # Coordinate swap
        ((1, 2, 1, 1), (2, 1, 1, 1)),  # Another coordinate swap
        ((0, 2, 0, 1), (2, 0, 1, 0)),  # Diagonal swap
        ((n-1, m-1, 1, 1), (n-1, m-1, 1, 1)),  # Bottom right edge
        ((n-1, 0, 1, 0), (0, n-1, 0, 1)),  # Top left edge
        ((0, m-1, 0, 1), (m-1, 0, 1, 0)),  # Top right edge
        ((n-1, m-1, 1, 1), (n-1, m-1, 1, 1)),  # Bottom right edge
        ((n-1, 0, 1, 0), (0, n-1, 0, 1)),  # Top left edge
        ((0, m-1, 0, 1), (m-1, 0, 1, 0)),  # Top right edge
        ((n-1, m-1, 1, 1), (n-1, m-1, 1, 1)),  # Bottom right edge
        ((n-1, 0, 1, 0), (0, n-1, 0, 1)),  # Top left edge
    ]
    
    print("Symmetry test results:")
    print("-" * 40)
    total_asymmetry = 0
    
    for node1, node2 in symmetric_pairs:
        if node1 in node_visits and node2 in node_visits:
            visits1 = node_visits[node1]
            visits2 = node_visits[node2]
            ratio = visits1 / max(visits2, 1)
            asymmetry = abs(visits1 - visits2) / max(visits1 + visits2, 1)
            total_asymmetry += asymmetry
            
            print(f"{node1}: {visits1} visits")
            print(f"{node2}: {visits2} visits") 
            print(f"Ratio: {ratio:.3f}, Asymmetry: {asymmetry:.3f}")
            print()
    
    avg_asymmetry = total_asymmetry / len(symmetric_pairs)
    print(f"Average asymmetry: {avg_asymmetry:.3f}")
    print("(Lower values indicate better symmetry)")
    
    # Show top 10 most visited nodes
    print(f"\nTop 10 most visited nodes:")
    print("-" * 40)
    sorted_visits = sorted(node_visits.items(), key=lambda x: x[1], reverse=True)
    for node, visits in sorted_visits[:10]:
        r, c, dx, dy = node
        print(f"({r},{c},{dx},{dy}): {visits} visits")

if __name__ == "__main__":
    test_coordinate_symmetry()