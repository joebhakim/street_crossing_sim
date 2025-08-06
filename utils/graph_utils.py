"""
Graph building and visualization utilities for street crossing simulation.
"""
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D


def build_city_graph(n, m, s_lengths, b_lengths):
    """
    Build a graph of an n x m Manhattan grid where each street intersection
    is itself a 2 x 2 sub‑grid of nodes.

    Parameters
    ----------
    n, m : int
        Number of "big" blocks (east‑west, north‑south).
    s_lengths : dict
        Lengths for street-crossing edges: {'vertical': float, 'horizontal': float}
    b_lengths : dict
        Lengths for block-along edges: {'vertical': float, 'horizontal': float}

    Returns
    -------
    G : networkx.Graph
        Undirected graph with two edge types:
        's' – street‑crossing edges (within the 2x2),
        'b' – block‑along edges (between neighbouring intersections).
    pos : dict
        Mapping node -> (x, y) coordinates for drawing.
    """
    G = nx.Graph()
    pos = {}

    # Calculate spacing between intersections based on b_lengths
    x_spacing = b_lengths['horizontal'] + s_lengths['horizontal']
    y_spacing = b_lengths['vertical'] + s_lengths['vertical']

    # Helper to turn intersection‑local coordinates into global.
    def node_id(r, c, dx, dy):
        # Base position of the intersection
        base_x = c * x_spacing
        base_y = (n - 1 - r) * y_spacing  # flip y‑axis so origin at bottom‑left
        
        # Local offset within the 2x2 intersection
        local_x = dx * s_lengths['horizontal']
        local_y = (1 - dy) * s_lengths['vertical']  # dy=0 is top, dy=1 is bottom
        
        x = base_x + local_x
        y = base_y + local_y
        return (r, c, dx, dy), (x, y)

    # Build nodes and "s" edges (inside each 2x2 intersection)
    for r in range(n):
        for c in range(m):
            nodes = {}
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:  # TL, TR, BL, BR
                nid, coord = node_id(r, c, dx, dy)
                G.add_node(nid)
                pos[nid] = coord
                nodes[(dx, dy)] = nid

            # Internal street‑crossing edges with lengths
            G.add_edge(nodes[(0, 0)], nodes[(1, 0)], edge_type='s', 
                      orientation='horizontal', length=s_lengths['horizontal'])  # top
            G.add_edge(nodes[(0, 1)], nodes[(1, 1)], edge_type='s', 
                      orientation='horizontal', length=s_lengths['horizontal'])  # bottom
            G.add_edge(nodes[(0, 0)], nodes[(0, 1)], edge_type='s', 
                      orientation='vertical', length=s_lengths['vertical'])  # left
            G.add_edge(nodes[(1, 0)], nodes[(1, 1)], edge_type='s', 
                      orientation='vertical', length=s_lengths['vertical'])  # right

    # "b" edges between adjacent intersections
    for r in range(n):
        for c in range(m):
            # east‑west neighbours
            if c < m - 1:
                G.add_edge(
                    (r, c, 1, 0), (r, c + 1, 0, 0), edge_type='b',
                    orientation='horizontal', length=b_lengths['horizontal']
                )
                G.add_edge(
                    (r, c, 1, 1), (r, c + 1, 0, 1), edge_type='b',
                    orientation='horizontal', length=b_lengths['horizontal']
                )

            # north‑south neighbours
            if r < n - 1:
                G.add_edge(
                    (r, c, 0, 1), (r + 1, c, 0, 0), edge_type='b',
                    orientation='vertical', length=b_lengths['vertical']
                )  # BL to TL below
                G.add_edge(
                    (r, c, 1, 1), (r + 1, c, 1, 0), edge_type='b',
                    orientation='vertical', length=b_lengths['vertical']
                )  # BR to TR below

    return G, pos


