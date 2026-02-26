```skill
---
name: schema-golden-guardrail
description: Add or update schema and golden-file checks for JSON, CSV, tile, and env outputs. Use when gating data drift before committing changes that affect structured outputs.
---

# Schema / Golden Guardrail Skill

## Purpose

Ensure structured outputs (JSON metrics, CSV data, PMTiles/MBTiles headers, `.env` vars) remain stable across code changes. This skill covers:

1. Authoring JSON Schema files for new output formats.
2. Writing golden-file snapshots for CSV headers and sample rows.
3. Adding tile header/size/checksum assertions.
4. Wiring schema validation into Vitest (frontend) or pytest (Python).

## Prerequisites

Before using this skill, gather context:

```
Subagent 1: "Find schemas/ directory at repo root. List all *.schema.json files. Return names + first 30 lines of each."
Subagent 2: "Find all *.test.ts files in frontend/src/ that import 'ajv' or 'json-schema' or 'zod'. Return file paths and relevant imports."
Subagent 3: "Find all conftest.py or test_*.py files in analysis/tests/. Return file paths and fixture names."
```

## Concepts

| Term | Meaning |
|------|---------|
| **Schema** | A JSON Schema (draft-07+) document describing required keys, types, and constraints for a JSON/CSV output. |
| **Golden file** | A committed reference copy of an output (or its hash). Tests compare the current output against this file. |
| **Drift** | Unintended structural change in an output (missing key, wrong type, extra column, changed tile size). |

## Implementation Steps

### Step 1: Author the JSON Schema

**Location**: `schemas/<domain>.schema.json`

```jsonc
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://itishotnow/schemas/<domain>.schema.json",
    "title": "<Domain> output",
    "description": "Schema for <domain> output produced by <pipeline or service>.",
    "type": "object",  // or "array"
    "required": ["field1", "field2"],
    "properties": {
        "field1": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" },
        "field2": { "type": "number", "minimum": -60, "maximum": 60 }
    },
    "additionalProperties": false
}
```

**Guidelines**:
- Mirror the TypeScript interface / Python dataclass that produces the output.
- Use `"additionalProperties": false` to catch unexpected keys.
- Use `"pattern"` for date strings, station IDs, ISO timestamps.
- Use `"minimum"` / `"maximum"` for plausible physical ranges (e.g., temperature −60…+60 °C).

### Step 2: Create a Golden File (CSV / JSON snapshot)

**Location**: `schemas/goldens/<domain>_golden.<ext>`

For CSV outputs, commit the header row and 3–5 representative rows:

```
date,stationId,tasmin,tasmax,tas
2024-01-01,00044,-2.3,5.1,1.4
2024-06-15,00044,14.2,28.7,21.5
2024-12-31,00044,-5.1,0.8,-2.2
```

For JSON outputs, commit a minified snapshot of the expected structure.

**Golden generation helper** (add to `scripts/update-goldens.sh`):

```bash
#!/usr/bin/env bash
# Regenerate golden files from current pipeline outputs.
# Run after intentional schema changes, then commit the updated goldens.
set -euo pipefail
SCHEMA_DIR="$(cd "$(dirname "$0")/../schemas/goldens" && pwd)"

# Example: copy first 5 rows of a CSV output
head -n 6 data/rolling_average/1951_2024/daily/00044_rolling_average.csv \
    > "$SCHEMA_DIR/rolling_average_golden.csv"

echo "Goldens updated in $SCHEMA_DIR"
```

### Step 3: Write Schema Validation Test (Frontend — Vitest)

**Location**: `frontend/src/__tests__/schema/<domain>.schema.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import Ajv from 'ajv';
import schema from '../../../../schemas/<domain>.schema.json';
import goldenData from '../../../../schemas/goldens/<domain>_golden.json';

const ajv = new Ajv({ allErrors: true });
const validate = ajv.compile(schema);

