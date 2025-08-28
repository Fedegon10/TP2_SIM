import numpy as np

def generar_uniforme(n, a, b):
    """
    Genera n números aleatorios con distribución uniforme U(a, b).
    Fórmula: X = a + (b - a) * R
    Donde R es una variable aleatoria U(0, 1).
    """
    # np.random.rand(n) genera n números con distribución U(0, 1)
    numeros = a + (b - a) * np.random.rand(n)
    return np.round(numeros, 4)

def generar_exponencial(n, media):
    """
    Genera n números aleatorios con distribución exponencial.
    El usuario ingresa la media (1/lambda).
    Fórmula (método de la transformada inversa): X = -media * ln(1 - R)
    Donde R es una variable aleatoria U(0, 1).
    """
    if media <= 0:
        raise ValueError("La media debe ser un número positivo.")
    
    numeros = -media * np.log(1 - np.random.rand(n))
    return np.round(numeros, 4)

def generar_normal(n, media, desviacion):
    """
    Genera n números aleatorios con distribución normal.
    Se utiliza el generador de alta calidad de NumPy, que se basa en 
    métodos avanzados como el Ziggurat, partiendo de generadores uniformes.
    Es el estándar de la industria para este propósito.
    """
    if desviacion <= 0:
        raise ValueError("La desviación estándar debe ser un número positivo.")
        
    numeros = np.random.normal(media, desviacion, n)
    return np.round(numeros, 4)