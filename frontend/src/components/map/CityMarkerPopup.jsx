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

                {/* Subtitle */}
                <div style={{
                    fontSize: '0.9rem',
                    color: '#666',
                    marginBottom: '20px'
                }}>
                    Placeholder - Yes, it's super hot here!
                </div>

                {/* Grid layout */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gridTemplateRows: 'repeat(2, auto)',
                    gap: '8px',
                    width: '100%'
                }}>
                    {/* First row */}
                    <div style={cellStyle}>
                        <BsThermometerSnow size={25} color="#1E88E5" /> {/* Freezing blue */}
                        <span style={{ marginLeft: '4px' }}>9.1°C</span>
                    </div>
                    <div style={cellStyle}>
                        <BsThermometerHalf size={25} color="#FF9800" /> {/* Moderate orange */}
                        <span style={{ marginLeft: '4px' }}>12.4°C</span>
                    </div>
                    <div style={cellStyle}>
                        <BsThermometerSun size={25} color="#F44336" /> {/* Blazing red */}
                        <span style={{ marginLeft: '4px' }}>18.2°C</span>
                    </div>

                    {/* Second row with dummy divs */}
                    <div style={cellStyle}>
                        {/* Empty dummy div */}
                    </div>
                    <div style={{ ...cellStyle, marginLeft: '-2px' }}>
                        <WiHumidity size={30} color="#444444" /> {/* Grey */}
                        <span style={{ marginLeft: '3px' }}>83%</span>
                    </div>
                    <div style={cellStyle}>
                        {/* Empty dummy div */}
                    </div>
                </div>
            </div>
        </Popup>
    );
};

export default CityMarkerPopup;
