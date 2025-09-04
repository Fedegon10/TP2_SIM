import numpy as np

def generar_poisson(n, lamb):
    # Genera 'n' números aleatorios que siguen una distribución de Poisson, definida por su tasa media 'lambda' (λ).
    # Esta distribución describe el número de eventos que ocurren en un intervalo fijo de tiempo o espacio.
    if lamb <= 0:
        raise ValueError("Lambda (λ) debe ser un número positivo.")
        
    # NumPy genera números enteros para Poisson, los devolvemos como flotantes para consistencia.
    numeros = np.random.poisson(lam=lamb, size=n).astype(float)
    
    return numeros