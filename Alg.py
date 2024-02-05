import random as rd
import networkx as nx
import OPDproblem


class Alg(OPDproblem):
    def search_app(self, set_edges, method='min', s=0, t=1):
        """

        Search a Search alph-aproximation in the set of edges set_edges

        :param method: a string, method to create subgraph
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
        for edge in subgraph.edges():
            if method == 'random':
                subgraph[edge[0]][edge[1]]['weight'] = rd.uniform(subgraph[edge[0]][edge[1]]['area'][0],
                                                                  subgraph[edge[0]][edge[1]]['area'][1])

            elif method == 'inf':
                subgraph[edge[0]][edge[1]]['weight'] = subgraph[edge[0]][edge[1]]['area'][0]

            elif method == 'sup':
                subgraph[edge[0]][edge[1]]['weight'] = subgraph[edge[0]][edge[1]]['area'][1]

        # Find the shortest path between s and t in the subgraph
        try:
            optimal_path = nx.shortest_path(subgraph, source=s, target=t, weight='weight')
            optimal_path_weight = nx.shortest_path_length(subgraph, source=s, target=t, weight='weight')
            return optimal_path, optimal_path_weight
        except nx.NetworkXNoPath:
            # There is no path between s and t in the subgraph
            print("There is no path between s and t in set.")