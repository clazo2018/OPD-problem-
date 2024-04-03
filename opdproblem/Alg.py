import random as rd
import networkx as nx
from .OPDproblem import OPDGraph
import matplotlib.pyplot as plt


class Alg:
    def __init__(self, opd: OPDGraph, alpha=1, s=0, t=1):
        self.graph = opd.graph.copy()
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
        graph = self.graph.copy()
        subgraph = graph.copy()  # Change name
        if method == 'random1':
            for u, v, data in subgraph.edges(data=True):
                data['weight'] = rd.uniform(data['area'][0], data['area'][1])

        elif method == 'inf':
            for u, v, data in subgraph.edges(data=True):
                data['weight'] = data['area'][0]

        i = 0
        while len(set(set_edges)) != len(graph.edges()):
            if method == 'random1':
                optimal_path = nx.shortest_path(subgraph, source=self.s, target=self.t, weight='weight')
                optimal_path_edge = [(min(optimal_path[i], optimal_path[i + 1]),
                                      max(optimal_path[i], optimal_path[i + 1])) for i in range(len(optimal_path) - 1)]
                # Reassign weight of edges if repeat optimal path
                if i != 0:
                    while set(optimal_path_edge) == set(previous_optimal_path_edge):
                        revealed_edges = set(set_edges)
                        for u, v, data in subgraph.edges(data=True):
                            if (u, v) not in revealed_edges and (v, u) not in revealed_edges:
                                data['weight'] = rd.uniform(data['area'][0], data['weight'])

                        optimal_path = nx.shortest_path(subgraph, source=self.s, target=self.t, weight='weight')
                        optimal_path_edge = [(min(optimal_path[i], optimal_path[i + 1]),
                                              max(optimal_path[i], optimal_path[i + 1]))
                                             for i in range(len(optimal_path) - 1)]

                previous_optimal_path_edge = optimal_path_edge

                set_edges.extend(optimal_path_edge)

                if self.opd.weight_type == 'dynamic':
                    self.opd.adversary(optimal_path_edge)

                # Change weight of edges of set_edges by the real weight
                for edge in optimal_path_edge:
                    subgraph[edge[0]][edge[1]]['weight'] = self.opd.graph[edge[0]][edge[1]]['weight']

                # Calculate weigth of optimal path after reveal it
                proposed_path, proposed_path_weight = self.opd.proposed_path(set_edges)

                # Check if it is a self.alpha certificate
                p_opt = self.opd.optimal_path_bound(set_edges)

                if proposed_path_weight <= self.alpha * p_opt[1]:
                    return list(set(set_edges))
                i += 1

            elif 'inf':
                # Find the shortest path between self.s and self.t in the subgraph
                optimal_path = nx.shortest_path(subgraph, source=self.s, target=self.t, weight='weight')
                optimal_path_edge = [(min(optimal_path[i], optimal_path[i + 1]),
                                      max(optimal_path[i], optimal_path[i + 1])) for i in range(len(optimal_path) - 1)]

                set_edges.extend(optimal_path_edge)

                # Change weight of edges of set_edges by the real weight
                if self.opd.weight_type == 'dynamic':
                    self.opd.adversary(optimal_path_edge)
                for edge in optimal_path_edge:

                    subgraph[edge[0]][edge[1]]['weight'] = self.opd.graph[edge[0]][edge[1]]['weight']

                # Calculate weigth of optimal path after reveal it
                proposed_path, proposed_path_weight = self.opd.proposed_path(set_edges)

                # Check if it is a self.alpha certificate
                p_opt = self.opd.optimal_path_bound(set_edges)
                if proposed_path_weight <= self.alpha*p_opt[1]:
                    return list(set(set_edges))

    def both_alg(self):
        graph_uncovered = nx.Graph()
        graph_uncovered.add_nodes_from(self.graph.nodes)
        m_s = set()
        m_t = set()
        p_su = {}
        p_ut = {}
        s_aux = self.s
        t_aux = self.t
        approx = float('inf')
        set_edges = []

        while approx > self.alpha:
            m_s.add(s_aux)
            m_t.add(t_aux)

            diff_set = m_t.union(m_s)
            # edges reveled
            if self.opd.weight_type == 'dynamic':
                self.opd.adversary([(s_aux, t_aux)])
            graph_uncovered.add_edge(s_aux, t_aux, weight=self.opd.graph[s_aux][t_aux]['weight'])
            set_edges.append((s_aux, t_aux))
            for u in (graph_uncovered.nodes() - diff_set):
                if self.opd.weight_type == 'dynamic':
                    self.opd.adversary([(s_aux, u)])
                graph_uncovered.add_edge(s_aux, u, weight=self.opd.graph[s_aux][u]['weight'])
                set_edges.append((s_aux, u))

            for v in (graph_uncovered.nodes() - diff_set):
                if self.opd.weight_type == 'dynamic':
                    self.opd.adversary([(t_aux, v)])
                graph_uncovered.add_edge(v, t_aux, weight=self.opd.graph[s_aux][v]['weight'])
                set_edges.append((t_aux, v))

            # Optimal path from s to t containing only uncovered edges.
            p_prop = nx.shortest_path(graph_uncovered, source=self.s, target=self.t, weight='weight')
            p_prop_edge = [(min(p_prop[i], p_prop[i + 1]), max(p_prop[i], p_prop[i + 1]))
                           for i in range(len(p_prop) - 1)]
            # Optimal path from s to u containing only uncovered edges.
            for u in (graph_uncovered.nodes() - diff_set):

                # Compute the optimal su-path containing only uncovered edges
                p_su[f'{u}'] = nx.shortest_path_length(graph_uncovered, source=self.s, target=u, weight='weight')

                # Compute the optimal ut-path containing only uncovered edges
                p_ut[f'{u}'] = nx.shortest_path_length(graph_uncovered, source=u, target=self.t, weight='weight')
            s_aux = min(p_su, key=lambda x: p_su[x])
            t_aux = min(p_ut, key=lambda x: p_ut[x])
            p_prop_weight = 0

            # Calculate weight of p_prop
            for arista in p_prop_edge:
                p_prop_weight += graph_uncovered.get_edge_data(*arista)['weight']

            approx = p_prop_weight / (p_su[f'{s_aux}'] + p_ut[f'{t_aux}'])

        return set_edges
