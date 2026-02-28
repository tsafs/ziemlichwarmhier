/**
 * Legend Component Tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Legend from '../ClimateMap/Legend.js';

describe('Legend', () => {
    it('renders the default title', () => {
        render(<Legend />);
        expect(screen.getByText('Temperaturanomalie')).toBeInTheDocument();
    });

    it('renders a custom title', () => {
        render(<Legend title="Custom Title" />);
        expect(screen.getByText('Custom Title')).toBeInTheDocument();
    });

    it('renders all tick labels', () => {
        render(<Legend />);
        expect(screen.getByText('-3°C')).toBeInTheDocument();
        expect(screen.getByText('+0°C')).toBeInTheDocument();
        expect(screen.getByText('+3°C')).toBeInTheDocument();
    });

    it('renders the gradient bar', () => {
        const { container } = render(<Legend />);
        // Find the gradient element by its background style
        const gradientEl = container.querySelector('[style*="linear-gradient"]');
        expect(gradientEl).not.toBeNull();
    });
});
