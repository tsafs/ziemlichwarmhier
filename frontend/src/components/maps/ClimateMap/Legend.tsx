/**
 * Legend Component
 *
 * Displays color scale legend for temperature anomaly tiles.
 */

import { useMemo } from 'react';
import type { CSSProperties } from 'react';
import { theme } from '../../../styles/design-system.js';
import { MAP_CONFIG } from '../../../constants/mapConfig.js';

const getContainerStyle = (): CSSProperties => ({
    position: 'absolute',
    bottom: 20,
    left: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: theme.borderRadius?.md ?? '4px',
    padding: theme.spacing.sm,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
    zIndex: 10,
    minWidth: 200,
});

const getTitleStyle = (): CSSProperties => ({
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.textDark,
    marginBottom: theme.spacing.xs,
    textAlign: 'center' as const,
});

const getGradientStyle = (): CSSProperties => ({
    height: 12,
    width: '100%',
    borderRadius: 2,
    background: `linear-gradient(to right, 
        ${MAP_CONFIG.ANOMALY_COLORS.min}, 
        ${MAP_CONFIG.ANOMALY_COLORS.zero} 50%, 
        ${MAP_CONFIG.ANOMALY_COLORS.max})`,
});

const getLabelsStyle = (): CSSProperties => ({
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: theme.spacing.xs,
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.textDark,
});

interface LegendProps {
    title?: string;
}

const Legend = ({ title = 'Temperaturanomalie' }: LegendProps) => {
    const ticks = useMemo(() => {
        const { ANOMALY_MIN, ANOMALY_MAX } = MAP_CONFIG;
        return [ANOMALY_MIN, 0, ANOMALY_MAX].map(value =>
            `${value >= 0 ? '+' : ''}${value}°C`
        );
    }, []);

    return (
        <div style={getContainerStyle()}>
            <div style={getTitleStyle()}>{title}</div>
            <div style={getGradientStyle()} />
            <div style={getLabelsStyle()}>
                {ticks.map((tick, i) => (
                    <span key={i}>{tick}</span>
                ))}
            </div>
        </div>
    );
};

export default Legend;
