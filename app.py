from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from PIL import Image
import cv2
import numpy as np
import os
import time
from image_processing import procesar_imagen, save_histogram, procesar_morfologia  # Importar las funciones del archivo separado
from newImages import save_histogram2, create_compound_image
from scipy.ndimage import binary_opening, binary_closing, label  # Asegúrate de importar las funciones necesarias
import matplotlib.pyplot as plt
from io import BytesIO
# Configuración del servidor Flask con WebSockets
app = Flask(__name__)
CORS(app, resources={r"/procesar_imagen": {"origins": "*"},r"/upload": {"origins": "*"},r"/espectro": {"origins": "*"} })
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
UPLOAD_FOLDER2 = 'uploads-m'
PROCESSED_FOLDER2 = 'processed-m'

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER2, exist_ok=True)
os.makedirs(PROCESSED_FOLDER2, exist_ok=True)

# Ruta para subir y procesar la imagen
@app.route('/procesar_imagen', methods=['POST'])
def procesar_imagen_endpoint():
    try:
        if 'imagen' not in request.files:
            return jsonify({"error": "No se encontró la imagen en la solicitud"}), 400
        
        file = request.files['imagen']
        print(f"Archivo recibido: {file.filename}")

        con_traslape = request.form.get('con_traslape') == 'true'
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"Archivo guardado en: {filepath}")

        # Procesar la imagen
        regiones, binary_path = procesar_imagen(filepath, filename, con_traslape)

        # Guardar histograma de la imagen
        histogram_path = save_histogram(filepath, filename)
        print(f"Histograma guardado en: {histogram_path}")

        # Realizar operaciones morfológicas
        apertura_path, cierre_path, labeled_path = procesar_morfologia(filepath, filename)

        return jsonify({
            "regiones": regiones,
            "file_path": filepath,
            "histogram_path": histogram_path,
            "binary_image": {
                "name": "Imagen binarizada",
                "image_url": binary_path,
                "class": 'img'
            },
            "morphological_operations": [
                {
                    "name": "Apertura morfológica",
                    "image_url": apertura_path,
                    "class": 'img'
                },
                {
                    "name": "Cierre morfológica",
                    "image_url": cierre_path,
                    "class": 'img'
                },
                {
                    "name": "Imagen etiquetada",
                    "image_url": labeled_path,
                    "class": 'img'
                }
            ]
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Ruta para servir archivos procesados
@app.route('/processed/<path:filename>', methods=['GET'])
def send_processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

# Evento para graficar en tiempo real durante el procesamiento
@socketio.on('procesar_y_graficar')
def procesar_y_graficar(data):
    file_path = data['file_path']
    con_traslape = data['con_traslape']

    # Asegúrate de que el archivo exista antes de intentar procesarlo
    if not os.path.exists(file_path):
        emit('error', {'message': 'El archivo no existe.'})
        return

    # Procesar la imagen con la ruta correcta
    regiones, _ = procesar_imagen(file_path, os.path.basename(file_path), con_traslape)

    for frame in range(100):
        time.sleep(0.1)  # Simular procesamiento en tiempo real
        regiones, _ = procesar_imagen(file_path, os.path.basename(file_path), con_traslape)
        emit('nueva_data', {'frame': frame, 'regiones': regiones})

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No se encontró la imagen"}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER2, filename)
    file.save(filepath)

    # Cargar la imagen
    image = Image.open(filepath)
    gray = np.asarray(image.convert('L'))

    # Guardar imagen en escala de grises
    gray_image_path = os.path.join(PROCESSED_FOLDER2, f'gray_{filename}')
    gray_image = Image.fromarray(gray)
    gray_image.save(gray_image_path)

    # Generar y guardar el histograma
    histogram_image_path = save_histogram2(gray, filename)

    # Umbralado
    th = 80
    binary_image = np.zeros_like(gray, dtype=int)
    binary_image[gray >= th] = 1

    # Guardar imagen binarizada
    binary_image_path = os.path.join(PROCESSED_FOLDER2, f'binary_{filename}')
    binary_image_pil = Image.fromarray(np.uint8(binary_image * 255))  # Convertir a imagen
    binary_image_pil.save(binary_image_path)

    # Apertura morfológica
    se1 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)
    opened_image = binary_opening(binary_image, structure=se1)

    # Guardar imagen después de apertura
    opened_image_path = os.path.join(PROCESSED_FOLDER2, f'opened_{filename}')
    opened_image_pil = Image.fromarray(np.uint8(opened_image * 255))
    opened_image_pil.save(opened_image_path)

    # Cierre morfológico
    radius = 3
    se2 = np.zeros((2 * radius + 1, 2 * radius + 1), dtype=bool)
    y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
    mask = x ** 2 + y ** 2 <= radius ** 2
    se2[mask] = 1
    closed_image = binary_closing(opened_image, structure=se2)

    # Guardar imagen después de cierre
    closed_image_path = os.path.join(PROCESSED_FOLDER2, f'closed_{filename}')
    closed_image_pil = Image.fromarray(np.uint8(closed_image * 255))
    closed_image_pil.save(closed_image_path)

    # Contar objetos
    labeled_image, num_objects = label(closed_image)

    # Guardar la imagen etiquetada
    labeled_image_pil = Image.fromarray(np.uint8(labeled_image * 255 / labeled_image.max()))
    labeled_image_path = os.path.join(PROCESSED_FOLDER2, f'labeled_{filename}')
    labeled_image_pil.save(labeled_image_path)

    # Crear imagen compuesta de quadbits
    overlap_option = request.form.get('overlap') == 'true'  # Obtener la opción de traslape
    compound_image_path = create_compound_image(binary_image, overlap_option)

    return jsonify({
        "message": "Imagen procesada correctamente",
        "num_objects": num_objects,
        "processed_image": f"/processed-m/labeled_{filename}",
        "gray_image": f"/processed-m/gray_{filename}",
        "histogram_image": f"/processed-m/histogram_{filename}.png",
        "binary_image": f"/processed-m/binary_{filename}",
        "opened_image": f"/processed-m/opened_{filename}",
        "closed_image": f"/processed-m/closed_{filename}",
        "compound_image": f"/processed-m/compound_quadbits.png"  # Añadir la imagen compuesta
    })

@app.route('/processed-m/<filename>', methods=['GET'])
def get_processed_image(filename):
    filepath = os.path.join(PROCESSED_FOLDER2, filename)
    return send_from_directory(PROCESSED_FOLDER2, filename)

@app.route('/espectro', methods=['POST'])
def procesar_imagen_espectro():
    if 'image' not in request.files:
        return jsonify({"error": "No se encontró la imagen"}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Leer la imagen multiespectral usando OpenCV
    image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    
    if image is None:
        return jsonify({"error": "No se pudo leer la imagen"}), 400

    # Verificar cuántas bandas tiene la imagen
    num_bands = image.shape[2] if len(image.shape) == 3 else 1
    band_images = []

    # Procesar cada banda y guardarla como imagen PNG en memoria
    for i in range(num_bands):
        band = image[:, :, i] if num_bands > 1 else image
        fig, ax = plt.subplots()
        ax.imshow(band)
        ax.set_title(f'Banda {i + 1}')
        ax.axis('off')

        # Guardar cada imagen de banda en un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close(fig)

        # Guardar la banda en una carpeta de procesados
        band_filename = f'band_{i + 1}_{filename}.png'
        band_image_path = os.path.join(PROCESSED_FOLDER, band_filename)
        with open(band_image_path, 'wb') as f:
            f.write(buffer.getvalue())

        band_images.append({
            "name": f"Banda {i + 1}",
            "image_url": f"/processed/{band_filename}"
        })

    return jsonify({
        "message": "Imagen multiespectral procesada correctamente",
        "num_bands": num_bands,
        "band_images": band_images
    })


if __name__ == '__main__':
    socketio.run(app, debug=True)
