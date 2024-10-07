import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale } from 'chart.js';
import 'chartjs-adapter-date-fns';

// Registrar los componentes de Chart.js que vamos a usar
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

// Clave de API de Finnhub (reemplaza con la tuya)
const API_KEY = 'cs1vhghr01qpjum5lucgcs1vhghr01qpjum5lud0';

// Lista de ETFs y monedas
const etfOptions = ['AMZN', 'AAPL', 'GOOGL', 'MSFT'];
const currencyOptions = ['USD', 'EUR', 'GBP', 'JPY'];

const ETFChart = () => {
  const [selectedETF, setSelectedETF] = useState(etfOptions[0]);
  const [selectedCurrencies, setSelectedCurrencies] = useState([]);
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: `Price of ${selectedETF} (USD)`,
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        fill: false,
      },
    ],
  });

  const fetchETFData = async (symbol) => {
    const response = await fetch(`https://finnhub.io/api/v1/quote?symbol=${symbol}&token=${API_KEY}`);
    const data = await response.json();
    return data.c; // Precio actual del ETF
  };

  const updateChart = async () => {
    const currentTime = new Date();
    const currentPrice = await fetchETFData(selectedETF);

    setChartData((prevData) => ({
      ...prevData,
      labels: [...prevData.labels, currentTime],
      datasets: [
        {
          ...prevData.datasets[0],
          label: `Price of ${selectedETF} (${selectedCurrencies})`,
          data: [...prevData.datasets[0].data, currentPrice],
        },
      ],
    }));
  };

  const handleCurrencyChange = (currency) => {
    setSelectedCurrencies((prevCurrencies) =>
      prevCurrencies.includes(currency)
        ? prevCurrencies.filter((c) => c !== currency)
        : [...prevCurrencies, currency]
    );
  };

  useEffect(() => {
    const intervalId = setInterval(updateChart, 60000);
    updateChart(); // Llamada inicial

    return () => clearInterval(intervalId);
  }, [selectedETF]);

  return (
    <div className="content">
      <div style={{ width: '80%', margin: 'auto', padding: '20px', backgroundColor: '#ffffff', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)' }}>
        <h1 style={{ textAlign: 'center', color: '#333' }}>Real-time ETF Chart</h1>

        {/* Selector de ETF */}
        <label style={{ display: 'block', marginBottom: '10px', color: '#333' }}>Select an ETF:</label>
        <select value={selectedETF} onChange={(e) => setSelectedETF(e.target.value)} style={{ padding: '10px', fontSize: '16px' }}>
          {etfOptions.map((etf) => (
            <option key={etf} value={etf}>
              {etf}
            </option>
          ))}
        </select>

        {/* Checkboxes para las monedas */}
        <div style={{ marginTop: '20px' }}>
          <h2 style={{ marginBottom: '10px', color: '#333' }}>Select Currencies:</h2>
          {currencyOptions.map((currency) => (
            <label key={currency} style={{ marginRight: '15px', color: '#333' }}>
              <input
                type="checkbox"
                value={currency}
                checked={selectedCurrencies.includes(currency)}
                onChange={() => handleCurrencyChange(currency)}
                style={{ marginRight: '5px' }}
              />
              {currency}
            </label>
          ))}
        </div>

        {/* Gráfico */}
        <div style={{ marginTop: '40px' }}>
          <Line
            data={chartData}
            options={{
              scales: {
                x: { type: 'time', time: { unit: 'minute' } },
              },
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ETFChart;
