Prompt 1:

I have the following fun question: what is the optimal strategy for walking in a manhattan-grid like sidewalk system, when there's (for now) random pedestrian traffic signals to stop or walk at each grid intersection point? 
Consider a rectangular lattice of n x m points, each one unit distance from the adjacent nodes, and a pedestrian's goal is to get from the origin to the point (n,m) via traversing the edges. However, each node is not a single point, but like a street intersection, could be modelled by a subgraph with four nodes, connected in a square (each edge crossing is a street crossing). At these intersection subgraphs, there's a random probability that for one unit time (the same it takes to cross the nxm graph, the supergraph's edges) the pedestrian cannot cross. For now, let's model each of these random pedestrian stop and go signals as a 1 second on 1 second off continuous wave with a random starting time in [0,1). 
Critically, at each subgraph, before any streets are crossed, the pedestrian MUST choose to go either right (towards higher column number m but not actually incrementing it, we're in the subgraph) or down (higher row number n), but then, has a choice of either crossing again (to the opposite street corner) OR then progressing to the next grid point.
Thus there's a strategy I think will be faster: biasing towards middle edges in the supergraph as opposed to hugging the edges, since this will prevent circumstances in which there's not as many opportunities for either going down in the subgraph or going across.


Prompt 2:

This is my intuition, but doesn't capture the entire scenario. Let's make a slightly better model. Instead of subgraphs and supergraphs, let's have one graph with two edge types: street crossings (s) and along a block (b). The total graph is an n x m grid of 2 x 2, so 2n x 2m total nodes. The nodes are connected in a pattern where the 2x2 are internally connected by (s) and ALSO connect to the next 2x2 grid by (b), but only with corresponding 2x2 node positions: the top right point in this street crossing is connected via a (b) edge to the top LEFT point in the street crossing one unit right, etc. 


