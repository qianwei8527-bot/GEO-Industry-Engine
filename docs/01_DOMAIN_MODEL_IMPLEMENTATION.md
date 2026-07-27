# 01_DOMAIN_MODEL_IMPLEMENTATION.md - Sprint 1 Domain Model

## Design Purpose

The domain model layer is the foundation of the entire GEO-Industry-Engine system.
It implements the "Industry Knowledge Layer" from the 7-layer architecture.

The models established in Sprint 1 will serve as the shared data foundation for:
- Industry Map (layer 2)
- GEO Scoring (layer 3)
- AI Search Optimization (layer 3)
- Context Engine (layer 4)
- Agent System (layer 4)
- Transaction Connection (layer 2)

## Models Overview

| Model | Type | Table | Key Fields |
|-------|------|-------|------------|
| Entity | Base (joined inheritance) | entities | geo_id, entity_type, name, description |
| Company | Entity subclass | companies | website, company_size, geo_score |
| Industry | Independent tree | industries | code, parent_id, level |
| Capability | Independent | capabilities | company_id, name, level |
| Relationship | Independent | relationships | source_id, target_id, relation_type |
| Event | Independent | events | entity_id, event_type, occurred_at |
| Evidence | Independent | evidences | target_id, claim, confidence_level |

## Architecture

### Entity Inheritance (Joined Table)

```
entities (Base)
  |-- companies (FK: id -> entities.id, polymorphic: "company")
  |-- products (future)
  |-- persons (future)
  |-- organizations (future)
```

### Relationships (Graph Edge)

```
(source_id, target_id, relation_type, weight)
  sup: source_id BIGINT FK -> entities.id
  sup: target_id BIGINT FK -> entities.id
```

All relationship types are stored as strings (not enums) for extensibility.

### Evidence-Trust Chain

```
Evidence (claims with confidence_level)
  -> TrustService.compute(entity_id) -> TrustScore
```

Trust is a computed value, not a stored table.

## Extension Strategy

All models include: tenant_id, region, lang_tag, metadata (JSONB).
These are reserved for Phase 2 multi-tenant/region/language support.