# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a street crossing simulation project that models pedestrian navigation through a Manhattan-grid-like sidewalk system with traffic signals. The project explores optimal pathfinding strategies when pedestrians encounter random traffic signals at intersections, comparing different routing strategies through Monte Carlo simulation.

## Architecture

The project implements two main components:

### 1. Graph-Based City Model
- **Graph Structure**: Each "big block" intersection is modeled as a 2×2 sub-grid of nodes
- **Edge Types**: 
  - `'s'` edges: Street crossings within each 2×2 intersection
  - `'b'` edges: Block-along edges connecting adjacent intersections
- **Coordinate System**: Uses (r, c, dx, dy) node IDs where:
  - r, c: big block row/column 
  - dx, dy: local position within the 2×2 sub-grid (0 or 1)
- **Configurable Edge Lengths**: Separate length parameters for street crossings vs block connections

### 2. Pedestrian Navigation Simulation
- **Traffic Signal Model**: Continuous 1-second on/off cycles with random phase offsets
- **Strategy Evaluation**: Compares multiple pathfinding approaches:
  - `greedy`: Choose direction with shortest wait time
  - `random`: Random direction selection
  - `edge`: Always prefer eastward movement
  - `alternate`: Alternate between east/south directions
- **Monte Carlo Analysis**: Statistical evaluation over thousands of simulation runs

## Development Commands

```bash
# Install dependencies (recommended)
uv pip install -e .

# Run main simulation and generate plots
python main.py

# Install with regular pip
pip install -e .
```

## Key Functions

### Graph Construction
- `build_city_graph(n, m, s_lengths, b_lengths)`: Creates the Manhattan grid graph structure
- `node_id(r, c, dx, dy)`: Maps intersection-local coordinates to global coordinates
- `plot_city_graph(n, m, s_lengths, b_lengths)`: Visualizes the graph structure

### Simulation Engine
- `wait_time_to_green(current_t, offset)`: Calculates signal wait times
- `choose_direction(strategy, ...)`: Implements different routing strategies
- `simulate_run(n, m, strategy)`: Single pedestrian journey simulation
- `simulate_many(n, m, strategy, N)`: Monte Carlo batch simulation

## Dependencies

- `networkx>=3.5`: Graph construction and manipulation
- `matplotlib>=3.10.5`: Visualization and plot generation
- `numpy>=1.24.0`: Numerical computations and statistics
- Python 3.12+ required

## Output Files

- `city_graph.png`: Graph structure visualization showing s/b edge types
- `travel_time_histograms.png`: Comparative strategy performance analysis
- Generated at 300 DPI with tight bounding boxes

## File Structure

- `main.py`: Complete simulation implementation (graph + analysis)
- `pyproject.toml`: uv-compatible project configuration
- `README.md`: Research context and problem description
- `uv.lock`: Dependency lock file
- Single-file architecture (no src/ layout)

## Research Context

The project investigates pedestrian pathfinding strategies in urban grid environments with the hypothesis that biasing towards middle edges rather than boundary paths may be more efficient due to increased routing flexibility at intersections with random traffic signals. Current implementation focuses on comparing deterministic vs. stochastic routing strategies through statistical analysis of travel times.