def plot_city_graph(n, m, s_lengths, b_lengths):
    """Plot the city graph with different line styles for edge types."""
    G, pos = build_city_graph(n, m, s_lengths, b_lengths)

    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Separate edges by type
    s_edges = [(u, v) for u, v, d in G.edges(data=True) if d['edge_type'] == 's']
    b_edges = [(u, v) for u, v, d in G.edges(data=True) if d['edge_type'] == 'b']
    
    # Draw nodes first
    nx.draw_networkx_nodes(G, pos=pos, node_size=80, node_color='black', ax=ax)
    
    # Draw edges with different line styles - dashed for street crossings, solid for block connections
    nx.draw_networkx_edges(G, pos=pos, edgelist=s_edges, edge_color='black', 
                          width=2, alpha=0.7, style='dashed', ax=ax)
    nx.draw_networkx_edges(G, pos=pos, edgelist=b_edges, edge_color='black', 
                          width=2, alpha=0.7, style='solid', ax=ax)
    
    ax.set_aspect('equal')
    ax.set_title(f"Manhattan grid with 2×2 intersections ({n}×{m} big blocks)\n" +
                f"s_lengths: vertical={s_lengths['vertical']}, horizontal={s_lengths['horizontal']} | " +
                f"b_lengths: vertical={b_lengths['vertical']}, horizontal={b_lengths['horizontal']}")
    
    # Add legend with line styles
    legend_elements = [
        Line2D([0], [0], color='black', lw=2, linestyle='dashed', label='Street crossings (s)'),
        Line2D([0], [0], color='black', lw=2, linestyle='solid', label='Block connections (b)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig("city_graph.png", dpi=300, bbox_inches='tight')
    plt.show()


def visualize_paths_on_graph(G, pos, path_lookup, n, m, s_lengths, b_lengths, max_paths_to_show=20):
    """Visualize paths overlaid on the city graph with color=time, thickness=frequency"""
    
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Draw base graph structure (nodes and edges in light gray)
    nx.draw_networkx_nodes(G, pos=pos, node_size=60, node_color='lightgray', ax=ax, alpha=0.5)
    nx.draw_networkx_edges(G, pos=pos, edge_color='lightgray', width=0.5, alpha=0.3, ax=ax)
    
    # Get used paths sorted by frequency
    used_paths = [(sig, info) for sig, info in path_lookup.items() if info['frequency'] > 0]
    used_paths.sort(key=lambda x: x[1]['frequency'], reverse=True)
    
    # Limit to top paths for clarity
    paths_to_show = used_paths[:max_paths_to_show]
    
    if not paths_to_show:
        print("No paths to visualize")
        return
    
    # Get time range for color mapping
    times = [info['mean_time'] for _, info in paths_to_show]
    min_time, max_time = min(times), max(times)
    
    # Get frequency range for thickness mapping
    frequencies = [info['frequency'] for _, info in paths_to_show]
    max_freq = max(frequencies)
    min_freq = min(frequencies)
    
    print(f"Visualizing top {len(paths_to_show)} paths:")
    print(f"Time range: {min_time:.2f}s to {max_time:.2f}s")
    print(f"Frequency range: {min_freq} to {max_freq}")
    
    # Draw each path
    for i, (sig, info) in enumerate(paths_to_show):
        nodes = info['nodes']
        
        # Create path edges for drawing
        path_edges = [(nodes[j], nodes[j+1]) for j in range(len(nodes)-1)]
        
        # Map time to color (red=slow, green=fast)
        if max_time > min_time:
            time_ratio = (info['mean_time'] - min_time) / (max_time - min_time)
        else:
            time_ratio = 0
        color = plt.cm.RdYlGn_r(time_ratio)  # Red for slow, green for fast
        
        # Map frequency to thickness
        if max_freq > min_freq:
            freq_ratio = (info['frequency'] - min_freq) / (max_freq - min_freq)
        else:
            freq_ratio = 0
        thickness = 1 + freq_ratio * 8  # Range from 1 to 9
        
        # Draw path
        nx.draw_networkx_edges(G, pos=pos, edgelist=path_edges, 
                             edge_color=[color], width=thickness, alpha=0.7, ax=ax)
    
    ax.set_aspect('equal')
    ax.set_title(f"Path Usage Visualization ({n}×{m} grid)\n" +
                f"Color: Red=slow, Green=fast | Thickness: Usage frequency\n" +
                f"Showing top {len(paths_to_show)} most frequent paths")
    
    # Create custom legend
    legend_elements = [
        Line2D([0], [0], color='red', lw=3, alpha=0.7, label=f'Slow paths (~{max_time:.1f}s)'),
        Line2D([0], [0], color='green', lw=3, alpha=0.7, label=f'Fast paths (~{min_time:.1f}s)'),
        Line2D([0], [0], color='gray', lw=8, alpha=0.7, label=f'High usage ({max_freq} times)'),
        Line2D([0], [0], color='gray', lw=1, alpha=0.7, label=f'Low usage ({min_freq} times)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.savefig("path_visualization_on_graph.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print top paths info
    print(f"\nTop {min(10, len(paths_to_show))} paths:")
    print("-" * 60)
    for i, (sig, info) in enumerate(paths_to_show[:10]):
        print(f"{i+1:2d}. Freq:{info['frequency']:3d} Time:{info['mean_time']:5.1f}s Edges:{info['edge_count']:2d}")
    
    return paths_to_show 