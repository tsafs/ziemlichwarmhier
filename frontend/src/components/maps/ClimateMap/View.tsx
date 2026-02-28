/**
 * ClimateMapView
 *
 * Top-level view wrapper that integrates ClimateMap into the main page layout.
 * The map fills the available viewport height minus the (future) header.
 * Content below the map section is visible when the user scrolls down.
 *
 * Layout default: `--header-height: 0px` — set to actual header height once
 * the header component is implemented.
 */

import type { CSSProperties } from 'react';
import ClimateMap from './ClimateMap.js';
import { theme } from '../../../styles/design-system.js';

/**
 * Height of the section title row (heading + vertical padding).
 * Used to subtract from the viewport so the map itself fills the rest.
 */
const TITLE_ROW_HEIGHT_PX = 60;

const getSectionStyle = (): CSSProperties => ({
    width: '100%',
    backgroundColor: theme.colors.background,
    padding: `${theme.spacing.md}px ${theme.spacing.lg}px`,
    boxSizing: 'border-box',
});

const getTitleStyle = (): CSSProperties => ({
    color: theme.colors.textLight,
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    marginBottom: theme.spacing.md,
    fontFamily: theme.typography.fontFamily,
});

/**
 * Compute the map container height:
 * 100vh − header − title row padding.
 * Falls back to a reasonable minimum via clamp().
 */
const MAP_HEIGHT = `clamp(400px, calc(100vh - var(--header-height, 0px) - ${TITLE_ROW_HEIGHT_PX}px), 100vh)`;

const ClimateMapView = () => (
    <section style={getSectionStyle()}>
        <h2 style={getTitleStyle()}>Temperaturanomalie Deutschland</h2>
        <ClimateMap height={MAP_HEIGHT} showControls />
    </section>
);

export default ClimateMapView;
