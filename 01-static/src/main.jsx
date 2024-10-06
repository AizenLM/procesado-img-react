import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './assets/styles.css'
import 'animate.css';

import MyChartComponent from './components/MyChartComponent.jsx'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
