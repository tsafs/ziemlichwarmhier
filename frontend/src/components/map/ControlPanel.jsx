import React from 'react';

/**
 * Control Panel overlay for map configuration
 * @param {Object} props
 * @param {number} props.citiesCount - Number of cities displayed
 * @param {boolean} props.showCities - Whether cities overlay is visible
 * @param {Function} props.setShowCities - Function to toggle cities visibility
 * @param {boolean} props.showGrid - Whether grid overlay is visible
 * @param {Function} props.setShowGrid - Function to toggle grid visibility
 * @param {boolean} props.isDebugMode - Whether debug mode is enabled
 */
const ControlPanel = ({
    citiesCount,
    showCities,
    setShowCities,
    showGrid,
    setShowGrid,
    isDebugMode = false
}) => {
    return (
        <div style={{
            position: 'absolute',
            zIndex: 1000,
            background: 'rgba(255,255,255,0.9)',
            padding: 12,
            borderRadius: 8,
            left: 20,
            top: 20,
            boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
        }}>
            <div style={{ marginBottom: 8, fontWeight: 'bold', borderBottom: '1px solid #eee', paddingBottom: 5 }}>
                Map Controls
            </div>

            <div style={{ marginBottom: 8 }}>
                <span>Cities displayed: <b>{citiesCount}</b></span>
            </div>

            {isDebugMode && (
                <>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                        <label htmlFor="show-cities">Show cities overlay:</label>
                        <input
                            id="show-cities"
                            type="checkbox"
                            checked={showCities}
                            onChange={e => setShowCities(e.target.checked)}
                        />
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <label htmlFor="show-grid">Show grid overlay:</label>
                        <input
                            id="show-grid"
                            type="checkbox"
                            checked={showGrid}
                            onChange={e => setShowGrid(e.target.checked)}
                        />
                    </div>
                </>
            )}
        </div>
    );
};

export default ControlPanel;
