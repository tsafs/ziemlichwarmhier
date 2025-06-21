import L from 'leaflet';

/**
 * Create a standard station marker with red dot
 * @returns {L.DivIcon} - A Leaflet DivIcon for the station marker
 */
function createStationMarkerIcon() {
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

/**
 * Create a highlighted station marker with red dot and rotating blue-white dashed circle
 * @returns {L.DivIcon} - A Leaflet DivIcon for the highlighted station marker
 */
function createHighlightedStationMarkerIcon() {
  const radius = 8;
  const outerRadius = radius + 4; // Directly touch the inner circle

  // Create a dashed stroke pattern for the circle
  const svg = `
    <svg width="${outerRadius * 2}" height="${outerRadius * 2}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="dashGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#3388ff" />
          <stop offset="50%" stop-color="white" />
          <stop offset="100%" stop-color="#3388ff" />
        </linearGradient>
      </defs>
      <!-- Blue background circle -->
      <circle cx="${outerRadius}" cy="${outerRadius}" r="${radius}" fill="none" 
        stroke="#000000" stroke-width="6" opacity="1" />
      
      <!-- White dashed rotating circle -->
      <circle cx="${outerRadius}" cy="${outerRadius}" r="${radius}" fill="none" 
        stroke="white" stroke-width="6" stroke-dasharray="4,6" opacity="1">
        <animateTransform 
          attributeName="transform" 
          attributeType="XML" 
          type="rotate" 
          from="0 ${outerRadius} ${outerRadius}"
          to="360 ${outerRadius} ${outerRadius}"
          dur="12s" 
          repeatCount="indefinite"
        />
      </circle>
      <circle cx="${outerRadius}" cy="${outerRadius}" r="${radius - 2}" fill="#d32f2f" stroke="#333" stroke-width="1" />
    </svg>
  `;
  return L.divIcon({
    className: '',
    html: svg,
    iconSize: [outerRadius * 2, outerRadius * 2],
    iconAnchor: [outerRadius, outerRadius]
  });
}

export { createStationMarkerIcon, createHighlightedStationMarkerIcon };