/**
 * ClimateMap Component
 *
 * Interactive map displaying ERA5-Land temperature anomaly tiles
 * for Germany using MapLibre GL JS.
 */

import { useRef, useEffect, useCallback, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';
import maplibregl, { type Map as MapLibreMap } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useAppDispatch } from '../../../store/hooks/useAppDispatch.js';
import { useAppSelector } from '../../../store/hooks/useAppSelector.js';
import { selectMapViewport, selectSelectedDate, setViewport, setLoading } from '../../../store/slices/mapSlice.js';
import { MAP_CONFIG, BASE_MAP_STYLE } from '../../../constants/mapConfig.js';
import { getTileUrlTemplate } from '../../../services/TileService.js';
import { theme } from '../../../styles/design-system.js';
import Legend from './Legend.js';
import DateSelector from './DateSelector.js';
import CityMarkers from './CityMarkers.js';

const ANOMALY_LAYER_ID = 'anomaly-tiles';
const ANOMALY_SOURCE_ID = 'anomaly-source';

const getContainerStyle = (height: number | string): CSSProperties => ({
    position: 'relative',
    width: '100%',
    height,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
});

const getMapStyle = (): CSSProperties => ({
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
});

interface ClimateMapProps {
    height?: number | string;
    showControls?: boolean;
}

const ClimateMap = ({ height = 500, showControls = true }: ClimateMapProps) => {
    const dispatch = useAppDispatch();
    const mapContainerRef = useRef<HTMLDivElement>(null);
    const mapRef = useRef<MapLibreMap | null>(null);
    const [mapReady, setMapReady] = useState(false);

    const viewport = useAppSelector(selectMapViewport);
    const selectedDate = useAppSelector(selectSelectedDate);

    const tileUrlTemplate = useMemo(() =>
        getTileUrlTemplate(selectedDate.year, selectedDate.month),
    [selectedDate.year, selectedDate.month]);

    // Initialize map on mount
    useEffect(() => {
        if (!mapContainerRef.current || mapRef.current) return;

        const map = new maplibregl.Map({
            container: mapContainerRef.current,
            style: BASE_MAP_STYLE,
            center: viewport.center as [number, number],
            zoom: viewport.zoom,
            minZoom: MAP_CONFIG.MIN_ZOOM,
            maxZoom: MAP_CONFIG.MAX_ZOOM,
            maxBounds: MAP_CONFIG.GERMANY_BOUNDS,
        });

        map.on('load', () => {
            // Add anomaly tile source
            map.addSource(ANOMALY_SOURCE_ID, {
                type: 'raster',
                tiles: [tileUrlTemplate],
                tileSize: MAP_CONFIG.TILE_SIZE,
            });

            // Add anomaly tile layer (no base layer underneath)
            map.addLayer({
                id: ANOMALY_LAYER_ID,
                type: 'raster',
                source: ANOMALY_SOURCE_ID,
                paint: {
                    'raster-opacity': 1.0,
                    'raster-fade-duration': 300,
                },
            });

            dispatch(setLoading(false));
            setMapReady(true);
        });

        map.on('moveend', () => {
            const center = map.getCenter();
            dispatch(setViewport({
                center: [center.lng, center.lat],
                zoom: map.getZoom(),
            }));
        });

        map.on('error', (e) => {
            console.error('MapLibre error:', e);
        });

        mapRef.current = map;

        return () => {
            map.remove();
            mapRef.current = null;
            setMapReady(false);
        };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []); // Only run once on mount

    // Update tile source when selected date changes
    useEffect(() => {
        const map = mapRef.current;
        if (!map || !mapReady) return;

        const source = map.getSource(ANOMALY_SOURCE_ID);
        if (source && source.type === 'raster') {
            dispatch(setLoading(true));
            (source as maplibregl.RasterTileSource).setTiles([tileUrlTemplate]);
            // Reset loading after a short delay (tiles load asynchronously)
            setTimeout(() => dispatch(setLoading(false)), 500);
        }
    }, [tileUrlTemplate, mapReady, dispatch]);

    const containerStyle = useMemo(() => getContainerStyle(height), [height]);

    return (
        <div style={containerStyle}>
            <div ref={mapContainerRef} style={getMapStyle()} />
            {mapReady && mapRef.current && (
                <CityMarkers map={mapRef.current} />
            )}
            {showControls && (
                <>
                    <DateSelector />
                    <Legend />
                </>
            )}
        </div>
    );
};

export default ClimateMap;
