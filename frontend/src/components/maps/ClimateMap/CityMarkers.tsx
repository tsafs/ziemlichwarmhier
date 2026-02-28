/**
 * CityMarkers Component
 *
 * Renders clickable city markers on the map.
 */

import { useEffect, useRef } from 'react';
import maplibregl, { type Map as MapLibreMap, type Marker } from 'maplibre-gl';
import { useAppDispatch } from '../../../store/hooks/useAppDispatch.js';
import { useAppSelector } from '../../../store/hooks/useAppSelector.js';
import { selectCities } from '../../../store/slices/cityDataSlice.js';
import { selectCity } from '../../../store/slices/selectedCitySlice.js';
import type { ICity } from '../../../classes/City.js';
import { theme } from '../../../styles/design-system.js';

interface CityMarkersProps {
    map: MapLibreMap;
    maxMarkers?: number;
}

const createMarkerElement = (city: ICity, isSelected: boolean): HTMLDivElement => {
    const el = document.createElement('div');
    el.style.width = isSelected ? '16px' : '12px';
    el.style.height = isSelected ? '16px' : '12px';
    el.style.borderRadius = '50%';
    el.style.backgroundColor = isSelected ? theme.colors.primary : theme.colors.hot;
    el.style.border = `2px solid ${isSelected ? 'white' : 'rgba(255,255,255,0.7)'}`;
    el.style.cursor = 'pointer';
    el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
    el.style.transition = 'all 0.2s ease';
    el.title = city.name;

    el.addEventListener('mouseenter', () => {
        el.style.transform = 'scale(1.2)';
    });
    el.addEventListener('mouseleave', () => {
        el.style.transform = 'scale(1)';
    });

    return el;
};

const CityMarkers = ({ map, maxMarkers = 50 }: CityMarkersProps) => {
    const dispatch = useAppDispatch();
    const cities = useAppSelector(selectCities);
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);
    const markersRef = useRef<Map<string, Marker>>(new Map());

    useEffect(() => {
        const cityList = Object.values(cities).slice(0, maxMarkers);

        // Remove old markers no longer in the list
        markersRef.current.forEach((marker, id) => {
            if (!cityList.find(c => c.id === id)) {
                marker.remove();
                markersRef.current.delete(id);
            }
        });

        // Add/update markers
        cityList.forEach(city => {
            const isSelected = city.id === selectedCityId;
            const existingMarker = markersRef.current.get(city.id);

            if (existingMarker) {
                // Replace element if selection changed
                const el = createMarkerElement(city, isSelected);
                el.addEventListener('click', () => dispatch(selectCity(city.id)));
                existingMarker.getElement().replaceWith(el);
            } else {
                // Create new marker
                const el = createMarkerElement(city, isSelected);
                el.addEventListener('click', () => dispatch(selectCity(city.id)));

                const marker = new maplibregl.Marker({ element: el })
                    .setLngLat([city.lon, city.lat])
                    .addTo(map);

                markersRef.current.set(city.id, marker);
            }
        });

        return () => {
            markersRef.current.forEach(marker => marker.remove());
            markersRef.current.clear();
        };
    }, [cities, selectedCityId, map, dispatch, maxMarkers]);

    return null; // Markers are rendered directly onto the map
};

export default CityMarkers;
