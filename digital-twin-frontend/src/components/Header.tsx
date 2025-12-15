import { useEffect, useState } from "react";
import "./Header.css";

function Header() {
  const [open, setOpen] = useState(false);

  // Close mobile menu when resizing to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 900) {
        setOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <header className="header">
      <nav className="nav">

        {/* Logo */}
        <div className="logo">
          <img src="/favicon_100.png" alt="Logo" />
        </div>

        {/* Desktop nav */}
        <ul className="nav-links">
          <li><a href="/">Home</a></li>
          <li><a href="/visualization">Visualization</a></li>
          <li><a href="/analysis">Analysis</a></li>
          <li><a href="/data">Data</a></li>
          <li><a href="/about">About</a></li>
          <li>
            <a
              href="https://github.com/michaelshehata/DigitalMappingTwin"
              target="_blank"
              rel="noopener noreferrer"
            >
              Repository
            </a>
          </li>
        </ul>

        {/* Hamburger */}
        <button
          className={`hamburger ${open ? "open" : ""}`}
          onClick={() => setOpen(prev => !prev)}
          aria-label="Menu"
        >
          <span />
          <span />
          <span />
        </button>

      </nav>

      {/* FULLSCREEN MOBILE MENU OVERLAY */}
      <div
        className={`mobile-menu ${open ? "show" : ""}`}
        onClick={() => setOpen(false)}
      >
        <div
          className="menu-content"
          onClick={(e) => e.stopPropagation()}
        >
          <a onClick={() => setOpen(false)} href="/">Home</a>
          <a onClick={() => setOpen(false)} href="/visualization">Visualization</a>
          <a onClick={() => setOpen(false)} href="/analysis">Analysis</a>
          <a onClick={() => setOpen(false)} href="/data">Data</a>
          <a onClick={() => setOpen(false)} href="/about">About</a>
          <a
            onClick={() => setOpen(false)}
            href="https://github.com/michaelshehata/DigitalMappingTwin"
            target="_blank"
            rel="noopener noreferrer"
          >
            Repository
          </a>
        </div>
      </div>

    </header>
  );
}

export default Header;
