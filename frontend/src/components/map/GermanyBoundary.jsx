import { useEffect, useState } from 'react';
import { GeoJSON, useMap } from 'react-leaflet';
import * as turf from '@turf/turf';

/**
 * Component for rendering Germany's boundaries and masking other countries
 */
const GermanyBoundary = () => {
    const [germanyData, setGermanyData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const map = useMap();

    useEffect(() => {
        // Fetch Germany GeoJSON data
        const fetchGermanyBoundaries = async () => {
            try {
                setIsLoading(true);
                const response = await fetch('/germany.geojson');
                const data = await response.json();
                setGermanyData(data);

                // For more precise bounds if needed
                const bounds = turf.bbox(data);
                const latLngBounds = [
                    [bounds[1], bounds[0]],  // southwest corner [lat, lng]
                    [bounds[3], bounds[2]]   // northeast corner [lat, lng]
                ];

                // Update map with more precise bounds
                map.fitBounds(latLngBounds);
                map.setMaxBounds(latLngBounds);
            } catch (error) {
                console.error('Failed to load Germany boundaries:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchGermanyBoundaries();
    }, [map]);

    // Styles for the boundary and mask
    const germanyStyle = {
        fillColor: 'transparent',
        weight: 1,
        opacity: 1,
        color: '#666',
        fillOpacity: 0,
    };

    // If still loading, show a loading indicator or nothing
    if (isLoading || !germanyData) {
        return null;
    }

    return (
        <>
            {/* Germany outline */}
            <GeoJSON
                data={germanyData}
                style={germanyStyle}
            />
        </>
    );
};

export default GermanyBoundary;
