import { Link } from "react-router-dom"
const HeadNav = () => {
    return(<>
    <nav>
        <div>
           <h1>Procesado de imagenes y grafica de regiones</h1>
        </div>
        <div>
            <ul>
                <li>
                    <Link to='/'>Home</Link>
                </li>
                <li>
                    <Link to='/graf-etf'>Graficar ETF</Link>
                </li>
                <li>
                    <Link to='/espectro'>MultiEspectral</Link>
                </li>
                <li>
                    <Link to='/about'>About</Link>
                </li>
            </ul>
        </div>
    </nav>
    </>)
}
export default HeadNav