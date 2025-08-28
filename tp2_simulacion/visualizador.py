import matplotlib.pyplot as plt

def graficar_histograma(numeros, limites, titulo_distribucion):
    """
    Genera y muestra un histograma de frecuencias.
    
    Args:
        numeros (list or np.array): La serie de números generados.
        limites (list or np.array): Los límites de los intervalos calculados previamente.
        titulo_distribucion (str): El nombre de la distribución para el título.
    """
    plt.figure(figsize=(10, 6))  # Crea una nueva figura para el gráfico
    
    # Crea el histograma
    plt.hist(numeros, bins=limites, edgecolor='black', alpha=0.7)
    
    # Añade títulos y etiquetas
    plt.title(f'Histograma de Frecuencias - Distribución {titulo_distribucion}', fontsize=16)
    plt.xlabel('Valor de la variable', fontsize=12)
    plt.ylabel('Frecuencia', fontsize=12)
    
    # Rótulos en el eje X para que coincidan con los límites de los intervalos
    plt.xticks(ticks=limites, rotation=45, ha="right")
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()  # Ajusta el gráfico para que todo quepa bien
    plt.show()