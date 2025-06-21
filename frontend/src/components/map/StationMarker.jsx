import { Marker, Popup } from 'react-leaflet';
import { createStationMarkerIcon, createHighlightedStationMarkerIcon } from './StationMarkerIcon';
import './StationMarker.css';

/**
 * Component for rendering a station marker on the map
 * @param {Object} props
 * @param {Object} props.station - Station data object
 * @param {number} props.index - Index for React key prop
 * @param {Function} props.onSelect - Callback function when station is selected
 * @param {boolean} props.isSelected - Whether this station is currently selected
 */
const StationMarker = ({ station, index, onSelect, isSelected }) => {
    return (
        <Marker
            key={`station-${index}`}
            position={[parseFloat(station.station_lat), parseFloat(station.station_lon)]}
            icon={isSelected ? createHighlightedStationMarkerIcon() : createStationMarkerIcon()}
            bubblingMouseEvents={false}
            eventHandlers={{
                click: () => onSelect(station),
                mouseover: (event) => event.target.openPopup(),
                mouseout: (event) => event.target.closePopup(),
            }}
            zIndexOffset={isSelected ? 1000 : 0} // Ensure selected marker is on top
            riseOnHover={true}
        >
            <Popup
                className={`simple-station-popup ${isSelected ? 'station-selected' : ''}`}
                closeButton={false}
                autoPan={false}
            >
                <div style={{ textAlign: 'center', fontWeight: 'bold' }}>
                    {station.station_name}
                    {isSelected && <span style={{ display: 'block', fontSize: '0.8em', color: '#3388ff' }}>• Ausgewählt •</span>}
                </div>
            </Popup>
        </Marker>
    );
};

export default StationMarker;