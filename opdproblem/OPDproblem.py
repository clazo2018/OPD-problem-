import random as rd
import networkx as nx


class OPDGraph:
    """ Create an Instance of OPD problem """

    def __init__(self, n, limit_inf=0, limit_sup=100, weight_type='static'):
        self.n = n
        self.graph = nx.complete_graph(n)
        self.start = []
        self.weight_type = weight_type
        # Generate random uncertainty areas for edges and assign weights
        for u, v in self.graph.edges():
            # Generate random start and end points for the interval
            start = rd.uniform(limit_inf, limit_sup) + rd.uniform(0, 50)
            end = start + rd.uniform(0, 50)

            # assign area
            self.graph[u][v]['area'] = (start, end)

            # assign weight
            if weight_type == 'static':
                # Generate a random number within the interval and assign it as weight
                weight = rd.uniform(start, end)
                self.graph[u][v]['weight'] = weight

    def adversary(self, set_ed):
        pass



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
        for u, v, data in graph_min.edges(data=True):
            data['weight'] = data['area'][0]
        for u, v in set_edges:
            graph_min[u][v]['weight'] = self.graph[u][v]['weight']

        optimal_path = nx.shortest_path(graph_min, source=s, target=t, weight='weight')
        optimal_path_bound = nx.shortest_path_length(graph_min, source=s, target=t, weight='weight')

        return optimal_path, optimal_path_bound

    def certificate(self, set_edges, proposed_path_weight, alpha=1):

        p_bound = self.optimal_path_bound(set_edges)
        if proposed_path_weight <= alpha * p_bound[1]:
            return True
        else:
            return False

    def min_certificate(self, s=0, t=1):
        optimal_path = nx.shortest_path(self.graph, source=s, target=t, weight='weight')
        optimal_path_weight = nx.shortest_path_length(self.graph, source=s, target=t, weight='weight')

        edges_certificate = [(optimal_path[i], optimal_path[i + 1]) for i in range(len(optimal_path) - 1)]
        edges_graph = list(self.graph.edges())
        len_iter = len(edges_graph) - len(edges_certificate)
        for i in range(1, len_iter + 1):
            for edge in range(0, len_iter, i):
                # Create list to test certificate

                l_aux = edges_certificate.copy()
                edge_test = edges_graph[edge: edge+i]
                set_aux = set(l_aux) | set(edge_test)
                l_aux = list(set_aux)

                # Test certificate
                certificate = self.certificate(l_aux, optimal_path_weight)

                if certificate:
                    return l_aux










