---
goal: Establish LLM self-correction enablement for botox phases
version: 1.2
date_created: 2026-02-24
last_updated: 2026-02-24
owner: Internal
status: 'Planned'
tags: [process, enabler, testing, ci, llm]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Prepare the repo so LLM agents can self-correct across all botox phases via deterministic local testing, fixtures/mocks, schema goldens, and locally runnable GitHub Actions parity before executing the phase plans.

## 1. Requirements & Constraints

- **REQ-001**: One-command local test harness for frontend (Vitest/RTL) and Python pipelines (pytest) with deterministic seeds and coverage thresholds enforced.
- **REQ-002**: Stable fixture packs (tiles, metrics JSON/CSV, plot CSVs, city-grid map, city correlation JSON, ERA5 subsets) to allow offline runs and snapshot/golden comparisons; real ERA5-derived samples kept <50 MB total and documented.
- **REQ-003**: Local CI parity: run GitHub Actions workflows locally (act or equivalent) with mocked secrets/providers, including build, tests, jobs, Playwright/Lighthouse, and actionlint.
- **REQ-004**: Schema/golden checks for tiles/JSON/CSV/env to gate drift before committing botox phase changes (metrics, plots, city correlation, decadal outputs, tile headers/size, env schema).
- **REQ-005**: LLM agent guidelines and guardrails (playbooks, run commands, expected outputs) to enable auto-correction loops.
- **REQ-006**: Reusable Agent Skills for repeatable patterns (schema/golden guardrail, frontend data service + slice, plot integration, metrics card, pipeline job, env validation, city search/slug/URL, GH Actions job matrix, Playwright/E2E) authored before executing other tasks.
- **REQ-007**: Preflight command enforces unit + schema + golden + coverage + actionlint + act dry-runs with mocked secrets and env validation before botox phase execution.
- **CON-001**: No external network required for tests (except optional integration opt-in); ERA5 fixture pull is a one-time step requiring CDS API key and user approval.
- **CON-002**: Keep added tooling lightweight; compatible with Node 20 and Python 3.13 (frontend still on Node 20).
- **GUD-001**: Prefer small, real-looking static fixtures over synthetic noise; document seeds/derivations and attribution for ERA5.
- **PAT-001**: Use snapshot/golden testing where outputs are structured (JSON/CSV) and image diff for tiles.

## 2. Implementation Steps

### Implementation Phase 0

- GOAL-000: Author repeatable Agent Skills needed for self-correction (exclude one-off tile generation).

| Task     | Description                                                        | Completed | Date |
| -------- | ------------------------------------------------------------------ | --------- | ---- |
| TASK-000 | Create schema/golden guardrail skill (JSON/CSV/tile): inputs, steps, validation, failure modes |           |      |
| TASK-00A | Create frontend data service + slice + selector + hook skill (Vitest/fixtures/schema validation) |           |      |
| TASK-00B | Create plot integration skill (Observable Plot data service/slice/component, CSV fixtures, tests) |           |      |
| TASK-00C | Create metrics card skill (service/slice/card wiring, tooltips, loading/error, schema tests) |           |      |
| TASK-00D | Create pipeline job skill (Python job + fixtures + pytest + Docker/GHA stub) |           |      |
| TASK-00E | Create env validation skill (.env.example + validate-env, mocked secrets, act inputs) |           |      |
| TASK-00F | Create city search/slug + URL param skill (fixtures, selectors, tests, routing) |           |      |
| TASK-00G | Create GH Actions job/pipeline matrix skill (act parity, actionlint, mocked secrets) |           |      |
| TASK-00H | Create Playwright/E2E execution skill (fixtures, auth-less flows, reporting) |           |      |

### Implementation Phase 1

- GOAL-001: Establish deterministic local test harnesses and fixtures for frontend and Python.

| Task     | Description                                                        | Completed | Date |
| -------- | ------------------------------------------------------------------ | --------- | ---- |
| TASK-001 | Add frontend Vitest config + npm `test`/`test:watch`/`test:coverage` scripts; wire RTL/jsdom; set coverage thresholds |           |      |
| TASK-002 | Create fixture pack (<50 MB): minimal tiles (z6 sample), metrics JSON/CSV, plot CSV, city-grid map, city correlation JSON, MapLibre mock tiles; document seeds/attribution |           |      |
| TASK-003 | Add Python pytest setup (Python 3.13) with fixtures for ERA5 slices (t2m, tmax, tmin, precip/solid precip as needed for metrics/plots) and HYRAS stubs; stub S3/CDS via local files |           |      |
| TASK-004 | Add schema/golden checks (JSON schema for metrics/plots/decadal outputs/city correlation, CSV headers, tile checksum/headers/size, env schema validation) to tests |           |      |

### Implementation Phase 2

- GOAL-002: Local CI parity and LLM agent guardrails.

