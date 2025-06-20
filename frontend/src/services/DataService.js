// Constants
const DEBUG_MODE = process.env.NODE_ENV === 'development';

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
            url = `/ist-es-gerade-warm/station_data/10min_station_data_${year}${month}${day}.csv`;
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
                station_name: cols[1],
                data_date: cols[2],
                station_lat: parseFloat(cols[3]), // Using city_lat for compatibility with CityMarker
                station_lon: parseFloat(cols[4]), // Using city_lon for compatibility with CityMarker
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

/**
 * Service to fetch Europe's boundary GeoJSON data
 * @param {string} url - URL to the GeoJSON file (default: '/"europe.geojson"')
 * @returns {Promise<Object>} GeoJSON data for Europe's boundaries
 */
export const fetchEuropeBoundaries = async (url = '/europe.geojson') => {
    try {
        if (!DEBUG_MODE) {
            url = "/ist-es-gerade-warm/europe.geojson";
        }
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error loading boundaries:", error);
        throw error;
    }
};