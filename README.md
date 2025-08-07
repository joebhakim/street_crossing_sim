# Street Crossing Simulation

Pedestrian pathfinding simulation comparing routing strategies in a Manhattan grid with random traffic signals.

## Overview

Models pedestrian navigation through a city grid where intersections have 2-second traffic signals with random phase offsets. Compares different routing strategies through Monte Carlo simulation.

## Usage

```bash
# Install dependencies
uv pip install -e .

# Run simulation
python main.py
```

## Components

- `main.py`: Main simulation runner and analysis
- `utils/graph_utils.py`: City grid graph construction and visualization
- `utils/simulation.py`: Core simulation logic and strategy evaluation
- `utils/strategies.py`: Available pathfinding strategies (random, oracular, edge-biased, etc.)
- `utils/plotting.py`: Statistical analysis and visualization

## Strategies

- **random**: Random direction selection at intersections
- **oracular_random**: Random with perfect traffic signal knowledge
- **option_maximizer**: Choose direction maximizing future options
- **edge**: Eastward movement preference
- **alternate**: Alternating east/south movement

## Output

Generates path visualizations, strategy performance comparisons, and statistical analysis plots. 