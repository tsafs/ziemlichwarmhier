import { useState } from 'react';
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
    const [isOpen, setIsOpen] = useState(false);

    const handleMouseOver = () => {
        setIsOpen(true);
    };

    const handleMouseOut = () => {
        setIsOpen(false);
    };

    return (
        <Marker
            key={`city-${index}`}
            position={[parseFloat(city.city_lat), parseFloat(city.city_lon)]}
            icon={createCityMarkerIcon()}
            bubblingMouseEvents={false}
            eventHandlers={{
                mouseover: handleMouseOver,
                mouseout: handleMouseOut,
            }}
        >
            {isOpen && <CityMarkerPopup city={city} />}
        </Marker>
    );
};

export default CityMarker;