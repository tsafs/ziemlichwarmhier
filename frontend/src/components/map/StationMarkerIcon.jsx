import L from 'leaflet';

/**
 * Create a weather station marker with blue dot
 * @returns {L.DivIcon} - A Leaflet DivIcon for the weather station marker
 */
function createStationMarkerIcon() {
    const radius = 7; // Slightly smaller than city markers
    const svg = `
    <svg width="${radius * 2}" height="${radius * 2}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${radius}" cy="${radius}" r="${radius - 1}" fill="#1976d2" stroke="#333" stroke-width="1" />
    </svg>
  `;
    return L.divIcon({
        className: '',
        html: svg,
        iconSize: [radius * 2, radius * 2],
        iconAnchor: [radius, radius]
    });
}

export default createStationMarkerIcon;
