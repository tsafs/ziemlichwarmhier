---
goal: "Phase 1: Testing Infrastructure & Development Setup"
version: 1.0
date_created: 2026-02-16
last_updated: 2026-02-27
owner: Sebastian
status: 'Completed'
tags: [phase-1, testing, infrastructure, vitest, pytest, ci-cd]
---

# Introduction

![Status: Completed](https://img.shields.io/badge/status-Completed-brightgreen)

This phase establishes comprehensive testing infrastructure for both frontend (TypeScript/React) and backend (Python) codebases **before any feature work begins**. Following a testing-first approach ensures code quality, enables confident refactoring, and provides a safety net for all subsequent phases.

**Current State:**
- Vitest v4.0.18 is installed but lacks configuration file and test script
- One test file exists: [frontend/src/utils/HardinessZoneUtils.test.ts](frontend/src/utils/HardinessZoneUtils.test.ts)
- No React Testing Library installed (jsdom, @testing-library/react)
- No pytest configuration or tests
- No CI workflow for running tests

**End State:**
- Vitest fully configured with coverage reporting
- React Testing Library available for component tests
- Pytest configured with fixtures and coverage
- Mock data directories established
- CI workflow runs tests on every PR/push
- Development environment reproducible from fresh clone

## 0. Preflight & Self-Correction

> **Mandatory gate**: Before starting any task in this phase and after every change, run the preflight script and follow the self-correction loop.

1. **Run preflight**: `./scripts/run-preflight.sh` — all checks must pass before starting work
2. **After each change**: re-run preflight or the targeted test subset (see `docs/self-correct-playbook.md`)
3. **On failure**: follow retry guidance in the playbook (max 3 attempts per issue, then revert and re-analyze)
4. **Local CI parity**: optionally run `./scripts/act-local.sh build` to verify GHA workflows locally (requires Docker + act)

## 0.1 Regular Commits

Commit after each logical unit of work to maintain a clear and reviewable change history. Avoid accumulating large batches of uncommitted changes — they make it harder to understand what belongs to what, harder to review PRs, and harder to revert individual changes if something goes wrong.

**Guidelines:**
- Commit after completing each task group or implementation sub-section
- Use [Conventional Commits](https://www.conventionalcommits.org/) format: `feat(phase-X):`, `fix(phase-X):`, `chore(phase-X):`, `test(phase-X):`, etc.
- Each commit should pass the preflight checks (see § 0 above)
- Keep PRs focused — one logical concern per PR makes reviews faster and safer

## 1. Requirements & Constraints

### Phase-Specific Requirements

- **REQ-P1-001**: Configure Vitest with jsdom for React component testing
- **REQ-P1-002**: Configure pytest with coverage reporting (>80% threshold)
- **REQ-P1-003**: Create reusable mock data fixtures for services and Redux state
- **REQ-P1-004**: Set up GitHub Actions workflow that blocks PRs on test failure
- **REQ-P1-005**: Ensure development environment is reproducible via setup script
- **REQ-P1-006**: Document environment variables with validation schema

### Referenced from Master Plan

- **GUD-005**: Test coverage > 80% for critical paths
- **NFR-001**: Keep operational costs low (testing should use free tiers)
- **PAT-001**: Use createDataSlice factory - mock factory for slice tests
- **PAT-002**: Service layer pattern - mock fetch for service tests

### Constraints

- **CON-P1-001**: Use existing Vitest v4.0.18 (already installed)
- **CON-P1-002**: Node.js 20.x (as per existing CI workflows)
- **CON-P1-003**: Python 3.13+ (as per pyproject.toml)
- **CON-P1-004**: GitHub Actions free tier for public repositories

## 2. Implementation Steps

### Implementation Phase 1.1: Vitest Configuration

**GOAL-P1-001**: Configure Vitest with React Testing Library and coverage reporting

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P1-001 | Install dev dependencies: @testing-library/react, @testing-library/jest-dom, jsdom, @vitest/coverage-v8 | | |
| TASK-P1-002 | Create `frontend/vitest.config.ts` with jsdom environment | | |
| TASK-P1-003 | Create `frontend/src/setupTests.ts` for global test setup | | |
| TASK-P1-004 | Update `frontend/tsconfig.json` to include test types | | |
| TASK-P1-005 | Add test scripts to `frontend/package.json` | | |
| TASK-P1-006 | Verify existing HardinessZoneUtils.test.ts passes with new config | | |

---

### Implementation Phase 1.2: Frontend Mock Data Structure

**GOAL-P1-002**: Create mock data fixtures and utilities for frontend testing

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P1-007 | Create `frontend/src/__mocks__/` directory structure | | |
| TASK-P1-008 | Create mock data for LiveDataService (10min station data) | | |
| TASK-P1-009 | Create mock data for city data (GeoNames format) | | |
| TASK-P1-010 | Create test utilities for Redux store setup | | |
| TASK-P1-011 | Create fetch mock utility for service tests | | |
| TASK-P1-012 | Add example component test demonstrating patterns | | |

---

### Implementation Phase 1.3: Pytest Configuration

**GOAL-P1-003**: Configure pytest with fixtures and coverage reporting

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P1-013 | Add pytest, pytest-cov, pytest-xdist to pyproject.toml | | |
| TASK-P1-014 | Create `[tool.pytest.ini_options]` configuration section | | |
| TASK-P1-015 | Create `analysis/conftest.py` with shared fixtures | | |
| TASK-P1-016 | Create `analysis/fixtures/` directory with sample data | | |
| TASK-P1-017 | Add example test file demonstrating patterns | | |
| TASK-P1-018 | Create mock for boto3 S3 client | | |

---

### Implementation Phase 1.4: CI Workflow Setup

**GOAL-P1-004**: Configure GitHub Actions for automated testing

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P1-019 | Create `.github/workflows/test.yml` for frontend tests | | |
| TASK-P1-020 | Add Python test job to workflow | | |
| TASK-P1-021 | Configure coverage reporting with thresholds | | |
| TASK-P1-022 | Add workflow badge to README.md | | |

---

### Implementation Phase 1.5: Development Environment Setup

**GOAL-P1-005**: Create reproducible development environment

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-P1-023 | Create `scripts/setup-dev.sh` for environment setup (`.env.example` created in Phase 2) | | |
| TASK-P1-024 | Update README.md with development setup instructions | | |
| TASK-P1-025 | Verify fresh clone setup works end-to-end | | |

## 3. Alternatives

- **ALT-001**: **Jest instead of Vitest** - Rejected because Vitest is already installed and provides better Vite integration with faster execution. Vitest v4.0.18 is the latest stable version.

- **ALT-002**: **unittest instead of pytest** - Rejected because pytest offers simpler syntax, better fixtures, and coverage integration. Most Python projects use pytest as the de facto standard.

- **ALT-003**: **Separate workflows per language** - Considered creating `test-frontend.yml` and `test-python.yml`. Rejected in favor of a single `test.yml` with multiple jobs for simpler PR status checking.

- **ALT-004**: **MSW (Mock Service Worker) for API mocking** - Considered for more realistic network mocking. Deferred to future work; simple fetch mocks sufficient for initial setup.

## 4. Dependencies

### NPM Dependencies (New)

- **DEP-001**: `@testing-library/react@^16.x` - React component testing utilities
- **DEP-002**: `@testing-library/jest-dom@^6.x` - Custom DOM matchers
- **DEP-003**: `jsdom@^26.x` - DOM environment for Node.js
- **DEP-004**: `@vitest/coverage-v8@^4.x` - Coverage provider (must match Vitest version)

### Python Dependencies (New)

- **DEP-005**: `pytest>=8.0.0` - Testing framework
- **DEP-006**: `pytest-cov>=5.0.0` - Coverage plugin
- **DEP-007**: `pytest-xdist>=3.0.0` - Parallel test execution (optional)

### Existing Dependencies (Referenced)

- **DEP-008**: `vitest@^4.0.18` - Already installed
- **DEP-009**: `@reduxjs/toolkit@^2.8.2` - For store test utilities
- **DEP-010**: `react@^19.1.0` - Current React version

## 5. Files

### Frontend Files

- **FILE-001**: `frontend/vitest.config.ts` - NEW - Vitest configuration
- **FILE-002**: `frontend/src/setupTests.ts` - NEW - Global test setup
- **FILE-003**: `frontend/package.json` - MODIFY - Add test scripts and deps
- **FILE-004**: `frontend/tsconfig.json` - MODIFY - Add test types
- **FILE-005**: `frontend/src/__mocks__/README.md` - NEW - Mock data documentation
- **FILE-006**: `frontend/src/__mocks__/data/liveData.ts` - NEW - Live data mock
- **FILE-007**: `frontend/src/__mocks__/data/cityData.ts` - NEW - City data mock
- **FILE-008**: `frontend/src/__mocks__/services/index.ts` - NEW - Service mocks
- **FILE-009**: `frontend/src/__mocks__/store/testStore.ts` - NEW - Test store setup
- **FILE-010**: `frontend/src/components/__tests__/ExampleComponent.test.tsx` - NEW - Example test

### Python Files

- **FILE-011**: `pyproject.toml` - MODIFY - Add pytest config and deps
- **FILE-012**: `analysis/conftest.py` - NEW - Shared pytest fixtures
- **FILE-013**: `analysis/fixtures/README.md` - NEW - Fixture documentation
- **FILE-014**: `analysis/fixtures/sample_netcdf.py` - NEW - NetCDF fixture generator
- **FILE-015**: `analysis/fixtures/sample_stations.csv` - NEW - Sample station data
- **FILE-016**: `analysis/utilities/tests/__init__.py` - NEW - Test package marker
- **FILE-017**: `analysis/utilities/tests/test_upload_to_s3.py` - NEW - Example test

### CI/CD Files

- **FILE-018**: `.github/workflows/test.yml` - NEW - Test workflow
- **FILE-019**: `scripts/setup-dev.sh` - NEW - Development setup script
- **FILE-020**: `README.md` - MODIFY - Add testing documentation

**Note:** `.env.example` is created in Phase 2 (Infrastructure) to avoid duplication.

## 6. Testing

### Frontend Test Patterns

- **TEST-001**: Utility functions tested with `describe`/`it`/`expect` pattern (see existing test)
- **TEST-002**: Services tested by mocking global `fetch` with `vi.fn()`
- **TEST-003**: Components tested with `@testing-library/react` render + queries
- **TEST-004**: Redux slices tested by creating test store with preloaded state
- **TEST-005**: Hooks tested with `@testing-library/react` renderHook

### Python Test Patterns

- **TEST-006**: Functions tested with pytest assertions
- **TEST-007**: External APIs mocked with `pytest-mock` or `monkeypatch`
- **TEST-008**: NetCDF data mocked with in-memory xarray Datasets
- **TEST-009**: S3 operations mocked with `moto` or manual mock

### Validation Tests

- **TEST-010**: `npm test` executes and passes with existing test
- **TEST-011**: `npm run test:coverage` generates coverage report
- **TEST-012**: `pytest` executes and passes with example test
- **TEST-013**: `pytest --cov` generates coverage report
- **TEST-014**: CI workflow completes successfully on test branch
- **TEST-015**: Fresh clone can run tests after setup-dev.sh

## 7. Risks & Assumptions

### Risks

- **RISK-001**: Vitest v4 may have breaking changes from v3 - **Mitigation**: Use existing test as compatibility check; version is already proven to work
- **RISK-002**: jsdom limitations for complex DOM interactions - **Mitigation**: Defer complex browser tests to E2E phase; jsdom sufficient for unit/integration tests
- **RISK-003**: Python version mismatch between local/CI - **Mitigation**: Pin Python 3.13 in CI; document requirement in README

### Assumptions

- **ASSUMPTION-001**: GitHub Actions free tier provides sufficient minutes for test runs
- **ASSUMPTION-002**: Existing test patterns in HardinessZoneUtils.test.ts are acceptable
- **ASSUMPTION-003**: React 19 is compatible with Testing Library 16.x
- **ASSUMPTION-004**: Coverage threshold of 80% is achievable and appropriate

## 8. Multi-Agent Execution Notes

### Execution Order

**Parallel tasks (can run simultaneously):**
- TASK-P1-001 to TASK-P1-006 (Vitest configuration)
- TASK-P1-013 to TASK-P1-018 (Pytest configuration)

**Sequential dependencies:**
- TASK-P1-007 to TASK-P1-012 must follow TASK-P1-001 to TASK-P1-006 (need Vitest working first)
- TASK-P1-019 to TASK-P1-022 (CI) must follow both frontend and Python setup
- TASK-P1-023 to TASK-P1-025 (Dev setup) can run partially in parallel with CI

### Agent Context Requirements

Each executing agent needs:
- This plan document
- Access to [frontend/package.json](frontend/package.json) for dependency management
- Access to [pyproject.toml](pyproject.toml) for Python deps
- Access to [frontend/src/utils/HardinessZoneUtils.test.ts](frontend/src/utils/HardinessZoneUtils.test.ts) as reference pattern

### Validation Checkpoints

- **After TASK-P1-006**: Run `cd frontend && npm test` - should pass
- **After TASK-P1-012**: Run `cd frontend && npm test` - should have 2+ tests passing
- **After TASK-P1-017**: Run `cd analysis && pytest` - should pass with example test
- **After TASK-P1-022**: Push to test branch, verify CI workflow passes
- **After TASK-P1-025**: Clone fresh repo, run `./scripts/setup-dev.sh`, run tests

## 9. Related Specifications / Further Reading

- [Master Plan: ERA5-Land Germany Climate Visualization](era5-germany-climate-visualization-1.md)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 10. Code Reference (REQUIRED)

This section provides complete code snippets for implementation.

### 10.1 Vitest Configuration

**File**: `frontend/vitest.config.ts` (NEW)

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    test: {
        // Use jsdom for DOM APIs (React component testing)
        environment: 'jsdom',
        
        // Global test setup file
        setupFiles: ['./src/setupTests.ts'],
        
        // Include test files
        include: ['src/**/*.{test,spec}.{ts,tsx}'],
        
        // Exclude node_modules and dist
        exclude: ['node_modules', 'dist'],
        
        // Enable global test APIs (describe, it, expect)
        globals: true,
        
        // Coverage configuration
        coverage: {
            provider: 'v8',
            reporter: ['text', 'html', 'lcov'],
            reportsDirectory: './coverage',
            exclude: [
                'node_modules/',
                'src/setupTests.ts',
                'src/**/*.test.{ts,tsx}',
                'src/**/*.d.ts',
                'src/vite-env.d.tsx',
            ],
            // Minimum coverage thresholds
            thresholds: {
                statements: 80,
                branches: 80,
                functions: 80,
                lines: 80,
            },
        },
        
        // Reporter configuration
        reporters: ['default'],
        
        // Watch mode excluded patterns
        watchExclude: ['node_modules', 'dist'],
    },
});
```

### 10.2 Test Setup File

**File**: `frontend/src/setupTests.ts` (NEW)

```typescript
/**
 * Global test setup for Vitest
 * 
 * This file runs before each test file and configures:
 * - jest-dom matchers for DOM assertions
 * - Global mocks (fetch, localStorage, etc.)
 * - Cleanup utilities
 */

