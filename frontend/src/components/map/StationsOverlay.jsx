import StationMarker from './StationMarker';

/**
 * Component for rendering weather station markers overlay on the map
 * @param {Object} props
 * @param {Array} props.stations - Array of weather station data objects
 * @param {boolean} props.visible - Whether the overlay is visible
 * @param {Function} props.onStationSelect - Callback function when a station is selected
 */
const StationsOverlay = ({ stations, visible, onStationSelect }) => {
    if (!visible || !stations?.length) return null;

    return (
        <>
            {stations.map((station, i) => (
                <StationMarker
                    key={`station-${station.station_id}`}
                    station={station}
                    index={i}
                    onSelect={onStationSelect}
                />
            ))}
        </>
    );
};

export default StationsOverlay;
