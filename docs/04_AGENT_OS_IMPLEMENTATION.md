# Agent OS Implementation

## Architecture

```
User Query
    |
    v
Agent Router (IntentRouter) -----> Agent Registry
    |                                    |
    v                                    v
Task Planner                     +------------------+
    |                            | IndustryAgent    |
    v                            | CompanyAgent     |
Agent OS Framework               | GEOGrowthAgent   |
    |                            | AnalystAgent     |
    +-- Context Engine (Sprint2) +------------------+
    +-- Decision Engine (Sprint3)       |
    +-- Tools (search/analyze)         v
    +-- Memory (future)           MCP Server
                                        |
                                        v
                                External AI Agents
```

## Components

### Core Framework (agents/core/)
- **BaseAgent**: Abstract class with context and decision engine integration
- **AgentRegistry**: Central registry for all agents
- **AgentContext**: Execution context with history tracking

### Router (agents/router/)
- **IntentRouter**: Keyword-based routing to appropriate agent
- Supports Chinese and English keywords

### Planner (agents/planner/)
- **TaskPlanner**: Multi-step task planning for complex queries

### Agents (agents/agents/)
| Agent | Name | Capabilities |
|-------|------|-------------|
| Industry Agent | industry_agent | Industry structure, trends, opportunities |
| Company Agent | company_agent | Company profile, strengths, competitive position |
| GEO Growth Agent | geo_growth_agent | GEO roadmap, content strategy, AI search growth |
| Analyst Agent | analyst_agent | Data gap analysis, missing data detection |

## Tools (agents/tools/)
- **ContextTool**: Wraps ContextEngine for agent use
- **DecisionTool**: Wraps DecisionEngine for agent use
- **SearchTool**: Entity search across the knowledge graph

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/agent/analyze | Analyze query with routed agent |
| GET | /api/v1/agent/list | List available agents |

## Industry Benchmark

Added to Decision Engine: compares company scores against industry averages
- Company GEO Score vs Industry Average
- Percentile ranking
- Strength/weakness identification

## Integration Rules
1. Agents NEVER access database directly
2. Agents ALWAYS go through Context Engine -> Knowledge Layer
3. Agents ALWAYS go through Decision Engine -> Scores
4. All agent outputs are explainable (scores + reasons + actions)
