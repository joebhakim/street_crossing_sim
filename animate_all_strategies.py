#!/usr/bin/env python3
"""
Script to generate agent navigation animations for all pathfinding strategies.
"""

from utils.graph_utils import animate_agent_strategy
from utils.strategies import Strategies

def main():
    """Generate animations for all strategies."""
    print("Generating agent navigation animations for all strategies...")
    
    # Use the same parameters as the main simulation
    n, m = 3, 5  # Grid size
    s_lengths = {'vertical': 0.5, 'horizontal': 1.0}
    b_lengths = {'vertical': 4.0, 'horizontal': 3.0}
    
    # Generate animation for each strategy
    for strategy in Strategies:
        print(f"\n{'='*50}")
        print(f"Creating animation for strategy: {strategy.name}")
        print('='*50)
        
        try:
            anim = animate_agent_strategy(n, m, s_lengths, b_lengths, strategy, 
                                        duration_buffer=1.0, fps=30)  # Lower fps for smaller files
            if anim is None:
                print(f"Failed to create animation for {strategy.name}")
            else:
                print(f"✓ Successfully created animation for {strategy.name}")
        except Exception as e:
            print(f"✗ Error creating animation for {strategy.name}: {e}")
    
    print(f"\n{'='*50}")
    print("All strategy animations complete!")
    print("Check the generated GIF files:")
    for strategy in Strategies:
        print(f"  - agent_animation_strategy_{strategy.name}.gif")
    print('='*50)

if __name__ == "__main__":
    main()