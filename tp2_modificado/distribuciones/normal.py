import numpy as np

def generar_normal(n, media, desviacion):
    # Genera 'n' números aleatorios que se agrupan alrededor de un valor central (la media), formando la  "Campana de Gauss".
    if desviacion <= 0:
        raise ValueError("La desviación estándar debe ser un número positivo.")
        
    numeros = np.random.normal(media, desviacion, n)
    return np.round(numeros, 4)