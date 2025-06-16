import React from 'react';
import CityMarker from './CityMarker';

/**
 * Component for rendering city markers overlay on the map
 * @param {Object} props
 * @param {Array} props.cities - Array of city data objects
 * @param {boolean} props.visible - Whether the overlay is visible
 */
const CitiesOverlay = ({ cities, visible }) => {
    if (!visible) return null;

    return (
        <>
            {cities.map((city, i) => (
                <CityMarker key={`city-${i}`} city={city} index={i} />
            ))}
        </>
    );
};

export default CitiesOverlay;