import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test (unmount React components)
afterEach(() => {
    cleanup();
});

// Mock window.matchMedia (used by responsive components)
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(), // deprecated
        removeListener: vi.fn(), // deprecated
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    })),
});

// Mock ResizeObserver (used by some chart libraries)
class ResizeObserverMock {
    observe = vi.fn();
    unobserve = vi.fn();
    disconnect = vi.fn();
}
window.ResizeObserver = ResizeObserverMock;

// Mock IntersectionObserver (used for lazy loading)
class IntersectionObserverMock {
    constructor(callback: IntersectionObserverCallback) {
        this.callback = callback;
    }
    callback: IntersectionObserverCallback;
    root = null;
    rootMargin = '';
    thresholds = [];
    observe = vi.fn();
    unobserve = vi.fn();
    disconnect = vi.fn();
    takeRecords = vi.fn().mockReturnValue([]);
}
window.IntersectionObserver = IntersectionObserverMock as unknown as typeof IntersectionObserver;

// Reset all mocks after each test
afterEach(() => {
    vi.clearAllMocks();
});
```

### 10.3 Package.json Updates

**File**: `frontend/package.json` (MODIFY - add to devDependencies and scripts)

```json
{
    "scripts": {
        "start": "vite",
        "start:now": "VITE_APP_NOW=2025-11-28T12:00:00Z vite",
        "build": "vite build",
        "serve": "vite preview",
        "test": "vitest run",
        "test:watch": "vitest",
        "test:coverage": "vitest run --coverage",
        "test:ui": "vitest --ui"
    },
    "devDependencies": {
        "@testing-library/jest-dom": "^6.6.3",
        "@testing-library/react": "^16.2.0",
        "@types/d3": "^7.4.3",
        "@types/luxon": "^3.6.0",
        "@types/node": "^22.13.0",
        "@types/react": "19.1.6",
        "@types/react-dom": "19.1.5",
        "@vitejs/plugin-react": "^5.0.0",
        "@vitest/coverage-v8": "^4.0.18",
        "jsdom": "^26.0.0",
        "typescript": "~5.9.2",
        "vite": "^7.1.2",
        "vite-plugin-node-polyfills": "^0.23.0",
        "vitest": "^4.0.18"
    }
}
```

### 10.4 TypeScript Configuration Update

**File**: `frontend/tsconfig.json` (MODIFY - add types)

```jsonc
{
    "compilerOptions": {
        "module": "esnext",
        "target": "esnext",
        "moduleResolution": "bundler",
        "types": ["vitest/globals", "@testing-library/jest-dom"],
        "sourceMap": true,
        "declaration": true,
        "declarationMap": true,
        "noUncheckedIndexedAccess": true,
        "exactOptionalPropertyTypes": true,
        "strict": true,
        "jsx": "react-jsx",
        "verbatimModuleSyntax": true,
        "isolatedModules": true,
        "noUncheckedSideEffectImports": true,
        "moduleDetection": "force",
        "skipLibCheck": true
    },
    "include": ["src"],
    "exclude": []
}
```

### 10.5 Mock Data Structure

**File**: `frontend/src/__mocks__/README.md` (NEW)

```markdown
# Mock Data Directory

