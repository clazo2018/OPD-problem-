import random as rd
from typing import Tuple

import networkx as nx
import OPDproblem


class Alg(OPDproblem):

    def search_app(self, method='min', alpha=1, s=0, t=1):
        """

        Search an alpha-approximation in the set of edges set_edges

        :param alpha: an int, alpha of alpha approximation
        :param method: a string, method to create subgraph
        :param s: an int, the source node for the path
        :param t: an int, the target node for the path
        :return: a list and float, proposed path and weight of proposed path, or
                 none, none if the optimal path does not exist
        """
        set_edges = []  # revealed edges

        # Create a subgraph with the set of edges
        subgraph = self.graph.copy()  # Change name

        for sub_edge in subgraph.edges():
            if method == 'random':
                subgraph[sub_edge[0]][sub_edge[1]]['weight'] = rd.uniform(subgraph[sub_edge[0]][sub_edge[1]]
                                                                          ['area'][0], subgraph[sub_edge[0]]
                                                                          [sub_edge[1]]['area'][1])

            elif method == 'inf':
                subgraph[sub_edge[0]][sub_edge[1]]['weight'] = subgraph[sub_edge[0]][sub_edge[1]]['area'][0]

            elif method == 'sup':
                subgraph[sub_edge[0]][sub_edge[1]]['weight'] = subgraph[sub_edge[0]][sub_edge[1]]['area'][1]

        while True:

            # Find the shortest path between s and t in the subgraph
            optimal_path = nx.shortest_path(subgraph, source=s, target=t, weight='weight')
            optimal_path_weight = nx.shortest_path_length(subgraph, source=s, target=t, weight='weight')

            set_edges.append(optimal_path)

            # Check if it is an alpha certificate
            p_opt = self.optimal_path_bound(self, set_edges)
            if optimal_path_weight <= alpha*p_opt[1]:
                return optimal_path, optimal_path_weight

            # Change weight of edges of set_edges by the real weight
            for edge in set_edges:
                subgraph[edge[0]][edge[1]]['weight'] = self.graph[edge[0]][edge[1]]['weight']




