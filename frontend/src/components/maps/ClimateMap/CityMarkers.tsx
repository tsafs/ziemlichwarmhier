/**
 * CityMarkers Component
 *
 * Renders clickable city markers on the map.
 * Uses MapLibre GL Marker instances with DOM elements.
 *
 * Important: Never use `replaceWith()` on marker elements — MapLibre holds
 * an internal reference to the original element for position updates.
 * Instead, mutate styles in-place when selection state changes.
 */

import { useEffect, useRef, useCallback } from 'react';
import maplibregl, { type Map as MapLibreMap, type Marker, Popup } from 'maplibre-gl';
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

/** Apply visual styles to a marker element based on selection state. */
const applyMarkerStyles = (el: HTMLDivElement, isSelected: boolean): void => {
    el.style.width = isSelected ? '16px' : '12px';
    el.style.height = isSelected ? '16px' : '12px';
    el.style.borderRadius = '50%';
    el.style.backgroundColor = isSelected
        ? theme.colors.primary
        : theme.colors.hot;
    el.style.border = `2px solid ${isSelected ? 'white' : 'rgba(255,255,255,0.7)'}`;
    el.style.cursor = 'pointer';
    el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
    // Only transition color/size — never transition `transform`,
    // because MapLibre uses transform for positioning.
    el.style.transition = 'width 0.2s ease, height 0.2s ease, background-color 0.2s ease, border 0.2s ease';
};

/** Create a fresh marker DOM element. */
const createMarkerElement = (city: ICity, isSelected: boolean): HTMLDivElement => {
    const el = document.createElement('div');
    applyMarkerStyles(el, isSelected);
    el.title = city.name;
    return el;
};

/** Create a popup for the city name label on hover. */
const createCityPopup = (cityName: string): Popup =>
    new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        offset: 12,
        className: 'city-marker-popup',
    }).setText(cityName);

interface TrackedMarker {
    marker: Marker;
    popup: Popup;
    clickHandler: () => void;
}

const CityMarkers = ({ map, maxMarkers = 50 }: CityMarkersProps) => {
    const dispatch = useAppDispatch();
    const cities = useAppSelector(selectCities);
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);
    const markersRef = useRef<Map<string, TrackedMarker>>(new Map());

    const handleCityClick = useCallback(
        (cityId: string) => dispatch(selectCity(cityId)),
        [dispatch],
    );

    // Create / remove markers when cities change
    useEffect(() => {
        const cityList = Object.values(cities).slice(0, maxMarkers);
        const cityIds = new Set(cityList.map(c => c.id));

        // Remove markers for cities no longer in the list
        markersRef.current.forEach((tracked, id) => {
            if (!cityIds.has(id)) {
                tracked.marker.getElement().removeEventListener('click', tracked.clickHandler);
                tracked.popup.remove();
                tracked.marker.remove();
                markersRef.current.delete(id);
            }
        });

        // Add new markers (skip existing ones)
        cityList.forEach(city => {
            if (markersRef.current.has(city.id)) return;

            const isSelected = city.id === selectedCityId;
            const el = createMarkerElement(city, isSelected);

            const popup = createCityPopup(city.name);
            const clickHandler = () => handleCityClick(city.id);
            el.addEventListener('click', clickHandler);

            // Show city name on hover
            el.addEventListener('mouseenter', () => {
                popup.setLngLat([city.lon, city.lat]).addTo(map);
            });
            el.addEventListener('mouseleave', () => {
                popup.remove();
            });

            const marker = new maplibregl.Marker({ element: el })
                .setLngLat([city.lon, city.lat])
                .addTo(map);

            markersRef.current.set(city.id, { marker, popup, clickHandler });
        });

        // Cleanup on unmount only
        return () => {
            markersRef.current.forEach(tracked => {
                tracked.marker.getElement().removeEventListener('click', tracked.clickHandler);
                tracked.popup.remove();
                tracked.marker.remove();
            });
            markersRef.current.clear();
        };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [cities, map, maxMarkers, handleCityClick]);

    // Update marker styles when selection changes (no re-creation)
    useEffect(() => {
        markersRef.current.forEach((tracked, id) => {
            const el = tracked.marker.getElement() as HTMLDivElement;
            applyMarkerStyles(el, id === selectedCityId);
        });
    }, [selectedCityId]);

    return null; // Markers are rendered directly onto the map
};

export default CityMarkers;
