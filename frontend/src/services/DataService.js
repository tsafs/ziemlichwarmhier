/**
 * Service to fetch city metadata from CSV file
 */
export const fetchCitiesMetadata = async () => {
    try {
        const response = await fetch('/cities_metadata.csv');
        const text = await response.text();

        const lines = text.split('\n');
        const header = lines[0].split(',');

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

export default {
    fetchCitiesMetadata
};
