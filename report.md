# Street Crossing Simulation: Path Analysis Report

## Executive Summary

This report analyzes pedestrian navigation strategies in a Manhattan-grid urban environment with traffic signals. We implemented a graph-based simulation modeling 2×2 intersections connected by street crossings ('s' edges) and block connections ('b' edges), comparing four navigation strategies through comprehensive path analysis and Monte Carlo simulation.

![City Graph Structure](city_graph.png)
*Figure 1: Manhattan grid structure with 2×2 intersections. Dashed lines represent street crossings ('s' edges) with traffic signals, solid lines represent block connections ('b' edges).*

## Key Findings

### Strategy Performance
- **Signal Observer (Realistic)**: 14.87±0.60s - performs nearly optimally using only observable signal states
- **Oracular (Perfect Information)**: 14.77±0.58s - baseline with perfect future knowledge
- **Random**: 15.98±0.94s - serves as control for unbiased exploration
- **Edge (Always East)**: 15.93±0.86s - deterministic eastward preference

### Critical Discovery: The realistic **Signal Observer** strategy achieves 99.3% of optimal performance (oracular) while using only currently observable information, validating that pedestrians don't need future signal prediction for near-optimal navigation.

![Strategy Performance Comparison](strategy_comparison_swarmplot.png)
*Figure 2: Performance comparison across navigation strategies. Each dot represents a simulation run, with red lines showing mean performance. Signal Observer achieves near-optimal performance.*

## Methodology

### Graph Model Architecture
- **Grid Structure**: n×m "big blocks" each containing 2×2 sub-intersections
- **Node Representation**: (r, c, dx, dy) coordinates where r,c are big-block positions and dx,dy are local intersection positions
- **Edge Types**:
  - 's' edges: Street crossings with traffic signals (1s on/off cycles, random phase offsets)
  - 'b' edges: Block connections with no signals
- **Movement Constraints**: Only eastward and southward moves allowed (no backtracking)

### Strategy Implementations

#### Signal Observer (Realistic Strategy)
1. **Signal State Assessment**: Observe current red/green state of all available crossing signals
2. **Decision Logic**:
   - If one signal green, others red → Cross immediately
   - If multiple signals green → Use balancing heuristic (prefer direction with more remaining moves)
   - If no signals green → Wait for first signal to turn green
3. **Key Innovation**: Achieves near-optimal performance using only observable information

#### Other Strategies
- **Oracular**: Perfect future signal timing knowledge, chooses minimum wait time
- **Random**: Uniform random selection among valid moves
- **Edge**: Systematic preference for eastward movement when possible

### Simulation Scale
- **Test Grid**: 3×5 big blocks (60 nodes, 104 edges, 2002 possible paths)
- **Sample Size**: 50,000 runs per strategy for statistical significance
- **Path Enumeration**: Complete enumeration of all valid trajectories

## Results and Analysis

### Path Utilization Patterns

| Strategy | Paths Used | Utilization | Most Frequent Path |
|----------|------------|-------------|-------------------|
| Random | 2002/2002 | 100.0% | Uniform exploration |
| Oracular | ~1400/2002 | ~70.0% | **Dense, focused network** |
| Signal Observer | ~1350/2002 | ~67.5% | **Dense, focused network** |
| Edge | ~800/2002 | ~40.0% | Concentrated on eastern routes |

### Key Insight: Strategy Intelligence vs Path Diversity

**Intelligent strategies (Oracular, Signal Observer) exhibit denser path networks**, using 67-70% of available paths compared to Random's 100% but achieving superior performance. This suggests:

![Path Visualization - Random Strategy](path_visualization_on_graph_strategy_random.png)
*Figure 3: Random strategy path usage. Blue numbers show node visit frequencies. Line thickness indicates path frequency, colors show performance (red=slow, green=fast).*

![Path Visualization - Signal Observer Strategy](path_visualization_on_graph_strategy_signal_observer.png)
*Figure 4: Signal Observer strategy path usage. Notice the denser, more focused network of frequently-used paths compared to random exploration.*

