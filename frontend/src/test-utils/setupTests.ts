/**
 * Vitest / RTL global setup.
 *
 * - Extends expect with DOM matchers (@testing-library/jest-dom)
 * - Stubs browser APIs unavailable in jsdom (e.g., ResizeObserver, matchMedia)
 */

import '@testing-library/jest-dom/vitest';

// Stub ResizeObserver (used by Observable Plot / MapLibre)
if (typeof globalThis.ResizeObserver === 'undefined') {
    globalThis.ResizeObserver = class {
        observe() { }
        unobserve() { }
        disconnect() { }
    } as unknown as typeof ResizeObserver;
}

// Stub matchMedia (used by useBreakpoint)
if (typeof globalThis.matchMedia === 'undefined') {
    globalThis.matchMedia = (query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: () => { },
        removeListener: () => { },
        addEventListener: () => { },
        removeEventListener: () => { },
        dispatchEvent: () => false,
    });
}

// Stub scrollTo (jsdom doesn't implement it)
if (typeof globalThis.scrollTo === 'undefined') {
    globalThis.scrollTo = () => { };
}
