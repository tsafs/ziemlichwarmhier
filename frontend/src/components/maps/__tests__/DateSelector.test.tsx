/**
 * DateSelector Component Tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { createElement, type PropsWithChildren } from 'react';
import mapReducer, { setSelectedDate } from '../../../store/slices/mapSlice.js';
import DateSelector from '../ClimateMap/DateSelector.js';

function createTestStore() {
    return configureStore({
        reducer: {
            map: mapReducer,
        },
    });
}

function createWrapper(store: ReturnType<typeof createTestStore>) {
    return ({ children }: PropsWithChildren) =>
        createElement(Provider, { store, children });
}

describe('DateSelector', () => {
    it('renders month and year dropdowns', () => {
        const store = createTestStore();
        render(<DateSelector />, { wrapper: createWrapper(store) });

        const comboboxes = screen.getAllByRole('combobox');
        expect(comboboxes).toHaveLength(2);
    });

    it('renders the "Aktuell" button', () => {
        const store = createTestStore();
        render(<DateSelector />, { wrapper: createWrapper(store) });

        expect(screen.getByRole('button', { name: 'Aktuell' })).toBeInTheDocument();
    });

    it('shows all 12 months for a complete historical year', () => {
        const store = createTestStore();
        store.dispatch(setSelectedDate({ year: 2020, month: 6 }));
        render(<DateSelector />, { wrapper: createWrapper(store) });

        // Month dropdown is the first combobox
        const monthDropdown = screen.getAllByRole('combobox')[0];
        const options = monthDropdown.querySelectorAll('option');
        expect(options).toHaveLength(12);
        expect(options[0].textContent).toBe('Januar');
        expect(options[11].textContent).toBe('Dezember');
    });

    it('year dropdown starts from 2016', () => {
        const store = createTestStore();
        render(<DateSelector />, { wrapper: createWrapper(store) });

        const yearDropdown = screen.getAllByRole('combobox')[1];
        const options = yearDropdown.querySelectorAll('option');
        expect(options[0].textContent).toBe('2016');
    });

    it('dispatches setSelectedDate when month is changed', () => {
        const store = createTestStore();
        store.dispatch(setSelectedDate({ year: 2020, month: 6 }));
        render(<DateSelector />, { wrapper: createWrapper(store) });

        const monthDropdown = screen.getAllByRole('combobox')[0];
        fireEvent.change(monthDropdown, { target: { value: '3' } });

        const state = store.getState();
        expect(state.map.selectedDate.month).toBe(3);
        expect(state.map.selectedDate.year).toBe(2020);
    });

    it('dispatches setSelectedDate when year is changed', () => {
        const store = createTestStore();
        store.dispatch(setSelectedDate({ year: 2020, month: 6 }));
        render(<DateSelector />, { wrapper: createWrapper(store) });

        const yearDropdown = screen.getAllByRole('combobox')[1];
        fireEvent.change(yearDropdown, { target: { value: '2022' } });

        const state = store.getState();
        expect(state.map.selectedDate.year).toBe(2022);
    });

    it('"Aktuell" button sets the latest available date', () => {
        const store = createTestStore();
        store.dispatch(setSelectedDate({ year: 2018, month: 3 }));
        render(<DateSelector />, { wrapper: createWrapper(store) });

        fireEvent.click(screen.getByRole('button', { name: 'Aktuell' }));

        const { year, month } = store.getState().map.selectedDate;
        // Should be a recent date, not 2018/3
        expect(year).toBeGreaterThanOrEqual(2025);
        expect(month).toBeGreaterThanOrEqual(1);
        expect(month).toBeLessThanOrEqual(12);
    });

    it('disables future months by not including them', () => {
        const store = createTestStore();
        const currentYear = new Date().getFullYear();
        store.dispatch(setSelectedDate({ year: currentYear, month: 1 }));
        render(<DateSelector />, { wrapper: createWrapper(store) });

        const monthDropdown = screen.getAllByRole('combobox')[0];
        const options = monthDropdown.querySelectorAll('option');
        // Current year should have fewer than 12 months available
        // (ERA5-Land has ~5 day delay so current month is not available)
        expect(options.length).toBeLessThan(12);
    });
});
