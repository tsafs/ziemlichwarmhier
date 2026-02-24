---
goal: Establish LLM self-correction enablement for botox phases
version: 1.1
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

- **REQ-001**: One-command local test harness for frontend (Vitest/RTL) and Python pipelines (pytest) with deterministic seeds.
- **REQ-002**: Stable fixture packs (tiles, metrics JSON/CSV, plot CSVs, city-grid map) to allow offline runs and snapshot/golden comparisons.
- **REQ-003**: Local CI parity: run GitHub Actions workflows locally (act or equivalent) with mocked secrets/providers.
- **REQ-004**: Schema/golden checks for tiles/JSON/CSV to gate drift before committing botox phase changes.
- **REQ-005**: LLM agent guidelines and guardrails (playbooks, run commands, expected outputs) to enable auto-correction loops.
- **REQ-006**: Reusable Agent Skills for repeatable patterns (schema/golden guardrail, frontend data service + slice, plot integration, metrics card, pipeline job) authored before executing other tasks.
- **CON-001**: No external network required for tests (except optional integration opt-in).
- **CON-002**: Keep added tooling lightweight; compatible with Node 20 and Python 3.11.
- **GUD-001**: Prefer small, real-looking static fixtures over synthetic noise; document seeds/derivations.
- **PAT-001**: Use snapshot/golden testing where outputs are structured (JSON/CSV) and image diff for tiles.

## 2. Implementation Steps

### Implementation Phase 0

- GOAL-000: Author repeatable Agent Skills needed for self-correction (exclude one-off city search and one-off tile generation).

| Task     | Description                                                        | Completed | Date |
| -------- | ------------------------------------------------------------------ | --------- | ---- |
| TASK-000 | Create schema/golden guardrail skill (JSON/CSV/tile): inputs, steps, validation, failure modes |           |      |
| TASK-00A | Create frontend data service + slice + selector + hook skill (Vitest/fixtures/schema validation) |           |      |
| TASK-00B | Create plot integration skill (Observable Plot data service/slice/component, CSV fixtures, tests) |           |      |
| TASK-00C | Create metrics card skill (service/slice/card wiring, tooltips, loading/error, schema tests) |           |      |
| TASK-00D | Create pipeline job skill (Python job + fixtures + pytest + Docker/GHA stub) |           |      |

### Implementation Phase 1

- GOAL-001: Establish deterministic local test harnesses and fixtures for frontend and Python.

| Task     | Description                                                        | Completed | Date |
| -------- | ------------------------------------------------------------------ | --------- | ---- |
| TASK-001 | Add frontend Vitest config + npm `test`/`test:watch` scripts; wire RTL/jsdom |           |      |
| TASK-002 | Create fixture pack: minimal tiles (z6 sample), metrics JSON/CSV, plot CSV, city-grid map; document seeds |           |      |
| TASK-003 | Add Python pytest setup with fixtures for ERA5/hyras slices; stub S3/CDS via local files |           |      |
| TASK-004 | Add schema/golden checks (JSON schema for metrics/plots, CSV headers, tile checksum) to tests |           |      |

### Implementation Phase 2

- GOAL-002: Local CI parity and LLM agent guardrails.

| Task     | Description                                                        | Completed | Date |
| -------- | ------------------------------------------------------------------ | --------- | ---- |
| TASK-005 | Add scripts/config to run key GitHub Actions locally (act), with mock secrets/providers |           |      |
| TASK-006 | Add "self-correct" playbook: commands, expected outputs, diff steps, retry guidance for LLM agents |           |      |
| TASK-007 | Add preflight command that runs unit + schema + golden checks + dry-run Actions; surface single summary |           |      |
| TASK-008 | Update botox phase plans references to require passing preflight/self-correct loop before phase tasks |           |      |

## 3. Alternatives

- **ALT-001**: Spin up full LocalStack for S3; rejected for heavier setup vs simple file-backed mocks.
- **ALT-002**: Use Cypress/E2E for all verification; rejected for enabler scope—unit/schema/golden faster and stable.

