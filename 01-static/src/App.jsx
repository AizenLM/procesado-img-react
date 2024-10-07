import { BrowserRouter as Router } from 'react-router-dom';
import Footer from "./components/Footer"
import HeadNav from "./components/HeadNav"
import MyChartComponent from "./components/MyChartComponent"
import RoutesNav from "./routes/RoutesNav"

const App = () => {
    return (
        <>
            <Router>
                <HeadNav>
                </HeadNav>
               
                <RoutesNav ></RoutesNav>
                <Footer></Footer>
            </Router>
        </>
    )
}
export default App