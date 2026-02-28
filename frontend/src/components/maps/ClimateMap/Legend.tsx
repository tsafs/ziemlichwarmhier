/**
 * Legend Component
 *
 * Displays color scale legend for temperature anomaly tiles.
 * Collapsible on mobile viewports to save screen space.
 */

import { useMemo, useState, useEffect, useCallback } from 'react';
import type { CSSProperties } from 'react';
import { theme } from '../../../styles/design-system.js';
import { MAP_CONFIG } from '../../../constants/mapConfig.js';

const MOBILE_BREAKPOINT = theme.breakpoints.tablet; // 768

const getContainerStyle = (collapsed: boolean): CSSProperties => ({
    position: 'absolute',
    bottom: 20,
    left: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
    zIndex: 10,
    minWidth: collapsed ? 'auto' : 200,
    cursor: collapsed ? 'pointer' : 'default',
    userSelect: 'none',
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

const getToggleStyle = (): CSSProperties => ({
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.textDark,
    cursor: 'pointer',
    background: 'none',
    border: 'none',
    padding: 0,
    textAlign: 'center' as const,
    width: '100%',
    marginTop: theme.spacing.xs,
    opacity: 0.6,
});

interface LegendProps {
    title?: string;
}

const Legend = ({ title = 'Temperaturanomalie' }: LegendProps) => {
    const [collapsed, setCollapsed] = useState(false);
    const [isMobile, setIsMobile] = useState(false);

    // Detect mobile viewport
    useEffect(() => {
        const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT}px)`);
        const onChange = (e: MediaQueryListEvent | MediaQueryList) => {
            setIsMobile(e.matches);
            if (e.matches) setCollapsed(true);
        };
        onChange(mql); // initial
        mql.addEventListener('change', onChange);
        return () => mql.removeEventListener('change', onChange);
    }, []);

    const toggle = useCallback(() => setCollapsed(c => !c), []);

    const ticks = useMemo(() => {
        const { ANOMALY_MIN, ANOMALY_MAX } = MAP_CONFIG;
        return [ANOMALY_MIN, 0, ANOMALY_MAX].map(value =>
            `${value >= 0 ? '+' : ''}${value}°C`
        );
    }, []);

    if (collapsed) {
        return (
            <div style={getContainerStyle(true)} onClick={toggle} role="button" tabIndex={0}>
                <div style={getTitleStyle()}>🌡️ Legende</div>
            </div>
        );
    }

    return (
        <div style={getContainerStyle(false)}>
            <div style={getTitleStyle()}>{title}</div>
            <div style={getGradientStyle()} />
            <div style={getLabelsStyle()}>
                {ticks.map((tick, i) => (
                    <span key={i}>{tick}</span>
                ))}
            </div>
            {isMobile && (
                <button type="button" style={getToggleStyle()} onClick={toggle}>
                    ▾ Einklappen
                </button>
            )}
        </div>
    );
};

export default Legend;