This directory contains mock data and utilities for testing.

## Structure

```
__mocks__/
├── data/              # Static mock data
│   ├── liveData.ts    # 10-minute station data
│   ├── cityData.ts    # GeoNames city data
│   └── rollingAverage.ts # Historical data
├── services/          # Service mocks
│   └── index.ts       # Centralized service mocks
└── store/             # Redux test utilities
    └── testStore.ts   # Test store factory
```

## Usage

### Mocking Services

```typescript
import { vi } from 'vitest';
import { mockLiveDataResponse } from '../__mocks__/data/liveData';

vi.mock('../services/LiveDataService', () => ({
    fetchLiveData: vi.fn().mockResolvedValue(mockLiveDataResponse),
}));
```

### Using Test Store

```typescript
import { createTestStore } from '../__mocks__/store/testStore';

const store = createTestStore({
    liveData: { data: mockLiveData, status: 'success' },
});
```
```

**File**: `frontend/src/__mocks__/data/liveData.ts` (NEW)

```typescript
/**
 * Mock data for LiveDataService responses
 * 
 * Based on actual 10-minute station data structure from 10min_station_data.csv
 */

import type { LiveDataResponse, LiveStationData } from '../../services/LiveDataService.js';

// Sample station data matching actual CSV structure
export const mockStationData: LiveStationData[] = [
    {
        stationId: 'P0036',
        stationName: 'Aachen (Seffent)',
        lat: 50.7983,
        lon: 6.0244,
        currentTemperature: 15.2,
        humidity: 72,
        maxToday: 18.5,
        minToday: 8.3,
        timestamp: '2026-02-16T12:00:00Z',
    },
    {
        stationId: 'P0301',
        stationName: 'Berlin (Tempelhof)',
        lat: 52.4700,
        lon: 13.4028,
        currentTemperature: 12.8,
        humidity: 65,
        maxToday: 14.2,
        minToday: 5.1,
        timestamp: '2026-02-16T12:00:00Z',
    },
    {
        stationId: 'P0917',
        stationName: 'München (Flughafen)',
        lat: 48.3537,
        lon: 11.7869,
        currentTemperature: 8.4,
        humidity: 80,
        maxToday: 10.1,
        minToday: 2.5,
        timestamp: '2026-02-16T12:00:00Z',
    },
];

