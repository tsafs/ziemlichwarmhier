import L from 'leaflet';

/**
 * Create a city marker with red dot and city name above
 * @returns {L.DivIcon} - A Leaflet DivIcon for the city marker
 */
function createCityMarkerIcon() {
  const radius = 8;
  const svg = `
    <svg width="${radius * 2}" height="${radius * 2}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${radius}" cy="${radius}" r="${radius - 2}" fill="#d32f2f" stroke="#333" stroke-width="1" />
    </svg>
  `;
  return L.divIcon({
    className: '',
    html: svg,
    iconSize: [radius * 2, radius * 2],
    iconAnchor: [radius, radius]
  });
}

export default createCityMarkerIcon;