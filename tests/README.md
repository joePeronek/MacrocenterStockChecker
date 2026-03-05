# Test Strategy and Reliability Baseline

This repository follows a pragmatic MVP test pyramid with deterministic tests only.

## Test Pyramid

1. **Unit tests (`tests/test_*.py`)**
   - Pure parsing and retry classification logic.
   - No network, no DB, no filesystem side effects beyond local fixtures.
2. **Parser regression tests (`tests/fixtures/`)**
   - Known problematic source strings are captured as fixtures.
   - Every parser behavior change should update fixtures and assertions.
3. **Integration tests (future: `tests/integration/`)**
   - End-to-end checks for connector + normalizer + storage using mocks/stubs.
   - Must remain deterministic; do not hit live store websites.

## Reliability Standards

- Classify failures into `transient`, `throttled`, or `permanent`.
- Retry policy tests must verify deterministic backoff.
- Parser tests must include:
  - locale-specific prices (`1.999,99`, `1,999.99`, space separators)
  - ambiguous or unknown stock strings
  - empty/invalid payload handling

## Fixture Guidance

- Add regression fixtures under `tests/fixtures/` in JSON format.
- Keep fixture entries small and explicit (`raw`, `expected`).
- Include invalid examples to assert parsing failures.

## Suggested Local QA Commands

```bash
ruff check .
pytest
```

## Suggested CI Matrix

- Python versions: `3.12`, `3.13`
- Commands:
  1. `python -m pip install -e . pytest ruff`
  2. `ruff check .`
  3. `pytest`
