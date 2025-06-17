import CityMarker from './CityMarker';

/**
 * Component for rendering weather station markers overlay on the map
 * @param {Object} props
 * @param {Array} props.stations - Array of weather station data objects
 * @param {boolean} props.visible - Whether the overlay is visible
 */
const StationsOverlay = ({ stations, visible }) => {
    if (!visible || !stations?.length) return null;

    return (
        <>
            {stations.map((station, i) => (
                <CityMarker key={`station-${station.station_id}`} city={station} index={i} />
            ))}
        </>
    );
};

export default StationsOverlay;
