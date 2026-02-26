```skill
---
name: playwright-e2e
description: Create Playwright end-to-end tests with fixtures, auth-less flows, and CI reporting. Use when adding browser-based integration tests for frontend features.
---

# Playwright / E2E Execution Skill

## Purpose

Add Playwright end-to-end tests that verify frontend behavior in a real browser. Covers: Playwright setup, test authoring for auth-less flows, fixture data, CI integration, and reporting.

## Prerequisites

Gather context:

```
Subagent 1: "Check if @playwright/test is in frontend/package.json devDependencies."
Subagent 2: "Check if playwright.config.ts exists in frontend/."
Subagent 3: "Read frontend/vite.config.js. Return: dev server config, proxy settings."
Subagent 4: "Read frontend/src/App.tsx. Return: route structure, initial data loading flow."
Subagent 5: "Check if frontend/e2e/ or frontend/tests/ directory exists."
```

## Implementation Steps

### Step 1: Install Playwright

```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install --with-deps chromium
```

### Step 2: Create Playwright Config

**Location**: `frontend/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: [
        ['html', { open: 'never' }],
        ['list'],
    ],
    use: {
        baseURL: 'http://localhost:5173',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        // Add more browsers as needed:
        // { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
        // { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    ],
    webServer: {
        command: 'npm run start',
        url: 'http://localhost:5173',
        reuseExistingServer: !process.env.CI,
        timeout: 30_000,
    },
});
```

### Step 3: Create Test Utilities

**Location**: `frontend/e2e/fixtures/test-utils.ts`

```typescript
import { test as base, expect } from '@playwright/test';

/**
 * Extended test fixture with common setup.
 */
export const test = base.extend<{
    waitForDataLoad: () => Promise<void>;
}>({
    waitForDataLoad: async ({ page }, use) => {
        const waitFn = async () => {
            // Wait for initial data load (station data + city data)
            await page.waitForResponse(resp =>
                resp.url().includes('10min_station_data') && resp.status() === 200,
                { timeout: 15_000 }
            );
            // Wait for loading overlay to disappear
            await page.waitForSelector('[data-testid="loading-overlay"]', {
                state: 'hidden',
                timeout: 10_000,
            }).catch(() => {
                // Loading overlay may not exist if data loads fast
            });
        };
        await use(waitFn);
    },
});

export { expect };
```

### Step 4: Write E2E Tests

**Location**: `frontend/e2e/homepage.spec.ts`

```typescript
import { test, expect } from './fixtures/test-utils.js';

test.describe('Homepage', () => {
    test('loads and displays map', async ({ page, waitForDataLoad }) => {
        await page.goto('/');
        await waitForDataLoad();

        // Map should be visible
        await expect(page.locator('canvas, .maplibregl-map')).toBeVisible({ timeout: 10_000 });
    });

    test('displays page title', async ({ page }) => {
        await page.goto('/');

        // Check the main title text
        await expect(page.locator('text=Es ist jetzt warm')).toBeVisible();
    });

    test('can select a city', async ({ page, waitForDataLoad }) => {
        await page.goto('/');
        await waitForDataLoad();

        // Click on a predefined city (e.g., Berlin)
        // Adjust selector based on actual UI
        const berlinMarker = page.locator('[data-city="Berlin"]').first();
        if (await berlinMarker.isVisible()) {
            await berlinMarker.click();
            // Verify city info panel appears
            await expect(page.locator('text=Berlin')).toBeVisible();
        }
    });
});

test.describe('Stats Section', () => {
    test('displays climate statistics cards', async ({ page, waitForDataLoad }) => {
        await page.goto('/');
        await waitForDataLoad();

        // Scroll to stats section
        const statsSection = page.locator('text=Klimastatistiken');
        if (await statsSection.isVisible()) {
            await statsSection.scrollIntoViewIfNeeded();
            // At least one stat card should be visible
            await expect(page.locator('[class*="stat-card"], [data-testid="stat-card"]')).toBeVisible();
        }
    });
});

test.describe('Navigation', () => {
    test('impressum page loads', async ({ page }) => {
        await page.goto('/impressum');
        await expect(page.locator('text=Impressum')).toBeVisible();
    });
});
```

### Step 5: Add Mock Data Server (optional for offline tests)

**Location**: `frontend/e2e/fixtures/mock-server.ts`

```typescript
import { Page } from '@playwright/test';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const FIXTURE_DIR = resolve(__dirname, '../../src/__fixtures__');

