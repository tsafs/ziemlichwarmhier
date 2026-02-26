```skill
---
name: env-validation
description: Add or update .env.example variables and env schema validation. Use when adding environment variables needed by the frontend, Python pipelines, or GitHub Actions workflows with mocked secrets for local act runs.
---

# Env Validation Skill

## Purpose

Ensure all required environment variables are documented in `.env.example`, validated at startup or preflight, and mockable for local CI parity via `act`. Covers: `.env.example` authoring, JSON schema for env vars, validation script, and act secret mocking.

## Prerequisites

Gather context:

```
Subagent 1: "Check if .env.example exists at repo root. Return contents or 'not found'."
Subagent 2: "Search for process.env or import.meta.env in frontend/src/. Return all occurrences with file paths."
Subagent 3: "Search for os.environ in analysis/ and jobs/. Return all occurrences with file paths."
Subagent 4: "Read .github/workflows/. Return all secrets.* and env references."
Subagent 5: "Check if scripts/validate-env.py exists. Return contents or 'not found'."
```

## Implementation Steps

### Step 1: Create or Update .env.example

**Location**: `.env.example` (repo root)

```bash
# Frontend (Vite)
# These are accessed via import.meta.env.VITE_*
VITE_APP_NOW=                    # Optional: override "now" datetime (ISO 8601, e.g., 2025-11-28T12:00:00Z)

# S3 / Object Storage (used by rclone deploy and Python jobs)
AWS_ACCESS_KEY_ID=               # Required for deploy/jobs
AWS_SECRET_ACCESS_KEY=           # Required for deploy/jobs
S3_ENDPOINT_URL=                 # Required for deploy/jobs (e.g., https://s3.fr-par.scw.cloud)
S3_BUCKET_NAME=                  # Required for deploy/jobs

# CDS API (one-time ERA5-Land fixture pull)
CDS_API_KEY=                     # Required only for ERA5-Land fixture generation

# Docker / GHCR (CI only)
GITHUB_TOKEN=                    # Provided by GitHub Actions automatically
```

Document each variable with a comment explaining: required vs optional, who uses it, example value.

### Step 2: Create Env JSON Schema

**Location**: `schemas/env.schema.json`

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://itishotnow/schemas/env.schema.json",
    "title": "Environment variables",
    "description": "Required and optional environment variables for itishotnow.",
    "type": "object",
    "required": [],
    "properties": {
        "VITE_APP_NOW": {
            "type": "string",
            "description": "Override current datetime for frontend (ISO 8601)",
            "pattern": "^(|\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z)$"
        },
        "AWS_ACCESS_KEY_ID": {
            "type": "string",
            "description": "S3 access key for deploy and jobs",
            "minLength": 1
        },
        "AWS_SECRET_ACCESS_KEY": {
            "type": "string",
            "description": "S3 secret key for deploy and jobs",
            "minLength": 1
        },
        "S3_ENDPOINT_URL": {
            "type": "string",
            "description": "S3 endpoint URL",
            "format": "uri"
        },
        "S3_BUCKET_NAME": {
            "type": "string",
            "description": "S3 bucket name",
            "minLength": 1
        },
        "CDS_API_KEY": {
            "type": "string",
            "description": "Copernicus CDS API key (one-time fixture pull)"
        }
    },
    "additionalProperties": true
}
```

Use `"required": [...]` to list vars that **must** be set for a given context. The validation script accepts a `--context` flag.

### Step 3: Create Validation Script

**Location**: `scripts/validate-env.py`

