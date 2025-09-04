import numpy as np

def generar_exponencial(n, media):
    # Genera 'n' números aleatorios que tienden a agruparse en valores bajos. 
    if media <= 0:
        raise ValueError("La media debe ser un número positivo.")
    
    numeros = -media * np.log(1 - np.random.rand(n))
    return np.round(numeros, 4)