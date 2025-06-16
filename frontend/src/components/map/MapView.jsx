import { useEffect, useState } from 'react';
import { MapContainer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Import components
import CitiesOverlay from './CitiesOverlay';
import GridOverlay from './GridOverlay';
import ControlPanel from './ControlPanel';
import GermanyBoundary from './GermanyBoundary';

// Import services
import { fetchCitiesMetadata } from '../../services/DataService';

// Constants
const DEBUG_MODE = process.env.NODE_ENV === 'development';
// Default map settings
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
    <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', height: '100vh', width: '100vw' }}>
      <div style={{ height: '600px', width: '450px', position: 'relative' }}>
        {/* Map */}
        <MapContainer
          zoom={DEFAULT_ZOOM}
          style={{ height: '100%', width: '100%', background: '#ffffff' }} // White background
          zoomControl={false}
          doubleClickZoom={false}
          scrollWheelZoom={false}
          dragging={false}
          attributionControl={true}
        >
          {/* Germany boundary mask */}
          {<GermanyBoundary />}

          {/* Overlays */}
          <GridOverlay cities={cities} visible={showGrid} />
          <CitiesOverlay cities={cities} visible={showCities} />
        </MapContainer>
      </div>

      {/* Control panel overlay */}
      {DEBUG_MODE &&
        <ControlPanel
          citiesCount={cities.length}
          showCities={showCities}
          setShowCities={setShowCities}
          showGrid={showGrid}
          setShowGrid={setShowGrid}
          isDebugMode={DEBUG_MODE}
        />
      }
    </div>
  );
}

export default MapView;