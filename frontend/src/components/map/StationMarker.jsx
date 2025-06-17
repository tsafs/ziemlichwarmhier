import { Marker } from 'react-leaflet';
import createStationMarkerIcon from './StationMarkerIcon';
import CityMarkerPopup from './CityMarkerPopup';

/**
 * Component for rendering a weather station marker on the map
 * @param {Object} props
 * @param {Object} props.station - Weather station data object
 * @param {number} props.index - Index for React key prop
 */
const StationMarker = ({ station, index }) => {
    return (
        <Marker
            key={`station-${index}`}
            position={[parseFloat(station.city_lat), parseFloat(station.city_lon)]}
            icon={createStationMarkerIcon()}
            bubblingMouseEvents={false}
            eventHandlers={{
                mouseover: (event) => event.target.openPopup(),
                mouseout: (event) => event.target.closePopup(),
            }}
            riseOnHover={true}
        >
            <CityMarkerPopup city={station} />
        </Marker>
    );
};

export default StationMarker;
