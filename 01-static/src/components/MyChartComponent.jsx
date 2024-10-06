import React, { useEffect, useRef, useState } from "react";
import { Chart, registerables } from "chart.js";
import io from "socket.io-client";
import axios from "axios";

Chart.register(...registerables);

const MyChartComponent = () => {
  const chartRef = useRef();
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: "Regiones Procesadas",
        data: [],
        backgroundColor: "rgba(75, 192, 192, 0.6)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [conTraslape, setConTraslape] = useState(false);
  const [numObjects,  setNumObjects] = useState('')

  //imgs
  const [binaryImgUrl, setBinaryImgUrl] = useState('');
  const [histogramUrl, setHistogramUrl] = useState("");
  const [morphologicalOperation, setMorphologicalOperations] = useState([])

  const [loading, setLoading] = useState(false);
  const [isChartReady, setIsChartReady] = useState(false); // Nuevo estado
  const socket = useRef();
  const chartInstance = useRef(); // Referencia al gráfico

  useEffect(() => {
    socket.current = io("http://localhost:5000");

    socket.current.on("nueva_data", (data) => {
      console.log(data);
      const nuevasRegiones = data.regiones.length;
      setChartData((prevData) => {
        const newLabels = [...prevData.labels, `Frame ${data.frame}`];
        const newData = [...prevData.datasets[0].data, nuevasRegiones];

        // Si los datos están completos, marcar el gráfico como listo
        if (newLabels.length === 10) {
          // Aquí puedes ajustar cuántos frames se esperan
          setIsChartReady(true);
        }

        return {
          labels: newLabels,
          datasets: [
            {
              ...prevData.datasets[0],
              data: newData,
            },
          ],
        };
      });
    });

    return () => {
      socket.current.disconnect();
    };
  }, []);

  useEffect(() => {
    const ctx = chartRef.current.getContext("2d");

    // Solo crear el gráfico si no existe uno ya
    if (!chartInstance.current) {
      chartInstance.current = new Chart(ctx, {
        type: "bar",
        data: chartData,
        options: {
          responsive: true,
          scales: {
            x: {
              title: {
                display: true,
                text: "Frames",
              },
            },
            y: {
              title: {
                display: true,
                text: "Número de Regiones",
              },
              beginAtZero: true,
            },
          },
        },
      });
    } else {
      // Actualizar los datos del gráfico sin volver a crear uno nuevo
      chartInstance.current.data = chartData;
      chartInstance.current.update();
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null;
      }
    };
  }, [chartData]);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    setMorphologicalOperations([])
    setLoading(true);
    const formData = new FormData();
    formData.append("imagen", selectedFile);
    formData.append("con_traslape", String(conTraslape));

    try {
      const response = await axios.post(
        "http://localhost:5000/procesar_imagen",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setHistogramUrl(`http://localhost:5000/${response.data.histogram_path}`);
      setBinaryImgUrl(`http://localhost:5000/${response.data.binary_image.image_url}`)
      const {morphological_operations} = response.data;
     
      setNumObjects(response.data.regiones);
      setMorphologicalOperations(prevOperations => [
        ...prevOperations,
        ...morphological_operations.map(morphological => ({
            name: morphological.name,
            url: morphological.image_url
        }))])
      const filePath = response.data.file_path;
      socket.current.emit("procesar_y_graficar", {
        file_path: filePath,
        con_traslape: conTraslape,
      });
      console.log("IMAGEN PROCESADA");
      console.log(morphologicalOperation)


    } catch (error) {
      console.error("Error al procesar la imagen:", error);
      alert(
        `Error al procesar la imagen: ${
          error.response?.data?.error || error.message
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Procesar Imagen y Graficar Regiones</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <label>
          <input
            type="checkbox"
            checked={conTraslape}
            onChange={() => setConTraslape(!conTraslape)}
          />
          Procesar con Traslape
        </label>
        <button type="submit">Subir y Procesar</button>
      </form>
      <canvas ref={chartRef} />
      {/* Mostrar las imágenes solo cuando el gráfico esté listo */}
      {isChartReady ? (

        <div className="content-imgs">
          {histogramUrl && (
            <>
            <div>
              <h2>Histograma de la Imagen</h2>
              <img src={histogramUrl} alt="Histograma" />
            </div>

            <div>
              <h2>Imagen Binaria</h2>
              <img src={binaryImgUrl} alt="Imagen Binaria" />
            </div>
            <h3>Operaciones Mofologicas</h3>
            <h3>Operaciones Morfológicas</h3>
            {morphologicalOperation.map(operation => (
                <div key={operation.name}>
                    <h4>{operation.name}</h4>
                    <img src={`http://localhost:5000/${operation.url}`} alt={operation.name} />
                </div>
            ))}
            </>
        
            
          )}
       
    
        </div>
      ) : (
        <div className="control-carga">Procesando la imagen 🦾 </div>
      )}
    </div>
  );
};

export default MyChartComponent;
