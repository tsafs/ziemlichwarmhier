---
goal: "Sprint 7 — Infrastructure: Production Deployment + Automated Nightly Updates"
version: 1.0
date_created: 2026-03-02
last_updated: 2026-03-02
owner: phoenix
status: 'Planned'
tags: [infrastructure, deployment, automation, docker, sprint-7]
---

# Sprint 7 — Infrastructure + Automation

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Deploy the frontend to production, configure tile hosting on Hetzner Object Storage with Cloudflare CDN, and set up automated batch jobs for nightly data updates. After this sprint, the site is live and self-updating.

**Prerequisite**: Sprint 6 completed — full-featured frontend (map + cities + metrics + 9 plots). Sprint 3b completed — backend pipeline validated, Docker jobs tested, data artifacts generated.

**Architecture reference**: See `plan/phoenix/00-architecture.md` §4.1 for tile hosting, §5 for infrastructure stack.

## 1. Requirements & Constraints

- **REQ-001**: Frontend deployed to Cloudflare Pages at production domain (`esistwarm.jetzt`)
- **REQ-002**: Anomaly tiles and data files hosted on Hetzner Object Storage (fsn1, S3-compatible) with proper CORS
- **REQ-003**: Cloudflare CDN caches tiles with `public, max-age=31536000, immutable` headers
- **REQ-004**: Frontend `VITE_TILE_BASE_URL`, `VITE_METRICS_BASE_URL`, `VITE_PLOT_DATA_BASE_URL` point to CDN URLs in production build
- **REQ-005**: Three Docker batch jobs adapted from existing jobs:
  - **Daily** (06:00 UTC): check for new ERA5-Land data (~5 day delay), fetch/process/generate tiles
  - **Monthly** (1st of month, 08:00 UTC): full reprocessing of previous month
  - **Yearly** (January 15, 10:00 UTC): recalculate all metrics for completed year
- **REQ-006**: Docker images pushed to GHCR, pulled and run by GitHub Actions on schedule
- **REQ-007**: Job failure triggers automatic GitHub Issue creation
- **REQ-008**: All jobs idempotent (safe to re-run)
- **REQ-009**: Jobs run in <60 minutes, images <1GB
- **REQ-010**: GitHub Actions workflow supports `workflow_dispatch` for manual execution
- **REQ-011**: Environment variables managed via GitHub Secrets (CDS_API_KEY, S3 credentials, bucket name)
- **CON-001**: Use existing Hetzner bucket configuration from `phoenix-backend/infrastructure/bucket/cors.json`
- **CON-002**: Use existing `phoenix-backend/analysis/utilities/upload_to_s3.py` for uploads
- **CON-003**: Cloudflare Pages build command: `cd phoenix-frontend && npm run build`
- **PAT-001**: Docker jobs copy `phoenix-backend/analysis/` into the container (same pattern as existing jobs)
- **GUD-001**: Zero-downtime deployment — frontend is static, new build replaces old atomically on Cloudflare Pages

## 2. Implementation Steps

### Phase 1: Hetzner Object Storage Setup

- GOAL-001: Production tile/data hosting with CORS configured

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create Hetzner Object Storage bucket `climate-tiles` in fsn1 region (if not already created). Verify S3-compatible endpoint URL. | | |
| TASK-002 | Apply CORS configuration from `phoenix-backend/infrastructure/bucket/cors.json` — allow GET from `esistwarm.jetzt` and `localhost:5173` origins | | |
| TASK-003 | Verify upload+download cycle: upload a test file via `upload_to_s3.py`, fetch it via HTTP, confirm Content-Type and CORS headers correct | | |

### Phase 2: Initial Data Upload

- GOAL-002: Upload existing generated tiles, metrics, and plot data to production storage. Sprint 3b validated that the pipeline runs correctly and produces the expected artifacts — this phase runs it at **full scale** (all months 2016–2025) and uploads to production.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-004 | Run the ERA5 data pipeline for all months 2016–2025 (using scripts validated in Sprint 3b: `run_pipeline_smoke_test.py` pattern extended to full date range) to generate GeoTIFF anomaly files for each month. This is a multi-hour batch operation (~120 monthly fetches). | | |
| TASK-005 | Generate WebP tiles from all GeoTIFFs using `phoenix-backend/analysis/tiles/generate_tiles.py`, validate each month with `validate_tiles.py` (patterns proven in Sprint 3b Phase 3) | | |
| TASK-006 | Upload tiles to Hetzner bucket using `phoenix-backend/analysis/tiles/upload_tiles.py` with correct `Content-Type: image/webp` and `Cache-Control: public, max-age=31536000, immutable` headers | | |
| TASK-007 | Run metrics calculation pipeline for all locations (germany + all ~2,949 city tile_ids) using `run_metrics_pipeline.py` (validated in Sprint 3b Phase 5). Upload JSON files to `metrics/` prefix in bucket. | | |
| TASK-008 | Run plot CSV generation for all locations (germany + all city tile_ids) using `run_plot_pipeline.py` (validated in Sprint 3b Phase 6). Upload CSVs to `plots/` prefix in bucket. | | |
| TASK-009 | Upload city correlation JSON (`cities.json` generated in Sprint 3b Phase 4) to bucket root | | |

