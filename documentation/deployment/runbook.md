# ERA5 Pipeline Operations Runbook

## Overview

The ERA5 pipeline processes ERA5-Land climate data for Germany. It consists of
three Docker-based jobs that run on different schedules:

| Job | Schedule | Purpose |
|-----|----------|---------|
| `job-era5-daily` | 03:15 UTC daily | Catch up on the last 3 months; idempotent |
| `job-era5-monthly` | 04:00 UTC on 1st | Full processing of the previous complete month |
| `job-era5-yearly` | 05:00 UTC on Jan 15 | Annual aggregation and metrics export |

---

## Prerequisites

### GitHub Secrets

Configure these secrets in the repository under **Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `CDS_API_KEY` | Copernicus Climate Data Store personal API key |
| `S3_ACCESS_KEY` | S3-compatible object storage access key |
| `S3_SECRET_KEY` | S3-compatible object storage secret key |
| `S3_ENDPOINT_URL` | S3 endpoint URL (e.g. `https://s3.eu-central-1.wasabisys.com`) |
| `BUCKET_NAME` | Target S3 bucket name |

### CDS API Key

Obtain a personal key from <https://cds.climate.copernicus.eu/profile>.  
The key has the form `<uid>:<uuid-token>`.

### Docker Images

Images are stored in the GitHub Container Registry (GHCR):

```
ghcr.io/tsafs/itishotnow:era5-daily-latest
ghcr.io/tsafs/itishotnow:era5-monthly-latest
ghcr.io/tsafs/itishotnow:era5-yearly-latest
```

Images are built automatically by `.github/workflows/build-era5-jobs.yml`
on any push to `main` that touches `jobs/job-era5-*/**` or `analysis/**`.

---

## Manual Job Execution

### Daily Pipeline (catch-up)

```bash
docker pull ghcr.io/tsafs/itishotnow:era5-daily-latest

docker run --rm \
  -e CDS_API_KEY="<your-key>" \
  -e ACCESS_KEY="<s3-access-key>" \
  -e SECRET_KEY="<s3-secret-key>" \
  -e ENDPOINT_URL="<s3-endpoint-url>" \
  -e BUCKET_NAME="<bucket>" \
  ghcr.io/tsafs/itishotnow:era5-daily-latest
```

#### Force reprocessing (ignore existing tiles)

```bash
docker run --rm \
  -e CDS_API_KEY="<your-key>" \
  -e ACCESS_KEY="<s3-access-key>" \
  -e SECRET_KEY="<s3-secret-key>" \
  -e ENDPOINT_URL="<s3-endpoint-url>" \
  -e BUCKET_NAME="<bucket>" \
  -e FORCE_REPROCESS="true" \
  ghcr.io/tsafs/itishotnow:era5-daily-latest
```

### Monthly Pipeline (specific month)

```bash
docker pull ghcr.io/tsafs/itishotnow:era5-monthly-latest

docker run --rm \
  -e CDS_API_KEY="<your-key>" \
  -e ACCESS_KEY="<s3-access-key>" \
  -e SECRET_KEY="<s3-secret-key>" \
  -e ENDPOINT_URL="<s3-endpoint-url>" \
  -e BUCKET_NAME="<bucket>" \
  -e TARGET_YEAR="2025" \
  -e TARGET_MONTH="8" \
  ghcr.io/tsafs/itishotnow:era5-monthly-latest
```

### Yearly Pipeline (specific year)

```bash
docker pull ghcr.io/tsafs/itishotnow:era5-yearly-latest

docker run --rm \
  -e CDS_API_KEY="<your-key>" \
  -e ACCESS_KEY="<s3-access-key>" \
  -e SECRET_KEY="<s3-secret-key>" \
  -e ENDPOINT_URL="<s3-endpoint-url>" \
  -e BUCKET_NAME="<bucket>" \
  -e TARGET_YEAR="2024" \
  ghcr.io/tsafs/itishotnow:era5-yearly-latest
```

---

## Manual Backfill

To backfill a range of months, run the monthly job for each missing month in
sequence. Example: backfilling Jan–Mar 2024:

```bash
for MONTH in 1 2 3; do
  docker run --rm \
    -e CDS_API_KEY="<your-key>" \
    -e ACCESS_KEY="<s3-access-key>" \
    -e SECRET_KEY="<s3-secret-key>" \
    -e ENDPOINT_URL="<s3-endpoint-url>" \
    -e BUCKET_NAME="<bucket>" \
    -e TARGET_YEAR="2024" \
    -e TARGET_MONTH="${MONTH}" \
    ghcr.io/tsafs/itishotnow:era5-monthly-latest
done
```

