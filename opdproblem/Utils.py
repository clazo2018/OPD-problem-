from tqdm import tqdm
from .Alg import *
from .OPDproblem import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


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