![Path Visualization - Oracular Strategy](path_visualization_on_graph_strategy_oracular.png)
*Figure 5: Oracular strategy path usage. Similar density to Signal Observer, confirming convergence on optimal path networks.*

1. **Focused Exploration**: Smart strategies identify and repeatedly use high-quality route subsets
2. **Adaptive Efficiency**: Path selection adapts to signal timing rather than exhaustive exploration
3. **Strategic Convergence**: Multiple intelligent approaches converge on similar optimal path networks

### Geometric Asymmetry in Random Walks

**Discovery**: Random strategy shows natural asymmetric behavior in rectangular grids (n≠m):

#### "Short Corner Bias" Phenomenon
- **Observation**: For 3×5 grid, paths preferentially route through the "short corner" (completing 3 southward moves early)
- **Mechanism**: Early completion of the shorter dimension provides maximum routing flexibility for remaining moves
- **Mathematical Basis**: Random walks naturally favor high-flexibility regions in asymmetric spaces
- **Validation**: Node visit frequencies remain symmetric (confirming no simulation bugs), while path frequencies show expected geometric bias

This validates the hypothesis that "middle paths with more routing options are more frequent" - exactly what occurs when short dimensions are completed early.

### Symmetry Verification

**Comprehensive Testing**: Implemented coordinate symmetry tests showing:
- **Average Asymmetry**: 0.7% (excellent symmetry)
- **Node Visits**: Symmetric coordinates show nearly identical visit frequencies
- **Systematic Bias Elimination**: Fixed diagonal move classification in intersection navigation

## Technical Implementation

### Bug Discovery and Resolution
**Issue**: Systematic east/south precedence in `get_valid_moves()` function created artificial bias when both directions were valid (diagonal moves within intersections).

**Solution**: Implemented random classification for diagonal moves, eliminating systematic bias while preserving geometric properties.

**Verification**: Symmetry tests confirm elimination of artificial asymmetries while preserving natural geometric patterns.

### Visualization Enhancements
1. **Path Overlay Visualization**: Color-coded performance (red=slow, green=fast) with thickness indicating frequency
2. **Node Visit Frequency Display**: Numerical overlays showing visit counts on each intersection node  
3. **Strategy Comparison Plots**: Statistical distribution visualization across multiple strategies

![Node Visit Frequencies - Symmetry Test](node_visit_frequencies.png)
*Figure 6: Detailed node visit frequency analysis on 3×3 grid showing coordinate symmetry validation. Each node displays visit count and coordinates (r,c,dx,dy).*

## Implications

### Urban Planning Insights
- **Signal Coordination**: Random phase offsets create minimal performance degradation vs coordinated signals
- **Pedestrian Behavior Modeling**: Realistic decision-making based on observable information is nearly optimal
- **Network Resilience**: Multiple high-quality routing options exist even with random signal timing

### Algorithmic Insights
- **Information Efficiency**: Current state observation is sufficient for near-optimal performance
- **Strategic Convergence**: Different intelligent approaches identify similar optimal path networks
- **Geometric Effects**: Network topology creates inherent routing preferences independent of strategy

### Future Research Directions
1. **Larger Grid Analysis**: Scale to metropolitan-sized networks
2. **Dynamic Signal Timing**: Investigate adaptive signal systems
3. **Multi-Agent Effects**: Consider pedestrian density and interaction effects
4. **Real-World Validation**: Compare with actual pedestrian GPS tracking data

## Conclusion

This analysis demonstrates that **pedestrians can achieve near-optimal navigation performance using only observable signal states**, without requiring complex prediction algorithms. The Signal Observer strategy's 99.3% efficiency relative to perfect information suggests that current traffic signal designs are reasonably well-suited to human decision-making capabilities.

The discovery of natural geometric asymmetries in random walks provides new insights into urban navigation patterns, while the dense path utilization by intelligent strategies reveals how effective routing algorithms naturally converge on optimal network subsets.

**Key Takeaway**: Simple, observation-based heuristics can achieve remarkable efficiency in complex urban navigation scenarios, with significant implications for both human behavioral modeling and automated navigation systems.