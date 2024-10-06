import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Registra todos los elementos de Chart.js
Chart.register(...registerables);


const socket = io('http://localhost:5000');  // URL del servidor Flask

const ProcesarImagen = () => {
  const [file, setFile] = useState(null);
  const [conTraslape, setConTraslape] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [data, setData] = useState([]);
  const [frame, setFrame] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Frames en tiempo real',
        data: [],
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
    ],
  });

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) return;

    const formData = new FormData();
    formData.append('imagen', file);
    formData.append('con_traslape', conTraslape);

    try {
      const response = await axios.post('http://localhost:5000/procesar_imagen', formData);
      setResultado(response.data.regiones);
    } catch (error) {
      console.error('Error al procesar la imagen:', error);
    }
  };

  useEffect(() => {
    socket.on('nueva_data', (nuevaData) => {
      setData(nuevaData.regiones);
      setFrame(nuevaData.frame);

      // Actualizar el gráfico con la nueva data
      setChartData(prevData => ({
        ...prevData,
        labels: [...prevData.labels, nuevaData.frame],
        datasets: [{
          ...prevData.datasets[0],
          data: [...prevData.datasets[0].data, nuevaData.valor]  // Cambia "valor" con el dato que quieras graficar
        }]
      }));
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleProcesarTiempoReal = () => {
    if (!file) return;

    setProcessing(true);
    const filePath = `uploads/${file.name}`; // Asegúrate de que este es el path correcto en tu backend
    socket.emit('procesar_y_graficar', { 
      file_path: filePath, 
      con_traslape: conTraslape 
    });

    socket.on('stop_procesamiento', () => {
      setProcessing(false);
    });
  };

  return (
    <div>
      <h2>Procesar Imagen</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Cargar imagen: </label>
          <input type="file" onChange={handleFileChange} />
        </div>
        <div>
          <label>
            <input
              type="checkbox"
              checked={conTraslape}
              onChange={() => setConTraslape(!conTraslape)}
            />
            Con traslape
          </label>
        </div>
        <button type="submit">Procesar Imagen</button>
        <button type="button" onClick={handleProcesarTiempoReal} disabled={processing}>
          Procesar en Tiempo Real
        </button>
      </form>

      {resultado && (
        <div>
          <h3>Resultado del procesamiento</h3>
          <pre>{JSON.stringify(resultado, null, 2)}</pre>
        </div>
      )}

      {data.length > 0 && (
        <div>
          <h3>Datos en tiempo real (Frame: {frame})</h3>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}

      {/* Gráfico de líneas para visualizar la evolución de frames */}
      <div>
        <h3>Gráfico de Frames en Tiempo Real</h3>
        <Line data={chartData} />
      </div>
    </div>
  );
};

export default ProcesarImagen;