/**
 * Intercept network requests and serve local fixture data.
 * Use for deterministic offline E2E tests.
 */
export async function setupMockRoutes(page: Page) {
    // Mock station data
    await page.route('**/station_data/**', async route => {
        const fixture = readFileSync(
            resolve(FIXTURE_DIR, 'stations/10min_station_data_sample.csv'),
            'utf-8'
        );
        await route.fulfill({
            status: 200,
            contentType: 'text/csv',
            body: fixture,
        });
    });

    // Mock city data
    await page.route('**/german_cities_p5000.csv', async route => {
        const fixture = readFileSync(
            resolve(FIXTURE_DIR, 'cities/sample_cities.csv'),
            'utf-8'
        );
        await route.fulfill({
            status: 200,
            contentType: 'text/csv',
            body: fixture,
        });
    });
}
```

### Step 6: Add npm Scripts

**File**: `frontend/package.json` — add to scripts:

```json
{
    "scripts": {
        "e2e": "playwright test",
        "e2e:ui": "playwright test --ui",
        "e2e:report": "playwright show-report"
    }
}
```

### Step 7: Add to GitHub Actions

**File**: `.github/workflows/build-and-deploy-frontend-to-s3.yml` — add test job:

```yaml
  e2e-test:
    runs-on: ubuntu-latest
    needs: build-and-deploy  # or standalone
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      - name: Install Playwright browsers
        working-directory: frontend
        run: npx playwright install --with-deps chromium
      - name: Run E2E tests
        working-directory: frontend
        run: npm run e2e
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: frontend/playwright-report/
          retention-days: 7
```

### Step 8: Add to .gitignore

```
# Playwright
frontend/playwright-report/
frontend/test-results/
frontend/blob-report/
```

## Test Patterns

### Wait for Specific Data

```typescript
// Wait for a specific API response
await page.waitForResponse(
    resp => resp.url().includes('/data/rolling_average/') && resp.status() === 200,
    { timeout: 10_000 }
);
```

### Visual Regression (Optional)

```typescript
test('heatmap matches snapshot', async ({ page, waitForDataLoad }) => {
    await page.goto('/');
    await waitForDataLoad();
    await page.waitForTimeout(2000); // Allow map tiles to render

    await expect(page.locator('.maplibregl-map')).toHaveScreenshot('heatmap.png', {
        maxDiffPixelRatio: 0.02, // Allow 2% pixel difference
    });
});
```

### Mobile Viewport

```typescript
test('responsive layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    // Check mobile-specific layout
});
```

## Run Commands

```bash
# Run all E2E tests
cd frontend && npm run e2e

# Run with UI mode (interactive)
cd frontend && npm run e2e:ui

# Run specific test file
cd frontend && npx playwright test e2e/homepage.spec.ts

# Run headed (see browser)
cd frontend && npx playwright test --headed

# View report
cd frontend && npm run e2e:report

# Update visual snapshots
cd frontend && npx playwright test --update-snapshots
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| `Timeout waiting for response` | Dev server slow to start or data proxy down | Increase `webServer.timeout`, check Vite proxy config |
| `Element not found` | Selector doesn't match actual DOM | Use Playwright's codegen: `npx playwright codegen localhost:5173` |
| Visual regression diff | Layout or data changed | Review screenshot diff, update snapshot if intentional |
| `net::ERR_CONNECTION_REFUSED` | Dev server not running | Check `webServer` config in playwright.config.ts |
| Flaky test on CI | Timing issue | Add explicit waits, increase retries, use `toBeVisible()` |
| `act` can't run Playwright | Docker container lacks browser deps | Use `npx playwright install --with-deps` in workflow |

## Checklist

- [ ] `@playwright/test` installed in devDependencies
- [ ] `playwright.config.ts` configured with webServer
- [ ] Chromium browser installed (`npx playwright install`)
- [ ] At least 3 E2E tests: page load, navigation, interaction
- [ ] Test utilities with data load waiters
- [ ] npm scripts: `e2e`, `e2e:ui`, `e2e:report`
- [ ] GitHub Actions step with artifact upload
- [ ] `.gitignore` updated for Playwright outputs
- [ ] Mock data server created for offline tests (optional)
- [ ] `npm run e2e` passes locally
```