### Phase 3: Cloudflare Configuration

- GOAL-003: CDN caching and custom domain setup

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-010 | Configure Cloudflare DNS for tile subdomain (e.g., `data.esistwarm.jetzt`) pointing to Hetzner Object Storage endpoint | | |
| TASK-011 | Set up Cloudflare cache rules: WebP files cached for 1 year, JSON/CSV files cached for 1 hour (allows metrics updates to propagate) | | |
| TASK-012 | Verify: fetch a tile from `https://data.esistwarm.jetzt/2024/07/6/33/21.webp` — correct content-type, CORS headers, CF-Cache-Status: HIT on second request | | |

### Phase 4: Docker Job Adaptation

- GOAL-004: Adapt existing Docker jobs for phoenix directory structure

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-013 | Update `phoenix-backend/jobs/job-era5-daily/Dockerfile` — copy from `phoenix-backend/analysis/` instead of `analysis/`. Verify COPY paths, entrypoint, and env var validation. | | |
| TASK-014 | Update `phoenix-backend/jobs/job-era5-monthly/Dockerfile` — same directory path adaptation | | |
| TASK-015 | Update `phoenix-backend/jobs/job-era5-yearly/Dockerfile` — same directory path adaptation. Ensure it runs metrics calculation + export after processing. | | |
| TASK-016 | Test each Docker job locally: `docker build -t phoenix-era5-daily phoenix-backend/jobs/job-era5-daily/ && docker run --env-file .env phoenix-era5-daily` (with test env vars). Verify it completes without error in dry-run mode. | | |
| TASK-017 | Push Docker images to GHCR: `ghcr.io/{owner}/phoenix-era5-daily:latest`, `phoenix-era5-monthly:latest`, `phoenix-era5-yearly:latest` | | |

### Phase 5: GitHub Actions Workflows

- GOAL-005: CI/CD and scheduled job workflows

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-018 | Create `.github/workflows/ci.yml` — runs on push/PR: `cd phoenix-backend && pytest`, `cd phoenix-frontend && npm test`, TypeScript type-check. Blocks merge on failure. | | |
| TASK-019 | Create `.github/workflows/deploy-frontend.yml` — runs on push to `main`: builds `phoenix-frontend` → deploys to Cloudflare Pages. Build env vars: `VITE_TILE_BASE_URL=https://data.esistwarm.jetzt`, `VITE_METRICS_BASE_URL=https://data.esistwarm.jetzt/metrics`, `VITE_PLOT_DATA_BASE_URL=https://data.esistwarm.jetzt/plots`. | | |
| TASK-020 | Create `.github/workflows/job-era5-daily.yml` — scheduled cron `0 6 * * *` (06:00 UTC). Pulls and runs `phoenix-era5-daily` image. Env: CDS_API_KEY, ACCESS_KEY, SECRET_KEY, ENDPOINT_URL, BUCKET_NAME from GitHub Secrets. On failure: creates GitHub Issue with error log. Supports `workflow_dispatch`. | | |
| TASK-021 | Create `.github/workflows/job-era5-monthly.yml` — scheduled cron `0 8 1 * *` (1st of month, 08:00 UTC). Same pattern as daily. | | |
| TASK-022 | Create `.github/workflows/job-era5-yearly.yml` — scheduled cron `0 10 15 1 *` (January 15, 10:00 UTC). Same pattern. | | |
| TASK-023 | Test workflows with `workflow_dispatch` manual trigger. Verify: daily job runs successfully, failure creates issue. | | |

### Phase 6: Frontend Production Build

- GOAL-006: Verify the production frontend connects to real data

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-024 | Create `phoenix-frontend/.env.production` with production URLs (CDN endpoints). `.env.development` keeps local defaults (mock-tiles, /data/...). | | |
| TASK-025 | Run `npm run build` — verify no build errors, output in `dist/` | | |
| TASK-026 | Deploy to Cloudflare Pages (initial deployment). Verify site loads at `esistwarm.jetzt`. | | |
| TASK-027 | Integration test: production site loads map tiles from CDN, metrics from CDN, plot CSVs from CDN. City selection works. Date navigation works. All 9 plots render. | | |

## 3. Alternatives

