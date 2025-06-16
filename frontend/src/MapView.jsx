import { useEffect, useState } from 'react';
import { MapContainer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Import components
import CitiesOverlay from './components/map/CitiesOverlay';
import GridOverlay from './components/map/GridOverlay';
import ControlPanel from './components/map/ControlPanel';
import GermanyBoundary from './components/map/GermanyBoundary';

// Import services
import { fetchCitiesMetadata } from './services/DataService';

// Constants
const DEBUG_MODE = process.env.NODE_ENV === 'development';
// Default map settings
const DEFAULT_MIN_ZOOM = 6;
const DEFAULT_MAX_ZOOM = 8;
const DEFAULT_ZOOM = 6;

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
    <div style={{ height: '600px', width: '450px', position: 'relative' }}>
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
      <MapContainer
        zoom={DEFAULT_ZOOM}
        minZoom={DEFAULT_MIN_ZOOM}
        maxZoom={DEFAULT_MAX_ZOOM}
        style={{ height: '100%', width: '100%', background: '#ffffff' }} // White background
        zoomControl={true}
        doubleClickZoom={false}
        scrollWheelZoom={true}
        attributionControl={true}
      >
        {/* Germany boundary mask */}
        {<GermanyBoundary />}

        {/* Overlays */}
        <GridOverlay cities={cities} visible={showGrid} />
        <CitiesOverlay cities={cities} visible={showCities} />
      </MapContainer>
    </div>
  );
}

export default MapView;