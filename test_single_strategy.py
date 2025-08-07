#!/usr/bin/env python3
"""
Test script to generate a single strategy animation for debugging.
"""

from utils.graph_utils import animate_agent_strategy
from utils.strategies import Strategies

def main():
    """Test animation with a single strategy."""
    print("Testing agent navigation animation...")
    
    # Use the same parameters as the main simulation
    n, m = 3, 5  # Grid size
    s_lengths = {'vertical': 0.5, 'horizontal': 1.0}
    b_lengths = {'vertical': 4.0, 'horizontal': 3.0}
    
    # Test with option_maximizer strategy (realistic and interesting)
    strategy = Strategies.option_maximizer
    
    print(f"Creating test animation for strategy: {strategy.name}")
    anim = animate_agent_strategy(n, m, s_lengths, b_lengths, strategy, 
                                duration_buffer=1.0, fps=20)  # Lower fps for faster testing
    
    if anim:
        print("✓ Test animation created successfully!")
    else:
        print("✗ Test animation failed!")

if __name__ == "__main__":
    main()