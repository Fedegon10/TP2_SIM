import numpy as np
import pandas as pd

def calcular_frecuencias(numeros, num_intervalos):
    """
    Calcula la tabla de frecuencias para una serie de números dada.
    
    Retorna:
        - Un DataFrame de pandas con la tabla de frecuencias.
        - Los límites de los intervalos para usar en el histograma.
    """
    # Usamos np.histogram para obtener las frecuencias y los límites de los intervalos
    frec_observada, limites = np.histogram(numeros, bins=num_intervalos)
    
    # Creamos las etiquetas para los intervalos (ej: "[0.50 - 1.25)")
    intervalos = []
    marcas_clase = []
    for i in range(len(limites) - 1):
        lim_inf = round(limites[i], 4)
        lim_sup = round(limites[i+1], 4)
        intervalos.append(f"[{lim_inf}, {lim_sup})")
        marcas_clase.append(round((lim_inf + lim_sup) / 2, 4))

    # Creamos la tabla con pandas
    tabla = pd.DataFrame({
        'Intervalo': intervalos,
        'Marca de Clase (xi)': marcas_clase,
        'Frecuencia Observada (fo)': frec_observada
    })
    
    return tabla, limites