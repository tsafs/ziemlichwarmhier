import React, { Suspense, useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import { fetchLiveData } from './store/slices/liveDataSlice';
import { fetchCityData, selectCities } from './store/slices/cityDataSlice';
import { selectCity } from './store/slices/selectedCitySlice';
import { PREDEFINED_CITIES } from './constants/map';

import { useAppSelector } from './store/hooks/useAppSelector';
import { useAppDispatch } from './store/hooks/useAppDispatch';
import theme from './styles/design-system';
import type { CSSProperties } from 'react';

// Plot registry-based lazy loading
import { plots } from './components/plots/registry';
const ImpressumPage = React.lazy(() => import('./pages/ImpressumPage'));

const DEFAULT_CITY = 'berlin';

// Pure style computation functions
const getAppContainerStyle = (): CSSProperties => ({
    position: 'relative',
    width: '100%',
    minHeight: '100vh',
    overflowX: 'visible',
    backgroundColor: theme.colors.background,
    display: 'flex',
    flexDirection: 'column',
});

const getContentWrapperStyle = (): CSSProperties => ({
    width: '100%',
    position: 'relative',
    flex: 1,
});

const getLoadingContainerStyle = (): CSSProperties => ({
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    fontSize: '1.5rem',
    color: '#666',
});

const getErrorContainerStyle = (): CSSProperties => ({
    display: 'flex',
    justifyContent: 'center',
    textAlign: 'center',
    alignItems: 'center',
    padding: '100px',
    color: '#d32f2f',
    fontWeight: 500,
});

function AppContent() {
    const dispatch = useAppDispatch();
    const [error, setError] = useState<string | null>(null);
    const didFetchDataRef = useRef(false);

    const cities = useAppSelector(selectCities);
    const selectedCityId = useAppSelector(state => state.selectedCity.cityId);

    // Load live-data → city-data on mount
    useEffect(() => {
        if (didFetchDataRef.current) return;
        didFetchDataRef.current = true;

        const loadData = async () => {
            try {
                await dispatch(fetchLiveData()).unwrap();
                const stations = store.getState().liveData.data?.stations;
                if (stations) {
                    await dispatch(fetchCityData({ stations }));
                }
            } catch (err) {
                console.error('Failed to load data:', err);
                setError('There is currently no data available. Please try again later.');
            }
        };

        loadData();
    }, [dispatch]);

    // Select default city once cities are available
    useEffect(() => {
        if (selectedCityId || !cities) return;
        const city = Object.values(cities).find(
            c => PREDEFINED_CITIES.includes(c.name) && c.name.toLowerCase().includes(DEFAULT_CITY),
        );
        if (city) dispatch(selectCity(city.id, false));
    }, [cities, selectedCityId, dispatch]);

    const LazyEntries = React.useMemo(
        () => plots.map(p => ({ ...p, Comp: React.lazy(p.loader) })),
        [],
    );

    const MainPage = React.useMemo(
        () =>
            () => (
                <Suspense fallback={<div style={getLoadingContainerStyle()}>Loading map data...</div>}>
                    {!error &&
                        LazyEntries.map(entry => {
                            const Comp = entry.Comp;
                            return <Comp key={entry.id} />;
                        })}
                    {error && <div style={getErrorContainerStyle()}>{error}</div>}
                </Suspense>
            ),
        [error, LazyEntries],
    );

    return (
        <div style={getAppContainerStyle()}>
            <main style={getContentWrapperStyle()}>
                <Routes>
                    <Route path="/" element={<MainPage />} />
                    <Route
                        path="/impressum"
                        element={
                            <Suspense fallback={<div style={getLoadingContainerStyle()}>Loading...</div>}>
                                <ImpressumPage />
                            </Suspense>
                        }
                    />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </main>
        </div>
    );
}

function App() {
    return (
        <Provider store={store}>
            <BrowserRouter>
                <AppContent />
            </BrowserRouter>
        </Provider>
    );
}

export default App;