| Task     | Description                                                        | Completed | Date |
| -------- | ------------------------------------------------------------------ | --------- | ---- |
| TASK-005 | Add scripts/config to run key GitHub Actions locally (act) for build/test, pipelines/jobs, Playwright/Lighthouse; include actionlint; mock secrets/providers |           |      |
| TASK-006 | Add "self-correct" playbook: commands, expected outputs, diff steps, retry guidance for LLM agents |           |      |
| TASK-007 | Add preflight command that runs unit + schema + golden + coverage + env validation + actionlint + act dry-runs; surface single summary |           |      |
| TASK-008 | Update botox phase plans references to require passing preflight/self-correct loop before phase tasks; note CDS fixture pull prompt |           |      |

## 3. Alternatives

- **ALT-001**: Spin up full LocalStack for S3; rejected for heavier setup vs simple file-backed mocks.
- **ALT-002**: Use Cypress/E2E for all verification; rejected for enabler scope—unit/schema/golden faster and stable.

## 4. Dependencies

- **DEP-001**: Node 20, npm; Vitest/RTL already listed in frontend deps.
- **DEP-002**: Python 3.13 with pytest to be added.
- **DEP-003**: act (or similar) for local GitHub Actions emulation.
- **DEP-004**: CDS API key (for one-time ERA5 fixture pull; user-provided when prompted).

## 5. Files

