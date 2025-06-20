import React from 'react';
import { Rectangle } from 'react-leaflet';

/**
 * Component for rendering a grid rectangle on the map
 * @param {Object} props
 * @param {Object} props.station - Station data with grid information
 * @param {number} props.index - Index for React key prop
 */
const GridItem = ({ station, index }) => {
    // Create bounds for the grid rectangle
    const bounds = [
        [parseFloat(station.grid_lat1), parseFloat(station.grid_lon1)],
        [parseFloat(station.grid_lat2), parseFloat(station.grid_lon2)]
    ];

    return (
        <Rectangle
            key={`grid-${index}`}
            bounds={bounds}
            pathOptions={{ color: '#FF0000', weight: 1, fillOpacity: 0.2 }}
        />
    );
};

export default GridItem;
