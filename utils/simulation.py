"""
Simulation logic for street crossing strategies.
"""
import random
import numpy as np


def wait_time_to_green(current_t, offset):
    """Calculate wait time until next green light."""
    phase = (current_t + offset) % 2
    return 0 if phase < 1 else 2 - phase


def is_signal_green(current_t, offset):
    """Check if signal is currently showing green/walk (observable state)."""
    phase = (current_t + offset) % 2
    return phase < 1  # Green for first half of 2-second cycle


def get_edge_signature(G, current_node, next_node):
    """Get (edge_type, orientation) signature for edge between nodes"""
    edge_data = G[current_node][next_node]
    return (edge_data['edge_type'], edge_data['orientation'])


def get_valid_moves(G, current_node):
    """Get only eastward and southward neighbors (no backtracking allowed)"""
    r1, c1, dx1, dy1 = current_node
    valid_neighbors = []
    
    for neighbor in G.neighbors(current_node):
        r2, c2, dx2, dy2 = neighbor
        
        # Check if move is eastward or southward
        is_east = (c2 > c1) or (c2 == c1 and dx2 > dx1)
        is_south = (r2 > r1) or (r2 == r1 and dy2 > dy1)
        
        if is_east or is_south:
            direction = "E" if is_east else "S"
            valid_neighbors.append((neighbor, direction))
    
    return valid_neighbors


def calculate_remaining_moves(current_node, end_node):
    """Calculate remaining big-block moves needed to reach destination."""
    r1, c1, dx1, dy1 = current_node
    r2, c2, dx2, dy2 = end_node
    
    # Count remaining big-block moves
    e_remaining = max(0, c2 - c1)
    s_remaining = max(0, r2 - r1)
    
    # If we're in the same big block, check local position
    if r1 == r2 and c1 == c2:
        if dx2 > dx1:
            e_remaining += 1
        if dy2 > dy1:
            s_remaining += 1
    
    return e_remaining, s_remaining


def choose_next_node(G, current_node, strategy, signal_offsets, current_time, end_node=None):
    """Choose next node based on strategy - only east/south moves allowed"""
    valid_moves = get_valid_moves(G, current_node)
    
    if not valid_moves:
        return None, None
    
    # Calculate signal states and wait times for moves
    move_data = []
    for neighbor, direction in valid_moves:
        edge_type, orientation = get_edge_signature(G, current_node, neighbor)
        
        if edge_type == 's':
            # Street crossing - has traffic signal
            edge_key = (current_node, neighbor)
            if edge_key not in signal_offsets:
                signal_offsets[edge_key] = random.random() * 2
            
            wait_time = wait_time_to_green(current_time, signal_offsets[edge_key])
            is_green = is_signal_green(current_time, signal_offsets[edge_key])
        else:
            # Block connection - no signal (always passable)
            wait_time = 0
            is_green = True
            
        move_data.append({
            'neighbor': neighbor,
            'direction': direction,
            'wait_time': wait_time,
            'is_green': is_green,
            'edge_type': edge_type,
            'orientation': orientation
        })
    
    # Apply strategy
    if strategy == "random":
        chosen = random.choice(move_data)
    elif strategy == "oracular":
        # Perfect information strategy - choose minimum wait time
        chosen = min(move_data, key=lambda x: x['wait_time'])
    elif strategy == "signal_observer":
        # Realistic strategy: observe current signal states
        green_moves = [m for m in move_data if m['is_green']]
        
        if len(green_moves) == 1:
            # Only one green signal - take it immediately
            chosen = green_moves[0]
        elif len(green_moves) > 1:
            # Multiple green signals - use balancing heuristic
            if end_node:
                e_remaining, s_remaining = calculate_remaining_moves(current_node, end_node)
                if e_remaining > s_remaining:
                    # More east moves needed, prefer east
                    east_green = [m for m in green_moves if m['direction'] == 'E']
                    chosen = east_green[0] if east_green else random.choice(green_moves)
                elif s_remaining > e_remaining:
                    # More south moves needed, prefer south
                    south_green = [m for m in green_moves if m['direction'] == 'S']
                    chosen = south_green[0] if south_green else random.choice(green_moves)
                else:
                    # Equal remaining, choose randomly among green signals
                    chosen = random.choice(green_moves)
            else:
                # No end node info, choose randomly among green signals
                chosen = random.choice(green_moves)
        else:
            # No green signals - wait for first one to turn green
            chosen = min(move_data, key=lambda x: x['wait_time'])
    elif strategy == "edge":
        # Prefer eastward moves
        east_moves = [m for m in move_data if m['direction'] == 'E']
        chosen = random.choice(east_moves) if east_moves else random.choice(move_data)
    elif strategy == "alternate":
        # For now, just random choice among available moves
        # TODO: track previous direction for true alternation
        chosen = random.choice(move_data)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return chosen['neighbor'], chosen['direction']


