import { useEffect, useState } from 'react';
import { MapContainer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Import components
import ControlPanel from './ControlPanel';
import GermanyBoundary from './GermanyBoundary';
import StationsOverlay from './StationsOverlay';
import StationInfoPanel from './StationInfoPanel';

// Import services
import {
  fetchLatestWeatherStationsData
} from '../../services/DataService';

// Constants
const DEBUG_MODE = process.env.NODE_ENV === 'development';
// Default map settings
const DEFAULT_ZOOM = 6;
const ZOOM_SNAP = 0.1;

function MapView() {
  // State
  const [stations, setStations] = useState([]);
  const [showGrid, setShowGrid] = useState(false);
  const [showStations, setShowStations] = useState(true);
  const [selectedStation, setSelectedStation] = useState(null);

  // Fetch stations data when component mounts
  useEffect(() => {
    const loadStations = async () => {
      try {
        // const stationsData = await fetchDailyWeatherStationsData();
        const stationsData = await fetchLatestWeatherStationsData();
        setStations(stationsData);
      } catch (error) {
        console.error("Failed to load stations data:", error);
      }
    };

    loadStations();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100vw' }}>
      <div style={{ height: '800px', width: '600px', position: 'relative' }}>
        {/* Map */}
        <MapContainer
          zoom={DEFAULT_ZOOM}
          // zoomSnap={ZOOM_SNAP}
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
          {/* <GridOverlay stations={stations} visible={showGrid} /> */}
          <StationsOverlay stations={stations} visible={showStations} onStationSelect={setSelectedStation} />
        </MapContainer>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', marginLeft: '20px' }}>

        {/* Station Info Panel */}
        <div style={{ marginTop: '20px', width: '100%' }}>
          <StationInfoPanel selectedStation={selectedStation} />
        </div>

        {/* Control panel overlay */}
        {DEBUG_MODE &&
          <ControlPanel
            showGrid={showGrid}
            setShowGrid={setShowGrid}
            showStations={showStations}
            setShowStations={setShowStations}
            stationsCount={stations.length}
          />
        }
      </div>
    </div>
  );
}

export default MapView;