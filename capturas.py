import os
import keyboard
from datetime import datetime, timedelta
from PIL import ImageGrab
import tkinter as tk
from tkinter import messagebox
import threading
import time
import queue
import win32clipboard
from io import BytesIO

# --- Configuración de rutas ---
CARPETA_BASE = "C:\\Capturas"
CARPETA_PERMANENTE = os.path.join(CARPETA_BASE, "Permanentes")
CARPETA_TEMPORAL = os.path.join(CARPETA_BASE, "Temporales")

# Crear carpetas si no existen
os.makedirs(CARPETA_PERMANENTE, exist_ok=True)
os.makedirs(CARPETA_TEMPORAL, exist_ok=True)

# Variables globales para el recorte
recorte_ventana = None
x1, y1, x2, y2 = 0, 0, 0, 0
rectangulo_recorte = None
modo_captura = "modal"

# Crear una cola de mensajes para comunicar hilos
tarea_queue = queue.Queue()

def limpiar_carpeta_temporal():
    """
    Función que se ejecuta en segundo plano para eliminar archivos
    de la carpeta temporal que sean más viejos de 24 horas.
    """
    while True:
        try:
            ahora = datetime.now()
            limite_tiempo = ahora - timedelta(hours=24)
            
            for nombre_archivo in os.listdir(CARPETA_TEMPORAL):
                ruta_completa = os.path.join(CARPETA_TEMPORAL, nombre_archivo)
                if os.path.isfile(ruta_completa):
                    fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                    if fecha_modificacion < limite_tiempo:
                        os.remove(ruta_completa)
                        print(f"Archivo temporal eliminado: {ruta_completa}")
        except Exception as e:
            print(f"Error al limpiar la carpeta temporal: {e}")
        
        time.sleep(3600)

def copiar_al_portapapeles(coordenadas):
    """
    Captura el área seleccionada y la copia al portapapeles de Windows.
    """
    try:
        imagen = ImageGrab.grab(bbox=coordenadas)
        
        salida = BytesIO()
        imagen.save(salida, 'BMP')
        data = salida.getvalue()[14:]
        salida.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        messagebox.showinfo("Copiado", "La captura se ha copiado al portapapeles.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar al portapapeles: {e}")

def capturar_area_seleccionada(ruta_guardado, coordenadas):
    """
    Captura una porción específica de la pantalla y la guarda.
    """
    try:
        imagen = ImageGrab.grab(bbox=coordenadas)
        nombre_archivo = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        ruta_completa = os.path.join(ruta_guardado, nombre_archivo)
        imagen.save(ruta_completa)
        messagebox.showinfo("Captura guardada", f"Se guardó en:\n{ruta_completa}")
    except Exception as e:
        messagebox.showerror("Error de captura", f"No se pudo guardar la captura: {e}")

def empezar_recorte(event):
    """
    Guarda las coordenadas iniciales del clic del mouse.
    """
    global x1, y1, rectangulo_recorte
    x1, y1 = event.x_root, event.y_root
    
    if rectangulo_recorte is None or not rectangulo_recorte.winfo_exists():
        rectangulo_recorte = tk.Canvas(recorte_ventana, highlightthickness=0)
        recorte_ventana.configure(cursor="cross")
        rectangulo_recorte.pack(fill="both", expand=True)

def mover_recorte(event):
    """
    Actualiza el tamaño del rectángulo de selección mientras se arrastra el mouse.
    """
    global x2, y2
    if rectangulo_recorte is None or not rectangulo_recorte.winfo_exists():
        return
        
    x2, y2 = event.x_root, event.y_root
    recorte_ventana.attributes("-alpha", 0.5)
    
    rectangulo_recorte.delete("reco_rect")
    rectangulo_recorte.create_rectangle(
        x1, y1, x2, y2, outline="red", width=2, tags="reco_rect"
    )

