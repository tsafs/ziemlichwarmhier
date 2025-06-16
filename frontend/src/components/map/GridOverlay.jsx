import React from 'react';
import GridItem from './GridItem';

/**
 * Component for rendering grid overlay on the map
 * @param {Object} props
 * @param {Array} props.cities - Array of city data objects
 * @param {boolean} props.visible - Whether the overlay is visible
 */
const GridOverlay = ({ cities, visible }) => {
    if (!visible) return null;

    return (
        <>
            {cities.map((city, i) => (
                <GridItem key={`grid-${i}`} city={city} index={i} />
            ))}
        </>
    );
};

export default GridOverlay;
