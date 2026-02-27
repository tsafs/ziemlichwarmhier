#!/usr/bin/env bash
# =============================================================================
# act-local.sh — Run GitHub Actions workflows locally via act
# =============================================================================
# Usage:
#   ./scripts/act-local.sh                     # Run all workflows (dry-run)
#   ./scripts/act-local.sh build               # Run build-and-deploy workflow
#   ./scripts/act-local.sh docker-10min        # Run 10min station data Docker build
#   ./scripts/act-local.sh docker-daily        # Run daily station data Docker build
#   ./scripts/act-local.sh lint                # Run actionlint only
#   ./scripts/act-local.sh --list              # List available workflows
#
# Prerequisites:
#   - act: https://github.com/nektos/act (brew install act / go install)
#   - actionlint: https://github.com/rhysd/actionlint (brew install actionlint)
#   - Docker running locally
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKFLOWS_DIR="$PROJECT_ROOT/.github/workflows"
SECRETS_FILE="$PROJECT_ROOT/.act-secrets"
SECRETS_EXAMPLE="$PROJECT_ROOT/.act-secrets.example"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------
check_dependencies() {
    local missing=0

    if ! command -v act &>/dev/null; then
        log_error "act not found. Install: https://github.com/nektos/act"
        missing=1
    fi

    if ! command -v actionlint &>/dev/null; then
        log_warn "actionlint not found. Install: https://github.com/rhysd/actionlint"
        log_warn "Skipping workflow linting."
    fi

    if ! command -v docker &>/dev/null; then
        log_error "docker not found. act requires Docker to run workflows."
        missing=1
    elif ! docker info &>/dev/null 2>&1; then
        log_error "Docker daemon not running. Start Docker first."
        missing=1
    fi

    if [[ $missing -eq 1 ]]; then
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Ensure secrets file exists
# ---------------------------------------------------------------------------
ensure_secrets() {
    if [[ ! -f "$SECRETS_FILE" ]]; then
        if [[ -f "$SECRETS_EXAMPLE" ]]; then
            log_warn "No .act-secrets found. Copying from .act-secrets.example"
            cp "$SECRETS_EXAMPLE" "$SECRETS_FILE"
        else
            log_error "No .act-secrets or .act-secrets.example found."
            exit 1
        fi
    fi
}

# ---------------------------------------------------------------------------
# Run actionlint on all workflow files
# ---------------------------------------------------------------------------
run_actionlint() {
    log_info "Running actionlint on workflow files..."
    if ! command -v actionlint &>/dev/null; then
        log_warn "actionlint not installed — skipping."
        return 0
    fi

    if actionlint "$WORKFLOWS_DIR"/*.yml; then
        log_ok "actionlint passed — all workflows valid."
        return 0
    else
        log_error "actionlint found issues."
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Run a specific workflow via act (dry-run by default)
# ---------------------------------------------------------------------------
run_workflow() {
    local workflow_file="$1"
    local workflow_name
    workflow_name="$(basename "$workflow_file")"

    log_info "Running workflow: $workflow_name"
    log_info "  (dry-run mode — deploy/push steps will use mocked secrets)"

    cd "$PROJECT_ROOT"
    act push \
        --workflows "$workflow_file" \
        --secret-file "$SECRETS_FILE" \
        --env GITHUB_ACTOR=act-local-user \
        --env GITHUB_REPOSITORY=tsafs/itishotnow \
        --platform ubuntu-latest=catthehacker/ubuntu:act-latest \
        --verbose \
        2>&1 | tail -100

    local exit_code=${PIPESTATUS[0]}
    if [[ $exit_code -eq 0 ]]; then
        log_ok "$workflow_name completed successfully."
    else
        log_error "$workflow_name failed (exit $exit_code)."
    fi
    return $exit_code
}

# ---------------------------------------------------------------------------
# List available workflows
# ---------------------------------------------------------------------------
list_workflows() {
    log_info "Available workflows:"
    for f in "$WORKFLOWS_DIR"/*.yml; do
        local name
        name="$(basename "$f" .yml)"
        local title
        title="$(grep -m1 '^name:' "$f" | sed 's/^name: *//')"
        echo "  - $name: $title"
    done
    echo ""
    echo "Shortcuts:"
    echo "  build         → build-and-deploy-frontend-to-s3"
    echo "  docker-10min  → docker-build-job-update-10min-station-data"
    echo "  docker-daily  → docker-build-job-update-daily-station-data"
    echo "  lint          → actionlint only"
    echo "  all           → lint + all workflows"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    local target="${1:-all}"

    case "$target" in
        --help|-h)
            list_workflows
            exit 0
            ;;
        --list)
            list_workflows
            exit 0
            ;;
        lint)
            check_dependencies
            run_actionlint
            ;;
        build)
            check_dependencies
            ensure_secrets
            run_actionlint || true
            run_workflow "$WORKFLOWS_DIR/build-and-deploy-frontend-to-s3.yml"
            ;;
        docker-10min)
            check_dependencies
            ensure_secrets
            run_workflow "$WORKFLOWS_DIR/docker-build-job-update-10min-station-data.yml"
            ;;
        docker-daily)
            check_dependencies
            ensure_secrets
            run_workflow "$WORKFLOWS_DIR/docker-build-job-update-daily-station-data.yml"
            ;;
        all)
            check_dependencies
            ensure_secrets

            local failures=0

            # 1. Lint workflows
            run_actionlint || ((failures++))

            # 2. Build & deploy frontend (dry-run)
            run_workflow "$WORKFLOWS_DIR/build-and-deploy-frontend-to-s3.yml" || ((failures++))

            # 3. Docker builds (dry-run)
            run_workflow "$WORKFLOWS_DIR/docker-build-job-update-10min-station-data.yml" || ((failures++))
            run_workflow "$WORKFLOWS_DIR/docker-build-job-update-daily-station-data.yml" || ((failures++))

            echo ""
            if [[ $failures -eq 0 ]]; then
                log_ok "All local CI checks passed."
            else
                log_error "$failures workflow(s) failed."
                exit 1
            fi
            ;;
        *)
            log_error "Unknown target: $target"
            list_workflows
            exit 1
            ;;
    esac
}

main "$@"
