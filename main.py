# Re-run after state reset
import random, math, matplotlib.pyplot as plt, numpy as np
import seaborn as sns


import networkx as nx

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
    
    # Use default edge lengths: s={'vertical': 0.5, 'horizontal': 1.0}, b={'vertical': 4.0, 'horizontal': 3.0}    
    # Example grid size

    G, pos = build_city_graph(n, m, s_lengths, b_lengths)

    fig, ax = plt.subplots(figsize=(12, 8))  # Increased size for larger graph
    
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
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='black', lw=2, linestyle='dashed', label='Street crossings (s)'),
        Line2D([0], [0], color='black', lw=2, linestyle='solid', label='Block connections (b)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig("city_graph.png", dpi=300, bbox_inches='tight')
    plt.show()

    


def wait_time_to_green(current_t, offset):
    phase = (current_t + offset) % 2
    return 0 if phase < 1 else 2 - phase

def choose_direction(strategy, e_left, s_left, w_e, w_s, prev_dir, step_idx):
    if e_left == 0:
        return "S"
    if s_left == 0:
        return "E"
    if strategy == "greedy":
        if w_e < w_s - 1e-9:
            return "E"
        if w_s < w_e - 1e-9:
            return "S"
        return "E" if e_left > s_left else "S"
    if strategy == "random":
        return random.choice(["E", "S"])
    if strategy == "edge":
        return "E"
    if strategy == "alternate":
        if prev_dir is None:
            return "E"
        if prev_dir == "E" and s_left > 0:
            return "S"
        if prev_dir == "S" and e_left > 0:
            return "E"
        return "E" if e_left > 0 else "S"
    raise ValueError

def simulate_run(n, m, strategy):
    t, e_left, s_left, prev_dir, step_idx = 0.0, n, m, None, 0
    while e_left + s_left:
        offset_e, offset_s = random.random()*2, random.random()*2
        w_e, w_s = wait_time_to_green(t, offset_e), wait_time_to_green(t, offset_s)
        d = choose_direction(strategy, e_left, s_left, w_e, w_s, prev_dir, step_idx)
        wait = w_e if d=="E" else w_s
        t += wait + 1
        if d=="E": e_left -= 1
        else: s_left -= 1
        prev_dir, step_idx = d, step_idx + 1
    return t

def simulate_many(n,m,strategy,N=5000):
    return [simulate_run(n,m,strategy) for _ in range(N)]

def main():
    n,m,Nsim=3,5,8000

    s_lengths={'vertical': 0.5, 'horizontal': 1.0}
    b_lengths={'vertical': 4.0, 'horizontal': 3.0}

    plot_city_graph(n, m, s_lengths, b_lengths)

    
    strategies=["greedy","random","alternate","edge"]
    results={s:simulate_many(n,m,s,Nsim) for s in strategies}

    fig,ax=plt.subplots(figsize=(10,6))
    
    # Prepare data for seaborn - sample from each strategy for faster plotting
    import pandas as pd
    plot_data = []
    sample_size = 200  # Sample size per strategy for faster plotting
    
    for strategy, times in results.items():
        # Sample randomly from each strategy
        sampled_times = np.random.choice(times, size=min(sample_size, len(times)), replace=False)
        for time in sampled_times:
            plot_data.append({'Strategy': strategy, 'Travel Time': time})
    df = pd.DataFrame(plot_data)

    print('plotting swarmplot of df', df.shape)
    
    # Create swarm plot
    sns.swarmplot(data=df, x='Strategy', y='Travel Time', ax=ax, size=3)
    
    # Add mean and std lines
    for i, strategy in enumerate(strategies):
        data = results[strategy]
        mean_val = np.mean(data)
        std_val = np.std(data)
        
        # Plot mean line
        ax.hlines(mean_val, i-0.4, i+0.4, colors='red', linewidth=2, alpha=0.8)
        
        # Add text with statistics
        ax.text(i, ax.get_ylim()[1] * 0.95, f'μ={mean_val:.2f}±{std_val:.2f}s', 
                ha='center', va='top', fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_ylabel("Travel time (s)")
    ax.set_title(f"Travel time distribution on {n}×{m} grid ({Nsim} runs per strategy)")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("travel_time_swarmplot.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    main()