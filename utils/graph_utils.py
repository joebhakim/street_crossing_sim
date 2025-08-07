"""
Graph building and visualization utilities for street crossing simulation.
"""
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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


def visualize_paths_on_graph(G, pos, path_lookup, n, m, s_lengths, b_lengths, max_paths_to_show=None, strategy=None):
    """Visualize paths overlaid on the city graph with color=time, thickness=frequency"""
    
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Calculate node visit frequencies from path data
    node_visits = {}
    for node in G.nodes():
        node_visits[node] = 0
    
    for path_sig, path_info in path_lookup.items():
        if path_info['frequency'] > 0:
            for node in path_info['nodes']:
                node_visits[node] += path_info['frequency']
    
    # Draw base graph structure (nodes and edges in light gray)
    nx.draw_networkx_nodes(G, pos=pos, node_size=60, node_color='lightgray', ax=ax, alpha=0.5)
    nx.draw_networkx_edges(G, pos=pos, edge_color='lightgray', width=0.5, alpha=0.3, ax=ax)
    
    # Add node visit frequency labels
    node_labels = {}
    for node in G.nodes():
        visits = node_visits.get(node, 0)
        if visits > 0:  # Only label nodes that were visited
            node_labels[node] = str(visits)
    
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='blue', ax=ax)

    # Get used paths sorted by frequency
    used_paths = [(sig, info) for sig, info in path_lookup.items() if info['frequency'] > 0]
    used_paths.sort(key=lambda x: x[1]['frequency'], reverse=True)
    
    # Limit to top paths for clarity
    if max_paths_to_show is not None:
        paths_to_show = used_paths[:max_paths_to_show]
    else:
        paths_to_show = used_paths
    
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
    ax.set_title(f"Path visualization with strategy {strategy.name} ({n}×{m} grid)\n" +
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
    plt.savefig(f"path_visualization_on_graph_strategy_{strategy.name}.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print top paths info
    print(f"\nTop {min(10, len(paths_to_show))} paths:")
    print("-" * 60)
    for i, (sig, info) in enumerate(paths_to_show[:10]):
        print(f"{i+1:2d}. Freq:{info['frequency']:3d} Time:{info['mean_time']:5.1f}s Edges:{info['edge_count']:2d}")
    
    return paths_to_show


def animate_traffic_lights(n, m, s_lengths, b_lengths, duration=10.0, fps=10):
    """
    Create an animated visualization of traffic light changes on the city graph.
    
    Parameters
    ----------
    n, m : int
        Grid dimensions (big blocks)
    s_lengths, b_lengths : dict
        Edge lengths for street crossings and block connections
    duration : float
        Animation duration in seconds
    fps : int
        Frames per second for the animation
        
    Returns
    -------
    None
        Saves animated GIF to 'traffic_lights_animation.gif'
    """
    # Build the graph
    G, pos = build_city_graph(n, m, s_lengths, b_lengths)
    
    # Generate random signal offsets for each s-edge
    signal_offsets = {}
    for u, v, data in G.edges(data=True):
        if data['edge_type'] == 's':
            # Create unique key for this edge
            edge_key = (data['edge_type'], data['orientation'])
            if (u, v) not in signal_offsets:
                signal_offsets[(u, v)] = random.random() * 2
    
    # Separate edges by type
    s_edges = [(u, v) for u, v, d in G.edges(data=True) if d['edge_type'] == 's']
    b_edges = [(u, v) for u, v, d in G.edges(data=True) if d['edge_type'] == 'b']
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_aspect('equal')
    
    # Time parameters
    dt = 1.0 / fps
    frames = int(duration * fps)
    
    def is_signal_green(current_t, offset):
        """Check if signal is currently showing green/walk."""
        phase = (current_t + offset) % 2
        return phase < 1  # Green for first half of 2-second cycle
    
    def animate_frame(frame):
        """Animation function called for each frame."""
        ax.clear()
        current_time = frame * dt
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos=pos, node_size=80, node_color='black', ax=ax)
        
        # Draw b-edges (no signals, always black)
        nx.draw_networkx_edges(G, pos=pos, edgelist=b_edges, edge_color='black', 
                              width=2, alpha=0.7, style='solid', ax=ax)
        
        # Draw s-edges with colors based on signal state
        green_edges = []
        red_edges = []
        
        for u, v in s_edges:
            offset = signal_offsets[(u, v)]
            if is_signal_green(current_time, offset):
                green_edges.append((u, v))
            else:
                red_edges.append((u, v))
        
        # Draw green and red s-edges
        if green_edges:
            nx.draw_networkx_edges(G, pos=pos, edgelist=green_edges, edge_color='green', 
                                  width=3, alpha=0.8, style='dashed', ax=ax)
        if red_edges:
            nx.draw_networkx_edges(G, pos=pos, edgelist=red_edges, edge_color='red', 
                                  width=3, alpha=0.8, style='dashed', ax=ax)
        
        # Set title with current time
        ax.set_title(f"Traffic Light Animation ({n}×{m} grid) - Time: {current_time:.1f}s\n" +
                    f"Green = Walk Signal | Red = Don't Walk Signal", fontsize=12)
        
        # Add legend
        legend_elements = [
            Line2D([0], [0], color='green', lw=3, linestyle='dashed', label='Green signals (Walk)'),
            Line2D([0], [0], color='red', lw=3, linestyle='dashed', label='Red signals (Don\'t Walk)'),
            Line2D([0], [0], color='black', lw=2, linestyle='solid', label='Block connections (no signals)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        ax.set_aspect('equal')
    
    # Create and run animation
    print(f"Creating traffic light animation ({duration}s at {fps}fps)...")
    anim = animation.FuncAnimation(fig, animate_frame, frames=frames, interval=1000/fps, repeat=True)
    
    # Save as GIF
    print("Saving animation as 'traffic_lights_animation.gif'...")
    anim.save('traffic_lights_animation.gif', writer='pillow', fps=fps, dpi=150)
    print("Animation saved successfully!")
    
    plt.show()
    return anim


def animate_agent_strategy(n, m, s_lengths, b_lengths, strategy, duration_buffer=2.0, fps=60):
    """
    Create an animated visualization of an agent navigating using a specific strategy.
    
    Parameters
    ----------
    n, m : int
        Grid dimensions (big blocks)
    s_lengths, b_lengths : dict
        Edge lengths for street crossings and block connections
    strategy : Strategies
        The pathfinding strategy to use
    duration_buffer : float
        Extra time to show at end of animation
    fps : int
        Frames per second for the animation
        
    Returns
    -------
    anim : matplotlib.animation.FuncAnimation
        The animation object
    """
    from utils.simulation import simulate_graph_run, wait_time_to_green, is_signal_green
    import numpy as np
    
    # Build the graph
    G, pos = build_city_graph(n, m, s_lengths, b_lengths)
    
    # Define start and end points
    start_node = (0, 0, 0, 0)
    end_node = (n-1, m-1, 1, 1)
    
    # Run simulation to get path data
    print(f"Running simulation for strategy: {strategy.name}")
    result = simulate_graph_run(G, start_node, end_node, strategy)
    
    if not result['success']:
        print(f"Simulation failed for strategy {strategy.name}")
        return None
    
    path_nodes = result['path_nodes']
    total_time = result['time']
    
    print(f"Journey time: {total_time:.1f}s, Path length: {len(path_nodes)} nodes")
    
    # Generate same signal offsets as used in simulation
    signal_offsets = {}
    random.seed(42)  # For reproducible animations
    for u, v, data in G.edges(data=True):
        if data['edge_type'] == 's':
            if (u, v) not in signal_offsets:
                signal_offsets[(u, v)] = random.random() * 2
    
    # Separate edges by type
    s_edges = [(u, v) for u, v, d in G.edges(data=True) if d['edge_type'] == 's']
    b_edges = [(u, v) for u, v, d in G.edges(data=True) if d['edge_type'] == 'b']
    
    # Create detailed timeline for agent movement
    timeline = []
    current_time = 0.0
    
    for i in range(len(path_nodes) - 1):
        current_node = path_nodes[i]
        next_node = path_nodes[i + 1]
        
        # Check if this is a signal crossing
        edge_data = G[current_node][next_node]
        is_signal_edge = edge_data['edge_type'] == 's'
        
        if is_signal_edge:
            # Calculate wait time for this crossing
            wait_time = wait_time_to_green(current_time, signal_offsets[(current_node, next_node)])
        else:
            wait_time = 0
            
        # Add waiting phase
        if wait_time > 0:
            timeline.append({
                'start_time': current_time,
                'end_time': current_time + wait_time,
                'phase': 'waiting',
                'position': pos[current_node],
                'current_node': current_node,
                'next_node': next_node
            })
            current_time += wait_time
        
        # Calculate actual crossing time based on edge length (speed = 1 m/s)
        edge_length = G[current_node][next_node]['length']
        crossing_time = edge_length
        
        # Add movement phase (actual crossing time)
        timeline.append({
            'start_time': current_time,
            'end_time': current_time + crossing_time,
            'phase': 'moving',
            'start_pos': pos[current_node],
            'end_pos': pos[next_node],
            'current_node': current_node,
            'next_node': next_node,
            'crossing_time': crossing_time
        })
        current_time += crossing_time
    
    # Add final position
    timeline.append({
        'start_time': current_time,
        'end_time': current_time + duration_buffer,
        'phase': 'finished',
        'position': pos[end_node],
        'current_node': end_node,
        'next_node': None
    })
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_aspect('equal')
    
    # Animation parameters
    dt = 1.0 / fps
    total_duration = current_time + duration_buffer
    frames = int(total_duration * fps)
    
    def animate_frame(frame):
        """Animation function called for each frame."""
        ax.clear()
        current_time = frame * dt
        
        # Draw base graph nodes
        nx.draw_networkx_nodes(G, pos=pos, node_size=80, node_color='black', ax=ax)
        
        # Draw b-edges (no signals, always black)
        nx.draw_networkx_edges(G, pos=pos, edgelist=b_edges, edge_color='black', 
                              width=2, alpha=0.7, style='solid', ax=ax)
        
        # Draw s-edges with traffic light colors
        green_edges = []
        red_edges = []
        
        for u, v in s_edges:
            offset = signal_offsets[(u, v)]
            if is_signal_green(current_time, offset):
                green_edges.append((u, v))
            else:
                red_edges.append((u, v))
        
        if green_edges:
            nx.draw_networkx_edges(G, pos=pos, edgelist=green_edges, edge_color='green', 
                                  width=3, alpha=0.8, style='dashed', ax=ax)
        if red_edges:
            nx.draw_networkx_edges(G, pos=pos, edgelist=red_edges, edge_color='red', 
                                  width=3, alpha=0.8, style='dashed', ax=ax)
        
        # Find agent position at current time
        agent_pos = None
        current_phase = None
        
        for event in timeline:
            if event['start_time'] <= current_time <= event['end_time']:
                current_phase = event
                break
        
        if current_phase:
            if current_phase['phase'] == 'waiting' or current_phase['phase'] == 'finished':
                # Agent is stationary at a node
                agent_pos = current_phase['position']
            elif current_phase['phase'] == 'moving':
                # Agent is moving between nodes
                progress = (current_time - current_phase['start_time']) / (current_phase['end_time'] - current_phase['start_time'])
                progress = max(0, min(1, progress))  # Clamp to [0, 1]
                
                start_pos = current_phase['start_pos']
                end_pos = current_phase['end_pos']
                agent_pos = (
                    start_pos[0] + progress * (end_pos[0] - start_pos[0]),
                    start_pos[1] + progress * (end_pos[1] - start_pos[1])
                )
        
        # Draw agent as purple star
        if agent_pos:
            ax.scatter(*agent_pos, marker='*', color='purple', s=200, zorder=10, edgecolor='white', linewidth=1)
        
        # Create status text
        status_text = f"Strategy: {strategy.name}\nTime: {current_time:.1f}s"
        if current_phase:
            if current_phase['phase'] == 'waiting':
                remaining_wait = current_phase['end_time'] - current_time
                status_text += f"\nWaiting for signal: {remaining_wait:.1f}s"
            elif current_phase['phase'] == 'moving':
                crossing_time = current_phase.get('crossing_time', 1.0)
                remaining_cross = current_phase['end_time'] - current_time
                status_text += f"\nCrossing ({crossing_time:.1f}s): {remaining_cross:.1f}s left"
            elif current_phase['phase'] == 'finished':
                status_text += f"\nJourney complete!"
        
        # Set title and add status
        ax.set_title(f"Agent Navigation Animation ({n}×{m} grid)\n{status_text}", fontsize=12)
        
        # Add legend
        legend_elements = [
            Line2D([0], [0], color='green', lw=3, linestyle='dashed', label='Green signals (Walk)'),
            Line2D([0], [0], color='red', lw=3, linestyle='dashed', label='Red signals (Don\'t Walk)'),
            Line2D([0], [0], color='black', lw=2, linestyle='solid', label='Block connections'),
            Line2D([0], [0], marker='*', color='purple', lw=0, markersize=10, label='Agent')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        ax.set_aspect('equal')
    
    # Create animation
    print(f"Creating agent animation ({total_duration:.1f}s at {fps}fps)...")
    anim = animation.FuncAnimation(fig, animate_frame, frames=frames, interval=1000/fps, repeat=True)
    
    # Save as GIF
    filename = f'agent_animation_strategy_{strategy.name}.gif'
    print(f"Saving animation as '{filename}'...")
    anim.save(filename, writer='pillow', fps=fps, dpi=150)
    print("Animation saved successfully!")
    
    plt.show()
    return anim