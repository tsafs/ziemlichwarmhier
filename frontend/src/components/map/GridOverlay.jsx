import React from 'react';
import GridItem from './GridItem';

/**
 * Component for rendering grid overlay on the map
 * @param {Object} props
 * @param {Array} props.stations - Array of station data objects
 * @param {boolean} props.visible - Whether the overlay is visible
 */
const GridOverlay = ({ stations, visible }) => {
    if (!visible) return null;

    return (
        <>
            {stations.map((station, i) => (
                <GridItem key={`grid-${i}`} station={station} index={i} />
            ))}
        </>
    );
};

export default GridOverlay;
