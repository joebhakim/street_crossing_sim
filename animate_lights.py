#!/usr/bin/env python3
"""
Script to demonstrate the traffic light animation.
"""

from utils.graph_utils import animate_traffic_lights

def main():
    """Run the traffic light animation demo."""
    print("Starting traffic light animation...")
    
    # Use the same parameters as the main simulation
    n, m = 3, 5  # Grid size
    s_lengths = {'vertical': 0.5, 'horizontal': 1.0}
    b_lengths = {'vertical': 4.0, 'horizontal': 3.0}
    
    # Create animation: 8 seconds at 8 fps (showing 4 complete signal cycles)
    animate_traffic_lights(n, m, s_lengths, b_lengths, duration=8.0, fps=8)

if __name__ == "__main__":
    main()