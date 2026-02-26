```skill
---
name: gha-matrix
description: Add or update GitHub Actions workflows with job matrices, local act parity, actionlint validation, and mocked secrets. Use when creating new CI/CD pipelines or ensuring local reproducibility of existing workflows.
---

# GH Actions Job/Pipeline Matrix Skill

## Purpose

Create or modify GitHub Actions workflows that can be validated locally using `act` and `actionlint`. Covers: workflow authoring, job matrices, mocked secrets, local dry-runs, and actionlint linting.

## Prerequisites

Gather context:

```
Subagent 1: "Read .github/workflows/. List all YAML files and return contents of each."
Subagent 2: "Check if .github/act/ directory exists. Return contents."
Subagent 3: "Check if actionlint is installed: run 'which actionlint' or 'actionlint --version'."
Subagent 4: "Check if act is installed: run 'which act' or 'act --version'."
Subagent 5: "Read .github/act/.secrets if it exists."
```

## Concepts

| Term | Meaning |
|------|---------|
| **act** | Tool to run GitHub Actions locally using Docker containers |
| **actionlint** | Static linter for GitHub Actions workflow YAML files |
| **Job matrix** | `strategy.matrix` that fans out a job across parameter combinations |
| **Mocked secrets** | Local `.secrets` file substituting real credentials for dry-runs |

## Implementation Steps

### Step 1: Create/Modify Workflow

**Location**: `.github/workflows/<name>.yml`

```yaml
name: <Workflow Name>

on:
  push:
    branches: [main]
    paths:
      - '<trigger-path>/**'
  pull_request:
    branches: [main]
    paths:
      - '<trigger-path>/**'
  workflow_dispatch:  # Allow manual trigger + act compatibility

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20]
        # Or for multiple targets:
        # target: [frontend, analysis]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Run tests
        working-directory: frontend
        run: npm run test -- --run

      - name: Build
        working-directory: frontend
        run: npm run build
```

### Step 2: Add Job Matrix for Multi-Target Builds

For workflows that build multiple Docker images or run multiple test suites:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - job: daily-station-data
            context: jobs/job-update-daily-station-data
            tag: daily-latest
          - job: 10min-station-data
            context: jobs/job-update-10min-station-data
            tag: latest
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - name: Build ${{ matrix.job }}
        uses: docker/build-push-action@v6
        with:
          context: ${{ matrix.context }}
          push: false  # Set to true for deploy
          tags: ghcr.io/${{ github.repository }}:${{ matrix.tag }}
```

### Step 3: Set Up act for Local Runs

**Install act** (if not present):

```bash
# macOS
brew install act

# Linux
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

**Create secrets file**:

**Location**: `.github/act/.secrets`

```
AWS_ACCESS_KEY_ID=test-key
AWS_SECRET_ACCESS_KEY=test-secret
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=test-bucket
GITHUB_TOKEN=ghp_test_token
```

**Create event payload** (optional):

**Location**: `.github/act/push-event.json`

```json
{
    "ref": "refs/heads/main",
    "repository": {
        "full_name": "owner/itishotnow"
    }
}
```

### Step 4: Run Workflows Locally

```bash
# List available workflows and jobs
act -l

# Dry-run the build-and-test job
act push \
    --secret-file .github/act/.secrets \
    --eventpath .github/act/push-event.json \
    -j build-and-test \
    --dryrun

# Actually run (requires Docker)
act push \
    --secret-file .github/act/.secrets \
    -j build-and-test \
    -P ubuntu-latest=catthehacker/ubuntu:act-22.04

# Run specific workflow file
act -W .github/workflows/<name>.yml \
    --secret-file .github/act/.secrets \
    --dryrun
```

### Step 5: Add actionlint Validation

**Install actionlint**:

```bash
# macOS
brew install actionlint

# Linux
curl -sL https://github.com/rhysd/actionlint/releases/latest/download/actionlint_linux_amd64.tar.gz | tar xz
sudo mv actionlint /usr/local/bin/
```

**Run**:

```bash
# Lint all workflows
actionlint

# Lint specific file
actionlint .github/workflows/<name>.yml
```

**Common actionlint fixes**:

| Error | Fix |
|-------|-----|
| `shellcheck reported issue` | Fix bash syntax in `run:` blocks |
| `expression type mismatch` | Use correct context types (e.g., `${{ matrix.node-version }}` is string) |
| `unknown action` | Pin action to specific version tag |
| `workflow_dispatch not allowed` | Ensure `on:` block syntax is correct |

### Step 6: Add Workflow Test to Preflight

**Location**: `scripts/run-preflight.sh` (add section)

```bash
echo "=== actionlint ==="
if command -v actionlint &>/dev/null; then
    actionlint
    echo "✓ actionlint passed"
else
    echo "⚠ actionlint not installed, skipping"
fi

echo "=== act dry-run ==="
if command -v act &>/dev/null; then
    act -l --secret-file .github/act/.secrets 2>/dev/null
    echo "✓ act workflow list succeeded"

    # Dry-run key workflows
    for wf in build-and-deploy-frontend-to-s3; do
        act push -W ".github/workflows/${wf}.yml" \
            --secret-file .github/act/.secrets \
            --dryrun 2>&1 | tail -5
        echo "✓ act dry-run: ${wf}"
    done
else
    echo "⚠ act not installed, skipping"
fi
```

## Workflow Patterns

### Conditional Deploy (skip in act)

```yaml
- name: Deploy
  if: ${{ !env.ACT }}  # ACT env var is set when running under act
  run: rclone sync dist/ remote:bucket/
```

### Reusable Workflow

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      working-directory:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
        working-directory: ${{ inputs.working-directory }}
      - run: npm test -- --run
        working-directory: ${{ inputs.working-directory }}
```

## Run Commands

```bash
# Lint all workflows
actionlint

# List act jobs
act -l

# Dry-run specific job
act push -j build-and-test --secret-file .github/act/.secrets --dryrun

# Full act run
act push -j build-and-test --secret-file .github/act/.secrets
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| `actionlint` reports unknown action | Action not pinned to version | Use `@v4` not `@main` |
| `act` can't find Docker image | Missing `-P` platform mapping | Add `-P ubuntu-latest=catthehacker/ubuntu:act-22.04` |
| Secrets not available in act | Wrong secrets file path | Use `--secret-file .github/act/.secrets` |
| Matrix job doesn't fan out in act | act may not fully support matrix | Run each matrix combination individually |
| Deploy step runs in act | Missing `if: ${{ !env.ACT }}` guard | Add guard to deploy/push steps |

## Checklist

- [ ] Workflow YAML authored with proper triggers and paths
- [ ] Job matrix configured (if multi-target)
- [ ] `actionlint` passes on all workflow files
- [ ] `.github/act/.secrets` created and gitignored
- [ ] `act --dryrun` succeeds for key jobs
- [ ] Deploy steps guarded with `if: ${{ !env.ACT }}`
- [ ] `workflow_dispatch` added for manual trigger compatibility
- [ ] Preflight script includes actionlint + act checks
```
