from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import time
from image_processing import procesar_imagen, save_histogram, procesar_morfologia  # Importar las funciones del archivo separado

# Configuración del servidor Flask con WebSockets
app = Flask(__name__)
CORS(app, resources={r"/procesar_imagen": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
UPLOAD_FOLDER2 = 'uploads-m'
PROCESSED_FOLDER2 = 'processed-m'

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

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
@app.route('/processed/<path:filename>')
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

if __name__ == '__main__':
    socketio.run(app, debug=True)
