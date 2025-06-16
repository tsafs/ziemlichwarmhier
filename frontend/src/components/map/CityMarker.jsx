import { Marker } from 'react-leaflet';
import createCityMarkerIcon from './CityMarkerIcon';
import CityMarkerPopup from './CityMarkerPopup';

/**
 * Component for rendering a city marker on the map
 * @param {Object} props
 * @param {Object} props.city - City data object
 * @param {number} props.index - Index for React key prop
 */
const CityMarker = ({ city, index }) => {
    return (
        <Marker
            key={`city-${index}`}
            position={[parseFloat(city.city_lat), parseFloat(city.city_lon)]}
            icon={createCityMarkerIcon()}
            bubblingMouseEvents={false}
            eventHandlers={{
                mouseover: (event) => event.target.openPopup(),
                mouseout: (event) => event.target.closePopup(),
            }}
            riseOnHover={true}
        >
            <CityMarkerPopup city={city} />
        </Marker>
    );
};

export default CityMarker;