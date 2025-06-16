import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Import components
import CitiesOverlay from './components/map/CitiesOverlay';
import GridOverlay from './components/map/GridOverlay';
import ControlPanel from './components/map/ControlPanel';

// Import services
import { fetchCitiesMetadata } from './services/DataService';

// Constants
const DEBUG_MODE = process.env.NODE_ENV === 'development';

function MapView() {
  // State
  const [cities, setCities] = useState([]);
  const [showCities, setShowCities] = useState(true);
  const [showGrid, setShowGrid] = useState(false);

  // Fetch cities data when component mounts
  useEffect(() => {
    const loadCities = async () => {
      try {
        const citiesData = await fetchCitiesMetadata();
        setCities(citiesData);
      } catch (error) {
        console.error("Failed to load cities data:", error);
      }
    };

    loadCities();
  }, []);

  return (
    <div style={{ height: '100vh', width: '100vw', position: 'relative' }}>
      {/* Control panel overlay */}
      <ControlPanel
        citiesCount={cities.length}
        showCities={showCities}
        setShowCities={setShowCities}
        showGrid={showGrid}
        setShowGrid={setShowGrid}
        isDebugMode={DEBUG_MODE}
      />

      {/* Map */}
      <MapContainer center={[51, 10]} zoom={6} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap contributors"
        />

        {/* Overlays */}
        <GridOverlay cities={cities} visible={showGrid} />
        <CitiesOverlay cities={cities} visible={showCities} />
      </MapContainer>
    </div>
  );
}

export default MapView;