def finalizar_recorte(event):
    """
    Finaliza el recorte, obtiene las coordenadas finales y ejecuta la acción.
    """
    global x2, y2, modo_captura
    x2, y2 = event.x_root, event.y_root
    
    if recorte_ventana and recorte_ventana.winfo_exists():
        recorte_ventana.destroy()
    
    coord_x1, coord_y1 = min(x1, x2), min(y1, y2)
    coord_x2, coord_y2 = max(x1, x2), max(y1, y2)
    
    if (coord_x2 - coord_x1) > 0 and (coord_y2 - coord_y1) > 0:
        if modo_captura == "copiar":
            copiar_al_portapapeles((coord_x1, coord_y1, coord_x2, coord_y2))
        else:
            mostrar_opciones_guardado((coord_x1, coord_y1, coord_x2, coord_y2))

def crear_ventana_recortes(modo):
    """
    Crea la ventana transparente que permite seleccionar el área de la pantalla.
    """
    global recorte_ventana, rectangulo_recorte, modo_captura
    
    recorte_ventana = None
    rectangulo_recorte = None
    modo_captura = modo

    recorte_ventana = tk.Toplevel(root)
    recorte_ventana.attributes("-fullscreen", True)
    recorte_ventana.attributes("-alpha", 0.1)
    recorte_ventana.attributes("-topmost", True)
    recorte_ventana.configure(bg='black')

    recorte_ventana.bind("<Button-1>", empezar_recorte)
    recorte_ventana.bind("<B1-Motion>", mover_recorte)
    recorte_ventana.bind("<ButtonRelease-1>", finalizar_recorte)
    recorte_ventana.bind("<Escape>", lambda e: recorte_ventana.destroy())

def mostrar_opciones_guardado(coordenadas):
    """
    Muestra una ventana modal con las opciones de guardado, incluyendo copiar al portapapeles.
    """
    ventana_opciones = tk.Toplevel(root)
    ventana_opciones.title("Guardar captura")
    ventana_opciones.geometry("300x190")
    ventana_opciones.resizable(False, False)
    ventana_opciones.grab_set()
    
    tk.Label(ventana_opciones, text="¿Qué querés hacer con la captura?").pack(pady=10)
    
    tk.Button(
        ventana_opciones, text="Guardar Permanente", width=20,
        command=lambda: [ventana_opciones.destroy(), capturar_area_seleccionada(CARPETA_PERMANENTE, coordenadas)]
    ).pack(pady=5)
    
    tk.Button(
        ventana_opciones, text="Guardar Temporal", width=20,
        command=lambda: [ventana_opciones.destroy(), capturar_area_seleccionada(CARPETA_TEMPORAL, coordenadas)]
    ).pack(pady=5)
    
    tk.Button(
        ventana_opciones, text="Copiar al Portapapeles", width=20,
        command=lambda: [ventana_opciones.destroy(), copiar_al_portapapeles(coordenadas)]
    ).pack(pady=5)
    
    ventana_opciones.mainloop()

def escuchar_tecla_hotkey():
    """
    Detecta los atajos de teclado y pone las tareas en la cola.
    """
    print("El programa se está ejecutando.")
    print("Presiona Alt+h para capturar la pantalla y ver el modal.")
    print("Presiona Ctrl+y para capturar y copiar directamente al portapapeles.")
    keyboard.add_hotkey("alt+h", lambda: tarea_queue.put(lambda: crear_ventana_recortes("modal")))
    keyboard.add_hotkey("ctrl+y", lambda: tarea_queue.put(lambda: crear_ventana_recortes("copiar")))
    keyboard.wait()

def procesar_cola():
    """
    Función que revisa la cola de tareas y las ejecuta en el hilo principal.
    """
    try:
        while True:
            tarea = tarea_queue.get_nowait()
            tarea()
    except queue.Empty:
        pass
    finally:
        root.after(200, procesar_cola)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    hilo_limpiador = threading.Thread(target=limpiar_carpeta_temporal, daemon=True)
    hilo_limpiador.start()
    
    hilo_teclado = threading.Thread(target=escuchar_tecla_hotkey, daemon=True)
    hilo_teclado.start()

    procesar_cola()
    
    root.mainloop()