# GEO-Industry-Engine — Data Architecture

## Database Strategy

| Database | Purpose |
|----------|---------|
| PostgreSQL | Users, companies, transactions, content |
| Neo4j | Industry knowledge graph (entity relationships) |
| Vector DB | AI semantic search, Prompt matching |
| ElasticSearch | Full-text search, log analysis |

## Entity Relationship Overview

### User Domain
- users, user_profiles, user_credentials

### Enterprise Domain
- companies, company_geo_scores, company_ai_mentions

### Industry Domain
- industries, industry_metrics, value_chain_layers, value_chain_nodes

### Business Domain
- products, subscriptions, business_model_map

### Transaction Domain
- marketplace_requests, marketplace_providers, marketplace_transactions

### Data Asset Domain
- geo_index, ai_answer_db, prompt_patterns, knowledge_graph_edges

### Agent Domain
- agent_definitions, agent_execution_logs, agent_collaboration_records

### Certification Domain (NEW)
- certification_requests, certifications

### Regional Domain (NEW)
- regions, region_geo_data, region_entities

## Key Design Principles

1. All business data flows through unified data pipeline
2. Structured data -> PostgreSQL
3. Relationship data -> Neo4j
4. Vector data -> Vector DB
5. Full-text data -> ElasticSearch

## Data Flow

`
Data Collection -> Validation -> Storage -> Indexing -> API Service
     (crawl/API)   (cleanse)    (DB)     (search)    (REST/GraphQL)
`

Refer to: docs/\u6570\u636e\u5e93ER\u8bbe\u8ba1.md (Chinese detail)
