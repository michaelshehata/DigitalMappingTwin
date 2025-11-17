import './Header.css'
import Logo3D from './logo'

function Header() {
    return (
        <header className="header">
            <nav className ="nav">

                {/*Logo container*/}
                <div className="logo-contaier"></div>
                <Logo3D />

                {/*Navigation links*/}
                <a href="#" className="nav-link">Home</a>
                <a href="#" className="nav-link">Visualization</a>
                <a href="#" className="nav-link">Analysis</a>
                <a href="#" className="nav-link">Scenarios</a>
                <a href="#" className="nav-link">Data</a>
                <a href="#" className="nav-link">About</a>
                <a href="https://github.com/michaelshehata/DigitalMappingTwin" className="nav-link">Repository</a>

            </nav>
        </header>
    )
}

export default Header