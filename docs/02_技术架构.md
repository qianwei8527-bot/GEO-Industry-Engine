# GEO-Industry-Engine — Technical Architecture

## System Architecture

`
Frontend (Next.js)
   │ REST API / WebSocket
API Gateway (FastAPI)
   │ Auth · Rate Limit · Router · Cache
   ├── AI Growth Service
   ├── Industry Nav Service
   ├── Market Place Service
   ├── Data Center Service
   └── AI Agent Runtime
         │
   Data Layer
   ├── PostgreSQL (structured data)
   ├── Neo4j (knowledge graph)
   ├── Vector DB (semantic search)
   └── ElasticSearch (full-text search)
`

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (React, TypeScript) |
| Backend | FastAPI (Python 3.12) |
| Relational DB | PostgreSQL |
| Graph DB | Neo4j |
| Vector DB | Chroma / Milvus |
| Search Engine | ElasticSearch |
| Agent Framework | LangGraph / AutoGen / CrewAI |
| Container | Docker + docker-compose |

## Non-functional Requirements

| Metric | Target |
|--------|--------|
| Availability | 99.9% |
| Response Time | P95 < 500ms |
| Concurrency | MVP 1000+ users |
| Security | End-to-end encryption |
| Observability | Log + Trace + Metric |

## Design Principles

- **Modularity**: Each core system as independent microservice
- **Data as Asset**: Unified data pipeline to data lake
- **Agent-ready**: All services expose Agent-friendly APIs (Function Calling)
- **Extensible**: Horizontal scaling, plugin architecture
- **Commercial-ready**: Multi-tenant, billing, SaaS subscription

Refer to: docs/\u6280\u672f\u67b6\u6784.md (Chinese detail)
