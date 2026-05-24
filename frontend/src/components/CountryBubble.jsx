function CountryBubble({ code, country, main = false }) {
  return (
    <div className={`country-bubble ${main ? "main" : ""}`}>
      <strong>{code}</strong>
      <span>
        {country}
        <br />
        Comparte
      </span>
    </div>
  );
}

export default CountryBubble;