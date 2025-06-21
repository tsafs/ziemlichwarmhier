import { useState, useEffect, useRef } from 'react';
import './StationSearch.css';

/**
 * Component for searching and selecting weather stations
 * @param {Object} props
 * @param {Array} props.stations - Array of station data objects
 * @param {Object} props.selectedStation - Currently selected station
 * @param {Function} props.onStationSelect - Callback for when a station is selected
 */
const StationSearch = ({ stations, selectedStation, onStationSelect }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [filteredStations, setFilteredStations] = useState([]);
    const [focusedIndex, setFocusedIndex] = useState(-1);
    const searchRef = useRef(null);
    const inputRef = useRef(null);

    // Handle clicks outside of the dropdown to close it
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchRef.current && !searchRef.current.contains(event.target)) {
                setIsDropdownOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    // Filter stations based on search term with improved matching
    useEffect(() => {
        if (!searchTerm.trim()) {
            setFilteredStations([]);
            return;
        }

        const searchTermLower = searchTerm.toLowerCase();

        // First, try exact matches (includes)
        let filtered = stations.filter(station =>
            station.station_name.toLowerCase().includes(searchTermLower)
        );

        // If we have few results, add fuzzy matches (station names that might have typos)
        if (filtered.length < 5) {
            const fuzzyMatches = stations.filter(station => {
                const stationName = station.station_name.toLowerCase();

                // Don't include stations already in filtered results
                if (stationName.includes(searchTermLower)) {
                    return false;
                }

                // Check if most characters match (allowing for some typos)
                let matches = 0;
                for (let char of searchTermLower) {
                    if (stationName.includes(char)) {
                        matches++;
                    }
                }

                // If at least 70% of characters match, include it
                return matches / searchTermLower.length >= 0.7;
            });

            filtered = [...filtered, ...fuzzyMatches].slice(0, 15); // Limit to 15 results
        }

        // Sort results: exact matches first, then by name length (shorter names first)
        filtered.sort((a, b) => {
            const aName = a.station_name.toLowerCase();
            const bName = b.station_name.toLowerCase();

            // Exact matches come first
            const aExact = aName.includes(searchTermLower);
            const bExact = bName.includes(searchTermLower);

            if (aExact && !bExact) return -1;
            if (!aExact && bExact) return 1;

            // If both are exact or both are fuzzy, sort by length
            return aName.length - bName.length;
        });

        setFilteredStations(filtered);
    }, [searchTerm, stations]);

    // Handle station selection
    const handleStationSelect = (station) => {
        onStationSelect(station);
        setSearchTerm('');
        setIsDropdownOpen(false);
    };

    // Reset focused index when filtered stations change
    useEffect(() => {
        setFocusedIndex(-1);
    }, [filteredStations]);

    return (
        <div ref={searchRef} className="station-search-container">
            <div className="station-search-input-container">
                <input
                    ref={inputRef}
                    type="text"
                    placeholder="Wetterstation suchen..."
                    value={searchTerm}
                    onChange={(e) => {
                        setSearchTerm(e.target.value);
                        setIsDropdownOpen(true);
                    }}
                    onClick={() => setIsDropdownOpen(true)}
                    className="station-search-input"
                />

                {isDropdownOpen && searchTerm && (
                    <div className="station-search-dropdown">
                        {filteredStations.length > 0 ? (
                            filteredStations.map((station, index) => (
                                <div
                                    key={station.station_id || index}
                                    onClick={() => handleStationSelect(station)}
                                    className={`station-search-item ${selectedStation && selectedStation.station_id === station.station_id ? 'station-search-item-selected' : ''} ${focusedIndex === index ? 'station-search-item-focused' : ''}`}
                                    title={`${station.station_name}: ${station.mean_temperature !== undefined ? `${station.mean_temperature.toFixed(1)}°C` : 'N/A'} | Luftfeuchtigkeit: ${station.humidity !== undefined ? `${station.humidity.toFixed(0)}%` : 'N/A'}`}
                                >
                                    <span>{station.station_name}</span>
                                    <span className="station-search-item-temperature">
                                        {station.mean_temperature !== undefined ? `${station.mean_temperature.toFixed(1)}°C` : ''}
                                    </span>
                                </div>
                            ))
                        ) : (
                            <div className="station-search-item">
                                Keine Stationen gefunden
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default StationSearch;
