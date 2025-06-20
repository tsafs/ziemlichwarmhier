import React from 'react';

/**
 * Control Panel overlay for map configuration
 * @param {Object} props
 * @param {boolean} props.showGrid - Whether grid overlay is visible
 * @param {Function} props.setShowGrid - Function to toggle grid visibility
 * @param {boolean} props.showStations - Whether stations overlay is visible
 * @param {Function} props.setShowStations - Function to toggle stations visibility
 * @param {number} props.stationsCount - Number of stations displayed
 */
const ControlPanel = ({
    showGrid,
    setShowGrid,
    showStations = false,
    setShowStations = () => { },
    stationsCount = 0,
}) => {
    return (
        <div style={{ marginTop: 20 }}>
            <div style={{ marginBottom: 8, fontWeight: 'bold', borderBottom: '1px solid #eee', paddingBottom: 5 }}>
                Debug Map Controls
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <label htmlFor="show-grid">Show grid overlay:</label>
                <input
                    id="show-grid"
                    type="checkbox"
                    checked={showGrid}
                    onChange={e => setShowGrid(e.target.checked)}
                />
            </div>

            <div style={{ marginBottom: 8 }}>
                <span>Weather stations displayed: <b>{stationsCount}</b></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <label htmlFor="show-stations">Show weather stations:</label>
                <input
                    id="show-stations"
                    type="checkbox"
                    checked={showStations}
                    onChange={e => setShowStations(e.target.checked)}
                />
            </div>
        </div >
    );
};

export default ControlPanel;
