import random as rd
import networkx as nx
from .OPDproblem import OPDGraph


class Alg:
    def __init__(self, opd: OPDGraph, alpha=1, s=0, t=1):
        self.graph = opd.graph
        self.alpha = alpha
        self.opd = opd
        self.s = s
        self.t = t

    def search_app(self, method='inf'):
        """

        Search an alpha-approximation in the set of edges set_edges

        :param method: a string, method to create subgraph
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

        while True: # Cambiar por un for de todas las aristas

            # Find the shortest path between self.s and self.t in the subgraph
            optimal_path = nx.shortest_path(subgraph, source=self.s, target=self.t, weight='weight')
            optimal_path_weight = nx.shortest_path_length(subgraph, source=self.s, target=self.t, weight='weight')
            optimal_path = [(optimal_path[i], optimal_path[i + 1]) for i in range(len(optimal_path) - 1)]
            set_edges.append(optimal_path)

            # Check if it is a self.alpha certificate
            p_opt = self.opd.optimal_path_bound(set_edges)
            if optimal_path_weight <= self.alpha*p_opt[1]:
                break

            # Change weight of edges of set_edges by the real weight
            for edge in set_edges:
                subgraph[edge[0]][edge[1]]['weight'] = self.graph[edge[0]][edge[1]]['weight']

        return [set_edges, optimal_path, optimal_path_weight]
