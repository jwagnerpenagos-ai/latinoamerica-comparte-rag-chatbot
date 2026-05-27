function CountryBubble({ image, country, main = false }) {
  return (
    <div className={`country-bubble ${main ? "main" : ""}`}>
      <img src={image} alt={`${country} Comparte`} />
    </div>
  );
}

export default CountryBubble;