export const mockLiveDataResponse: LiveDataResponse = {
    stations: mockStationData,
    timestamp: '2026-02-16T12:00:00Z',
    dataSource: 'DWD',
};

// Factory for creating custom mock data
export const createMockStationData = (
    overrides: Partial<LiveStationData> = {}
): LiveStationData => ({
    stationId: 'TEST001',
    stationName: 'Test Station',
    lat: 51.0,
    lon: 10.0,
    currentTemperature: 20.0,
    humidity: 50,
    maxToday: 22.0,
    minToday: 15.0,
    timestamp: new Date().toISOString(),
    ...overrides,
});
```

**File**: `frontend/src/__mocks__/data/cityData.ts` (NEW)

```typescript
/**
 * Mock data for city selection/search
 * 
 * Based on german_cities_p5000.csv format (GeoNames)
 */

import type { City } from '../../types/City.js';

export const mockCities: City[] = [
    {
        id: 2950159,
        name: 'Berlin',
        lat: 52.52437,
        lon: 13.41053,
        population: 3426354,
        admin1: 'Berlin',
    },
    {
        id: 2867714,
        name: 'München',
        lat: 48.13743,
        lon: 11.57549,
        population: 1260391,
        admin1: 'Bavaria',
    },
    {
        id: 2911298,
        name: 'Hamburg',
        lat: 53.55073,
        lon: 9.99302,
        population: 1739117,
        admin1: 'Hamburg',
    },
    {
        id: 2886242,
        name: 'Köln',
        lat: 50.93333,
        lon: 6.95,
        population: 963395,
        admin1: 'North Rhine-Westphalia',
    },
    {
        id: 2925533,
        name: 'Frankfurt am Main',
        lat: 50.11552,
        lon: 8.68417,
        population: 650000,
        admin1: 'Hesse',
    },
];

export const findMockCity = (name: string): City | undefined =>
    mockCities.find(c => c.name.toLowerCase().includes(name.toLowerCase()));

