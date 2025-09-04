# --- Importaciones de librerías ---
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import queue
import numpy as np
import ttkbootstrap as b
from ttkbootstrap.scrolled import ScrolledText

# --- Módulos propios del proyecto ---
from distribuciones import generar_uniforme, generar_exponencial, generar_normal
import procesador_datos as proc
import visualizador as vis

# --- Clase Principal de la Aplicación ---
class App(b.Window):
    def __init__(self):
        # Constructor: inicializa la ventana principal y llama a la creación de la interfaz.
        super().__init__(themename="litera")
        self.title("Generador de Variables Aleatorias Pro")
        self.geometry("900x650")

        self.numeros_generados = None

        self.crear_widgets()
        self.verificar_cola()

    def crear_widgets(self):
        # Este método construye toda la interfaz gráfica, organizando los paneles y widgets.
        main_frame = b.Frame(self, padding="15 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel izquierdo para la configuración de la simulación.
        config_frame = b.Frame(main_frame)
        config_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        b.Label(config_frame, text="Configuración", font="-size 13 -weight bold", bootstyle="primary").pack(anchor="w", pady=(0, 15))

        dist_frame = b.LabelFrame(config_frame, text="Distribución", padding="10")
        dist_frame.pack(fill=tk.X, pady=10)
        self.distribucion_seleccionada = tk.StringVar(value="Uniforme")
        self.dist_combo = b.Combobox(
            dist_frame, textvariable=self.distribucion_seleccionada, 
            values=["Uniforme", "Exponencial", "Normal"], state="readonly"
        )
        self.dist_combo.pack(fill=tk.X, expand=True)
        self.dist_combo.bind("<<ComboboxSelected>>", self.actualizar_parametros)

        self.params_frame = b.LabelFrame(config_frame, text="Parámetros", padding="10")
        self.params_frame.pack(fill=tk.X, pady=10)
        self.entries_params = {}
        self.actualizar_parametros()

        muestra_frame = b.LabelFrame(config_frame, text="Muestra e Intervalos", padding="10")
        muestra_frame.pack(fill=tk.X, pady=10)
        
        b.Label(muestra_frame, text="Tamaño de Muestra (n):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_n = b.Entry(muestra_frame)
        self.entry_n.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        
        b.Label(muestra_frame, text="Intervalos:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # --- CAMBIO 1: Reemplazar Combobox por Entry ---
        self.entry_intervalos = b.Entry(muestra_frame)
        self.entry_intervalos.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        self.entry_intervalos.insert(0, "10") # Valor por defecto
        # --- FIN DEL CAMBIO 1 ---

        action_buttons_frame = b.Frame(config_frame)
        action_buttons_frame.pack(fill=tk.X, pady=(25, 10))

        self.generate_button = b.Button(
            action_buttons_frame, text="▶  Generar y Analizar", command=self.iniciar_generacion, 
            bootstyle="primary"
        )
        self.generate_button.pack(fill=tk.X, ipady=5, pady=(0, 5))

        self.export_button = b.Button(
            action_buttons_frame, text="💾  Exportar a CSV", command=self.exportar_a_csv, 
            bootstyle="secondary", state="disabled"
        )
        self.export_button.pack(fill=tk.X, ipady=5, pady=(0, 5))
        
        self.reset_button = b.Button(
            action_buttons_frame, text="🔄  Realizar Otra Prueba", command=self.resetear_interfaz,
            bootstyle="info-outline", state="disabled"
        )
        self.reset_button.pack(fill=tk.X, ipady=5)
        
        self.status_label = b.Label(config_frame, text="", anchor="center")
        self.status_label.pack(fill=tk.X, pady=10)

        results_frame = b.LabelFrame(main_frame, text="Resultados", padding="15")
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        notebook = b.Notebook(results_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.resultado_queue = queue.Queue()
        
        tab1 = b.Frame(notebook)
        notebook.add(tab1, text=' Muestra de la Serie')
        self.text_serie = ScrolledText(tab1, wrap=tk.WORD, autohide=True)
        self.text_serie.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        b.Label(tab1, text="* Se muestran los primeros 1000 números generados.", bootstyle="secondary").pack(side=tk.BOTTOM, fill=tk.X)

        tab2 = b.Frame(notebook)
        notebook.add(tab2, text=' Tabla de Frecuencias')
        
        columnas = ('intervalo', 'marca_clase', 'frecuencia')
        self.tree_tabla = b.Treeview(tab2, columns=columnas, show='headings', bootstyle="primary")
        
        self.tree_tabla.heading('intervalo', text='Intervalo')
        self.tree_tabla.heading('marca_clase', text='Marca de Clase (xi)')
        self.tree_tabla.heading('frecuencia', text='Frec. Observada (fo)')
        
        self.tree_tabla.column('intervalo', width=150, anchor=tk.CENTER)
        self.tree_tabla.column('marca_clase', width=150, anchor=tk.CENTER)
        self.tree_tabla.column('frecuencia', width=150, anchor=tk.CENTER)
        
        scrollbar = b.Scrollbar(tab2, orient="vertical", command=self.tree_tabla.yview, bootstyle="round")
        self.tree_tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree_tabla.pack(side="left", fill="both", expand=True)

    def resetear_interfaz(self):
        # Limpia todos los campos y resultados para una nueva simulación.
        self.entry_n.delete(0, tk.END)
        for entry in self.entries_params.values():
            entry.delete(0, tk.END)
        
        self.dist_combo.set("Uniforme")
        self.actualizar_parametros()
        
        # --- CAMBIO 3: Resetear el Entry de intervalos ---
        self.entry_intervalos.delete(0, tk.END)
        self.entry_intervalos.insert(0, "10")
        # --- FIN DEL CAMBIO 3 ---
        
        self.text_serie.delete('1.0', tk.END)
        for item in self.tree_tabla.get_children():
            self.tree_tabla.delete(item)
        
        self.status_label.config(text="")
        self.generate_button.config(state="normal")
        self.export_button.config(state="disabled")
        self.reset_button.config(state="disabled")
        
        self.numeros_generados = None

    def iniciar_generacion(self):
        # Se activa al presionar "Generar". Prepara la UI y lanza el cálculo en segundo plano.
        self.generate_button.config(state='disabled')
        self.export_button.config(state='disabled')
        self.reset_button.config(state='disabled')
        self.status_label.config(text="Procesando, por favor espere...")
        
        self.text_serie.delete('1.0', tk.END)
        for item in self.tree_tabla.get_children():
            self.tree_tabla.delete(item)

        try:
            params = self.validar_entradas()
            # El trabajo pesado se ejecuta en un hilo para no congelar la interfaz.
            thread = threading.Thread(target=self.proceso_largo, args=(params,))
            thread.daemon = True
            thread.start()
        except (ValueError, tk.TclError) as e:
            messagebox.showerror("Error de Entrada", str(e))
            self.generate_button.config(state='normal')
            self.reset_button.config(state='normal')
            self.status_label.config(text="")

    def verificar_cola(self):
        # Revisa periódicamente si el hilo de cálculo ya terminó y dejó resultados.
        try:
            # Intenta obtener un resultado de la cola de comunicación.
            resultado = self.resultado_queue.get_nowait()
            
            # Si hay resultados, actualiza la interfaz y habilita los botones.
            if resultado.get("error"):
                messagebox.showerror("Error en el Cálculo", str(resultado["error"]))
            else:
                self.mostrar_resultados(resultado["tabla"])
                vis.graficar_histograma(self.numeros_generados, resultado["limites"], resultado["dist"])
                self.export_button.config(state="normal")

            self.generate_button.config(state='normal')
            self.reset_button.config(state='normal')
            self.status_label.config(text="¡Proceso completado!")

        except queue.Empty:
            pass # Si la cola está vacía, no hace nada.
        
        # Vuelve a ejecutar esta función cada 100ms para seguir revisando.
        self.after(100, self.verificar_cola)

    def exportar_a_csv(self):
        # Permite al usuario guardar la serie completa de números en un archivo CSV.
        if self.numeros_generados is None:
            messagebox.showwarning("Sin Datos", "Primero debes generar una serie de números.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar serie de números"
        )
        
        if not filepath:
            return
            
        try:
            np.savetxt(filepath, self.numeros_generados, delimiter=",", fmt='%.4f', header='valor_aleatorio', comments='')
            messagebox.showinfo("Éxito", f"Archivo guardado exitosamente en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo.\nError: {e}")

    def actualizar_parametros(self, event=None):
        # Muestra los campos de entrada correctos según la distribución elegida.
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        dist = self.distribucion_seleccionada.get()
        self.entries_params = {}
        
        if dist == "Uniforme":
            b.Label(self.params_frame, text="Desde (a):").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.entries_params['a'] = b.Entry(self.params_frame)
            self.entries_params['a'].grid(row=0, column=1, pady=2, padx=(10,0))
            
            b.Label(self.params_frame, text="Hasta (b):").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.entries_params['b'] = b.Entry(self.params_frame)
            self.entries_params['b'].grid(row=1, column=1, pady=2, padx=(10,0))

        elif dist == "Exponencial":
            b.Label(self.params_frame, text="Media (μ):").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.entries_params['media_exp'] = b.Entry(self.params_frame)
            self.entries_params['media_exp'].grid(row=0, column=1, pady=2, padx=(10,0))

        elif dist == "Normal":
            b.Label(self.params_frame, text="Media (μ):").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.entries_params['media_norm'] = b.Entry(self.params_frame)
            self.entries_params['media_norm'].grid(row=0, column=1, pady=2, padx=(10,0))
            
            b.Label(self.params_frame, text="Desviación (σ):").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.entries_params['desviacion'] = b.Entry(self.params_frame)
            self.entries_params['desviacion'].grid(row=1, column=1, pady=2, padx=(10,0))
    
    def validar_entradas(self):
        # Lee y comprueba que todos los datos ingresados por el usuario sean válidos.
        params = {}
        params['n'] = int(self.entry_n.get())
        if not (0 < params['n'] <= 1000000):
            raise ValueError("El tamaño de la muestra debe estar entre 1 y 1,000,000.")
        
        # --- CAMBIO 2: Validar el Entry de intervalos ---
        num_intervalos = int(self.entry_intervalos.get())
        if not (2 <= num_intervalos <= 100):
            raise ValueError("El número de intervalos debe estar entre 2 y 100.")
        params['num_intervalos'] = num_intervalos
        # --- FIN DEL CAMBIO 2 ---
        
        params['dist'] = self.distribucion_seleccionada.get()

        if params['dist'] == "Uniforme":
            params['a'] = float(self.entries_params['a'].get())
            params['b'] = float(self.entries_params['b'].get())
            if params['a'] >= params['b']: raise ValueError("El parámetro 'a' debe ser menor que 'b'.")
        elif params['dist'] == "Exponencial":
            params['media_exp'] = float(self.entries_params['media_exp'].get())
        elif params['dist'] == "Normal":
            params['media_norm'] = float(self.entries_params['media_norm'].get())
            params['desviacion'] = float(self.entries_params['desviacion'].get())
        
        return params

    def proceso_largo(self, params):
        # Esta función se ejecuta en el hilo secundario.
        try:
            # 1. Llama a las funciones de generación y procesamiento de datos.
            numeros = None
            if params['dist'] == "Uniforme":
                numeros = generar_uniforme(params['n'], params['a'], params['b'])
            elif params['dist'] == "Exponencial":
                numeros = generar_exponencial(params['n'], params['media_exp'])
            elif params['dist'] == "Normal":
                numeros = generar_normal(params['n'], params['media_norm'], params['desviacion'])
            
            self.numeros_generados = numeros
            tabla_frec, limites = proc.calcular_frecuencias(numeros, params['num_intervalos'])
            
            # 2. Prepara el paquete de resultados.
            resultado = {
                "tabla": tabla_frec, 
                "limites": limites, "dist": params['dist'], "error": None
            }
        except Exception as e:
            resultado = {"error": e}
            self.numeros_generados = None
            
        # 3. Coloca los resultados en la cola para que la interfaz los reciba.
        self.resultado_queue.put(resultado)

    def mostrar_resultados(self, tabla):
        # Actualiza la interfaz con los resultados de la simulación.
        self.text_serie.delete('1.0', tk.END)
        muestra_numeros = self.numeros_generados[:1000]
        serie_str = ", ".join(map(str, muestra_numeros))
        self.text_serie.insert(tk.END, serie_str)
        
        for item in self.tree_tabla.get_children():
            self.tree_tabla.delete(item)

        for _, row in tabla.iterrows():
            self.tree_tabla.insert('', tk.END, values=list(row))

# Punto de entrada para ejecutar la aplicación.
if __name__ == "__main__":
    app = App()
    app.mainloop()