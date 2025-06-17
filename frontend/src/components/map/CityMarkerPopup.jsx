import { Popup } from 'react-leaflet';
import { WiHumidity } from 'react-icons/wi';
import { BsThermometerSnow, BsThermometerHalf, BsThermometerSun } from "react-icons/bs";
import './CityMarkerPopup.css'; // Add a CSS import (will create this file next)

/**
 * Popup component for city markers
 * @param {Object} props
 * @param {Object} props.city - City data object
 */
const CityMarkerPopup = ({ city }) => {
    // Common cell style for consistency
    const cellStyle = {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        padding: '4px',
        minWidth: '70px'  // Ensure consistent width
    };

    return (
        <Popup autoPan={false} closeButton={false} className="transparent-popup">
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
            }}>
                {/* City name */}
                <div style={{
                    fontWeight: 'bold',
                    fontSize: '1.2rem',
                    marginBottom: '20px'
                }}>
                    {city.city_name}
                </div>

                {/* Subtitle - only shown if content is provided */}
                {city.subtitle && (
                    <div style={{
                        fontSize: '0.9rem',
                        color: '#666',
                        marginBottom: '20px'
                    }}>
                        {city.subtitle}
                    </div>
                )}

                {/* Grid layout */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gridTemplateRows: 'repeat(2, auto)',
                    gap: '8px',
                    width: '100%'
                }}>
                    {/* First row - Temperature values */}
                    <div style={cellStyle}>
                        <BsThermometerSnow size={25} color="#1E88E5" /> {/* Freezing blue */}
                        <span style={{ marginLeft: '4px' }}>
                            {city.min_temperature !== undefined
                                ? `${city.min_temperature.toFixed(1)}°C`
                                : "N/A"}
                        </span>
                    </div>
                    <div style={cellStyle}>
                        <BsThermometerHalf size={25} color="#FF9800" /> {/* Moderate orange */}
                        <span style={{ marginLeft: '4px' }}>
                            {city.mean_temperature !== undefined
                                ? `${city.mean_temperature.toFixed(1)}°C`
                                : "N/A"}
                        </span>
                    </div>
                    <div style={cellStyle}>
                        <BsThermometerSun size={25} color="#F44336" /> {/* Blazing red */}
                        <span style={{ marginLeft: '4px' }}>
                            {city.max_temperature !== undefined
                                ? `${city.max_temperature.toFixed(1)}°C`
                                : "N/A"}
                        </span>
                    </div>

                    {/* Second row - Humidity and empty cells */}
                    <div style={cellStyle}>
                        {/* Empty div */}
                    </div>
                    <div style={{ ...cellStyle, marginLeft: '-2px' }}>
                        <WiHumidity size={30} color="#444444" /> {/* Grey */}
                        <span style={{ marginLeft: '3px' }}>
                            {city.humidity !== undefined
                                ? `${city.humidity.toFixed(0)}%`
                                : "N/A"}
                        </span>
                    </div>
                    <div style={cellStyle}>
                        {/* Empty div */}
                    </div>
                </div>
            </div>
        </Popup>
    );
};

export default CityMarkerPopup;
