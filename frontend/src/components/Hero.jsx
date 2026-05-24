import { Sparkles } from "lucide-react";
import CountryBubble from "./CountryBubble";

function Hero() {
  return (
    <section className="hero" id="inicio">
      <div className="hero-grid"></div>

      <div className="hero-content">
        <div className="eyebrow">
          <Sparkles size={16} />
          Asistente inteligente con RAG
        </div>

        <h1>Un propósito que nació de Colombia</h1>
        <h2>hoy inspira a toda Latinoamérica</h2>

        <div className="country-row">
          <CountryBubble code="CO" country="Colombia" />
          <CountryBubble code="EC" country="Ecuador" />
          <CountryBubble code="LATAM" country="Latinoamérica" main />
          <CountryBubble code="CL" country="Chile" />
          <CountryBubble code="AR" country="Argentina" />
        </div>

        <p>
          Una red que une personas, empresas y comunidades para construir una
          región más humana, productiva y consciente.
        </p>
      </div>
    </section>
  );
}

export default Hero;