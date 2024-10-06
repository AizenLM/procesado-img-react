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
  const [histogramUrl, setHistogramUrl] = useState("");
  const [compoundImageUrl, setCompoundImageUrl] = useState("");
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
      console.log(response.data.histogram_path);
      setHistogramUrl(`http://localhost:5000/${response.data.histogram_path}`);
      setCompoundImageUrl(
        `http://localhost:5000/${response.data.compound_image_path}`
      );

      const filePath = response.data.file_path;
      socket.current.emit("procesar_y_graficar", {
        file_path: filePath,
        con_traslape: conTraslape,
      });
      console.log("IMAGEN PROCESADA");
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

      {loading && <div>Cargando... Por favor, espera.</div>}

      <canvas ref={chartRef} />

      {/* Mostrar las imágenes solo cuando el gráfico esté listo */}
      {isChartReady ? (
        <div>
          {histogramUrl && (
            <div>
              <h2>Histograma de la Imagen</h2>
              <img src={histogramUrl} alt="Histograma" />
            </div>
          )}
          {compoundImageUrl && (
            <div>
              <h2>Imagen Compuesta (Quadbits)</h2>
              <img src={compoundImageUrl} alt="Imagen Compuesta" />
            </div>
          )}
        </div>
      ) : (
        <div className="control-carga">Procesando la imagen 🦾 </div>
      )}
    </div>
  );
};

export default MyChartComponent;
