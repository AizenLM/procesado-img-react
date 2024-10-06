import os
import numpy as np
import cv2
import matplotlib.pyplot as plt

PROCESSED_FOLDER = 'processed'

# Función para detectar regiones usando conectividad de 4 vecinos
def detectar_regiones(imagen):
    filas, columnas = imagen.shape
    visitado = np.zeros((filas, columnas), dtype=bool)
    regiones = []

    def expandir_region(x, y):
        pila = [(x, y)]
        region_actual = []
        vecinos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while pila:
            px, py = pila.pop()
            if visitado[px, py] or imagen[px, py] == 0:
                continue
            visitado[px, py] = True
            region_actual.append((px, py))
            for dx, dy in vecinos:
                nx, ny = px + dx, py + dy
                if 0 <= nx < filas and 0 <= ny < columnas and not visitado[nx, ny] and imagen[nx, ny] == 1:
                    pila.append((nx, ny))
        return region_actual

    for i in range(filas):
        for j in range(columnas):
            if not visitado[i, j] and imagen[i, j] == 1:
                region = expandir_region(i, j)
                regiones.append(region)
    
    return regiones

# Función para procesar la imagen en 3 cuadrantes (quadnits)
def procesar_3_cuadrantes(imagen):
    filas, columnas = imagen.shape
    cuadrantes = [
        (0, 0, filas // 2, columnas // 2),          
        (0, columnas // 2, filas // 2, columnas),   
        (filas // 2, 0, filas, columnas // 2)       
    ]

    regiones_cuadrantes = []
    for (x1, y1, x2, y2) in cuadrantes:
        subimagen = imagen[x1:x2, y1:y2]
        regiones = detectar_regiones(subimagen)
        regiones_cuadrantes.append(regiones)
    
    return regiones_cuadrantes

# Función para procesar la imagen con traslape
def procesar_cuadrantes_con_traslape(imagen, margen_traslape=10):
    filas, columnas = imagen.shape
    cuadrantes = [
        (0, 0, filas // 2 + margen_traslape, columnas // 2 + margen_traslape),
        (0, columnas // 2 - margen_traslape, filas // 2 + margen_traslape, columnas),
        (filas // 2 - margen_traslape, 0, filas, columnas // 2 + margen_traslape)
    ]
    
    regiones_cuadrantes = []
    for (x1, y1, x2, y2) in cuadrantes:
        subimagen = imagen[x1:x2, y1:y2]
        regiones = detectar_regiones(subimagen)
        regiones_cuadrantes.append(regiones)
    
    return regiones_cuadrantes

# Función para procesar la imagen con o sin traslape
def procesar_imagen(filepath, filename, con_traslape=False):
    # Verificar si el archivo existe
    if not os.path.exists(filepath):
        raise ValueError(f"El archivo {filepath} no existe.")
    
    # Leer la imagen en escala de grises y binarizarla
    imagen = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    if imagen is None:
        raise ValueError(f"La imagen {filepath} no se pudo leer. Verifica que sea una imagen válida.")
    
    _, imagen_binaria = cv2.threshold(imagen, 128, 1, cv2.THRESH_BINARY)
    binary_path = os.path.join(PROCESSED_FOLDER, f'binary_{filename}.png')
    cv2.imwrite(binary_path, imagen_binaria * 255)

    # Procesar la imagen para obtener las regiones
    if con_traslape:
        regiones = procesar_cuadrantes_con_traslape(imagen_binaria)
    else:
        regiones = procesar_3_cuadrantes(imagen_binaria)

    return regiones, binary_path

# Función para guardar histograma
def save_histogram(filepath, filename):
    imagen = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    plt.hist(imagen.ravel(), bins=256, range=[0, 256])
    plt.title('Histograma')
    plt.xlabel('Intensidad de píxeles')
    plt.ylabel('Frecuencia')
    histogram_path = os.path.join(PROCESSED_FOLDER, f'histogram_{filename}.png')
    plt.savefig(histogram_path)
    plt.close()
    return histogram_path

# Función para realizar operaciones morfológicas y etiquetado
def procesar_morfologia(filepath, filename):
    # Leer la imagen binaria
    imagen_binaria = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

    # Suavizar la imagen para reducir el ruido
    imagen_suavizada = cv2.GaussianBlur(imagen_binaria, (5, 5), 0)

    # Ajustar el tamaño del kernel según tus necesidades
    kernel = np.ones((5, 5), np.uint8)

    # Aplicar apertura y cierre
    apertura = cv2.morphologyEx(imagen_suavizada, cv2.MORPH_OPEN, kernel)
    apertura_path = os.path.join(PROCESSED_FOLDER, f'opened_{filename}.png')
    cv2.imwrite(apertura_path, cv2.normalize(apertura, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    cierre = cv2.morphologyEx(imagen_suavizada, cv2.MORPH_CLOSE, kernel)
    cierre_path = os.path.join(PROCESSED_FOLDER, f'closed_{filename}.png')
    cv2.imwrite(cierre_path, cv2.normalize(cierre, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    # Etiquetar componentes conectados
    num_labels, labels_im = cv2.connectedComponents(imagen_binaria)
    labeled_path = os.path.join(PROCESSED_FOLDER, f'labeled_{filename}.png')
    
    # Normalizar la imagen etiquetada
    labels_normalized = cv2.normalize(labels_im, None, 0, 255, cv2.NORM_MINMAX)
    cv2.imwrite(labeled_path, labels_normalized.astype(np.uint8))

    return apertura_path, cierre_path, labeled_path

