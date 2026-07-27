# Context Engine Implementation

## Architecture

Context Engine sits between the Knowledge Layer (Entity/Relationship/Event/Evidence) and the Application/Agent Layer. It is the orchestration layer that assembles raw data into structured, queryable, rankable context.

`
Knowledge Layer (Sprint 1)
    |
    v
  Retrieval Layer
  EntityRetriever / RelationshipRetriever / EvidenceRetriever
    |
    v
  Builders
  CompanyContextBuilder / IndustryContextBuilder / CapabilityContextBuilder
    |
    v
  Ranking
  RelevanceScorer / TrustScorer / GEOScorer
    |
    v
  Context Engine (orchestrator)
    |
    v
  Context API / MCP Server
`

## Module Structure

backend/app/context/
  engine.py              # ContextEngine orchestrator
  builders/
    company_context.py   # Company context assembly
    industry_context.py  # Industry context assembly
    capability_context.py # Capability context assembly
  retrieval/
    entity_retriever.py  # Company/Industry/Capability queries
    relationship_retriever.py  # Graph edge queries
    evidence_retriever.py  # Evidence queries by target
  ranking/
    relevance.py         # Keyword relevance scoring
    trust_score.py       # Evidence-based trust scoring
    geo_score.py         # GEO Score calculation
  schemas/
    context_schema.py    # Pydantic models for all context types

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/context/company/{id} | Full company profile + capabilities + relationships + events + evidence + scoring |
| GET | /api/v1/context/industry/{id} | Industry structure + companies + capabilities + trends + events |
| GET | /api/v1/context/capability/{id} | Capability detail + providers + relationships + evidence |
| POST | /api/v1/context/query | Natural language search across entities |

## Context Data Flow

### Company Context
1. EntityRetriever.get_company()
2. EntityRetriever.get_capabilities_by_company()
3. RelationshipRetriever.get_relationships() + resolve entity names
4. Event query (SQLAlchemy direct)
5. EvidenceRetriever.get_evidence()
6. TrustScorer.compute() + GEOScorer.compute()
7. Assembly into CompanyContext response

### Industry Context
1. EntityRetriever.get_industry()
2. EntityRetriever.get_companies_by_industry()
3. Capability query across all companies
4. Event query across all companies
5. Assembly into IndustryContext response

### Capability Context
1. EntityRetriever.get_capability()
2. EntityRetriever.get_company() for provider
3. RelationshipRetriever.get_relationships() for provider
4. EvidenceRetriever.get_evidence()
5. Assembly into CapabilityContext response

### Natural Language Query
1. EntityRetriever.search_companies() - PostgreSQL ILIKE search
2. RelevanceScorer.score_companies() - keyword relevance
3. Top N results returned

## Ranking Framework

| Factor | Source | Weight (configurable) |
|--------|--------|----------------------|
| Relevance | Keyword match score | 0.3 (in YAML) |
| Trust | Evidence confidence levels | 0.3 (in YAML) |
| GEO Score | Company.geo_score | 0.2 (in YAML) |
| Capability | Capability level match | 0.2 (in YAML) |

## Agent Interface Preparation

Context Engine is designed as the single entry point for Agent data access:

`
Agent -> Tool -> Context API -> ContextEngine -> Knowledge Layer
`

No Agent should directly access the database. The Context API provides a complete, ranked, explainable context response.

## Future Extensions

1. Vector DB integration: Replace ILIKE search with embedding similarity
2. Graph DB integration: Replace ORM relationship queries with Neo4j traversal
3. Cache layer: Redis cache for frequently accessed contexts
4. Streaming: Long-running context assembly with progress reporting
5. Event-driven: Real-time context updates when entities change