- **ALT-001**: Use Vercel instead of Cloudflare Pages — rejected; Cloudflare Pages is free, integrates with Cloudflare CDN (already used for tiles), and supports custom domains
- **ALT-002**: Self-host on a VPS instead of static hosting — rejected; static hosting eliminates server management, costs €0/month for frontend, and has better global performance via CDN
- **ALT-003**: Use GitHub Actions to build Docker images on each job run instead of pre-built images — rejected; pre-built images reduce CI minutes and job startup time (<30s pull vs. 5min build)
- **ALT-004**: Single GitHub Actions workflow for all three jobs — rejected; separate workflows allow independent scheduling, failure tracking, and manual triggers

## 4. Dependencies

- **DEP-001**: Sprint 6 completed (full frontend feature set)
- **DEP-002**: Sprint 3b completed (pipeline validated, Docker jobs tested, orchestration scripts proven)
- **DEP-003**: Hetzner Object Storage account (existing)
- **DEP-004**: Cloudflare account with `esistwarm.jetzt` domain (existing)
- **DEP-005**: GitHub Container Registry access (via repo permissions)
- **DEP-006**: CDS API key for ERA5-Land data access (existing)
- **DEP-007**: S3 credentials for Hetzner Object Storage

## 5. Files

### Backend — Docker Jobs (Modified)
- **FILE-001**: `phoenix-backend/jobs/job-era5-daily/Dockerfile` — MODIFY — update COPY paths
- **FILE-002**: `phoenix-backend/jobs/job-era5-monthly/Dockerfile` — MODIFY — update COPY paths
- **FILE-003**: `phoenix-backend/jobs/job-era5-yearly/Dockerfile` — MODIFY — update COPY paths

### GitHub Actions Workflows
- **FILE-004**: `.github/workflows/ci.yml` — NEW — CI pipeline (tests + type-check)
- **FILE-005**: `.github/workflows/deploy-frontend.yml` — NEW — Cloudflare Pages deployment
- **FILE-006**: `.github/workflows/job-era5-daily.yml` — NEW — Daily ERA5 job
- **FILE-007**: `.github/workflows/job-era5-monthly.yml` — NEW — Monthly ERA5 job
- **FILE-008**: `.github/workflows/job-era5-yearly.yml` — NEW — Yearly ERA5 job

### Frontend — Environment
- **FILE-009**: `phoenix-frontend/.env.production` — NEW — Production env vars
- **FILE-010**: `phoenix-frontend/.env.development` — NEW — Development env vars (local defaults)

## 6. Testing

- **TEST-001**: Hetzner upload/download cycle — upload test file, fetch via HTTP, verify Content-Type and CORS
- **TEST-002**: CDN cache verification — first request returns CF-Cache-Status: MISS, second returns HIT
- **TEST-003**: Docker job dry-run — each job starts, validates env vars, runs processing logic (with test data or small subset)
- **TEST-004**: GitHub Actions CI — push a test branch, verify pipeline runs pytest + npm test + type-check
- **TEST-005**: Production site smoke test — map loads tiles, city selection works, metrics display, plots render
- **TEST-006**: Workflow dispatch — manually trigger daily job, verify it runs and completes
- **TEST-007**: Failure notification — trigger a job with invalid credentials, verify GitHub Issue is created
- **TEST-008**: Regression — all Sprint 1–6 tests still pass locally

## 7. Risks & Assumptions

### Risks
- **RISK-001**: ERA5-Land data availability delay may exceed 5 days, causing daily job to no-op — **Mitigation**: job checks for new data and exits gracefully if nothing new; logged but not treated as failure
- **RISK-002**: Hetzner Object Storage S3 compatibility may have edge cases — **Mitigation**: existing `upload_to_s3.py` has been validated; test upload cycle in Phase 1
- **RISK-003**: Cloudflare CDN cache invalidation for updated metrics/CSV (1-hour TTL) may cause stale data — **Mitigation**: 1-hour TTL is acceptable; for urgent updates, Cloudflare API can purge cache
- **RISK-004**: Docker image size may exceed 1GB if Python scientific stack is large — **Mitigation**: use multi-stage build, install only needed packages, use slim base image
- **RISK-005**: GitHub Actions scheduled workflows may have delays (up to 15 minutes) — **Mitigation**: acceptable for batch jobs; not time-critical

### Assumptions
- **ASSUMPTION-001**: The Hetzner Object Storage bucket and Cloudflare domain are already provisioned from previous work
- **ASSUMPTION-002**: CDS API key is valid and has sufficient quota for daily data requests
- **ASSUMPTION-003**: GitHub Actions free tier provides sufficient minutes for daily job execution (<60 min/run)
- **ASSUMPTION-004**: Cloudflare Pages supports single-page app routing (all paths → index.html)