## 4. Dependencies

- **DEP-001**: Node 20, npm; Vitest/RTL already listed in frontend deps.
- **DEP-002**: Python 3.11 with pytest to be added.
- **DEP-003**: act (or similar) for local GitHub Actions emulation.

## 5. Files

- **FILE-001**: frontend/package.json — MODIFY — add test scripts and devDeps for RTL/jsdom config.
- **FILE-002**: frontend/vitest.config.(ts|js) — NEW — Vitest + jsdom + path aliases.
- **FILE-003**: frontend/src/test-utils/setupTests.ts — NEW — RTL setup/mocks.
- **FILE-004**: frontend/src/__fixtures__/** — NEW — tiles/metrics/plots/city-grid fixture pack + README on seeds.
- **FILE-005**: python/pytest.ini or pyproject.toml — MODIFY — pytest config.
- **FILE-006**: analysis/tests/** — NEW — pytest suites using fixtures/mocks for pipelines.
- **FILE-007**: schemas/metrics.schema.json, schemas/plots.schema.json — NEW — schema contracts for JSON/CSV.
- **FILE-008**: scripts/run-preflight.sh — NEW — orchestrates unit/schema/golden + act dry-run.
- **FILE-009**: docs/self-correct-playbook.md — NEW — commands, expected outputs, troubleshooting.
- **FILE-010**: .github/workflows/* — MODIFY — note/local inputs for act (or add .actrc/sample env).
- **FILE-011**: .github/skills/schema-golden-guardrail/SKILL.md — NEW — Agent Skill for schema/golden checks.
- **FILE-012**: .github/skills/frontend-data-slice/SKILL.md — NEW — Agent Skill for service/slice/selector/hook.
- **FILE-013**: .github/skills/plot-integration/SKILL.md — NEW — Agent Skill for plot data + component wiring.
- **FILE-014**: .github/skills/metrics-card/SKILL.md — NEW — Agent Skill for metrics card addition.
- **FILE-015**: .github/skills/pipeline-job/SKILL.md — NEW — Agent Skill for Python job + CI stub.

## 6. Testing

- **TEST-001**: `npm run test` (frontend) passes with fixtures; snapshot/golden diffs stable.
- **TEST-002**: `pytest` (analysis) passes with local fixtures and no network.
- **TEST-003**: `scripts/run-preflight.sh` completes and reports summary; act run succeeds with mocked secrets.
- **TEST-004**: Schema checks fail on intentional drift (guardrail validation).

## 7. Risks & Assumptions

### Risks
- **RISK-001**: Fixture drift vs real data; **Mitigation**: document seeds, periodic refresh gated by schema.
- **RISK-002**: act parity gaps vs GH Actions; **Mitigation**: limit scope to key workflows, document known differences.
- **RISK-003**: Golden image flakiness; **Mitigation**: pin rendering libs, use tolerance-aware diff or checksum.

### Assumptions
- **ASSUMPTION-001**: Node 20 and Python 3.11 available locally.
- **ASSUMPTION-002**: Contributors can install act (or alternative) locally.

## 8. Multi-Agent Execution Notes

### Execution Order
- **Sequential dependencies**: Phase 0 skills (TASK-000–TASK-00D) precede all other tasks. Phase 1 tasks parallelizable (TASK-001, TASK-002, TASK-003), then TASK-004. Phase 2 follows after Phase 1; TASK-008 last.

### Agent Context Requirements
- Access to fixture seeds and schema files.
- Commands for tests/preflight documented in playbook.
- act installed for workflow dry-runs.

### Validation Checkpoints
- After Phase 0: All skills published (TASK-000–TASK-00D) and reference current paths; city search and tile-gen intentionally excluded.
- After TASK-002: Fixture pack documented and referenced by tests.
- After TASK-005: act run of frontend build workflow succeeds with mocked secrets.
- After Phase 2: Preflight command exits 0; botox plans updated with preflight requirement.

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
