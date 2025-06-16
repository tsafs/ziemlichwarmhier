import React from 'react';
import { Popup } from 'react-leaflet';

/**
 * Popup component for city markers
 * @param {Object} props
 * @param {Object} props.city - City data object
 */
const CityMarkerPopup = ({ city }) => (
    <Popup>
        <b>City:</b> {city.city_name}<br />
        <b>Grid:</b> X: {city.grid_x}, Y: {city.grid_y}
    </Popup>
);

export default CityMarkerPopup;
