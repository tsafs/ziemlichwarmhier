# Self-Correct Playbook for LLM Agents

> Commands, expected outputs, diff steps, and retry guidance for LLM agents working on the botox phases.

## Quick Reference

| Check | Command | Expected Exit | Typical Runtime |
|-------|---------|---------------|-----------------|
| Frontend unit tests | `cd frontend && npm run test` | 0 | ~5s |
| Frontend coverage | `cd frontend && npm run test:coverage` | 0 | ~10s |
| Python unit tests | `python -m pytest analysis/tests/ -v` | 0 | ~3s |
| Python coverage | `python -m pytest analysis/tests/ --cov=analysis --cov-report=term-missing` | 0 | ~5s |
| Schema validation (frontend) | `cd frontend && npx vitest run src/__tests__/schema-validation.test.ts` | 0 | ~3s |
| Fixture integrity | `cd frontend && npx vitest run src/__fixtures__/__tests__/fixtures.test.ts` | 0 | ~3s |
| TypeScript check | `cd frontend && npx tsc --noEmit` | 0 | ~10s |
| actionlint | `actionlint .github/workflows/*.yml` | 0 | <1s |
| Full preflight | `./scripts/run-preflight.sh` | 0 | ~30s |

---

## 1. Before Starting Any Botox Phase Task

Run the preflight command to verify the repo is in a clean, passing state:

```bash
./scripts/run-preflight.sh
```

**Expected output**: All sections show `[OK]` and the final summary reads:

```
═══════════════════════════════════════════════
  PREFLIGHT SUMMARY
═══════════════════════════════════════════════
  Frontend tests .............. OK
  Frontend coverage ........... OK
  Python tests ................ OK
  Schema validation ........... OK
  actionlint .................. OK
═══════════════════════════════════════════════
  Result: ALL CHECKS PASSED
═══════════════════════════════════════════════
```

If any check fails, fix the issue before proceeding with phase work.

---

## 2. After Making Changes

### 2.1 Run Targeted Tests First

After editing code, run the most relevant test suite before the full preflight:

**Frontend changes:**
```bash
cd frontend && npm run test
```

**Python pipeline changes:**
```bash
python -m pytest analysis/tests/ -v
```

**Schema or fixture changes:**
```bash
cd frontend && npx vitest run src/__tests__/schema-validation.test.ts
```

### 2.2 Check for TypeScript Errors

```bash
cd frontend && npx tsc --noEmit
```

Expected: clean exit (code 0), no output.

### 2.3 Run Full Preflight

Once targeted tests pass, run the full suite:

```bash
./scripts/run-preflight.sh
```

---

## 3. Understanding Test Failures

### 3.1 Frontend Test Failures

**Symptom**: `npm run test` exits non-zero.

**Steps to diagnose:**
1. Read the error output — Vitest shows the failing test name, expected vs actual values
2. Check if it's a fixture issue: `npx vitest run src/__fixtures__/__tests__/fixtures.test.ts`
3. Check if it's a schema drift: `npx vitest run src/__tests__/schema-validation.test.ts`

**Common causes:**
- JSON fixture doesn't match schema → update fixture or schema
- CSV headers changed → update `schemas/plot-csv-headers.schema.json`
- Import path changed → update the import in test file

### 3.2 Python Test Failures

**Symptom**: `python -m pytest analysis/tests/ -v` exits non-zero.

**Steps to diagnose:**
1. Read pytest output — shows assertion details and stack trace
2. Check if `conftest.py` fixtures match expected data shapes
3. Verify `pyproject.toml` `pythonpath` includes new module directories

**Common causes:**
- Missing module in `pythonpath` → add to `[tool.pytest.ini_options]` in `pyproject.toml`
- Fixture data shape mismatch → update `analysis/tests/conftest.py`
- Network call not mocked → `no_network` fixture should block; check `monkeypatch`

### 3.3 Schema Validation Failures

**Symptom**: `schema-validation.test.ts` fails.

**Steps to diagnose:**
1. Error shows which schema property failed (e.g., `"must have required property 'version'"`)
2. Compare fixture JSON against the schema in `schemas/`
3. Check if schema was updated without updating fixtures, or vice versa

**Fix pattern:**
```
1. Open the failing schema (e.g., schemas/metrics.schema.json)
2. Open the fixture (e.g., frontend/src/__fixtures__/metrics/germany.json)
3. Align the two — either update the schema to accept new shape or update the fixture
4. Re-run: npx vitest run src/__tests__/schema-validation.test.ts
```

### 3.4 actionlint Failures

**Symptom**: `actionlint` reports workflow syntax errors.

**Steps to diagnose:**
1. Error includes file path, line number, and rule
2. Common: missing `shell:` in `run:` steps, deprecated action versions, expression typos

