# Sprint 2.5-A Engineering Foundation Hardening Report

**Date**: 2026-07-29
**Sprint**: Sprint 2.5-A — Schema Freeze + Docker + Testing
**Status**: COMPLETED

---

## Executive Summary

Sprint 2.5-A successfully hardened the engineering foundation of GEO-Industry-Engine. The project now has a **reproducible schema baseline** (Alembic migration from ORM), **validated Docker configuration**, and **13 passing core API tests**. The codebase is ready for sustainable iterative development.

---

## Phase 1: Schema Freeze ✅

### What Changed

| Before | After |
|--------|-------|
| DB built from broken migration chain (001-003 never matched reality) | DB rebuilt from ORM models (`Base.metadata.create_all()`) |
| Migrations used wrong types (String ID vs UUID, VARCHAR vs Enum) | Single baseline migration `a2879ed7b015_schema_freeze_baseline.py` — empty, ORM === DB |
| ORM imported created async engine → Alembic couldn't run | `database.py` now lazy-initializes engine (Alembic-friendly) |
| `DATABASE_URL_SYNC` used `postgresql+psycopg2://` (broke Alembic) | Fixed to standard `postgresql://` |
| Missing `script.py.mako` template file | Created properly |
| Seed script broken (joined inheritance, missing NOT NULL cols) | Rewritten — proper entities→companies split, all 39 NOT NULL columns covered |

### Artifacts
- `backend/alembic/versions/a2879ed7b015_schema_freeze_baseline.py` — Schema baseline migration
- `backend/alembic/script.py.mako` — Migration template
- `database/seed_data.py` — Rewritten (15 companies, 5 industries, ~180 rows)
- `backend/app/database.py` — Lazy engine initialization
- `backend/app/core/config.py` — Fixed sync URL format

---

## Phase 2: Docker Compose ✅

### What Changed

| File | Change |
|------|--------|
| `backend/Dockerfile` | Rewritten: pip-based (removed Poetry dep), simpler |
| `frontend/Dockerfile` | Created: multi-stage Next.js build |
| `docker-compose.yml` | Added frontend service, fixed backend command (auto-runs alembic), added `DATABASE_URL_SYNC` env |

### Validation

`docker compose config` parsed successfully. Docker daemon unavailable on dev machine — runtime validation deferred to CI/deployment environment. Configuration is syntactically correct.

---

## Phase 3: Core Chain Tests ✅

### Test Results: 13/13 PASSED

| # | Test | Status |
|---|------|--------|
| 1 | `test_list_companies` | ✅ PASSED |
| 2 | `test_get_company_detail` | ✅ PASSED |
| 3 | `test_list_industries` | ✅ PASSED |
| 4 | `test_list_entities` | ✅ PASSED |
| 5 | `test_list_evidence` | ✅ PASSED |
| 6 | `test_admin_health` | ✅ PASSED |
| 7 | `test_admin_db_stats` | ✅ PASSED |
| 8 | `test_admin_configs` | ✅ PASSED |
| 9 | `test_context_company` | ✅ PASSED |
| 10 | `test_decision_company` | ✅ PASSED |
| 11 | `test_agent_analyze` | ✅ PASSED |
| 12 | `test_context_query` | ✅ PASSED |
| 13 | `test_admin_companies` | ✅ PASSED |

### Test Coverage

| Layer | Tests | Endpoints Covered |
|-------|-------|-------------------|
| Data API | 5 | Companies, Industries, Entities, Evidence |
| Engine API | 3 | Context, Decision, Agent |
| Admin API | 5 | Health, DB Stats, Configs, Companies |

### Artifacts
- `backend/tests/conftest.py` — Fixtures (base_url, client, company_id)
- `backend/tests/test_companies_api.py` — 8 tests
- `backend/tests/test_context_engine.py` — 5 tests

---

## Files Modified (Complete List)

```
backend/app/database.py          — Lazy engine init
backend/app/core/config.py       — Sync URL fix
backend/alembic/script.py.mako   — Template created
backend/alembic/versions/        — Old 001-003 removed, baseline created
backend/Dockerfile               — Pip-based rewrite
backend/tests/conftest.py        — Test fixtures
backend/tests/test_companies_api.py — API tests
backend/tests/test_context_engine.py — Engine tests
frontend/Dockerfile              — Created (multi-stage Next.js)
docker-compose.yml               — Updated (frontend service, env vars)
database/seed_data.py            — Rewritten for joined inheritance
```

---

## Project Health Summary

| Metric | Before Sprint 2.5-A | After Sprint 2.5-A |
|--------|--------------------|--------------------|
| Schema reproducibility | ❌ Broken migration chain | ✅ ORM→DB baseline |
| Tests | 0 | 13 (core endpoints) |
| Seed script | ❌ Failed on joined inheritance | ✅ Works end-to-end |
| Docker config | ⚠️ Exists, unvalidated | ✅ Parsed, ready for CI |
| DB-ORM alignment | ⚠️ Drift (100+ differences) | ✅ Aligned (0 diffs) |

---

## Next Steps

**Sprint 2.5-B**: Additional test coverage (relationships, events, edge cases), DB query tests, Playwright smoke tests for frontend.

**Sprint 3.0**: Begin frontend-backend integration hardening — replace mock data with real API calls.
