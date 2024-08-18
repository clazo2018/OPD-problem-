import opdproblem as opd
import pandas as pd
import joblib
from tqdm import tqdm
import time

# Cargar DataFrame desde el archivo
df_bounded_homogeneous = joblib.load('df_bounded_homogeneous.pkl')

cliques = df_bounded_homogeneous['clique'].unique()
cliques = cliques[4:]

dfclique_list = []
# Límite de tiempo en segundos para cada iteración
limite_tiempo_iteracion = 50000  # Por ejemplo, 1 hora

for clique in tqdm(cliques, desc='Procesando clique', unit='clique'):
    tiempo_inicio_iteracion = time.time()

    df = df_bounded_homogeneous[df_bounded_homogeneous['clique'] == clique].copy()
    # Calculo de beta para cada alg
    df.loc[:, 'min_certificate'] = df.apply(lambda row: row['opd'].min_certificate(), axis=1)
    # Tiempo transcurrido en la iteración
    dfclique_list.append(df)

    tiempo_transcurrido = time.time() - tiempo_inicio_iteracion

    # Guardar archivo
    df_concatenado = pd.concat(dfclique_list)
    joblib.dump(df_concatenado, 'dataframes_min/df_bounded_homogeneous_2.pkl')
    print(tiempo_transcurrido)

    # Verificar si se ha superado el límite de tiempo
    if tiempo_transcurrido > limite_tiempo_iteracion:
        print(f"Se ha superado el límite de tiempo en el clique {clique}")
        break
