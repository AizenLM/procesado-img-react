import React, { useState } from 'react';
import axios from 'axios';

const EspectroUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [bandImages, setBandImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Manejar la selección de archivo
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setError('');
  };

  // Enviar la imagen al servidor
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Por favor, selecciona una imagen multiespectral.');
      return;
    }

    setLoading(true);
    setBandImages([]);
    setError('');

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post('http://localhost:5000/espectro', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { band_images } = response.data;
      setBandImages(band_images);
    } catch (err) {
      setError('Ocurrió un error al procesar la imagen.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='content'>
      <h1>Procesar Imagen Multiespectral</h1>

      <input type="file" onChange={handleFileChange} accept=".tiff,.tif" />
      <button className='btn-primary' onClick={handleUpload} disabled={loading}>
        {loading ? 'Procesando...' : 'Subir y Procesar Imagen'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div>
        {bandImages.length > 0 && (
          <div>
            <h2>Bandas Procesadas:</h2>
            <div style={{ display: 'flex', flexWrap: 'wrap' }}>
              {bandImages.map((band, index) => (
                <div className='img-more' key={index} style={{ margin: '10px' }}>
                  <h2>{band.name}</h2>
                  <img
                    src={`http://localhost:5000${band.image_url}`}
                    alt={`Banda ${index + 1}`}
                    style={{ width: '200px', height: '200px', objectFit: 'cover' }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EspectroUploader;
