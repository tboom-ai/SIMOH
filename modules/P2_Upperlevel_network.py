import networkx as nx
import matplotlib.pyplot as plt
import math
import P1_BIM as BIM

class NodeLocator:
    def __init__(self, nodes):
        """Initialize the locator with a dictionary of nodes."""
        self.nodes = nodes

    def calculate_distance(self, location, node):
        """Calculate the Euclidean distance between the given location and a node."""
        x1, y1 = location
        x2, y2 = self.nodes[node]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def find_closest_node(self, location):
        """Find the closest node to the given location."""
        closest_node = None
        min_distance = float('inf')

        for node in self.nodes:
            distance = self.calculate_distance(location, node)
            if distance < min_distance:
                min_distance = distance
                closest_node = node

        return closest_node, self.nodes[closest_node], min_distance

class GraphAnalyzer:
    def __init__(self, nodes, connections):
        """Initialize the graph with nodes and connections."""
        self.G = nx.Graph()
        self.add_nodes(nodes)
        self.add_connections(connections)

    def add_nodes(self, nodes):
        """Add nodes with coordinates to the graph."""
        for node_id, coord in nodes.items():
            self.G.add_node(node_id, coord=coord)  # Store node with its coordinates

    def add_connections(self, connections):
        """Add connections (edges) to the graph."""
        for node, conn_list in connections:
            for conn in conn_list:
                if len(conn) > 1:  # Ensure connection has both target node and weight
                    target_node, weight = conn
                    self.G.add_edge(node, target_node, weight=weight)

    def find_shortest_path(self, source, target):
        """Find and return the shortest path between two nodes."""
        if nx.has_path(self.G, source, target):
            shortest_path = nx.shortest_path(self.G, source=source, target=target, weight='weight')
            return shortest_path
        else:
            return None

# For local usage
if __name__ == "__main__":
    # Initialize the graph with nodes and connections from the mockup
    graph_analyzer = GraphAnalyzer(BIM.nodes, BIM.connections_list)

    # Define source and target nodes
    source = 0  # Starting node
    target = 19  # Target node

    # Find the shortest path
    shortest_path = graph_analyzer.find_shortest_path(source, target)
    if shortest_path:
        print(f"The shortest path from node {source} to node {target} is: {shortest_path}")
    else:
        print(f"No path exists between node {source} and node {target}.")