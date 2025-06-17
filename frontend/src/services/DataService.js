/**
 * Service to fetch city metadata from CSV file
 */
export const fetchCitiesMetadata = async () => {
    try {
        const response = await fetch('/cities_metadata.csv');
        const text = await response.text();

        const lines = text.split('\n');

        // Parse CSV data into array of city objects
        const data = lines.slice(1).map(line => {
            const cols = line.split(',');
            if (cols.length < 10) return null;

            return {
                city_id: cols[0],
                city_name: cols[1],
                city_lat: parseFloat(cols[2]),
                city_lon: parseFloat(cols[3]),
                grid_y: parseInt(cols[4]),
                grid_x: parseInt(cols[5]),
                grid_lat1: parseFloat(cols[6]),
                grid_lon1: parseFloat(cols[7]),
                grid_lat2: parseFloat(cols[8]),
                grid_lon2: parseFloat(cols[9])
            };
        }).filter(Boolean); // Remove null entries

        return data;
    } catch (error) {
        console.error("Error loading cities data:", error);
        throw error;
    }
};

/**
 * Service to fetch weather stations data from CSV file
 * @param {string} filename - Name of the CSV file (default: 'active_stations_daily.csv')
 * @returns {Promise<Array>} Array of station data objects
 */
export const fetchWeatherStationsData = async (filename = 'active_stations_daily.csv') => {
    try {
        const response = await fetch(`/${filename}`);
        const text = await response.text();

        const lines = text.split('\n');

        // Parse CSV data into array of station objects
        const data = lines.slice(1).map(line => {
            if (!line.trim()) return null; // Skip empty lines

            const cols = line.split(',');
            if (cols.length < 13) return null; // Ensure we have all required columns

            // Format date for subtitle
            const fromDate = formatDate(cols[1]);
            const toDate = formatDate(cols[2]);
            const subtitle = `Data from ${fromDate} to ${toDate}`;

            return {
                station_id: cols[0],
                from_date: cols[1],
                to_date: cols[2],
                city_lat: parseFloat(cols[3]), // Using city_lat for compatibility with CityMarker
                city_lon: parseFloat(cols[4]), // Using city_lon for compatibility with CityMarker
                mean_temperature_date: cols[5],
                mean_temperature: parseFloat(cols[6]),
                min_temperature_date: cols[7],
                min_temperature: parseFloat(cols[8]),
                max_temperature_date: cols[9],
                max_temperature: parseFloat(cols[10]),
                humidity_date: cols[11],
                humidity: parseFloat(cols[12]),
                city_name: cols[0], // Use station_id as city_name for compatibility with CityMarker
                subtitle: subtitle
            };
        }).filter(Boolean); // Remove null entries

        return data;
    } catch (error) {
        console.error(`Error loading weather stations data from ${filename}:`, error);
        throw error;
    }
};

// Helper function to format date from YYYYMMDD to YYYY-MM-DD
const formatDate = (dateString) => {
    if (!dateString || dateString.length !== 8) return dateString;
    return `${dateString.substring(0, 4)}-${dateString.substring(4, 6)}-${dateString.substring(6, 8)}`;
};
