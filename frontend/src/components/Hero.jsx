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
          <CountryBubble image="/Colombia Co N.png" country="Colombia" />
          <CountryBubble image="/Ecuador Co N.png" country="Ecuador" />
          <CountryBubble image="/Latinoamérica Co N.png" country="Latinoamérica" main />
          <CountryBubble image="/Chile Co N.png" country="Chile" />
          <CountryBubble image="/Argentina Co N.png" country="Argentina" />
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