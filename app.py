from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import numpy as np
import cv2  # Usado para manipular imágenes
import os
import matplotlib.pyplot as plt
from PIL import Image
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time

# Configuración del servidor Flask con WebSockets
app = Flask(__name__)
CORS(app, resources={r"/procesar_imagen": {"origins": "*"}})  # Configuración de CORS
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

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
def procesar_imagen(imagen, con_traslape=False):
    if con_traslape:
        return procesar_cuadrantes_con_traslape(imagen)
    else:
        return procesar_3_cuadrantes(imagen)

# Función para guardar histograma
def save_histogram(image, filename):
    # Crear histograma y guardarlo
    plt.hist(image.ravel(), bins=256, range=[0, 256])
    plt.title('Histograma')
    plt.xlabel('Intensidad de píxeles')
    plt.ylabel('Frecuencia')
    histogram_path = os.path.join(PROCESSED_FOLDER, f'histogram_{filename}.png')
    plt.savefig(histogram_path)
    plt.close()  # Cerrar la figura para evitar conflictos de memoria
    return histogram_path

# Función para crear imagen compuesta de quadbits
def create_compound_image(image, overlap):
    height, width = image.shape
    step = 2 if not overlap else 1
    quadbit_size = 2
    
    # Determinar las dimensiones de la imagen compuesta
    num_rows = (height - quadbit_size) // step + 1
    num_cols = (width - quadbit_size) // step + 1
    compound_image = np.zeros((num_rows * quadbit_size, num_cols * quadbit_size), dtype=np.uint8)

    for i in range(0, height, step):
        for j in range(0, width, step):
            quadbit = image[i:i + quadbit_size, j:j + quadbit_size]
            if quadbit.shape[0] == 2 and quadbit.shape[1] == 2:
                # Colocar el quadbit en la imagen compuesta
                compound_image[i // step * quadbit_size: (i // step + 1) * quadbit_size,
                               j // step * quadbit_size: (j // step + 1) * quadbit_size] = quadbit * 255

    # Guardar la imagen compuesta
    compound_image_path = os.path.join(PROCESSED_FOLDER, 'compound_quadbits.png')
    Image.fromarray(compound_image).save(compound_image_path)
    return compound_image_path

# Ruta para subir y procesar la imagen
@app.route('/procesar_imagen', methods=['POST'])
def procesar_imagen_endpoint():
    try:
        file = request.files['imagen']
        print(f"Archivo recibido: {file.filename}")

        con_traslape = request.form.get('con_traslape') == 'true'
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"Archivo guardado en: {filepath}")

        # Leer la imagen en escala de grises y binarizarla
        imagen = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if imagen is None:
            print("Error: la imagen no se pudo leer.")
            return jsonify({"error": "La imagen no se pudo leer."}), 400

        _, imagen_binaria = cv2.threshold(imagen, 128, 1, cv2.THRESH_BINARY)

        # Procesar la imagen (con o sin traslape)
        regiones = procesar_imagen(imagen_binaria, con_traslape)
        print(f"Regiones procesadas: {len(regiones)}")

        # Guardar histograma de la imagen
        histogram_path = save_histogram(imagen, filename)
        print(f"Histograma guardado en: {histogram_path}")

        # Crear imagen compuesta de quadbits
        compound_image_path = create_compound_image(imagen_binaria, con_traslape)
        print(f"Imagen compuesta guardada en: {compound_image_path}")

        return jsonify({
            "regiones": regiones,
            "file_path": filepath,
            "histogram_path": f'/processed/histogram_{filename}.png',  # URL corregida
            "compound_image_path": '/processed/compound_quadbits.png'   # URL corregida
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Ruta para servir archivos procesados
@app.route('/processed/<path:filename>')
def send_processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

# Evento para graficar en tiempo real durante el procesamiento
@socketio.on('procesar_y_graficar')
def procesar_y_graficar(data):
    file_path = data['file_path']
    con_traslape = data['con_traslape']

    # Leer la imagen en escala de grises y binarizarla
    imagen = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    _, imagen_binaria = cv2.threshold(imagen, 128, 1, cv2.THRESH_BINARY)

    # Enviar datos de las regiones procesadas en tiempo real
    for frame in range(100):
        time.sleep(0.1)  # Simular procesamiento en tiempo real
        regiones = procesar_imagen(imagen_binaria, con_traslape)
        emit('nueva_data', {'frame': frame, 'regiones': regiones})


if __name__ == '__main__':
    socketio.run(app, debug=True)
