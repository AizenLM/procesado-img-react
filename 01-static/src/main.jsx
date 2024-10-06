import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import ProcesarImagen from './ProcesarImagen.jsx'
import MyChartComponent from './components/MyChartComponent.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <MyChartComponent />
  </StrictMode>,
)