## 8. Multi-Agent Execution Notes

### Execution Order
- **Phase 1** (Hetzner setup): External/manual, do first
- **Phase 2** (data upload): Requires Phase 1 + existing pipeline runs
- **Phase 3** (Cloudflare): Requires Phase 1 (bucket URL needed for DNS)
- **Phase 4** (Docker jobs): Independent of Phase 1–3, can parallel
- **Phase 5** (GitHub Actions): Requires Phase 4 (workflows reference Docker images)
- **Phase 6** (production build): Requires Phase 3 (CDN URLs) + Phase 5 (deploy workflow)

### Agent Context Requirements
- Read `phoenix-backend/infrastructure/bucket/cors.json` for CORS config
- Read `phoenix-backend/jobs/job-era5-daily/Dockerfile` for Docker pattern
- Read `phoenix-backend/analysis/tiles/upload_tiles.py` for upload interface
- Read `phoenix-frontend/src/config/climateDataConfig.ts` for env var names
- Read existing job entrypoint scripts for env var validation pattern

### Validation Checkpoints
- [After TASK-003]: Test file uploadable and downloadable from Hetzner
- [After TASK-012]: Tiles served via CDN with correct headers
- [After TASK-016]: All 3 Docker jobs pass local dry-run
- [After TASK-023]: GitHub Actions workflows executable via manual dispatch
- [After TASK-027]: Production site fully functional

## 9. Related Specifications / Further Reading

- `plan/phoenix/00-architecture.md` — §4.1 Anomaly Tiles, §5 Technology Stack (Infrastructure)
- `plan/phoenix/sprint-3b-data-pipeline.md` — Pipeline validation, Docker dry-runs, orchestration scripts
- `phoenix-backend/infrastructure/bucket/cors.json` — CORS configuration
- `phoenix-backend/analysis/tiles/upload_tiles.py` — S3 upload utility
- `phoenix-backend/docs/pipeline-runbook.md` — Pipeline operations documentation (created in Sprint 3b)
- Hetzner Object Storage docs: https://docs.hetzner.com/storage/object-storage/
- Cloudflare Pages docs: https://developers.cloudflare.com/pages/
- GitHub Actions scheduled workflows: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule

## 10. Code Reference

### 10.1 CORS Configuration

**File**: `phoenix-backend/infrastructure/bucket/cors.json`

```json
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedOrigins": [
        "https://esistwarm.jetzt",
        "https://www.esistwarm.jetzt",
        "http://localhost:5173"
      ],
      "ExposeHeaders": ["Content-Length", "Content-Type"],
      "MaxAgeSeconds": 86400
    }
  ]
}
```

### 10.2 GitHub Actions Daily Job Workflow

**File**: `.github/workflows/job-era5-daily.yml` (to be created)

```yaml
name: ERA5 Daily Update
on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  era5-daily:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - name: Pull and run ERA5 daily job
        run: |
          docker pull ghcr.io/${{ github.repository_owner }}/phoenix-era5-daily:latest
          docker run --rm \
            -e CDS_API_KEY=${{ secrets.CDS_API_KEY }} \
            -e ACCESS_KEY=${{ secrets.HETZNER_ACCESS_KEY }} \
            -e SECRET_KEY=${{ secrets.HETZNER_SECRET_KEY }} \
            -e ENDPOINT_URL=${{ secrets.HETZNER_ENDPOINT_URL }} \
            -e BUCKET_NAME=${{ secrets.HETZNER_BUCKET_NAME }} \
            ghcr.io/${{ github.repository_owner }}/phoenix-era5-daily:latest

      - name: Create issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `ERA5 Daily Job Failed - ${new Date().toISOString().split('T')[0]}`,
              body: `The ERA5 daily update job failed.\n\nRun: ${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`,
              labels: ['bug', 'automation']
            });
```

### 10.3 CI Workflow

**File**: `.github/workflows/ci.yml` (to be created)

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: phoenix-backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install poetry && poetry install
      - run: poetry run pytest -x --tb=short

  frontend-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: phoenix-frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm test
```

### 10.4 Production Environment Variables

**File**: `phoenix-frontend/.env.production` (to be created)

```env
VITE_CLIMATE_DATASET_ID=era5-land
VITE_CLIMATE_DISPLAY_NAME=ERA5-Land
VITE_TILE_BASE_URL=https://data.esistwarm.jetzt
VITE_METRICS_BASE_URL=https://data.esistwarm.jetzt/metrics
VITE_PLOT_DATA_BASE_URL=https://data.esistwarm.jetzt/plots
VITE_NATIVE_RESOLUTION=0.1
VITE_DATA_DELAY_DAYS=5
VITE_GRID_RESOLUTION_LABEL=~9 km
```
