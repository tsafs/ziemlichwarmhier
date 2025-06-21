import StationMarker from './StationMarker';

/**
 * Component for rendering weather station markers overlay on the map
 * @param {Object} props
 * @param {Array} props.stations - Array of weather station data objects
 * @param {boolean} props.visible - Whether the overlay is visible
 * @param {Function} props.onStationSelect - Callback function when a station is selected
 * @param {Object} props.selectedStation - The currently selected station
 */
const StationsOverlay = ({ stations, visible, onStationSelect, selectedStation }) => {
    if (!visible || !stations?.length) return null;

    return (
        <>
            {stations.map((station, i) => (
                <StationMarker
                    key={`station-${station.station_id}`}
                    station={station}
                    index={i}
                    onSelect={onStationSelect}
                    isSelected={selectedStation && selectedStation.station_id === station.station_id}
                />
            ))}
        </>
    );
};

export default StationsOverlay;
