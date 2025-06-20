import { useEffect, useState } from 'react';
import { GeoJSON, Rectangle, useMap } from 'react-leaflet';
import * as turf from '@turf/turf';
import { fetchEuropeBoundaries } from '../../services/DataService';

/**
 * Component for rendering Europe's boundaries and masking other countries
 */
const EuropeBoundary = ({ fitBounds = false }) => {
    const [boundaryData, setBoundaryData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const map = useMap();

    useEffect(() => {
        // Fetch Europe GeoJSON data
        const loadGermanyBoundaries = async () => {
            try {
                setIsLoading(true);
                const data = await fetchEuropeBoundaries();
                setBoundaryData(data);

                if (fitBounds) {
                    // For more precise bounds if needed
                    const bounds = turf.bbox(data);
                    const latLngBounds = [
                        [bounds[1], bounds[0]],  // southwest corner [lat, lng]
                        [bounds[3], bounds[2]]   // northeast corner [lat, lng]
                    ];

                    // Update map with more precise bounds
                    map.fitBounds(latLngBounds);
                    map.setMaxBounds(latLngBounds);
                }
            } catch (error) {
                console.error('Failed to load Europe boundaries:', error);
            } finally {
                setIsLoading(false);
            }
        };

        loadGermanyBoundaries();
    }, [map, fitBounds]);

    // Styles for the boundary and mask
    const germanyStyle = {
        fillColor: 'white',
        weight: 1,
        opacity: 1,
        color: '#666',
        fillOpacity: 1,
    };

    const maskStyle = {
        fillColor: '#cdcdcd',
        color: 'transparent',
        fillOpacity: 1,
    };

    // If still loading, show a loading indicator or nothing
    if (isLoading || !boundaryData) {
        return null;
    }

    return (
        <>
            {/* Gray background for the entire world */}
            <Rectangle bounds={[
                [-90, -180], // southwest corner (whole world)
                [90, 180]    // northeast corner (whole world)
            ]} pathOptions={maskStyle} />

            <GeoJSON
                data={boundaryData}
                style={germanyStyle}
            />
        </>
    );
};

export default EuropeBoundary;
