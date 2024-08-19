from tqdm import tqdm
from .Alg import *
from .OPDproblem import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import networkx as nx
import numpy as np
import plotly.graph_objects as go

def exp_alg(n_clique, n_instance, limit_inf=0, limit_sup=100, weight_type='static', area_type='bounded_non_homogeneous'):
    both = []
    inf = []
    random = []
    clique = []
    l_opd = []

    for n in tqdm(range(4, n_clique + 1), desc='Procesando clique', unit='clique'):
        #    print(f'es el grafo  k{n}')
        #     print('+' * 10)
        for i in range(n_instance):
            # print('es la instancia: ', i)
            # print('-' * 10)

            # se inicializa el grafo y el algoritmo
            opd = OPDGraph(n=n, limit_inf=limit_inf, limit_sup=limit_sup, weight_type=weight_type, area_type=area_type)
            search = Alg(opd)

            # Se busca el alpha-certificado
            search_inf = search.search_app(method='inf')
            search_random = search.search_app(method='random1')
            search_both = search.both_alg()

            both.append(search_both)
            inf.append(search_inf)
            random.append(search_random)
            l_opd.append(opd)
        l_aux = [f'k{n}'] * n_instance
        clique.extend(l_aux)
    cert_dict = {'clique': clique, 'inf': inf, 'random': random, 'both': both, 'opd': l_opd}

    return pd.DataFrame(cert_dict)


def bar_plot(df, clique='k4'):
    # Inicializar el plot con subplots
    fig, axes = plt.subplots(3, 1, figsize=(10, 18))

    # Iterar sobre cada columna y generar un gráfico de barras para cada una
    for i, column in enumerate(['inf', 'random', 'both']):
        # Contar el número de elementos en la columna para cada fila
        counts = df[df['clique'] == clique][column].apply(len)
        # Contar el número de veces que se repite cada cantidad de elementos
        counts = counts.value_counts().sort_index()
        # Crear el gráfico de barras
        counts.plot(kind='bar', color='purple', ax=axes[i])
        axes[i].set_title('Tamaño del certificado para "{}"'.format(column))
        axes[i].set_xlabel('Cantidad de aristas del certificado')
        axes[i].set_ylabel('Frecuencia')
        axes[i].grid(axis='y', linestyle='--', alpha=0.7)

        # Agregar el valor numérico a cada barra
        for index, value in enumerate(counts):
            axes[i].text(index, value + 0.1, str(value), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()


def box_plot(df_list: list, colors=('#1f77b4', '#2ca02c', '#d8dcd6')):
    colors2 = ('orange', 'red', 'purple')
    plt.figure(figsize=(15, 7))
    l_bp = []
    for i, df in enumerate(df_list):
        # Graficar boxplot para el primer dataframe
        l_bp.append(plt.boxplot(df, showmeans=True, showfliers=False, positions=range(1, len(df.columns) + 1),
                                patch_artist=True,
                                boxprops=dict(facecolor=colors[i], alpha=0.7),
                                whiskerprops=dict(color=colors[i]),
                                capprops=dict(color=colors[i]),
                                meanprops=dict(marker='D', markerfacecolor=colors2[i], markeredgecolor=colors2[i]),
                                medianprops=dict(color=colors2[i]),
                                ))

    plt.title('Boxplots de algoritmos')
    plt.xlabel('Clique')
    plt.ylabel('Tamaño del certificado')
    plt.grid(True)

    # Etiquetas de los ticks en el eje x
    plt.xticks(range(1, len(df_list[0].columns) + 1), df_list[0].columns)

    # Crear etiquetas para la leyenda
    legend_labels = ['A. inf', 'A. random', 'A. both']
    mean_labels = ['Media (' + label + ')' for label in legend_labels]
    median_labels = ['Mediana (' + label + ')' for label in legend_labels]

    # Añadir las leyendas de media y mediana
    plt.legend([l_bp[0]["boxes"][0], l_bp[1]["boxes"][0], l_bp[2]["boxes"][0],
                l_bp[0]["means"][0], l_bp[1]["means"][0], l_bp[2]["means"][0],
                l_bp[0]["medians"][0], l_bp[1]["medians"][0], l_bp[2]["medians"][0]],
               legend_labels + mean_labels + median_labels)

    plt.show()

def plot_opd_graph(opd):
    """
    Dibuja el grafo con los pesos y áreas de las aristas redondeados a dos decimales.
    
    :param graph: Un objeto de tipo networkx.Graph.
    """
    # Redondear los pesos a dos decimales
    graph = opd.graph
    for u, v in graph.edges():
        graph[u][v]['weight'] = round(graph[u][v]['weight'], 2)

    # Redondear las áreas a dos decimales
    for u, v in graph.edges():
        area_start, area_end = graph[u][v]['area']
        graph[u][v]['area'] = (round(area_start, 2), round(area_end, 2))

    # Obtener los pesos y áreas de las aristas
    weights = [graph[u][v]['weight'] for u, v in graph.edges()]
    areas = [graph[u][v]['area'] for u, v in graph.edges()]

    # Dibujar el grafo con más espacio entre nodos
    plt.figure(figsize=(8, 8))
    pos = nx.circular_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000)

    # Ajustar las etiquetas de peso para que no se superpongan
    nx.draw_networkx_edge_labels(graph, pos, edge_labels={(u, v): f"Weight: {graph[u][v]['weight']}\nArea: {graph[u][v]['area']}" for u, v in graph.edges()}, 
                                 label_pos=0.5, font_size=8)
    
    # Mostrar la gráfica
    plt.title('Grafo con pesos e intervalos')
    plt.show()

