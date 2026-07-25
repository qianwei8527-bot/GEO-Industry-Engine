# GEO-Industry-Engine — Agent OS Design

## Overview

The GEO Agent OS is a multi-agent intelligent operating system that simulates an AI company organizational structure. Each agent has specific responsibilities, inputs, outputs, permissions, and tool access.

## Agent Organization

`
                CEO Agent
                    |
         +----------+----------+
         |          |          |
      CTO Agent  Product    Industry
         |        Agent      Agent
         |          |          |
   +-----+-----+    |          |
   |     |     |    |          |
Scanner Content Data  |          |
 Agent   Agent  Agent |          |
                     |          |
                Market Agent --- Sales Agent
                     |
                   QA Agent
`

## Agent Definitions

| Agent | Responsibility | Tools |
|-------|--------------|-------|
| CEO | Global coordination, task allocation | All agents, scheduling |
| CTO | Technical architecture, system design | Code analysis, architecture review |
| Product | Product planning, requirements | Data analysis, competitive research |
| Industry | Industry research, ecosystem maps | Neo4j, data crawling, reports |
| Scanner | AI search scanning, GEO monitoring | AI search APIs, scoring engine |
| Content | Content creation, optimization | LLM, knowledge base, media tools |
| Data | Data collection, ETL, knowledge graph | ETL pipelines, databases |
| Market | Demand matching, transaction matching | AI matching, credit scoring |
| Sales | Lead identification, renewals | CRM, email, analytics |
| QA | Quality testing, compliance | Testing frameworks, review tools |

## Development Priority

Agent OS is planned for Phase 5 (P5) of the MVP roadmap. All earlier modules must be designed with Agent-callable interfaces.

## Design Guidelines

1. Each agent uses Function Calling specification
2. Agents communicate via standardized message protocol
3. All agent actions are logged for audit and improvement
4. Agent capabilities are configurable and extensible

Refer to: docs/Agent_OS\u8bbe\u8ba1.md (Chinese detail)
