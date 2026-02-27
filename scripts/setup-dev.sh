#!/usr/bin/env bash
# =============================================================================
# setup-dev.sh — One-time development environment setup
# =============================================================================
# Sets up the full development environment from a fresh clone.
#
# Requirements:
#   - Python 3.13+ (pyenv recommended)
#   - Node.js 20+ (nvm recommended)
#   - Poetry (pip install poetry)
#
# Usage:
#   ./scripts/setup-dev.sh          # Full setup
#   ./scripts/setup-dev.sh --ci     # CI mode: skip optional tool checks
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

CI_MODE=false
for arg in "$@"; do
    case "$arg" in
        --ci) CI_MODE=true ;;
    esac
done

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_fail()    { echo -e "${RED}[FAIL]${NC}  $*"; }
log_section() { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }

# ---------------------------------------------------------------------------
# 1. Check prerequisites
# ---------------------------------------------------------------------------
log_section "Checking prerequisites"

check_command() {
    local cmd="$1"
    local install_hint="$2"
    if command -v "$cmd" &>/dev/null; then
        log_ok "$cmd found: $(command -v "$cmd")"
        return 0
    else
        log_fail "$cmd not found. $install_hint"
        return 1
    fi
}

PREREQS_OK=true

check_command python3 "Install Python 3.13+ from python.org or via pyenv" || PREREQS_OK=false
check_command node "Install Node.js 20+ from nodejs.org or via nvm" || PREREQS_OK=false
check_command npm "Install Node.js 20+ (npm is bundled)" || PREREQS_OK=false

# Check Python version
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if python3 -c "import sys; assert sys.version_info >= (3,13)" 2>/dev/null; then
        log_ok "Python $PY_VERSION (>=3.13 required)"
    else
        log_warn "Python $PY_VERSION found — 3.13+ recommended"
    fi
fi

# Check Node version
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
    if [[ "$NODE_MAJOR" -ge 20 ]]; then
        log_ok "Node.js v$NODE_VERSION (>=20 required)"
    else
        log_warn "Node.js v$NODE_VERSION found — v20+ recommended"
    fi
fi

if [[ "$PREREQS_OK" == false ]]; then
    log_fail "Some prerequisites are missing. Please install them and re-run."
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Environment variables
# ---------------------------------------------------------------------------
log_section "Environment variables"

ENV_FILE="$PROJECT_ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
    log_ok ".env already exists — skipping copy"
else
    if [[ -f "$PROJECT_ROOT/.env.example" ]]; then
        cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
        log_ok "Copied .env.example → .env"
        log_warn "Fill in your credentials in .env before running pipelines."
    else
        log_warn ".env.example not found — skipping"
    fi
fi

# Validate env schema (non-fatal in dev setup)
if [[ -f "$PROJECT_ROOT/scripts/validate-env.py" && -f "$ENV_FILE" ]]; then
    log_info "Validating environment variables..."
    python3 "$PROJECT_ROOT/scripts/validate-env.py" --quiet || \
        log_warn "Some env vars are missing or invalid (expected for fresh setup)"
fi

# ---------------------------------------------------------------------------
# 3. Python dependencies
# ---------------------------------------------------------------------------
log_section "Python dependencies"

cd "$PROJECT_ROOT"

if command -v poetry &>/dev/null; then
    log_info "Installing Python dependencies via Poetry..."
    poetry install --with test
    log_ok "Python dependencies installed (Poetry)"
elif pip3 show pip &>/dev/null; then
    log_info "Poetry not found — falling back to pip install..."
    pip3 install -e ".[test]"
    log_ok "Python dependencies installed (pip)"
else
    log_fail "Neither poetry nor pip3 found. Cannot install Python dependencies."
    exit 1
fi

# ---------------------------------------------------------------------------
# 4. Frontend dependencies
# ---------------------------------------------------------------------------
log_section "Frontend dependencies"

cd "$FRONTEND_DIR"

log_info "Installing Node.js dependencies..."
npm ci
log_ok "Frontend dependencies installed"

# ---------------------------------------------------------------------------
# 5. Verify tests pass
# ---------------------------------------------------------------------------
log_section "Verifying test setup"

cd "$FRONTEND_DIR"
log_info "Running frontend smoke tests..."
if npm run test 2>&1 | tail -5; then
    log_ok "Frontend tests pass"
else
    log_warn "Frontend tests had failures — check output above"
fi

cd "$PROJECT_ROOT"
log_info "Running Python smoke tests..."
if python3 -m pytest analysis/tests/test_smoke.py -q 2>&1 | tail -5; then
    log_ok "Python tests pass"
else
    log_warn "Python tests had failures — check output above"
fi

# ---------------------------------------------------------------------------
# 6. Optional tools
# ---------------------------------------------------------------------------
if [[ "$CI_MODE" == false ]]; then
    log_section "Optional tools"

    if ! command -v actionlint &>/dev/null; then
        log_info "actionlint not found (optional). Install: https://github.com/rhysd/actionlint"
    else
        log_ok "actionlint: $(actionlint --version 2>/dev/null | head -1)"
    fi

    if ! command -v act &>/dev/null; then
        log_info "act not found (optional, for local GHA runs). Install: https://github.com/nektos/act"
    else
        log_ok "act: $(act --version 2>/dev/null)"
    fi

    if ! command -v docker &>/dev/null; then
        log_info "docker not found (optional, required for local job testing)"
    else
        log_ok "docker: $(docker --version)"
    fi
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
log_section "Setup complete"
echo -e ""
echo -e "  ${GREEN}Next steps:${NC}"
echo -e "  1. Fill in ${BOLD}.env${NC} with your credentials"
echo -e "  2. Run ${BOLD}./scripts/run-preflight.sh${NC} to verify everything works"
echo -e "  3. Start the frontend: ${BOLD}cd frontend && npm start${NC}"
echo -e ""
