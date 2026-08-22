# Changelog

## Unreleased — V2 Foundation

- Added `tuvi_engine.engine` facade with chart builder, input normalization, serialization, geometry, and cache modules.
- Kept `tuvi_lap_so_engine.lap_la_so()` as a backwards-compatible entry point.
- Added foundation tests for normalization, palace relationships, cache isolation, and chart schema.
- Added canonical V2 JSON Schema at `tuvi_engine/schema_v2.json`.
- Added schema conversion and validation helpers in `tuvi_engine/schema.py`.
- Chart output now exposes `meta.schema_version = "2.0"` and stable engine metadata.
- No changes were made to the low-level an-sao implementation under `tuvi_engine/_engine`.

## Deployment

- Canonical frontend remains `new-ui/`; no engine behavior changes.