export const searchMockCities = (query: string, limit = 10): City[] =>
    mockCities
        .filter(c => c.name.toLowerCase().includes(query.toLowerCase()))
        .slice(0, limit);
```

### 10.6 Test Store Utility

**File**: `frontend/src/__mocks__/store/testStore.ts` (NEW)

```typescript
/**
 * Test store factory for Redux testing
 * 
 * Creates a configured store with optional preloaded state for testing.
 */

import { configureStore, type PreloadedState } from '@reduxjs/toolkit';
import type { RootState } from '../../store/index.js';

// Import all reducers (same as production store)
// Note: This list should match frontend/src/store/index.ts
import cityDataReducer from '../../store/slices/cityDataSlice.js';
import liveDataReducer from '../../store/slices/liveDataSlice.js';
// ... add other reducers as needed

/**
 * Creates a test store with optional preloaded state
 * 
 * @example
 * const store = createTestStore({
 *     liveData: { data: mockData, status: 'success' }
 * });
 */
export const createTestStore = (preloadedState?: PreloadedState<RootState>) => {
    return configureStore({
        reducer: {
            cityData: cityDataReducer,
            liveData: liveDataReducer,
            // Add other reducers as needed
        },
        preloadedState,
        // Disable serializable check for testing (allows Date objects, etc.)
        middleware: (getDefaultMiddleware) =>
            getDefaultMiddleware({
                serializableCheck: false,
            }),
    });
};

/**
 * Type for the test store
 */
export type TestStore = ReturnType<typeof createTestStore>;
```

### 10.7 Example Component Test

**File**: `frontend/src/components/__tests__/ExampleComponent.test.tsx` (NEW)

```typescript
/**
 * Example component test demonstrating testing patterns
 * 
 * This file serves as a template for component testing.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { createTestStore } from '../../__mocks__/store/testStore.js';

// Example: Testing a simple presentational component
describe('ExampleComponent Patterns', () => {
    describe('Presentational Component Testing', () => {
        it('should render text content', () => {
            render(<div data-testid="example">Hello, World!</div>);
            expect(screen.getByTestId('example')).toHaveTextContent('Hello, World!');
        });

        it('should handle user interactions', async () => {
            const user = userEvent.setup();
            const handleClick = vi.fn();

            render(<button onClick={handleClick}>Click me</button>);

            await user.click(screen.getByRole('button', { name: /click me/i }));

            expect(handleClick).toHaveBeenCalledTimes(1);
        });
    });

    describe('Connected Component Testing', () => {
        it('should render with Redux Provider', () => {
            const store = createTestStore();

            render(
                <Provider store={store}>
                    <BrowserRouter>
                        <div>Connected Component</div>
                    </BrowserRouter>
                </Provider>
            );

            expect(screen.getByText('Connected Component')).toBeInTheDocument();
        });
    });

    describe('Async Testing', () => {
        it('should wait for async operations', async () => {
            // Mock a component that loads data asynchronously
            const AsyncComponent = () => {
                const [data, setData] = useState<string | null>(null);

                useEffect(() => {
                    setTimeout(() => setData('Loaded'), 100);
                }, []);

                return <div>{data ?? 'Loading...'}</div>;
            };

            render(<AsyncComponent />);

            // Initially shows loading state
            expect(screen.getByText('Loading...')).toBeInTheDocument();

            // Wait for async update
            await waitFor(() => {
                expect(screen.getByText('Loaded')).toBeInTheDocument();
            });
        });
    });
});

// Import useState and useEffect for the async example
import { useState, useEffect } from 'react';
```

### 10.8 Service Mock Utility

**File**: `frontend/src/__mocks__/services/index.ts` (NEW)

```typescript
/**
 * Centralized service mocking utilities
 * 
 * Use these utilities to mock fetch calls in service tests.
 */

import { vi } from 'vitest';

/**
 * Creates a mock fetch response
 */