def simulate_graph_run(G, start_node, end_node, strategy):
    """Simulate a pedestrian journey through the actual graph - only east/south moves"""
    current_node = start_node
    current_time = 0.0
    path_history = [current_node]
    edge_signatures = []
    signal_offsets = {}  # Cache signal offsets for each edge
    
    while current_node != end_node:
        next_node, direction = choose_next_node(G, current_node, strategy, signal_offsets, current_time, end_node)
        
        if next_node is None:
            # No valid moves available - shouldn't happen with proper graph
            break
            
        # Get edge properties
        edge_type, orientation = get_edge_signature(G, current_node, next_node)
        edge_signatures.append((edge_type, orientation))
        
        # Calculate wait time and travel time
        if edge_type == 's':
            edge_key = (current_node, next_node)
            wait_time = wait_time_to_green(current_time, signal_offsets[edge_key])
        else:
            wait_time = 0
            
        # Add wait time plus crossing time (1 second)
        current_time += wait_time + 1
        
        # Move to next node
        current_node = next_node
        path_history.append(current_node)
    
    # Return results
    success = current_node == end_node
    return {
        'time': current_time,
        'path_nodes': path_history,
        'edge_signatures': edge_signatures,
        'success': success
    }


def simulate_graph_many(G, start_node, end_node, strategy, N=100):
    """Run many graph simulations"""
    results = []
    for _ in range(N):
        result = simulate_graph_run(G, start_node, end_node, strategy)
        if result['success']:
            results.append(result)
    return results


def enumerate_all_paths(G, start_node, end_node):
    """Enumerate all possible paths from start to end using only E/S moves"""
    all_paths = []
    
    def find_paths_recursive(current_node, current_path, visited_edges):
        if current_node == end_node:
            all_paths.append({
                'nodes': current_path.copy(),
                'edges': visited_edges.copy()
            })
            return
        
        valid_moves = get_valid_moves(G, current_node)
        for next_node, direction in valid_moves:
            edge_sig = get_edge_signature(G, current_node, next_node)
            new_path = current_path + [next_node]
            new_edges = visited_edges + [edge_sig]
            find_paths_recursive(next_node, new_path, new_edges)
    
    find_paths_recursive(start_node, [start_node], [])
    return all_paths


def path_signature(edge_list):
    """Convert edge list to hashable signature for frequency counting"""
    return tuple(edge_list)


def analyze_random_strategy_paths(G, start_node, end_node, N=1000):
    """Analyze path frequency and performance for random strategy"""
    print("Enumerating all possible paths...")
    all_paths = enumerate_all_paths(G, start_node, end_node)
    print(f"Found {len(all_paths)} possible paths")
    
    # Create mapping from signature to path info
    path_lookup = {}
    for i, path in enumerate(all_paths):
        sig = path_signature(path['edges'])
        path_lookup[sig] = {
            'index': i,
            'nodes': path['nodes'],
            'edges': path['edges'],
            'edge_count': len(path['edges']),
            'times': [],
            'frequency': 0
        }
    
    print(f"Running {N} random strategy simulations...")
    # Run simulations and track path usage
    for _ in range(N):
        result = simulate_graph_run(G, start_node, end_node, 'random')
        if result['success']:
            sig = path_signature(result['edge_signatures'])
            if sig in path_lookup:
                path_lookup[sig]['times'].append(result['time'])
                path_lookup[sig]['frequency'] += 1
    
    # Calculate statistics
    for sig, path_info in path_lookup.items():
        if path_info['times']:
            path_info['mean_time'] = np.mean(path_info['times'])
            path_info['std_time'] = np.std(path_info['times'])
        else:
            path_info['mean_time'] = float('inf')
            path_info['std_time'] = 0
    
    return path_lookup, all_paths


# Legacy simulation functions (simplified grid-based)
def choose_direction(strategy, e_left, s_left, w_e, w_s, prev_dir, step_idx):
    """Legacy function for simple grid simulation."""
    if e_left == 0:
        return "S"
    if s_left == 0:
        return "E"
    if strategy == "oracular":
        if w_e < w_s - 1e-9:
            return "E"
        if w_s < w_e - 1e-9:
            return "S"
        return "E" if e_left > s_left else "S"
    if strategy == "signal_observer":
        # In legacy sim, approximate signal_observer as checking if signals are green (wait_time == 0)
        green_e = (w_e == 0)
        green_s = (w_s == 0)
        
        if green_e and not green_s:
            return "E"
        elif green_s and not green_e:
            return "S"
        elif green_e and green_s:
            # Both green - use balancing heuristic
            return "E" if e_left > s_left else "S"
        else:
            # Neither green - wait for first to turn green (like oracular)
            if w_e < w_s - 1e-9:
                return "E"
            elif w_s < w_e - 1e-9:
                return "S"
            else:
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
    """Legacy simple simulation function."""
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


def simulate_many(n, m, strategy, N=5000):
    """Legacy function to run many simple simulations."""
    return [simulate_run(n, m, strategy) for _ in range(N)] 