**Fix pattern:**
```
1. Open the workflow file at the reported line
2. Fix the syntax per actionlint's suggestion
3. Re-run: actionlint .github/workflows/*.yml
```

---

## 4. Retry Guidance

### 4.1 When a Fix Doesn't Work

1. **Re-read the error carefully** — don't guess, parse the exact assertion
2. **Check the diff** — `git diff` to see exactly what changed
3. **Isolate the test** — run only the failing test:
   ```bash
   # Frontend (specific test file)
   cd frontend && npx vitest run path/to/failing.test.ts

   # Python (specific test)
   python -m pytest analysis/tests/test_smoke.py::test_name -v
   ```
4. **Check for cascading failures** — fix the first failure, re-run, repeat

### 4.2 Maximum Retry Attempts

For any single issue:
- **3 attempts** to fix a test failure before escalating
- After 3 attempts: revert the change (`git checkout -- <file>`), re-analyze the root cause, try a different approach

### 4.3 When to Revert

Revert immediately if:
- The fix introduces new failing tests
- The change touches files outside the current task scope
- Coverage drops below thresholds (10% for both frontend and Python)

```bash
# Revert specific file
git checkout -- path/to/file

# Revert all uncommitted changes
git checkout -- .
```

---

## 5. Diff & Verification Steps

### 5.1 Before Committing

Always verify your changes:

```bash
# See what files changed
git status

# See line-by-line diff
git diff

# Verify no unintended files are modified
git diff --stat
```

### 5.2 Verify Schemas Match Fixtures

When modifying any schema in `schemas/`:
```bash
cd frontend && npx vitest run src/__tests__/schema-validation.test.ts
```

When modifying any fixture in `frontend/src/__fixtures__/`:
```bash
cd frontend && npx vitest run src/__fixtures__/__tests__/fixtures.test.ts
cd frontend && npx vitest run src/__tests__/schema-validation.test.ts
```

### 5.3 Verify New Files Are Importable

After creating new TypeScript modules:
```bash
cd frontend && npx tsc --noEmit
```

After creating new Python modules:
```bash
python -c "import <module_name>"
```

---

## 6. Environment & Setup

### 6.1 Required Tools

| Tool | Version | Check Command |
|------|---------|---------------|
| Node.js | 20.x | `node --version` |
| npm | 10.x+ | `npm --version` |
| Python | 3.13.x | `python --version` |
| Poetry | 2.x | `poetry --version` |
| actionlint | latest | `actionlint --version` |
| act (optional) | latest | `act --version` |

### 6.2 First-Time Setup

```bash
# Frontend
cd frontend && npm ci

# Python
poetry install --with test

# Verify everything works
./scripts/run-preflight.sh
```

### 6.3 Environment Variables

For pipeline work requiring S3/CDS access, copy the env template:
```bash
cp .env.example .env
# Edit .env with real credentials (never commit .env)
```

The env schema is defined in `schemas/env.schema.json`. For local testing, mocked values in `.act-secrets` are sufficient.

---

## 7. CDS Fixture Pull (One-Time)

The ERA5-Land fixture data requires a one-time download from the Copernicus Climate Data Store. This is NOT needed for running tests (fixtures are pre-generated and committed), but IS needed when refreshing fixture data:

1. Obtain a CDS API key from https://cds.climate.copernicus.eu/
2. Set `CDS_API_KEY` in `.env`
3. Run the fixture pull script (documented per phase plan)
4. Verify fixtures: `./scripts/run-preflight.sh`

**Important**: Prompt the user for their CDS API key — never assume it's available.

---

## 8. Common Patterns

### 8.1 Adding a New Schema

1. Create `schemas/<name>.schema.json` (JSON Schema draft-07)
2. Add validation test in `frontend/src/__tests__/schema-validation.test.ts`
3. Create matching fixture in `frontend/src/__fixtures__/`
4. Run: `cd frontend && npm run test`

### 8.2 Adding a New Fixture

1. Create fixture file in `frontend/src/__fixtures__/<category>/`
2. Export from `frontend/src/__fixtures__/index.ts`
3. Add integrity test in `frontend/src/__fixtures__/__tests__/fixtures.test.ts`
4. Run: `cd frontend && npm run test`

### 8.3 Adding a New Python Test

1. Add test function in `analysis/tests/`
2. Use conftest fixtures (`mock_s3`, `mock_era5_env`, `tmp_csv`, etc.)
3. Run: `python -m pytest analysis/tests/ -v`

### 8.4 Modifying a Workflow

1. Edit `.github/workflows/<name>.yml`
2. Lint: `actionlint .github/workflows/*.yml`
3. Dry-run: `./scripts/act-local.sh <shortcut>`