export const createMockResponse = <T>(data: T, options?: ResponseInit): Response => {
    return new Response(JSON.stringify(data), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
};

/**
 * Creates a mock CSV response
 */
export const createMockCSVResponse = (csv: string, options?: ResponseInit): Response => {
    return new Response(csv, {
        status: 200,
        headers: { 'Content-Type': 'text/csv' },
        ...options,
    });
};

/**
 * Creates a mock error response
 */
export const createMockErrorResponse = (
    status: number,
    message: string
): Response => {
    return new Response(JSON.stringify({ error: message }), {
        status,
        headers: { 'Content-Type': 'application/json' },
    });
};

/**
 * Mock fetch for a single successful call
 * 
 * @example
 * mockFetchOnce(mockLiveDataResponse);
 * const result = await fetchLiveData();
 */
export const mockFetchOnce = <T>(data: T): void => {
    vi.spyOn(global, 'fetch').mockResolvedValueOnce(createMockResponse(data));
};

/**
 * Mock fetch with CSV data
 * 
 * @example
 * mockFetchCSVOnce('header1,header2\nvalue1,value2');
 */
export const mockFetchCSVOnce = (csv: string): void => {
    vi.spyOn(global, 'fetch').mockResolvedValueOnce(createMockCSVResponse(csv));
};

/**
 * Mock fetch to reject with error
 */
export const mockFetchError = (message: string): void => {
    vi.spyOn(global, 'fetch').mockRejectedValueOnce(new Error(message));
};

/**
 * Restore original fetch implementation
 */
export const restoreFetch = (): void => {
    vi.restoreAllMocks();
};
```

### 10.9 Pytest Configuration

**File**: `pyproject.toml` (MODIFY - add pytest section)

```toml
[project]
name = "ziemlichwarmhier"
version = "0.1.0"
description = ""
authors = [
    {name = "Sebastian Fast",email = "s.fast@cognigy.com"}
]
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "requests (>=2.32.4,<3.0.0)",
    "bs4 (>=0.0.2,<0.0.3)",
    "matplotlib (>=3.10.3,<4.0.0)",
    "xarray (>=2025.6.1,<2026.0.0)",
    "numpy (>=2.3.0,<3.0.0)",
    "boto3 (>=1.38.39,<2.0.0)",
    "tqdm (>=4.67.1,<5.0.0)",
    "ephem (>=4.2,<5.0)",
    "netcdf4 (>=1.7.2,<2.0.0)"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-xdist>=3.0.0",
    "moto[s3]>=5.0.0",
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["analysis"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests requiring external resources",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["analysis"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/conftest.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
fail_under = 80
show_missing = true
```

### 10.10 Python Conftest and Fixtures

**File**: `analysis/conftest.py` (NEW)

```python
#!/usr/bin/env python3
"""
Shared pytest fixtures for analysis module testing.

This conftest.py is automatically discovered by pytest and provides
reusable fixtures across all test modules.
"""

import pytest
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import os


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for all tests."""
    monkeypatch.setenv('ACCESS_KEY', 'test_access_key')
    monkeypatch.setenv('SECRET_KEY', 'test_secret_key')
    monkeypatch.setenv('BUCKET_NAME', 'test-bucket')
    monkeypatch.setenv('REGION', 'eu-central-1')
    monkeypatch.setenv('ENDPOINT_URL', 'https://test.example.com')


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_stations_df():
    """Sample station data as DataFrame."""
    return pd.DataFrame({
        'station_id': ['P0036', 'P0301', 'P0917'],
        'station_name': ['Aachen', 'Berlin', 'München'],
        'lat': [50.7983, 52.4700, 48.3537],
        'lon': [6.0244, 13.4028, 11.7869],
    })


@pytest.fixture
def sample_temperature_data():
    """Sample temperature time series data."""
    dates = pd.date_range('2025-01-01', periods=365, freq='D')
    return pd.DataFrame({
        'date': dates,
        'tasmax': np.random.uniform(0, 30, 365),
        'tasmin': np.random.uniform(-10, 20, 365),
    })


@pytest.fixture
def sample_netcdf_dataset():
    """
    Create a sample xarray Dataset mimicking NetCDF climate data.
    
    This fixture creates a small 10x10 grid covering Germany with
    realistic coordinate structure.
    """
    # Germany approximate bounds
    lat = np.linspace(47.2, 55.1, 10)
    lon = np.linspace(5.8, 15.1, 10)
    time = pd.date_range('2025-01-01', periods=12, freq='ME')
    
    # Create temperature data (monthly means)
    tasmax = np.random.uniform(5, 25, (12, 10, 10))
    tasmin = np.random.uniform(-5, 15, (12, 10, 10))
    
    ds = xr.Dataset(
        {
            'tasmax': (['time', 'lat', 'lon'], tasmax),
            'tasmin': (['time', 'lat', 'lon'], tasmin),
        },
        coords={
            'time': time,
            'lat': lat,
            'lon': lon,
        },
        attrs={
            'title': 'Test Climate Dataset',
            'institution': 'Test',
            'source': 'pytest fixture',
        }
    )
    
    return ds


@pytest.fixture
def sample_era5_dataset():
    """
    Create a sample xarray Dataset mimicking ERA5-Land structure.
    
    ERA5-Land has 0.1° resolution with specific variable names (t2m for temperature).
    """
    # Germany bounds at 0.1° resolution
    lat = np.arange(47.2, 55.2, 0.1)
    lon = np.arange(5.8, 15.2, 0.1)
    time = pd.date_range('2025-01-01', periods=12, freq='ME')
    
    # Temperature in Kelvin (ERA5-Land convention)
    t2m = np.random.uniform(270, 300, (12, len(lat), len(lon)))
    
    ds = xr.Dataset(
        {
            't2m': (['time', 'latitude', 'longitude'], t2m),
        },
        coords={
            'time': time,
            'latitude': lat,
            'longitude': lon,
        },
        attrs={
            'Conventions': 'CF-1.6',
            'history': 'pytest fixture for ERA5-Land',
        }
    )
    
    return ds


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client for testing upload/download functions."""
    client = MagicMock()
    client.upload_file = MagicMock(return_value=None)
    client.download_file = MagicMock(return_value=None)
    client.list_objects_v2 = MagicMock(return_value={'Contents': []})
    return client


@pytest.fixture
def mock_cds_api():
    """Mock CDS API client for testing ERA5-Land downloads."""
    client = MagicMock()
    client.retrieve = MagicMock(return_value=None)
    return client


# ============================================================================
# File Fixtures
# ============================================================================

@pytest.fixture
def tmp_data_dir(tmp_path):
    """Create a temporary data directory structure."""
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    (data_dir / '10min_station_data').mkdir()
    (data_dir / 'daily_station_data').mkdir()
    (data_dir / 'hyras').mkdir()
    return data_dir


@pytest.fixture
def sample_csv_file(tmp_path, sample_stations_df):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / 'stations.csv'
    sample_stations_df.to_csv(csv_path, index=False)
    return csv_path


# ============================================================================
# Utility Functions
# ============================================================================

def assert_valid_dataset(ds: xr.Dataset, expected_vars: list[str]) -> None:
    """Assert that a Dataset contains expected variables."""
    for var in expected_vars:
        assert var in ds.data_vars, f"Missing variable: {var}"


def assert_valid_dataframe(df: pd.DataFrame, expected_cols: list[str]) -> None:
    """Assert that a DataFrame contains expected columns."""
    for col in expected_cols:
        assert col in df.columns, f"Missing column: {col}"
```

**File**: `analysis/fixtures/sample_stations.csv` (NEW)

```csv
station_id,station_name,lat,lon
P0036,Aachen (Seffent),50.7983,6.0244
P0301,Berlin (Tempelhof),52.4700,13.4028
P0917,München (Flughafen),48.3537,11.7869
P0622,Hamburg (Fuhlsbüttel),53.6332,9.9881
P0433,Frankfurt (Flughafen),50.0259,8.5213
P0855,Köln (Bonn),50.8659,7.1427
P1049,Stuttgart (Echterdingen),48.6878,9.2247
P0473,Düsseldorf,51.2805,6.7734
P0306,Bremen,53.0447,8.7986
P1048,Nürnberg,49.5030,11.0549
```

### 10.11 Example Python Test

**File**: `analysis/utilities/tests/__init__.py` (NEW)

```python
"""Tests for analysis utilities module."""
```

**File**: `analysis/utilities/tests/test_upload_to_s3.py` (NEW)

```python
#!/usr/bin/env python3
"""
Tests for S3 upload utilities.

Demonstrates testing patterns for functions that interact with AWS S3.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestS3Upload:
    """Tests for S3 upload functionality."""

    def test_upload_file_success(self, mock_s3_client, tmp_path):
        """Test successful file upload to S3."""
        # Arrange
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')
        
        # Mock the boto3.client call to return our mock
        with patch('boto3.client', return_value=mock_s3_client):
            # Import after patching to use mock
            from analysis.utilities.upload_to_s3 import upload_file
            
            # Act
            result = upload_file(str(test_file), 'test-bucket', 'test-key')
            
            # Assert
            assert result is True
            mock_s3_client.upload_file.assert_called_once()

    def test_upload_file_missing_credentials(self, monkeypatch):
        """Test that upload fails when credentials are missing."""
        # Remove credentials
        monkeypatch.delenv('ACCESS_KEY', raising=False)
        monkeypatch.delenv('SECRET_KEY', raising=False)
        
        # Re-import to pick up new env vars
        from analysis.utilities.upload_to_s3 import upload_file
        
        # Act & Assert
        result = upload_file('test.txt', 'bucket', 'key')
        assert result is False

    def test_upload_file_handles_exception(self, mock_s3_client, tmp_path):
        """Test that upload handles S3 exceptions gracefully."""
        # Arrange
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test content')
        
        # Make upload raise an exception
        mock_s3_client.upload_file.side_effect = Exception('S3 error')
        
        with patch('boto3.client', return_value=mock_s3_client):
            from analysis.utilities.upload_to_s3 import upload_file
            
            # Act
            result = upload_file(str(test_file), 'test-bucket', 'test-key')
            
            # Assert
            assert result is False


class TestDatasetProcessing:
    """Tests demonstrating xarray Dataset testing patterns."""

    def test_dataset_has_expected_variables(self, sample_netcdf_dataset):
        """Test that sample dataset has expected structure."""
        assert 'tasmax' in sample_netcdf_dataset.data_vars
        assert 'tasmin' in sample_netcdf_dataset.data_vars
        assert 'time' in sample_netcdf_dataset.coords
        assert 'lat' in sample_netcdf_dataset.coords
        assert 'lon' in sample_netcdf_dataset.coords

    def test_dataset_dimensions(self, sample_netcdf_dataset):
        """Test dataset dimensions."""
        assert sample_netcdf_dataset.dims['time'] == 12
        assert sample_netcdf_dataset.dims['lat'] == 10
        assert sample_netcdf_dataset.dims['lon'] == 10

    def test_era5_kelvin_to_celsius_conversion(self, sample_era5_dataset):
        """Test temperature conversion from Kelvin to Celsius."""
        # ERA5-Land data is in Kelvin, convert to Celsius
        t2m_celsius = sample_era5_dataset['t2m'] - 273.15
        
        # Check reasonable temperature range for Germany
        assert t2m_celsius.min() > -50, "Temperature too cold"
        assert t2m_celsius.max() < 50, "Temperature too hot"
```

### 10.12 GitHub Actions Test Workflow

**File**: `.github/workflows/test.yml` (NEW)

```yaml
name: Run Tests

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
      - 'analysis/**'
      - '.github/workflows/test.yml'
  pull_request:
    branches:
      - main
    paths:
      - 'frontend/**'
      - 'analysis/**'
      - '.github/workflows/test.yml'
  workflow_dispatch:  # Allows manual triggering

jobs:
  frontend-tests:
    name: Frontend Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
          
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
        
      - name: Run tests with coverage
        working-directory: frontend
        run: npm run test:coverage
        
      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: frontend-coverage
          path: frontend/coverage/
          retention-days: 7

  python-tests:
    name: Python Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
          
      - name: Run tests with coverage
        run: pytest --cov --cov-report=xml --cov-report=html
        env:
          ACCESS_KEY: test_key
          SECRET_KEY: test_secret
          
      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: python-coverage
          path: htmlcov/
          retention-days: 7
```

### 10.13 Environment Configuration

**File**: `.env.example` (NEW)

```bash
# Environment Variables for itishotnow Development
# Copy this file to .env and fill in your values
# NEVER commit actual credentials to the repository

# ============================================================================
# S3/Object Storage Configuration (for Hetzner/Scaleway)
# ============================================================================

# Access credentials for object storage
ACCESS_KEY=your_access_key_here
SECRET_KEY=your_secret_key_here

# Bucket configuration
BUCKET_NAME=your-bucket-name
REGION=eu-central-1

# S3-compatible endpoint URL
# Hetzner: https://fsn1.your-objectstorage.com or https://hel1.your-objectstorage.com
# Scaleway: https://s3.fr-par.scw.cloud
ENDPOINT_URL=https://your-endpoint.example.com

# ============================================================================
# Copernicus Climate Data Store (CDS) - ERA5-Land Data Access
# ============================================================================

# CDS API URL (default, rarely needs changing)
CDS_API_URL=https://cds.climate.copernicus.eu/api

# CDS API Key - Get from https://cds.climate.copernicus.eu/how-to-api
CDS_API_KEY=your_cds_api_key_here

# ============================================================================
# Development Settings
# ============================================================================

# Override "now" for frontend development (ISO 8601 format)
# Useful for testing date-dependent features
# VITE_APP_NOW=2025-11-28T12:00:00Z

# Log level for Python scripts (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ============================================================================
# CI/CD Settings (typically set in GitHub Actions secrets)
# ============================================================================

# These are set via GitHub Secrets, not .env
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# S3_ENDPOINT_URL
# S3_BUCKET_NAME
```

### 10.14 Development Setup Script

**File**: `scripts/setup-dev.sh` (NEW)

```bash
#!/usr/bin/env bash
#
# Development environment setup script
#
# Usage: ./scripts/setup-dev.sh
#
# This script sets up the complete development environment for itishotnow.
# Run this after cloning the repository.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Determine script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

log_info "Setting up development environment for itishotnow"
log_info "Project root: $PROJECT_ROOT"

# ============================================================================
# Check Prerequisites
# ============================================================================

log_info "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 20.x or later."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    log_error "Node.js version 20.x or later required. Found: $(node --version)"
    exit 1
fi
log_info "Node.js version: $(node --version) ✓"

# Check npm
if ! command -v npm &> /dev/null; then
    log_error "npm is not installed."
    exit 1
fi
log_info "npm version: $(npm --version) ✓"

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.13 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 13 ]); then
    log_warn "Python 3.13+ recommended. Found: Python $PYTHON_VERSION"
fi
log_info "Python version: $(python3 --version) ✓"

# Check pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    log_error "pip is not installed."
    exit 1
fi
log_info "pip available ✓"

# ============================================================================
# Setup Frontend
# ============================================================================

log_info "Setting up frontend..."

cd "$PROJECT_ROOT/frontend"

# Install npm dependencies
log_info "Installing npm dependencies..."
npm ci

# Verify test command works
log_info "Verifying frontend tests..."
if npm test 2>/dev/null; then
    log_info "Frontend tests pass ✓"
else
    log_warn "Frontend tests did not pass (this may be expected on fresh setup)"
fi

cd "$PROJECT_ROOT"

# ============================================================================
# Setup Python Environment
# ============================================================================

log_info "Setting up Python environment..."

# Create virtual environment if it doesn't exist
VENV_DIR="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip

# Install package with dev dependencies
log_info "Installing Python dependencies..."
pip install -e ".[dev]"

# Verify pytest works
log_info "Verifying Python tests..."
if pytest --collect-only 2>/dev/null; then
    log_info "Python test collection successful ✓"
else
    log_warn "Python tests may need additional setup"
fi

# ============================================================================
# Setup Environment Variables
# ============================================================================

log_info "Checking environment configuration..."

ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
        log_info "Creating .env from .env.example..."
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        log_warn "Please edit .env and add your credentials"
    else
        log_warn ".env.example not found, skipping .env setup"
    fi
else
    log_info ".env file exists ✓"
fi

# ============================================================================
# Create Data Directories (if needed)
# ============================================================================

log_info "Ensuring data directories exist..."

mkdir -p "$PROJECT_ROOT/data/10min_station_data"
mkdir -p "$PROJECT_ROOT/data/daily_station_data"
mkdir -p "$PROJECT_ROOT/data/hyras"

# ============================================================================
# Summary
# ============================================================================

echo ""
log_info "============================================"
log_info "Development environment setup complete!"
log_info "============================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your credentials (if needed)"
echo "  2. Run frontend tests: cd frontend && npm test"
echo "  3. Run Python tests: source .venv/bin/activate && pytest"
echo "  4. Start frontend dev server: cd frontend && npm start"
echo ""
echo "Virtual environment: source $VENV_DIR/bin/activate"
echo ""
```

### 10.15 Existing Test Pattern Reference

**File**: `frontend/src/utils/HardinessZoneUtils.test.ts` (EXISTING - for reference)

```typescript
import { describe, it, expect } from 'vitest';
import {
    getHardinessZoneYearRange,
    calculateAverageAnnualExtremeMinimum,
    getHardinessZone,
    getTemperatureRange,
    getHardinessZoneDetails,
    HARDINESS_ZONES,
} from './HardinessZoneUtils.js';
import type { RollingAverageRecordList } from '../classes/RollingAverageRecord.js';

describe('HardinessZoneUtils', () => {
    describe('getHardinessZoneYearRange', () => {
        it('should return last 30 complete years for Feb 2026', () => {
            const date = new Date('2026-02-15');
            const range = getHardinessZoneYearRange(date);
            expect(range).toEqual({ startYear: 1996, endYear: 2025 });
        });

        it('should return last 30 complete years for Jan 2027', () => {
            const date = new Date('2027-01-15');
            const range = getHardinessZoneYearRange(date);
            expect(range).toEqual({ startYear: 1997, endYear: 2026 });
        });
        
        // ... additional tests follow same pattern
    });
});
```

**Key patterns from existing test:**
1. Uses `describe`/`it`/`expect` from Vitest
2. Tests pure functions with known inputs/outputs
3. Uses `.toEqual()` for object comparison
4. Uses `.toBeCloseTo()` for floating point comparison
5. Tests edge cases (null returns, boundary conditions)
6. Groups related tests in nested `describe` blocks