- **FILE-001**: frontend/package.json — MODIFY — add test/test:watch/test:coverage scripts and devDeps for RTL/jsdom config.
- **FILE-002**: frontend/vitest.config.(ts|js) — NEW — Vitest + jsdom + path aliases + coverage thresholds.
- **FILE-003**: frontend/src/test-utils/setupTests.ts — NEW — RTL setup/mocks.
- **FILE-004**: frontend/src/__fixtures__/** — NEW — tiles/metrics/plots/city-grid/city-correlation/MapLibre fixture pack + README on seeds/attribution.
- **FILE-005**: python/pytest.ini or pyproject.toml — MODIFY — pytest config with Python 3.13 and coverage thresholds.
- **FILE-006**: analysis/tests/** — NEW — pytest suites using fixtures/mocks for pipelines.
- **FILE-007**: schemas/metrics.schema.json, schemas/plots.schema.json, schemas/decadal.schema.json — NEW — schema contracts for JSON/CSV outputs.
- **FILE-008**: schemas/city-correlation.schema.json — NEW — schema for city correlation JSON.
- **FILE-009**: schemas/tile-headers.schema.json — NEW — expected headers/size/checksum rules.
- **FILE-010**: schemas/env.schema.json — NEW — env validation spec (mirrors .env.example).
- **FILE-011**: scripts/run-preflight.sh — NEW — orchestrates unit/schema/golden/coverage/env validation + actionlint + act dry-runs.
- **FILE-012**: docs/self-correct-playbook.md — NEW — commands, expected outputs, troubleshooting.
- **FILE-013**: analysis/tests/fixtures/era5/** — NEW — ERA5 NetCDF/GeoTIFF/daily temp subsets (<50 MB) with attribution; includes precip/solid precip where needed.
- **FILE-014**: .env.example — MODIFY — add required vars; used by env schema.
- **FILE-015**: scripts/validate-env.py — NEW — env schema validator.
- **FILE-016**: .github/workflows/* — MODIFY — note/local inputs for act; include Playwright/Lighthouse/actionlint/job builds.
- **FILE-017**: .github/skills/schema-golden-guardrail/SKILL.md — NEW — Agent Skill for schema/golden checks.
- **FILE-018**: .github/skills/frontend-data-slice/SKILL.md — NEW — Agent Skill for service/slice/selector/hook.
- **FILE-019**: .github/skills/plot-integration/SKILL.md — NEW — Agent Skill for plot data + component wiring.
- **FILE-020**: .github/skills/metrics-card/SKILL.md — NEW — Agent Skill for metrics card addition.
- **FILE-021**: .github/skills/pipeline-job/SKILL.md — NEW — Agent Skill for Python job + CI stub.
- **FILE-022**: .github/skills/env-validation/SKILL.md — NEW — Agent Skill for env schema + validate-env + act secrets.
- **FILE-023**: .github/skills/city-search-url/SKILL.md — NEW — Agent Skill for city search/slug/URL param wiring.
- **FILE-024**: .github/skills/gha-matrix/SKILL.md — NEW — Agent Skill for GH Actions job/pipeline matrix + act.
- **FILE-025**: .github/skills/playwright-e2e/SKILL.md — NEW — Agent Skill for Playwright/E2E execution.

## 6. Testing

- **TEST-001**: `npm run test` and `npm run test:coverage` (frontend) pass with fixtures; coverage thresholds met; snapshot/golden diffs stable.
- **TEST-002**: `pytest` (analysis, Python 3.13) passes with local fixtures and no network; coverage thresholds met.
- **TEST-003**: `scripts/run-preflight.sh` completes and reports summary; actionlint passes; act dry-runs succeed for build/test, pipelines/jobs, Playwright/Lighthouse with mocked secrets/env.
- **TEST-004**: Schema checks fail on intentional drift (guardrail validation), including env schema and tile headers/size.

## 7. Risks & Assumptions

### Risks
- **RISK-001**: Fixture drift vs real data; **Mitigation**: document seeds, periodic refresh gated by schema.
- **RISK-002**: act parity gaps vs GH Actions; **Mitigation**: limit scope to key workflows, document known differences.
- **RISK-003**: Golden image flakiness; **Mitigation**: pin rendering libs, use tolerance-aware diff or checksum.
- **RISK-004**: ERA5 fixture pull blocked by missing CDS credentials or network; **Mitigation**: prompt contributor for CDS API key once; cache pulled subset; keep fixtures <50 MB.

### Assumptions
- **ASSUMPTION-001**: Node 20 and Python 3.13 available locally.
- **ASSUMPTION-002**: Contributors can install act (or alternative) locally and supply CDS API key when prompted for the one-time ERA5 fixture pull.

## 8. Multi-Agent Execution Notes

### Execution Order
- **Sequential dependencies**: Phase 0 skills (TASK-000–TASK-00H) precede all other tasks. Phase 1 tasks parallelizable (TASK-001, TASK-002, TASK-003), then TASK-004. Phase 2 follows after Phase 1; TASK-008 last.

### Agent Context Requirements
- Access to fixture seeds and schema files.
- Commands for tests/preflight documented in playbook.
- act installed for workflow dry-runs.
- CDS API key available when performing the one-time ERA5 fixture pull (user-provided on prompt).

### Validation Checkpoints
- After Phase 0: All skills published (TASK-000–TASK-00H) and reference current paths; city search and tile-gen intentionally excluded.
- After TASK-002: Fixture pack documented and referenced by tests.
- After TASK-005: act runs for build/test, pipelines/jobs, Playwright/Lighthouse, and actionlint succeed with mocked secrets.
- After Phase 2: Preflight command exits 0; botox plans updated with preflight requirement and CDS fixture pull note.

## 9. Related Specifications / Further Reading

- botox phase plans in plan/botox/** (to be updated post-enabler).
- GitHub Actions build/deploy workflow for reference: see Code Reference 10.3.

## 10. Code Reference (REQUIRED)

### 10.1 Frontend package scripts (current state)

**File**: frontend/package.json

```json
"scripts": {
    "start": "vite",
    "start:now": "VITE_APP_NOW=2025-11-28T12:00:00Z vite",
    "build": "vite build",
    "serve": "vite preview"
},
"devDependencies": {
    ...
    "vitest": "^4.0.18"
}
```

**Notes**: Vitest present but no test script; add test/test:watch and setup to enable self-correction loop.

### 10.2 Existing Vitest test pattern

**File**: frontend/src/utils/HardinessZoneUtils.test.ts

```typescript
import { describe, it, expect } from 'vitest';
...
describe('calculateAverageAnnualExtremeMinimum', () => {
    it('should calculate AAEMT correctly from known dataset', () => {
        const records: RollingAverageRecordList = [];
        for (let year = 1996; year <= 2025; year++) {
            const yearlyMin = -10 - ((year - 1996) % 10);
            for (let day = 1; day <= 365; day++) {
                const dateStr = `${year}-${String(Math.ceil(day / 30)).padStart(2, '0')}-${String((day % 28) + 1).padStart(2, '0')}`;
                records.push({
                    date: dateStr,
                    tasmin: day === 50 ? yearlyMin : yearlyMin + 20,
                });
            }
        }
        const aaemt = calculateAverageAnnualExtremeMinimum(records, 1996, 2025);
        expect(aaemt).toBeCloseTo(-14.5, 1);
    });
});
```

**Notes**: Demonstrates deterministic fixture generation and explicit assertions; reuse pattern for golden/schema tests.

### 10.3 GitHub Actions workflow to mirror locally

**File**: .github/workflows/build-and-deploy-frontend-to-s3.yml

```yaml
jobs:
  build-and-deploy:
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
      - name: Build frontend
        working-directory: frontend
        run: npm run build
      - name: Install rclone
        run: curl https://rclone.org/install.sh | sudo bash
      - name: Configure rclone
        run: |
          mkdir -p ~/.config/rclone
          echo "[scaleway]
          type = s3
          provider = Other
          env_auth = false
          access_key_id = ${{ secrets.AWS_ACCESS_KEY_ID }}
          secret_access_key = ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          endpoint = ${{ secrets.S3_ENDPOINT_URL }}" > ~/.config/rclone/rclone.conf
      - name: Deploy with rclone
        working-directory: frontend
        run: rclone sync dist/ scaleway:${{ secrets.S3_BUCKET_NAME }} --fast-list --exclude "{data,station_data,hyras_data}/**"
```

**Notes**: Target for local act run; mock secrets and skip remote deploy step for dry-run.
