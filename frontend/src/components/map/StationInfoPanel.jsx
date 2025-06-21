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
                    Klicke auf eine Wetterstation oder nutze die Suche um Details anzuzeigen
                </div>
            </div>
        );
    }

    const labelStyle = {
        fontSize: '0.8rem',
        color: '#666',
        fontWeight: 'bold',
        textTransform: 'uppercase',
    }

    const valueStyle = {
        fontSize: '1.2rem',
        fontWeight: 'bold',
        color: '#333',
        padding: '4px'
    };

    // Common cell style for consistency
    const cellStyle = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '4px',
        minWidth: '70px'  // Ensure consistent width
    };

    return (
        <div className="station-info-panel">
            <div style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                textAlign: 'center',
            }}>
                <div style={cellStyle}>
                    <span style={labelStyle}>Zuletzt</span>
                    <span style={valueStyle}>
                        {selectedStation.mean_temperature !== undefined
                            ? `${selectedStation.mean_temperature.toFixed(1)}°C`
                            : "N/A"}
                    </span>
                </div>
                <div style={cellStyle}>
                    <span style={labelStyle}>Min</span>
                    <span style={valueStyle}>
                        {selectedStation.min_temperature !== undefined
                            ? `${selectedStation.min_temperature.toFixed(1)}°C`
                            : "N/A"}
                    </span>
                </div>
                <div style={cellStyle}>
                    <span style={labelStyle}>Max</span>
                    <span style={valueStyle}>
                        {selectedStation.max_temperature !== undefined
                            ? `${selectedStation.max_temperature.toFixed(1)}°C`
                            : "N/A"}
                    </span>
                </div>
                <div style={cellStyle}>
                    <span style={labelStyle}>Luft</span>
                    <span style={valueStyle}>
                        {selectedStation.humidity !== undefined
                            ? `${selectedStation.humidity.toFixed(0)}%`
                            : "N/A"}
                    </span>
                </div>

                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'start',
                    marginLeft: '20px',
                }}>
                    <div style={{
                        fontWeight: 'bold',
                        fontSize: '1.2rem',
                    }}>
                        {selectedStation.station_name}
                    </div>

                    {selectedStation.subtitle && (
                        <div style={{
                            fontSize: '0.8rem',
                            color: '#666',
                            marginTop: '2px',
                        }}>
                            {`${selectedStation.data_date + ' Uhr'}`}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StationInfoPanel;