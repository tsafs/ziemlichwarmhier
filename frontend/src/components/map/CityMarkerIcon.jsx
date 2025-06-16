import L from 'leaflet';

/**
 * Create a city marker with red dot and city name above
 * @param {string} cityName - The name of the city
 * @returns {L.DivIcon} - A Leaflet DivIcon for the city marker
 */
function createCityMarkerIcon(cityName) {
    const radius = 8;
    const svg = `
    <svg width="${radius * 2 + 100}" height="${radius * 2 + 25}" xmlns="http://www.w3.org/2000/svg">
      <text x="${radius}" y="${radius - 10}" text-anchor="start" fill="#d32f2f" font-size="12" font-family="sans-serif" font-weight="bold">${cityName}</text>
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
