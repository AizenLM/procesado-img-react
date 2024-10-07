import React from 'react'
import MyChartComponent from '../components/MyChartComponent'

import About from '../page/About'
import { Route, Routes } from 'react-router-dom'
import ETFChart from '../page/EtfChart'
import EspectroUploader from '../components/EspectroUploader'


export default function RoutesNav() {
  return (
        <Routes>
            <Route path='/' element={<MyChartComponent></MyChartComponent>}> </Route>
            <Route path='about' element={<About></About>} ></Route>
            <Route path='/espectro' element={<EspectroUploader></EspectroUploader>} ></Route>
            <Route path='/graf-etf' element={<ETFChart />} ></Route>
        </Routes>
  
  )
}
