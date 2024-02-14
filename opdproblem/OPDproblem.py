import random as rd
import networkx as nx


class OPDGraph:
    """ Create an Instance of OPD problem """

    def __init__(self, n, limit_inf=0, limit_sup=10, seed=None):
        self.n = n
        self.graph = nx.complete_graph(n)
        self.seed = seed
        if self.seed is not None:
            rd.seed(self.seed)
        # Generate random uncertainty areas for edges and assign weights
        for u, v in self.graph.edges():
            # Generate random start and end points for the interval
            start = rd.uniform(limit_inf, limit_sup) + rd.uniform(0, 5)
            end = start + rd.uniform(0, 5)

            # Generate a random number within the interval and assign it as weight
            weight = rd.uniform(start, end)

            # assign area
            self.graph[u][v]['area'] = (start, end)

            # assign weight
            self.graph[u][v]['weight'] = weight

    def proposed_path(self, set_edges, s=0, t=1):
        """

        Search a proposed path in the set of edges set_edges

        :param s: an int, the source node for the path
        :param t: an int, the target node for the path
        :param set_edges: a list, set where you want to find the path
        :return: a list and float, proposed path and weight of proposed path, or
                 none, none if the optimal path does not exist
        """

        # Create a subgraph with the set of edges
        subgraph = nx.Graph()
        H = self.graph.edge_subgraph(set_edges).copy()
        subgraph.add_nodes_from(list(self.graph.nodes()))
        subgraph.add_edges_from(H.edges(data=True))

        # Find the shortest path between s and t in the subgraph
        try:
            optimal_path = nx.shortest_path(subgraph, source=s, target=t, weight='weight')
            optimal_path_weight = nx.shortest_path_length(subgraph, source=s, target=t, weight='weight')
            return optimal_path, optimal_path_weight
        except nx.NetworkXNoPath:
            # There is no path between s and t in the subgraph
            return None, None

    def optimal_path_bound(self, set_edges, s=0, t=1):
        """

         Search a proposed path in the set of edges set_edges

         :param s: an int, the source node for the path
         :param t: an int, the target node for the path
         :param set_edges: a list, set where you want to find the path
         :return: a list and float, proposed path and weight of proposed path, or
                  none, none if the optimal path does not exist
         """

        graph_min = self.graph.copy()

        # Assign as weight the lower bound of the area to those I do not know
        print(list(self.graph.edges()))
        for edge in list(self.graph.edges()):
            if edge not in set_edges:
                graph_min[edge[0]][edge[1]]['weight'] = graph_min[edge[0]][edge[1]]['area'][0]

        optimal_path = nx.shortest_path(graph_min, source=s, target=t, weight='weight')
        optimal_path_bound = nx.shortest_path_length(graph_min, source=s, target=t, weight='weight')

        return optimal_path, optimal_path_bound




