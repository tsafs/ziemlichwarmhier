import { Marker, Popup } from 'react-leaflet';
import createStationMarkerIcon from './StationMarkerIcon';
import './StationMarker.css';

/**
 * Component for rendering a station marker on the map
 * @param {Object} props
 * @param {Object} props.station - Station data object
 * @param {number} props.index - Index for React key prop
 * @param {Function} props.onSelect - Callback function when station is selected
 */
const StationMarker = ({ station, index, onSelect }) => {
    return (
        <Marker
            key={`station-${index}`}
            position={[parseFloat(station.station_lat), parseFloat(station.station_lon)]}
            icon={createStationMarkerIcon()}
            bubblingMouseEvents={false}
            eventHandlers={{
                click: () => onSelect(station),
                mouseover: (event) => event.target.openPopup(),
                mouseout: (event) => event.target.closePopup(),
            }}
            riseOnHover={true}
        >
            <Popup
                className="simple-station-popup"
                closeButton={false}
                autoPan={false}
            >
                <div style={{ textAlign: 'center', fontWeight: 'bold' }}>
                    {station.station_name}
                </div>
            </Popup>
        </Marker>
    );
};

export default StationMarker;