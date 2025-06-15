import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Rectangle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Create a city marker with red dot and city name above
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

// City Overlay component that can be enabled/disabled
const CitiesOverlay = ({ cities, visible }) => {
  if (!visible) return null;

  return (
    <>
      {/* Render grid rectangles */}
      {cities.map((city, i) => {
        // Create bounds for the grid rectangle
        const bounds = [
          [parseFloat(city.grid_lat1), parseFloat(city.grid_lon1)],
          [parseFloat(city.grid_lat2), parseFloat(city.grid_lon2)]
        ];

        return (
          <Rectangle
            key={`grid-${i}`}
            bounds={bounds}
            pathOptions={{ color: '#FF0000', weight: 1, fillOpacity: 0.2 }}
          />
        );
      })}

      {/* Render city markers */}
      {cities.map((city, i) => (
        <Marker
          key={`city-${i}`}
          position={[parseFloat(city.city_lat), parseFloat(city.city_lon)]}
          icon={createCityMarkerIcon(city.city_name)}
        >
          <Popup>
            <b>City:</b> {city.city_name}<br />
            <b>Grid:</b> X: {city.grid_x}, Y: {city.grid_y}
          </Popup>
        </Marker>
      ))}
    </>
  );
};

function MapView() {
  const [cities, setCities] = useState([]);
  const [showCities, setShowCities] = useState(true);

  useEffect(() => {
    // Fetch cities data from cities_metadata.csv
    fetch('/cities_metadata.csv')
      .then(res => res.text())
      .then(text => {
        const lines = text.split('\n');
        const header = lines[0].split(',');
        const data = lines.slice(1).map(line => {
          const cols = line.split(',');
          if (cols.length < 10) return null;
          return {
            city_id: cols[0],
            city_name: cols[1],
            city_lat: parseFloat(cols[2]),
            city_lon: parseFloat(cols[3]),
            grid_y: parseInt(cols[4]),
            grid_x: parseInt(cols[5]),
            grid_lat1: parseFloat(cols[6]),
            grid_lon1: parseFloat(cols[7]),
            grid_lat2: parseFloat(cols[8]),
            grid_lon2: parseFloat(cols[9])
          };
        }).filter(Boolean);
        setCities(data);
      })
      .catch(error => {
        console.error("Error loading cities data:", error);
      });
  }, []);

  return (
    <div style={{ height: '100vh', width: '100vw', position: 'relative' }}>
      {/* Simple control panel */}
      <div style={{ position: 'absolute', zIndex: 1000, background: 'rgba(255,255,255,0.9)', padding: 12, borderRadius: 8, left: 20, top: 20 }}>
        <div style={{ marginBottom: 8 }}>
          <span>Cities displayed: <b>{cities.length}</b></span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <label htmlFor="show-cities">Show cities overlay:</label>
          <input
            id="show-cities"
            type="checkbox"
            checked={showCities}
            onChange={e => setShowCities(e.target.checked)}
          />
        </div>
      </div>
      <MapContainer center={[51, 10]} zoom={6} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap contributors"
        />
        {/* Cities overlay component that can be enabled/disabled */}
        <CitiesOverlay cities={cities} visible={showCities} />
      </MapContainer>
    </div>
  );
}

export default MapView;