describe('<domain> schema validation', () => {
    it('golden file conforms to schema', () => {
        const valid = validate(goldenData);
        if (!valid) {
            console.error(validate.errors);
        }
        expect(valid).toBe(true);
    });

    it('rejects payload with missing required field', () => {
        const broken = { ...goldenData };
        delete (broken as Record<string, unknown>)['field1'];
        expect(validate(broken)).toBe(false);
    });

    it('rejects payload with wrong type', () => {
        const broken = { ...goldenData, field2: 'not-a-number' };
        expect(validate(broken)).toBe(false);
    });
});
```

**Dev dependency**: `npm install --save-dev ajv` (if not already present).

### Step 4: Write Schema Validation Test (Python — pytest)

**Location**: `analysis/tests/test_schema_<domain>.py`

```python
import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"

@pytest.fixture
def schema():
    with open(SCHEMA_DIR / "<domain>.schema.json") as f:
        return json.load(f)

@pytest.fixture
def golden():
    with open(SCHEMA_DIR / "goldens" / "<domain>_golden.json") as f:
        return json.load(f)

def test_golden_conforms(schema, golden):
    validate(instance=golden, schema=schema)

def test_rejects_missing_field(schema, golden):
    broken = {k: v for k, v in golden.items() if k != "field1"}
    with pytest.raises(ValidationError):
        validate(instance=broken, schema=schema),

def test_rejects_wrong_type(schema, golden):
    broken = {**golden, "field2": "not-a-number"}
    with pytest.raises(ValidationError):
        validate(instance=broken, schema=schema)
```

**Python dependency**: `pip install jsonschema` (add to pyproject.toml `[project.optional-dependencies]` under `test`).

### Step 5: CSV Header Golden Check

For CSV outputs where the schema is the header row:

```typescript
// frontend/src/__tests__/schema/csv-headers.test.ts
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const GOLDEN_DIR = resolve(__dirname, '../../../../schemas/goldens');

const CSV_GOLDENS: Record<string, string[]> = {
    'rolling_average_golden.csv': ['date', 'tas', 'tasmin', 'tasmax', 'hurs'],
    // Add more as needed
};

describe('CSV header goldens', () => {
    for (const [file, expectedHeaders] of Object.entries(CSV_GOLDENS)) {
        it(`${file} has expected headers`, () => {
            const content = readFileSync(resolve(GOLDEN_DIR, file), 'utf-8');
            const headerLine = content.split('\n')[0].trim();
            const headers = headerLine.split(',');
            expect(headers).toEqual(expectedHeaders);
        });
    }
});
```

### Step 6: Tile Header / Size Assertion (optional)

For PMTiles or MBTiles outputs:

```python
# analysis/tests/test_tile_golden.py
import struct
from pathlib import Path

TILE_FIXTURE = Path(__file__).parent / "fixtures" / "sample.pmtiles"

def test_pmtiles_magic_bytes():
    """PMTiles v3 starts with 0x4d50 ('PM')."""
    with open(TILE_FIXTURE, "rb") as f:
        magic = f.read(2)
    assert magic == b"PM", f"Expected PMTiles magic 'PM', got {magic!r}"

def test_tile_size_within_bounds():
    size = TILE_FIXTURE.stat().st_size
    assert 1_000 < size < 50_000_000, f"Tile size {size} out of expected range"
```

## Failure Modes & Self-Correction

| Failure | Cause | Fix |
|---------|-------|-----|
| `validate(golden)` returns `false` | Schema stricter than data | Relax schema constraints or update golden |
| Golden file mismatch after code change | Intentional output change | Re-run `scripts/update-goldens.sh`, review diff, commit |
| `additionalProperties` rejection | New field added to output | Add field to schema, regenerate golden |
| CSV header mismatch | Column renamed/added/removed | Update `CSV_GOLDENS` map and golden file |
| Tile size out of bounds | Rendering change or zoom level drift | Adjust bounds or regenerate fixture tile |

## Checklist

- [ ] JSON Schema authored in `schemas/` with `additionalProperties: false`
- [ ] Golden file committed in `schemas/goldens/`
- [ ] Vitest validation test passes (`npm run test`)
- [ ] pytest validation test passes (`pytest analysis/tests/`)
- [ ] Negative tests (missing field, wrong type) fail validation as expected
- [ ] `scripts/update-goldens.sh` documented and runnable
- [ ] Schema referenced in the relevant botox phase plan
```