To trigger a manual run from GitHub Actions:

1. Go to **Actions → ERA5 Monthly Pipeline → Run workflow**
2. Enter `target_year` and `target_month`
3. Click **Run workflow**

---

## Monitoring

### Checking GitHub Actions Runs

1. Navigate to **Actions** in the repository
2. Filter by workflow: `ERA5 Daily Pipeline`, `ERA5 Monthly Pipeline`, or `ERA5 Yearly Pipeline`
3. Green tick = success; red cross = failure
4. On failure, a GitHub Issue is automatically created (label: `bug`, `automated`)

### Checking S3 Contents

Tiles are stored under `tiles/{year}/{month:02d}/` in the S3 bucket.
Metrics JSON files are stored under `metrics/`.

Using the AWS CLI (configure with your credentials first):

```bash
# List months with tiles
aws s3 ls s3://<bucket>/tiles/ --recursive --endpoint-url <s3-endpoint-url>

# Count tiles for a specific month
aws s3 ls s3://<bucket>/tiles/2025/08/ --recursive --endpoint-url <s3-endpoint-url> | wc -l

# Inspect metrics file
aws s3 cp s3://<bucket>/metrics/metrics_2024.json - --endpoint-url <s3-endpoint-url>
```

---

## Recovery Procedures

### Missing Month (tiles not in S3)

1. Confirm the month is not in S3:
   ```bash
   aws s3 ls s3://<bucket>/tiles/2025/07/ --endpoint-url <s3-endpoint-url>
   ```
2. Run the monthly job with `TARGET_YEAR` / `TARGET_MONTH` set (see above).
3. Re-check S3 after the run completes.

### CDS API Down / Data Not Yet Available

ERA5-Land data is typically published ~5 days after month end.  
If the daily job detects data is unavailable it logs `"ERA5 data not yet available"` and skips — no action required.  
If the CDS service is down, the job will fail with a network error and a GitHub Issue will be created automatically.  
Wait 24 hours and re-trigger the workflow manually once the service recovers.

### Partial Tile Upload (validation failed)

The job logs `"Tile validation failed"` and exits with code 1.

1. Check the workflow logs for the validation error details.
2. Re-run with `FORCE_REPROCESS=true` to regenerate and re-upload tiles:
   ```bash
   docker run --rm \
     -e CDS_API_KEY="..." \
     ...
     -e FORCE_REPROCESS="true" \
     ghcr.io/tsafs/itishotnow:era5-monthly-latest
   ```

### Docker Image Build Failure

1. Go to **Actions → Build ERA5 Docker Images**
2. Review the failed step's logs
3. Common causes: dependency version conflict, analysis module import error
4. Fix the issue, push to `main`, and the build re-triggers automatically

---

## Debugging

### Inspect Container Logs

All jobs emit structured JSON logs to stdout:

```json
{"time": "2025-08-01T04:05:12Z", "level": "INFO", "message": "Fetching monthly ERA5 data"}
```

To stream logs while a container runs:

```bash
docker run --rm \
  -e CDS_API_KEY="..." \
  ... \
  ghcr.io/tsafs/itishotnow:era5-daily-latest 2>&1 | jq .
```

### Run Container Interactively

```bash
docker run --rm -it \
  -e CDS_API_KEY="..." \
  ... \
  --entrypoint bash \
  ghcr.io/tsafs/itishotnow:era5-daily-latest
```

Then manually run steps:

```bash
python src/check_new_data.py 2025 8
python src/process_daily.py
```

### Common Error Messages

| Message | Likely Cause | Action |
|---------|-------------|--------|
| `CDS_API_KEY is not set` | Secret missing in environment | Add `CDS_API_KEY` env var |
| `Failed to initialise provider` | Invalid `CLIMATE_DATA_PROVIDER` value | Check env var; default is `era5-land` |
| `ERA5 data not yet available` | Month not yet published by CDS | Wait until ~5 days after month end |
| `S3 list_objects failed` | Wrong endpoint/credentials | Verify `ACCESS_KEY`, `SECRET_KEY`, `ENDPOINT_URL` |
| `Tile validation failed` | Incomplete tile set generated | Force reprocess |
