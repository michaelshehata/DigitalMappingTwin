import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      {/* Left */}
      <div className="footer-left">
        © 2026, Michael Shehata
      </div>

      {/* Right */}
      <div className="footer-right">
        <a
          href="https://github.com/michaelshehata"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="GitHub"
        >
          <img src="/github.svg" alt="GitHub" />
        </a>

        <a
          href="https://www.linkedin.com/in/michaelehabshehata"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="LinkedIn"
        >
          <img src="/linkedin.svg" alt="LinkedIn" />
        </a>

        <a
          href="mailto:sbb23byu@uea.ac.uk"
          aria-label="Email"
        >
          <img src="/email.svg" alt="Email" />
        </a>
      </div>
    </footer>
  );
}

export default Footer;
