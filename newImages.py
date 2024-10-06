import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.ndimage import binary_opening, binary_closing, label

PROCESSED_FOLDER2 = 'processed-m'

def save_histogram2(image, filename):
    # Crear histograma y guardarlo
    plt.hist(image.ravel(), bins=256, range=[0, 256])
    plt.title('Histograma')
    plt.xlabel('Intensidad de píxeles')
    plt.ylabel('Frecuencia')
    histogram_path = os.path.join(PROCESSED_FOLDER2, f'histogram_{filename}.png')
    plt.savefig(histogram_path)
    plt.close()  # Cerrar la figura para evitar conflictos de memoria
    return histogram_path

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
    compound_image_path = os.path.join(PROCESSED_FOLDER2, 'compound_quadbits.png')
    Image.fromarray(compound_image).save(compound_image_path)
    return compound_image_path