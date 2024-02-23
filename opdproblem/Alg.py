import random as rd
import networkx as nx
from .OPDproblem import OPDGraph
import matplotlib.pyplot as plt



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
        if method == 'random':
            for u, v, data in subgraph.edges(data=True):

                data['weight'] = rd.uniform(data['area'][0], data['area'][1])

        elif method == 'inf':
            for u, v, data in subgraph.edges(data=True):
                data['weight'] = data['area'][0]

        elif method == 'sup':
            for u, v, data in subgraph.edges(data=True):
                data['weight'] = data['area'][1]

        for i in range(len(list(self.graph.edges()))):

            # Find the shortest path between self.s and self.t in the subgraph
            optimal_path = nx.shortest_path(subgraph, source=self.s, target=self.t, weight='weight')
            optimal_path_edge = [(optimal_path[i], optimal_path[i + 1]) for i in range(len(optimal_path) - 1)]
            optimal_path_peso = nx.shortest_path_length(subgraph, source=self.s, target=self.t, weight='weight')

            set_edges.extend(optimal_path_edge)

            # Change weight of edges of set_edges by the real weight
            for edge in optimal_path_edge:
                subgraph[edge[0]][edge[1]]['weight'] = self.graph[edge[0]][edge[1]]['weight']
            # Calculate weigth of optimal path after reveal it
            optimal_path_weight = nx.path_weight(subgraph, optimal_path, 'weight')

            # Check if it is a self.alpha certificate
            p_opt = self.opd.optimal_path_bound(set_edges)
            print(i)
            print(optimal_path_weight, optimal_path_peso, self.alpha * p_opt[1],  p_opt[0], optimal_path_edge)
            print(set_edges)
            #########
            # Extraemos las posiciones de los nodos para un gráfico más ordenado
            pos = nx.spring_layout(subgraph)

            # Dibujamos los nodos y las aristas
            nx.draw_networkx_nodes(subgraph, pos, node_color='skyblue', node_size=500)
            nx.draw_networkx_edges(subgraph, pos, edge_color='black', arrows=True)
            nx.draw_networkx_labels(subgraph, pos)

            # Agregamos las etiquetas de los pesos
            truncated_labels = {edge: f"{weight:.0f}" for edge, weight in nx.get_edge_attributes(subgraph, 'weight').items()}
            nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=truncated_labels)

            # Mostramos el gráfico
            plt.title("Grafo con pesos")
            plt.axis('off')
            plt.show()
            #########
            if optimal_path_weight <= self.alpha*p_opt[1]:
                break
        return [set_edges, optimal_path, optimal_path_weight]
