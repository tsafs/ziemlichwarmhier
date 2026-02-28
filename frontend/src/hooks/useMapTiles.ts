/**
 * useMapTiles Hook
 *
 * Custom hook providing all data needed for the ClimateMap component.
 */

import { useMemo } from 'react';
import { useAppSelector } from '../store/hooks/useAppSelector.js';
import {
    selectMapViewport,
    selectSelectedDate,
    selectMapIsLoading,
    selectMapError,
} from '../store/slices/mapSlice.js';
import { selectCities, selectCityDataStatus } from '../store/slices/cityDataSlice.js';
import { getTileUrlTemplate, isDateAvailable } from '../services/TileService.js';
import type { MapViewport, SelectedDate, CityMarker } from '../types/map.js';

export interface UseMapTilesReturn {
    viewport: MapViewport;
    selectedDate: SelectedDate;
    tileUrlTemplate: string;
    isLoading: boolean;
    error: string | null;
    isDateValid: boolean;
    cityMarkers: CityMarker[];
    citiesLoaded: boolean;
}

export function useMapTiles(): UseMapTilesReturn {
    const viewport = useAppSelector(selectMapViewport);
    const selectedDate = useAppSelector(selectSelectedDate);
    const isLoading = useAppSelector(selectMapIsLoading);
    const error = useAppSelector(selectMapError);
    const cities = useAppSelector(selectCities);
    const cityDataStatus = useAppSelector(selectCityDataStatus);
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);

    const tileUrlTemplate = useMemo(
        () => getTileUrlTemplate(selectedDate.year, selectedDate.month),
        [selectedDate.year, selectedDate.month],
    );

    const isDateValid = useMemo(
        () => isDateAvailable(selectedDate.year, selectedDate.month),
        [selectedDate.year, selectedDate.month],
    );

    const cityMarkers = useMemo((): CityMarker[] => {
        return Object.values(cities).map(city => ({
            id: city.id,
            name: city.name,
            coordinates: [city.lon, city.lat] as [number, number],
            isSelected: city.id === selectedCityId,
        }));
    }, [cities, selectedCityId]);

    const citiesLoaded = cityDataStatus === 'succeeded';

    return {
        viewport,
        selectedDate,
        tileUrlTemplate,
        isLoading,
        error,
        isDateValid,
        cityMarkers,
        citiesLoaded,
    };
}