def plot_opd_graph_3d(opd):
    """
    Dibuja el grafo con los pesos y áreas de las aristas redondeados a dos decimales usando Plotly en 3D.
    
    :param opd: Un objeto de tipo OPDGraph.
    """
    graph = opd.graph

    # Redondear los pesos a dos decimales
    for u, v, data in graph.edges(data=True):
        data['weight'] = round(data.get('weight', 0), 2)
        area_start, area_end = data.get('area', (0, 0))
        data['area'] = (round(area_start, 2), round(area_end, 2))

    # Obtener las posiciones de los nodos en 3D
    pos = nx.spring_layout(graph, dim=3)
    x_nodes = np.array([pos[node][0] for node in graph.nodes()])
    y_nodes = np.array([pos[node][1] for node in graph.nodes()])
    z_nodes = np.array([pos[node][2] for node in graph.nodes()])

    # Crear listas para los datos de las aristas
    x_edges = []
    y_edges = []
    z_edges = []
    edge_texts = []

    for u, v, data in graph.edges(data=True):
        x_edge = [pos[u][0], pos[v][0]]
        y_edge = [pos[u][1], pos[v][1]]
        z_edge = [pos[u][2], pos[v][2]]
        x_edges.extend(x_edge)
        y_edges.extend(y_edge)
        z_edges.extend(z_edge)
        
        # Crear texto para la etiqueta de la arista
        label = f"Weight: {data['weight']}<br>Area: {data['area']}"
        mid_point = [(pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2, (pos[u][2] + pos[v][2]) / 2]
        edge_texts.append(mid_point)

    # Crear trazas para nodos y aristas
    edge_trace = go.Scatter3d(
        x=x_edges,
        y=y_edges,
        z=z_edges,
        mode='lines',
        line=dict(width=0.5, color='#888')
    )

    node_trace = go.Scatter3d(
        x=x_nodes,
        y=y_nodes,
        z=z_nodes,
        mode='markers+text',
        marker=dict(size=5, color='skyblue'),
        text=[node for node in graph.nodes()],
        textposition="bottom center"
    )

    # Trazas para las etiquetas de las aristas
    edge_labels_trace = go.Scatter3d(
        x=[p[0] for p in edge_texts],
        y=[p[1] for p in edge_texts],
        z=[p[2] for p in edge_texts],
        mode='text',
        text=[f"Weight: {data['weight']}<br>Area: {data['area']}" for _, _, data in graph.edges(data=True)],
        textposition='top center'
    )

    fig = go.Figure(data=[edge_trace, node_trace, edge_labels_trace],
                    layout=go.Layout(
                        title="Grafo en 3D",
                        showlegend=False,
                        scene=dict(
                            xaxis_title='X',
                            yaxis_title='Y',
                            zaxis_title='Z'
                        )
                    ))

    fig.show()