/**
 * DateSelector Component
 *
 * Month/year picker for selecting which anomaly tiles to display.
 */

import { useMemo, useCallback } from 'react';
import type { CSSProperties, ChangeEvent } from 'react';
import { useAppDispatch } from '../../../store/hooks/useAppDispatch.js';
import { useAppSelector } from '../../../store/hooks/useAppSelector.js';
import { selectSelectedDate, setSelectedDate } from '../../../store/slices/mapSlice.js';
import { getAvailableYears, getAvailableMonths, getLatestAvailableDate } from '../../../services/TileService.js';
import { theme } from '../../../styles/design-system.js';

const MONTH_NAMES = [
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
    'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember',
];

const getContainerStyle = (): CSSProperties => ({
    position: 'absolute',
    top: 20,
    left: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.sm,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
    zIndex: 10,
    display: 'flex',
    gap: theme.spacing.sm,
    alignItems: 'center',
});

const getSelectStyle = (): CSSProperties => ({
    padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
    borderRadius: theme.borderRadius.sm,
    border: `1px solid ${theme.colors.border}`,
    fontSize: theme.typography.fontSize.sm,
    backgroundColor: 'white',
    cursor: 'pointer',
});

const getButtonStyle = (): CSSProperties => ({
    padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
    borderRadius: theme.borderRadius.sm,
    border: 'none',
    backgroundColor: theme.colors.primary,
    color: 'white',
    fontSize: theme.typography.fontSize.sm,
    cursor: 'pointer',
    fontWeight: theme.typography.fontWeight.medium,
});

const DateSelector = () => {
    const dispatch = useAppDispatch();
    const selectedDate = useAppSelector(selectSelectedDate);

    const availableYears = useMemo(() => getAvailableYears(), []);
    const availableMonths = useMemo(
        () => getAvailableMonths(selectedDate.year),
        [selectedDate.year],
    );

    const handleYearChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
        const year = parseInt(e.target.value, 10);
        const months = getAvailableMonths(year);
        // If current month not available in new year, use latest available
        const fallbackMonth = months[months.length - 1] ?? selectedDate.month;
        const month = months.includes(selectedDate.month)
            ? selectedDate.month
            : fallbackMonth;
        dispatch(setSelectedDate({ year, month }));
    }, [dispatch, selectedDate.month]);

    const handleMonthChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
        const month = parseInt(e.target.value, 10);
        dispatch(setSelectedDate({ ...selectedDate, month }));
    }, [dispatch, selectedDate]);

    const handleLatestClick = useCallback(() => {
        const latest = getLatestAvailableDate();
        dispatch(setSelectedDate(latest));
    }, [dispatch]);

    return (
        <div style={getContainerStyle()}>
            <select
                style={getSelectStyle()}
                value={selectedDate.month}
                onChange={handleMonthChange}
            >
                {availableMonths.map(month => (
                    <option key={month} value={month}>
                        {MONTH_NAMES[month - 1]}
                    </option>
                ))}
            </select>

            <select
                style={getSelectStyle()}
                value={selectedDate.year}
                onChange={handleYearChange}
            >
                {availableYears.map(year => (
                    <option key={year} value={year}>{year}</option>
                ))}
            </select>

            <button
                style={getButtonStyle()}
                onClick={handleLatestClick}
                type="button"
            >
                Aktuell
            </button>
        </div>
    );
};

export default DateSelector;
