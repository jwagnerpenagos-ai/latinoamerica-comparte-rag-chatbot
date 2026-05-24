import { NAV_LINKS, OFFICIAL_SITE } from "../constants/site";

function Navbar() {
  return (
    <header className="navbar">
      <a
        className="brand"
        href={OFFICIAL_SITE}
        target="_blank"
        rel="noreferrer"
        aria-label="Ir a Latinoamérica Comparte"
      >
        <div className="logo-symbol">
          <span className="dot red"></span>
          <span className="dot orange"></span>
          <span className="dot purple"></span>
          <span className="dot blue"></span>
        </div>

        <div>
          <p className="brand-title">Latinoamérica Comparte</p>
          <p className="brand-subtitle">Asistente RAG</p>
        </div>
      </a>

      <nav className="nav-links">
        {NAV_LINKS.map((link) => (
          <a
            key={link.label}
            href={link.href}
            target="_blank"
            rel="noreferrer"
          >
            {link.label}
          </a>
        ))}
      </nav>
    </header>
  );
}

export default Navbar;