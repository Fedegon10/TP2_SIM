import numpy as np

def generar_uniforme(n, a, b):
    # Genera una cantidad 'n' de números aleatorios donde todos tienen la misma probabilidad de aparecer dentro de un rango [a, b].
    numeros = a + (b - a) * np.random.rand(n)
    return np.round(numeros, 4)