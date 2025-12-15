import './Header.css'


function Header() {
    return (
        <header className="header">
            <nav className ="nav">

                {/*Navigation links*/}
                <a href="./App.tsx" className="nav-link">Home</a>
                <a href="./Visualization.tsx" className="nav-link">Visualization</a>
                <a href="./Analysis.tsx" className="nav-link">Analysis</a>
                <a href="./Data.tsx" className="nav-link">Data</a>
                <a href="./About.tsx" className="nav-link">About</a>
                <a href="https://github.com/michaelshehata/DigitalMappingTwin" className="nav-link">Repository</a>

            </nav>
        </header>
    )
}

export default Header