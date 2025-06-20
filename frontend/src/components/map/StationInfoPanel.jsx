import { WiHumidity } from 'react-icons/wi';
import { BsThermometerSnow, BsThermometerHalf, BsThermometerSun } from "react-icons/bs";
import './StationInfoPanel.css'; // We'll need to create this CSS file

/**
 * Panel component to display station information outside the map
 * @param {Object} props
 * @param {Object} props.selectedStation - Selected station data object
 */
const StationInfoPanel = ({ selectedStation }) => {
    // If no station is selected, show a placeholder
    if (!selectedStation) {
        return (
            <div className="station-info-panel">
                <div className="station-info-placeholder">
                    Klicke auf eine Wetterstation um Details anzuzeigen
                </div>
            </div>
        );
    }

    // Common cell style for consistency
    const cellStyle = {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        padding: '4px',
        minWidth: '70px'  // Ensure consistent width
    };

    return (
        <div className="station-info-panel">
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
            }}>
                {/* Station name */}
                <div style={{
                    fontWeight: 'bold',
                    fontSize: '1.2rem',
                    marginBottom: '20px'
                }}>
                    {selectedStation.station_name}
                </div>

                {/* Subtitle - only shown if content is provided */}
                {selectedStation.subtitle && (
                    <div style={{
                        fontSize: '0.9rem',
                        color: '#666',
                        marginBottom: '20px'
                    }}>
                        {selectedStation.subtitle}
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
                            {selectedStation.min_temperature !== undefined
                                ? `${selectedStation.min_temperature.toFixed(1)}°C`
                                : "N/A"}
                        </span>
                    </div>
                    <div style={cellStyle}>
                        <BsThermometerHalf size={25} color="#FF9800" /> {/* Moderate orange */}
                        <span style={{ marginLeft: '4px' }}>
                            {selectedStation.mean_temperature !== undefined
                                ? `${selectedStation.mean_temperature.toFixed(1)}°C`
                                : "N/A"}
                        </span>
                    </div>
                    <div style={cellStyle}>
                        <BsThermometerSun size={25} color="#F44336" /> {/* Blazing red */}
                        <span style={{ marginLeft: '4px' }}>
                            {selectedStation.max_temperature !== undefined
                                ? `${selectedStation.max_temperature.toFixed(1)}°C`
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
                            {selectedStation.humidity !== undefined
                                ? `${selectedStation.humidity.toFixed(0)}%`
                                : "N/A"}
                        </span>
                    </div>
                    <div style={cellStyle}>
                        {/* Empty div */}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StationInfoPanel;