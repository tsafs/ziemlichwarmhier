import { useEffect, useState } from 'react';
import { MapContainer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Import components
import ControlPanel from './ControlPanel';
import EuropeBoundary from './EuropeBoundary';
import StationsOverlay from './StationsOverlay';
import StationInfoPanel from './StationInfoPanel';

// Import services
import {
  fetchLatestWeatherStationsData
} from '../../services/DataService';

// Constants
const DEBUG_MODE = false;//process.env.NODE_ENV === 'development';
// Default map settings
const DEFAULT_ZOOM = 6.1;
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

  // Set Berlin as the default selected station
  useEffect(() => {
    if (stations.length > 0) {
      const berlinStation = stations.find(station =>
        station.station_name.toLowerCase() == "berlin");

      if (berlinStation) {
        setSelectedStation(berlinStation);
      }
    }
  }, [stations]);

  return (
    <div style={{ height: '1000px', width: '100vw', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {/* Station Info Panel */}
      <StationInfoPanel selectedStation={selectedStation} />

      {/* Map */}
      <MapContainer
        zoom={DEFAULT_ZOOM}
        zoomSnap={ZOOM_SNAP}
        style={{ height: '80%', width: '100%' }}
        zoomControl={false}
        doubleClickZoom={false}
        scrollWheelZoom={false}
        dragging={false}
        attributionControl={false}
        center={[51.165691, 10.451526]}
      >
        {/* Germany boundary mask */}
        {<EuropeBoundary />}

        {/* Overlays */}
        {/* <GridOverlay stations={stations} visible={showGrid} /> */}
        <StationsOverlay stations={stations} visible={showStations} onStationSelect={setSelectedStation} />
      </MapContainer>

      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%', position: 'absolute', top: '20px', right: '100px', zIndex: 400 }}>
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