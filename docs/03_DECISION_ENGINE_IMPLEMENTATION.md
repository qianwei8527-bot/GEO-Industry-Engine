# Decision Engine Implementation

## Architecture

Decision Engine sits above Context Engine, transforming contextual data into actionable business intelligence.

`
Context API (Sprint 2)
    |
    v
Decision Engine
    |
    +-- 9 Decision Models (3 layers)
    |       |-> Layer 1: Visibility, Industry Index, Trust Score
    |       |-> Layer 2: Capability Match, Opportunity, Competitive Position
    |       |-> Layer 3: Roadmap, Content Strategy, Market Connection
    |
    +-- Scoring Calculator (YAML-configured weights)
    |
    +-- Explanation Generator (score + reason + action)
    |
    +-- Recommendation Engine (rule-based)
    |
    v
Decision API / MCP Tools
`

## 9 Decision Models

### Layer 1: Cognitive (Understanding)

| Model | Input | Output | Purpose |
|-------|-------|--------|---------|
| GEO Visibility Score | CompanyContext | visibility_score (0-100) | AI search visibility |
| Industry GEO Index | IndustryContext | index_score (0-100) | Industry AI maturity |
| Entity Trust Score | Evidence list | trust_score (0-100) | AI trustworthiness |

### Layer 2: Judgment (Analysis)

| Model | Input | Output | Purpose |
|-------|-------|--------|---------|
| Capability Match | CapabilityContext | match_score (0-100) | Capability-market fit |
| Opportunity Score | CompanyContext | opportunity_score (0-100) | Growth potential |
| Competitive Position | CompanyContext | position_score (0-100) | Market position |

### Layer 3: Growth (Action)

| Model | Input | Output | Purpose |
|-------|-------|--------|---------|
| GEO Optimization Roadmap | CompanyContext | action_plan | Improvement steps |
| Content Strategy | CompanyContext | content_plan | Content recommendations |
| Market Connection | CompanyContext | connection_opps | Partnership opportunities |

## Scoring System

All weight configurations are in config/scoring/*.yaml:

| Config File | Models Using It | Factors |
|-------------|-----------------|---------|
| geo_visibility.yaml | GEOVisibilityScore | entity_quality, evidence, capability_match, relationship, recency |
| trust_score.yaml | (future) | evidence_quality, quantity, verification, longevity |
| industry_index.yaml | IndustryOpportunityScore | company_density, capability_depth, event_frequency, growth |
| opportunity.yaml | (future) | market_growth, competition_gap, capability_overlap, trend |

## Explanation System

Every score returns: score + level + reasons[] + actions[]

Score levels: excellent (80+), good (60-79), average (40-59), developing (<40)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/decision/company/{id} | Full decision report with 6 model scores + recommendations |
| GET | /api/v1/decision/industry/{id} | Industry analysis with index score |
| POST | /api/v1/decision/analyze | Natural language analysis query |

## MCP Tools

| Tool | Description | Source |
|------|-------------|--------|
| get_company_context | Full context | ContextTool (Sprint 2) |
| get_geo_score | GEO score + explanation | DecisionTool |
| get_recommendation | Actionable recommendations | DecisionTool |

## Key Design Decisions

1. **No hardcoded weights** - All weights loaded from YAML at runtime
2. **No black-box scores** - Every score has reasons[] and actions[] for explainability
3. **No LLM dependency** - All calculations are rule-based, no AI API calls
4. **Context Engine dependency** - Decision Engine never reads database directly
