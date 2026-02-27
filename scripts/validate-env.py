#!/usr/bin/env python3
"""
validate-env.py — Validate environment variables against schemas/env.schema.json.

Reads a .env file (or the current environment) and validates the key-value pairs
against the JSON Schema defined in schemas/env.schema.json.

Usage:
    python scripts/validate-env.py                    # Validate .env in project root
    python scripts/validate-env.py --env-file .env    # Specify a .env file
    python scripts/validate-env.py --from-environment # Validate from os.environ
    python scripts/validate-env.py --quiet            # Exit code only, no output

Exit codes:
    0 — All required variables present and valid
    1 — Validation failed (missing or invalid variables)
    2 — Schema file not found or parse error
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "env.schema.json"

# ANSI colors
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def parse_env_file(env_path: Path) -> dict[str, str]:
    """Parse a .env file into a dict, ignoring comments and blank lines."""
    env_vars: dict[str, str] = {}
    if not env_path.exists():
        return env_vars
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        env_vars[key] = value
    return env_vars


def load_schema() -> dict:
    """Load and return the env JSON schema."""
    if not SCHEMA_PATH.exists():
        print(f"{RED}[ERROR]{NC} Schema not found: {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(SCHEMA_PATH.read_text())
    except json.JSONDecodeError as e:
        print(f"{RED}[ERROR]{NC} Schema parse error: {e}", file=sys.stderr)
        sys.exit(2)


def validate_string_property(key: str, value: str, prop_schema: dict) -> list[str]:
    """Validate a single string property against its schema definition."""
    errors: list[str] = []

    if prop_schema.get("type") == "string":
        min_length = prop_schema.get("minLength", 0)
        if len(value) < min_length:
            errors.append(f"  '{key}': too short (min {min_length} chars)")

        if "enum" in prop_schema:
            if value not in prop_schema["enum"]:
                allowed = ", ".join(prop_schema["enum"])
                errors.append(f"  '{key}': must be one of [{allowed}], got '{value}'")

        if "pattern" in prop_schema:
            pattern = prop_schema["pattern"]
            if not re.match(pattern, value):
                errors.append(f"  '{key}': does not match pattern {pattern}")

        if "format" in prop_schema and prop_schema["format"] == "uri":
            if not value.startswith(("http://", "https://")):
                errors.append(f"  '{key}': not a valid URI")

    return errors


def validate_env(env_vars: dict[str, str], schema: dict, quiet: bool = False) -> bool:
    """Validate env vars against the schema. Returns True if valid."""
    errors: list[str] = []
    warnings: list[str] = []

    # Check required keys
    required_keys = schema.get("required", [])
    properties = schema.get("properties", {})

    for key in required_keys:
        if key not in env_vars:
            errors.append(f"  '{key}': MISSING (required)")
        elif not env_vars[key] or env_vars[key].startswith("your-"):
            warnings.append(f"  '{key}': appears to be a placeholder value")

    # Validate present keys against property schemas
    for key, value in env_vars.items():
        if key in properties:
            prop_errors = validate_string_property(key, value, properties[key])
            errors.extend(prop_errors)

    if not quiet:
        if errors:
            print(f"\n{RED}[FAIL]{NC} Environment validation failed:\n")
            for e in errors:
                print(f"  {RED}✗{NC} {e}")
        if warnings:
            print(f"\n{YELLOW}[WARN]{NC} Potential issues:\n")
            for w in warnings:
                print(f"  {YELLOW}⚠{NC} {w}")
        if not errors and not warnings:
            print(f"\n{GREEN}[OK]{NC} All environment variables valid.")
        elif not errors:
            print(f"\n{GREEN}[OK]{NC} Schema validation passed (with warnings).")

        # Print summary
        total = len(required_keys)
        present = sum(1 for k in required_keys if k in env_vars)
        print(f"\n  {present}/{total} required variables present")

    return len(errors) == 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate environment variables against schemas/env.schema.json"
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=PROJECT_ROOT / ".env",
        help="Path to .env file (default: <project>/.env)",
    )
    parser.add_argument(
        "--from-environment",
        action="store_true",
        help="Validate from os.environ instead of .env file",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output; exit code only",
    )
    parser.add_argument(
        "--check-example",
        action="store_true",
        help="Validate .env.example instead (for CI — checks structure, not values)",
    )
    args = parser.parse_args()

    schema = load_schema()

    if args.from_environment:
        env_vars = dict(os.environ)
        if not args.quiet:
            print(f"{BLUE}[INFO]{NC} Validating from os.environ")
    elif args.check_example:
        example_path = PROJECT_ROOT / ".env.example"
        env_vars = parse_env_file(example_path)
        if not args.quiet:
            print(f"{BLUE}[INFO]{NC} Validating {example_path}")
        # For --check-example, only verify keys exist (values are placeholders)
        required = schema.get("required", [])
        missing = [k for k in required if k not in env_vars]
        if missing and not args.quiet:
            print(f"\n{RED}[FAIL]{NC} .env.example missing required keys:")
            for k in missing:
                print(f"  {RED}✗{NC} {k}")
        elif not args.quiet:
            print(f"\n{GREEN}[OK]{NC} .env.example has all {len(required)} required keys.")
        sys.exit(1 if missing else 0)
    else:
        env_path = args.env_file
        if not env_path.exists():
            if not args.quiet:
                print(
                    f"{YELLOW}[WARN]{NC} No .env file found at {env_path}\n"
                    f"  Copy from .env.example: cp .env.example .env"
                )
            sys.exit(1)
        env_vars = parse_env_file(env_path)
        if not args.quiet:
            print(f"{BLUE}[INFO]{NC} Validating {env_path}")

    valid = validate_env(env_vars, schema, quiet=args.quiet)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
