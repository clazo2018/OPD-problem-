from itertools import combinations
import random as rd
import networkx as nx


class OPDGraph:
    """ Create an Instance of OPD problem """

    def __init__(self, n, limit_inf=1, limit_sup=100, weight_type='static', area_type='bounded_homogeneous'):
        self.n = n
        self.graph = nx.complete_graph(n)
        self.area_type = area_type
        self.weight_type = weight_type
        # Generate random uncertainty areas for edges and assign weights
        for u, v in self.graph.edges():
            # Generate random start and end points for the interval
            if self.area_type == 'bounded_homogeneous':
                self.graph[u][v]['area'] = (limit_inf, limit_sup)

            elif self.area_type == 'bounded_non_homogeneous':
                start = rd.uniform(limit_inf, limit_sup) + rd.uniform(0, 50)
                end = start + rd.uniform(0, 50)

                # assign area
                self.graph[u][v]['area'] = (start, end)

            elif self.area_type == 'unbounded_non_homogeneous':
                self.graph[u][v]['area'] = (rd.uniform(limit_inf, limit_sup), limit_sup)

            # assign weight
            if weight_type == 'static':
                # Generate a random number within the interval and assign it as weight

                weight = rd.uniform(self.graph[u][v]['area'][0], self.graph[u][v]['area'][1])
                self.graph[u][v]['weight'] = weight
            if weight_type == 'dynamic':
                # Generate a random number within the interval and assign it as weight
                self.graph[u][v]['weight'] = None

    def adversary(self, set_edges, s=0, t=1):

        G_s = {s}
        G_t = {t}

        g = {}
        eps = (self.graph[s][t]['area'][0] + self.graph[s][t]['area'][1]) / 2
        b = (eps + self.graph[s][t]['area'][1]) / 2
        gamma = (b + self.graph[s][t]['area'][1]) / 2  # alpha *

        st_set = {s, t}
        for v in (self.graph.nodes() - st_set):
            g[f'{v}'] = float('-inf')
        g[f'{s}'] = s
        g[f'{t}'] = t
        graph_uncovered = nx.Graph()
        graph_uncovered.add_nodes_from(self.graph.nodes)

        for e in set_edges:
            if e == (s, t):
                self.graph[e[0]][e[1]]['weight'] = b

            elif e[0] == s:
                if g[f'{e[1]}'] == float('-inf'):
                    self.graph[e[0]][e[1]]['weight'] = eps
                    g[f'{e[1]}'] = s
                    G_s = G_s.union([e[1]])
                    graph_uncovered.add_edge(*e)

                elif g[f'{e[1]}'] == t:
                    self.graph[e[0]][e[1]]['weight'] = gamma

            elif e[0] == t:
                if g[f'{e[1]}'] == float('-inf'):
                    self.graph[e[0]][e[1]]['weight'] = eps
                    g[f'{e[1]}'] = t
                    G_t = G_t.union([e[1]])
                    graph_uncovered.add_edge(*e)

                elif g[f'{e[1]}'] == s:
                    self.graph[e[0]][e[1]]['weight'] = gamma
            elif e[0] not in st_set:
                if g[f'{e[0]}'] == g[f'{e[1]}'] == float('-inf'):
                    self.graph[e[0]][e[1]]['weight'] = eps
                    graph_uncovered.add_edge(*e)

                elif g[f'{e[0]}'] == float('-inf') and (g[f'{e[1]}'] in st_set):
                    self.graph[e[0]][e[1]]['weight'] = eps
                    g[f'{e[0]}'] = g[f'{e[1]}']
                    nodes_path = set()
                    graph_uncovered.add_edge(*e)
                    for u in graph_uncovered.nodes:
                        if nx.has_path(graph_uncovered, u, e[0]):
                            nodes_path.add(u)
                    for v in nodes_path:
                        g[f'{v}'] = g[f'{e[1]}']

                    if g[f'{e[1]}'] == s:
                        G_s = G_s.union(e[0])
                        G_s = G_s.union(nodes_path)
                    else:
                        G_t = G_t.union(e[0])
                        G_t = G_t.union(nodes_path)

                elif g[f'{e[1]}'] in (st_set.difference([g[f'{e[1]}']])):
                    self.graph[e[0]][e[1]]['weight'] = gamma
                else:
                    self.graph[e[0]][e[1]]['weight'] = eps
                    graph_uncovered.add_edge(*e)

    def proposed_path(self, set_edges, s=0, t=1):
        """

        Search a proposed path in the set of edges set_edges

        :param s: an int, the source node for the path
        :param t: an int, the target node for the path
        :param set_edges: a list, set where you want to find the path
        :return: a list and float, proposed path and weight of proposed path, or
                 none, none if the optimal path does not exist
        """

        # Create an uncovered_graph with the set of edges
        uncovered_graph = nx.Graph()
        aux_graph = self.graph.edge_subgraph(set_edges).copy()
        uncovered_graph.add_nodes_from(list(self.graph.nodes()))
        uncovered_graph.add_edges_from(aux_graph.edges(data=True))

        # Find the shortest path between s and t in the uncovered_graph
        try:
            proposed_path = nx.shortest_path(uncovered_graph, source=s, target=t, weight='weight')
            proposed_path_weight = nx.shortest_path_length(uncovered_graph, source=s, target=t, weight='weight')
            return proposed_path, proposed_path_weight
        except nx.NetworkXNoPath:
            # There is no path between s and t in the uncovered_graph
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

        min_graph = self.graph.copy()

        # Assign as weight the lower bound of the area to those I do not know
        for u, v, data in min_graph.edges(data=True):
            data['weight'] = data['area'][0]
        # Assign real weight those I know
        for u, v in set_edges:
            min_graph[u][v]['weight'] = self.graph[u][v]['weight']

        # Calculate optimal path in min graph
        proposed_path = nx.shortest_path(min_graph, source=s, target=t, weight='weight')
        proposed_path_weight = nx.shortest_path_length(min_graph, source=s, target=t, weight='weight')

        return proposed_path, proposed_path_weight

    def certificate(self, set_edges, proposed_path_weight, alpha=1):

        """
        Check if set_edges is alpha-certificate alpha

        :param set_edges: an int, set where you want to find the path
        :param proposed_path_weight: a float, weight of proposed path
        :param alpha: a float, factor of alpha-certificate

        :return: bool, return true if set edges is alpha-certificate
        """

        p_bound = self.optimal_path_bound(set_edges)
        if proposed_path_weight <= alpha * p_bound[1]:
            return True
        else:
            return False

    def min_certificate(self, s=0, t=1, alpha=1):
        """
        Calculate the minimum alpha-certificate on the graph

        :param s: an int, the source node for the path
        :param t: an int, the target node for the path
        :param alpha: a float, factor of alpha-certificate

        :return l_aux: a list, alpha-certificate edge list
        """
        optimal_path = nx.shortest_path(self.graph, source=s, target=t, weight='weight')
        optimal_path_weight = nx.shortest_path_length(self.graph, source=s, target=t, weight='weight')

        edges_certificate = [(optimal_path[i], optimal_path[i + 1]) for i in range(len(optimal_path) - 1)]
        edges_certificate = [(min(u, v), max(u, v)) for u, v in edges_certificate]
        edges_graph = list(self.graph.edges())

        for i in range(1, len(edges_graph) + 1):
            for test in combinations(edges_graph, i):
                # Create list to test certificate
                cert_test = set(edges_certificate)
                cert_test.update(test)
                l_aux = list(cert_test)

                # Test certificate
                certificate = self.certificate(l_aux, optimal_path_weight, alpha)

                if certificate:
                    return l_aux