```python
#!/usr/bin/env python3
"""
Validate environment variables against schemas/env.schema.json.

Usage:
    python scripts/validate-env.py                     # Validate all optional
    python scripts/validate-env.py --context deploy     # Require deploy vars
    python scripts/validate-env.py --context jobs       # Require job vars
    python scripts/validate-env.py --context cds        # Require CDS API key
    python scripts/validate-env.py --env-file .env      # Load from file first
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "env.schema.json"

# Context-specific required fields
CONTEXT_REQUIRED = {
    "deploy": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_ENDPOINT_URL", "S3_BUCKET_NAME"],
    "jobs": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_ENDPOINT_URL", "S3_BUCKET_NAME"],
    "cds": ["CDS_API_KEY"],
    "frontend": [],  # All optional for frontend
}


def load_env_file(path: str) -> None:
    """Load key=value pairs from file into os.environ."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate environment variables")
    parser.add_argument("--context", choices=list(CONTEXT_REQUIRED.keys()), default="frontend")
    parser.add_argument("--env-file", help="Load .env file before validating")
    args = parser.parse_args()

    if args.env_file:
        load_env_file(args.env_file)

    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    # Override required fields based on context
    schema = {**schema, "required": CONTEXT_REQUIRED.get(args.context, [])}

    # Build env dict from current environment, filtered to schema properties
    env_vars = {}
    for key in schema.get("properties", {}):
        value = os.environ.get(key, "")
        if value:
            env_vars[key] = value

    try:
        validate(instance=env_vars, schema=schema)
        print(f"✓ Env validation passed (context: {args.context})")
        sys.exit(0)
    except ValidationError as e:
        print(f"✗ Env validation failed: {e.message}", file=sys.stderr)
        print(f"  Path: {'.'.join(str(p) for p in e.absolute_path)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Step 4: Create act Secrets Mock

**Location**: `.github/act/.secrets` (gitignored)

```
AWS_ACCESS_KEY_ID=test-key-id
AWS_SECRET_ACCESS_KEY=test-secret-key
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=test-bucket
GITHUB_TOKEN=ghp_test_token_for_act
```

Add to `.gitignore`:
```
.github/act/.secrets
```

### Step 5: Write Tests

**Location**: `analysis/tests/test_validate_env.py`

```python
import os
import subprocess
import pytest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate-env.py"


def test_frontend_context_passes_with_empty_env():
    """Frontend context has no required vars."""
    result = subprocess.run(
        ["python", str(SCRIPT), "--context", "frontend"],
        capture_output=True, text=True,
        env={**os.environ, "PATH": os.environ["PATH"]},
    )
    assert result.returncode == 0


def test_deploy_context_fails_without_vars():
    """Deploy context requires S3 vars."""
    clean_env = {k: v for k, v in os.environ.items()
                 if k not in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")}
    result = subprocess.run(
        ["python", str(SCRIPT), "--context", "deploy"],
        capture_output=True, text=True, env=clean_env,
    )
    assert result.returncode == 1


def test_deploy_context_passes_with_vars():
    """Deploy context passes with all vars set."""
    env = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "S3_ENDPOINT_URL": "http://localhost:9000",
        "S3_BUCKET_NAME": "test",
    }
    result = subprocess.run(
        ["python", str(SCRIPT), "--context", "deploy"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0
```

## Run Commands

```bash
# Validate for frontend (no required vars)
python scripts/validate-env.py --context frontend

# Validate for deploy
python scripts/validate-env.py --context deploy --env-file .env

# Run tests
python -m pytest analysis/tests/test_validate_env.py -v
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| `jsonschema` not installed | Missing dependency | `pip install jsonschema` or add to pyproject.toml |
| Schema file not found | Wrong relative path | Check `SCHEMA_PATH` resolves correctly from script location |
| `act` can't find secrets | `.secrets` not in expected path | Pass `--secret-file .github/act/.secrets` to act |
| Validation passes when it shouldn't | `required` array empty | Check `--context` flag and `CONTEXT_REQUIRED` mapping |
| `.env.example` not in sync with schema | Vars added to code but not documented | Grep for `process.env` / `import.meta.env` / `os.environ` |

## Checklist

- [ ] `.env.example` created/updated with all vars documented
- [ ] `schemas/env.schema.json` covers all vars with types/patterns
- [ ] `scripts/validate-env.py` runs with context flags
- [ ] `.github/act/.secrets` created and gitignored
- [ ] Tests pass for frontend (no-op) and deploy (requires S3) contexts
- [ ] Preflight script calls `validate-env.py`
```
