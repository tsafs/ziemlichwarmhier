// Constants
const DEBUG_MODE = process.env.NODE_ENV === 'development';

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
export const fetchDailyWeatherStationsData = async (filename = 'active_stations_daily.csv') => {
    try {
        const response = await fetch(`/${filename}`);
        const text = await response.text();

        const lines = text.split('\n');

        // Parse CSV data into array of station objects
        const data = lines.slice(1).map(line => {
            if (!line.trim()) return null; // Skip empty lines

            const cols = line.split(',');
            if (cols.length < 14) return null; // Ensure we have all required columns

            // Format date for subtitle
            const fromDate = formatDate(cols[2]);
            const toDate = formatDate(cols[3]);
            const subtitle = `Data from ${fromDate} to ${toDate}`;

            return {
                station_id: cols[0],
                city_name: cols[1],
                from_date: cols[2],
                to_date: cols[3],
                city_lat: parseFloat(cols[4]), // Using city_lat for compatibility with CityMarker
                city_lon: parseFloat(cols[5]), // Using city_lon for compatibility with CityMarker
                mean_temperature_date: cols[6],
                mean_temperature: parseFloat(cols[7]),
                min_temperature_date: cols[8],
                min_temperature: parseFloat(cols[9]),
                max_temperature_date: cols[10],
                max_temperature: parseFloat(cols[11]),
                humidity_date: cols[12],
                humidity: parseFloat(cols[13]),
                subtitle: subtitle
            };
        }).filter(Boolean); // Remove null entries

        return data;
    } catch (error) {
        console.error(`Error loading weather stations data from ${filename}:`, error);
        throw error;
    }
};

/**
 * Service to fetch weather stations data from CSV file
 * @param {string} url - Name of the CSV file (default: '/active_stations_daily.csv')
 * @returns {Promise<Array>} Array of station data objects
 */
export const fetchLatestWeatherStationsData = async (url = '/station_10min_data.csv') => {
    try {
        if (!DEBUG_MODE) {
            // Get today's date in YYYYMMDD format
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
            const day = String(today.getDate()).padStart(2, '0');
            url = `/10min_station_data_${year}${month}${day}.csv`;
        }

        const response = await fetch(url);

        // in case of a 404 error, error out
        if (!response.ok) {
            throw new Error(`Failed to fetch data from ${url}: ${response.status} ${response.statusText}. Are you in the wrong timezone? Our data is based on UTC.`);
        }

        const text = await response.text();

        const lines = text.split('\n');

        // Parse CSV data into array of station objects
        const data = lines.slice(1).map(line => {
            if (!line.trim()) return null; // Skip empty lines

            const cols = line.split(',');
            if (cols.length < 9) return null; // Ensure we have all required columns

            return {
                station_id: cols[0],
                city_name: cols[1],
                data_date: cols[2],
                city_lat: parseFloat(cols[3]), // Using city_lat for compatibility with CityMarker
                city_lon: parseFloat(cols[4]), // Using city_lon for compatibility with CityMarker
                mean_temperature: parseFloat(cols[7]),
                min_temperature: parseFloat(cols[8]),
                max_temperature: parseFloat(cols[6]),
                humidity: parseFloat(cols[5]),
                subtitle: `Aktualisiert um ${cols[2] ? cols[2] + ' Uhr' : 'unbekannt'}`
            };
        }).filter(Boolean); // Remove null entries

        return data;
    } catch (error) {
        console.error(`Error loading weather stations data from ${url}:`, error);
        throw error;
    }
};

// Helper function to format date from YYYYMMDD to YYYY-MM-DD
const formatDate = (dateString) => {
    if (!dateString || dateString.length !== 8) return dateString;
    return `${dateString.substring(0, 4)}-${dateString.substring(4, 6)}-${dateString.substring(6, 8)}`;
};
