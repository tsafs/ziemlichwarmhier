#!/usr/bin/env bash
# =============================================================================
# run-preflight.sh — Pre-commit / pre-phase quality gate
# =============================================================================
# Runs all deterministic checks and surfaces a single pass/fail summary.
# Exit code 0 = all passed, non-zero = at least one failed.
#
# Checks (in order):
#   1. Frontend unit tests (Vitest)
#   2. Frontend coverage thresholds
#   3. Python unit tests (pytest)
#   4. Schema / golden validation (frontend)
#   5. TypeScript type-check
#   6. actionlint (workflow linting)
#   7. Env validation (validate-env.py)
#
# Optional (if tools available):
#   8. act dry-run (requires Docker + act)
#
# Usage:
#   ./scripts/run-preflight.sh          # Run all checks
#   ./scripts/run-preflight.sh --quick  # Skip act dry-runs and coverage
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Parse args
QUICK_MODE=false
for arg in "$@"; do
    case "$arg" in
        --quick) QUICK_MODE=true ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Result tracking
declare -a CHECK_NAMES
declare -a CHECK_RESULTS

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_fail()    { echo -e "${RED}[FAIL]${NC}  $*"; }
log_skip()    { echo -e "${YELLOW}[SKIP]${NC}  $*"; }
log_section() { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }

# Record a check result: record_result "Name" 0|1|skip
record_result() {
    CHECK_NAMES+=("$1")
    CHECK_RESULTS+=("$2")
}

# ---------------------------------------------------------------------------
# 1. Frontend unit tests
# ---------------------------------------------------------------------------
run_frontend_tests() {
    log_section "Frontend Unit Tests"

    if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
        log_info "Installing frontend dependencies..."
        (cd "$FRONTEND_DIR" && npm ci --silent) || {
            log_fail "npm ci failed"
            record_result "Frontend tests" "FAIL"
            return
        }
    fi

    if (cd "$FRONTEND_DIR" && npm run test 2>&1); then
        log_ok "Frontend tests passed."
        record_result "Frontend tests" "OK"
    else
        log_fail "Frontend tests failed."
        record_result "Frontend tests" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# 2. Frontend coverage
# ---------------------------------------------------------------------------
run_frontend_coverage() {
    if $QUICK_MODE; then
        log_skip "Frontend coverage (--quick mode)"
        record_result "Frontend coverage" "SKIP"
        return
    fi

    log_section "Frontend Coverage"

    if (cd "$FRONTEND_DIR" && npm run test:coverage 2>&1); then
        log_ok "Frontend coverage thresholds met."
        record_result "Frontend coverage" "OK"
    else
        log_fail "Frontend coverage below thresholds."
        record_result "Frontend coverage" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# 3. Python unit tests
# ---------------------------------------------------------------------------
run_python_tests() {
    log_section "Python Unit Tests"

    if python -m pytest analysis/tests/ -v 2>&1; then
        log_ok "Python tests passed."
        record_result "Python tests" "OK"
    else
        log_fail "Python tests failed."
        record_result "Python tests" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# 4. Schema / golden validation
# ---------------------------------------------------------------------------
run_schema_validation() {
    log_section "Schema Validation"

    if (cd "$FRONTEND_DIR" && npx vitest run src/__tests__/schema-validation.test.ts 2>&1); then
        log_ok "Schema validation passed."
        record_result "Schema validation" "OK"
    else
        log_fail "Schema validation failed."
        record_result "Schema validation" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# 5. TypeScript type-check
# ---------------------------------------------------------------------------
run_typecheck() {
    log_section "TypeScript Type-Check"

    if (cd "$FRONTEND_DIR" && npx tsc --noEmit 2>&1); then
        log_ok "TypeScript type-check passed."
        record_result "TypeScript check" "OK"
    else
        log_fail "TypeScript type-check failed."
        record_result "TypeScript check" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# 6. actionlint
# ---------------------------------------------------------------------------
run_actionlint() {
    log_section "actionlint (Workflow Linting)"

    if ! command -v actionlint &>/dev/null; then
        log_skip "actionlint not installed."
        record_result "actionlint" "SKIP"
        return
    fi

    if actionlint "$PROJECT_ROOT/.github/workflows"/*.yml 2>&1; then
        log_ok "actionlint passed."
        record_result "actionlint" "OK"
    else
        log_fail "actionlint found issues."
        record_result "actionlint" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# 7. Env validation
# ---------------------------------------------------------------------------
run_env_validation() {
    log_section "Env Validation (.env.example)"

    if python "$PROJECT_ROOT/scripts/validate-env.py" --check-example 2>&1; then
        log_ok ".env.example matches env schema."
        record_result "Env validation" "OK"
    else
        log_fail ".env.example missing required keys."
        record_result "Env validation" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# 8. act dry-run (optional)
# ---------------------------------------------------------------------------
run_act_dryrun() {
    if $QUICK_MODE; then
        log_skip "act dry-run (--quick mode)"
        record_result "act dry-run" "SKIP"
        return
    fi

    log_section "act Dry-Run (Local CI)"

    if ! command -v act &>/dev/null; then
        log_skip "act not installed — skipping local CI dry-run."
        record_result "act dry-run" "SKIP"
        return
    fi

    if ! docker info &>/dev/null 2>&1; then
        log_skip "Docker not running — skipping act dry-run."
        record_result "act dry-run" "SKIP"
        return
    fi

    if bash "$SCRIPT_DIR/act-local.sh" build 2>&1; then
        log_ok "act dry-run passed."
        record_result "act dry-run" "OK"
    else
        log_fail "act dry-run failed."
        record_result "act dry-run" "FAIL"
    fi
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print_summary() {
    local total=${#CHECK_NAMES[@]}
    local passed=0
    local failed=0
    local skipped=0

    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  PREFLIGHT SUMMARY${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"

    for i in "${!CHECK_NAMES[@]}"; do
        local name="${CHECK_NAMES[$i]}"
        local result="${CHECK_RESULTS[$i]}"
        local dots
        dots=$(printf '%*s' $((30 - ${#name})) '' | tr ' ' '.')

        case "$result" in
            OK)
                echo -e "  ${name} ${dots} ${GREEN}OK${NC}"
                ((passed++))
                ;;
            FAIL)
                echo -e "  ${name} ${dots} ${RED}FAIL${NC}"
                ((failed++))
                ;;
            SKIP)
                echo -e "  ${name} ${dots} ${YELLOW}SKIP${NC}"
                ((skipped++))
                ;;
        esac
    done

    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"

    if [[ $failed -eq 0 ]]; then
        echo -e "  Result: ${GREEN}ALL CHECKS PASSED${NC} ($passed passed, $skipped skipped)"
    else
        echo -e "  Result: ${RED}$failed CHECK(S) FAILED${NC} ($passed passed, $failed failed, $skipped skipped)"
    fi

    echo -e "${BOLD}═══════════════════════════════════════════════${NC}"
    echo ""

    [[ $failed -eq 0 ]]
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    echo -e "${BOLD}"
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║       PREFLIGHT QUALITY GATE          ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo -e "${NC}"

    cd "$PROJECT_ROOT"

    run_frontend_tests
    run_frontend_coverage
    run_python_tests
    run_schema_validation
    run_typecheck
    run_actionlint
    run_env_validation
    run_act_dryrun

    print_summary
}

main "$@"
