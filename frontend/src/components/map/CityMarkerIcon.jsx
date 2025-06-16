import L from 'leaflet';

/**
 * Create a city marker with red dot and city name above
 * @returns {L.DivIcon} - A Leaflet DivIcon for the city marker
 */
function createCityMarkerIcon() {
  const radius = 8;
  const svg = `
    <svg width="${radius * 2 + 100}" height="${radius * 2 + 25}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${radius}" cy="${radius + 14}" r="${radius - 2}" fill="#d32f2f" stroke="#333" stroke-width="1" />
    </svg>
  `;
  return L.divIcon({
    className: '',
    html: svg,
    iconSize: [radius * 2 + 100, radius * 2 + 25],
    iconAnchor: [radius, radius + 14]
  });
}

export default createCityMarkerIcon;
