/**
 * ClimateMapView
 *
 * Top-level view wrapper that integrates ClimateMap into the main page layout.
 */

import type { CSSProperties } from 'react';
import ClimateMap from './ClimateMap.js';
import { theme } from '../../../styles/design-system.js';

const getSectionStyle = (): CSSProperties => ({
    width: '100%',
    backgroundColor: theme.colors.background,
    padding: `${theme.spacing.xl}px ${theme.spacing.lg}px`,
    boxSizing: 'border-box',
});

const getTitleStyle = (): CSSProperties => ({
    color: theme.colors.textLight,
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    marginBottom: theme.spacing.md,
    fontFamily: theme.typography.fontFamily,
});

const ClimateMapView = () => (
    <section style={getSectionStyle()}>
        <h2 style={getTitleStyle()}>Temperaturanomalie Deutschland</h2>
        <ClimateMap height={550} showControls={true} />
    </section>
);

export default ClimateMapView;
