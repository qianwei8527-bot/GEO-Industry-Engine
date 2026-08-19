path = r'D:\GEO-Industry-Engine\docs\10_GEO_Universe_Relationship_Intelligence.md'

content = u'''---
status: draft
authority: design
version: v0.1
last_review: 2026-07-31
parent: 09_GEO_Universe_Relationship_Lifecycle.md
role: design document \u2014 not implementation

governance_tier: Frozen Design
precedes:
  - C6 Transaction / Marketplace
interfaces_with:
  - C4 Future Connection Engine
  - C5.1 Reputation Engine
  - C5.2 Relationship Lifecycle Engine
  - Context Engine
  - Possibility Graph
---

# GEO Universe Relationship Intelligence Engine \u2014 \u5173\u7cfb\u667a\u80fd\u5f15\u64ce

> C4 \u56de\u7b54\u201c\u53ef\u80fd\u8fde\u63a5\u8c01\u201d\u3002
> C5.1 \u56de\u7b54\u201c\u8c01\u503c\u5f97\u4fe1\u4efb\u201d\u3002
> C5.2 \u56de\u7b54\u201c\u5173\u7cfb\u5982\u4f55\u6210\u957f\u201d\u3002
> C5.3 \u56de\u7b54\u201c\u4e3a\u4ec0\u4e48\u8fd9\u4e2a\u8fde\u63a5\u503c\u5f97\u53d1\u751f\u201d\u3002
>
> \u8fd9\u662f\u4ea4\u6613\u53d1\u751f\u524d\u7684\u667a\u80fd\u5c42\u3002\u628a Connection Candidate \u5347\u7ea7\u4e3a Relationship Opportunity\u3002

---

## \u7b2c\u96f6\u7ae0\uff1a\u6587\u6863\u5b9a\u4f4d

### \u524d\u7f6e\u6587\u6863\u94fe

`
07_GEO_Universe_World_Engine.md          \u2192 \u4e16\u754c\u8fd0\u884c\u539f\u7406
08_GEO_Universe_Reputation_Engine.md     \u2192 \u4fe1\u4efb\u7269\u7406\u5b66
09_GEO_Universe_Relationship_Lifecycle.md \u2192 \u5173\u7cfb\u751f\u547d\u5468\u671f
10_GEO_Universe_Relationship_Intelligence.md \u2192 \u672c\u6587\u4ef6\uff1a\u5173\u7cfb\u667a\u80fd\u63a8\u6f14
`

### \u672c\u6587\u6863\u7684\u804c\u8d23

\u5b9a\u4e49 Relationship Opportunity \u7684\u8ba1\u7b97\u6a21\u578b\uff0c\u4ee5\u53ca C4 \u2192 C5.2 \u2192 C5.3 \u7684\u878d\u5408\u63a5\u53e3\u3002\u5c06\u5206\u6563\u7684\u80fd\u529b\u6a21\u5757\u95ed\u5408\u4e3a\u7edf\u4e00\u7684\u5173\u7cfb\u63a8\u8350\u94fe\u8def\u3002

---

## \u7b2c\u4e00\u7ae0\uff1a\u5173\u7cfb\u667a\u80fd\u7b2c\u4e00\u6027\u539f\u7406

### 1.1 \u4e00\u53e5\u8bdd\u5b9a\u4e49

> **Relationship Intelligence Engine \u4e0d\u662f\u63a8\u8350\u7cfb\u7edf\u3002\u5b83\u662f\u5c06 Node Context\u3001Possibility Graph\u3001Reputation \u548c Relationship History \u878d\u5408\u4e3a\u4e00\u4e2a\u95ee\u9898\u7684\u7b54\u6848\uff1a\u4e3a\u4ec0\u4e48\u8fd9\u4e24\u4e2a\u8282\u70b9\u5e94\u8be5\u5efa\u7acb\u5173\u7cfb\uff1f**

### 1.2 \u4f20\u7edf\u63a8\u8350 vs Universe \u63a8\u6f14

**\u9519\uff08\u4f20\u7edf B2B \u63a8\u8350\uff09\uff1a**

`
A\u9700\u8981 B \u2192 \u6807\u7b7e\u5339\u914d \u2192 \u63a8\u8350
`

\u4e0d\u53ef\u89e3\u91ca\u3002\u4e0d\u53ef\u9a8c\u8bc1\u3002\u4e0d\u53ef\u8ffd\u6eaf\u3002

**\u5bf9\uff08Universe\u2019\uff09\uff1a**

`
Node A Context (\u6211\u662f\u8c01\uff0c\u6211\u5728\u54ea\uff0c\u6211\u7f3a\u4ec0\u4e48)
      +
Possibility Graph (A \u672a\u6765\u53ef\u80fd\u53bb\u54ea)
      +
Node B Context + Reputation (B \u662f\u8c01\uff0c\u503c\u5f97\u4fe1\u4efb\u5417)
      +
Relationship History (A-B \u4e4b\u524d\u5408\u4f5c\u8fc7\u5417)
      +
Capability Gap Analysis (B \u80fd\u586b\u8865 A \u7684\u7f3a\u53e3\u5417)
      =
Relationship Opportunity Report
`

### 1.3 \u4e09\u4e2a\u6838\u5fc3\u95ee\u9898

| \u95ee\u9898 | \u6765\u6e90 | \u8f93\u51fa |
|------|------|------|
| \u4e3a\u4ec0\u4e48\u63a8\u8350\u4ed6\u4eec\u5408\u4f5c\uff1f | Context + Possibility | \u80fd\u529b\u4e92\u8865\u5206\u6790 |
| \u5386\u53f2\u5408\u4f5c\u600e\u4e48\u6837\uff1f | C5.2 Relationship History | \u5173\u7cfb\u4fe1\u8a89 + \u6210\u529f\u7387 |
| \u5931\u8d25\u98ce\u9669\u662f\u4ec0\u4e48\uff1f | Reputation + Gap | \u98ce\u9669\u4fe1\u53f7\u5217\u8868 |

---

## \u7b2c\u4e8c\u7ae0\uff1aRelationshipOpportunity \u6570\u636e\u6a21\u578b

`yaml
RelationshipOpportunity:
  opportunity_id:       string
  node_a_id:            string
  node_b_id:            string

  # \u4e3a\u4ec0\u4e48\u63a8\u8350
  reasons:
    capability_gap:     List[Dict]    # A\u7f3a\u4ec0\u4e48\uff0cB\u6709\u4ec0\u4e48
    future_alignment:   float          # B\u80fd\u5e2eA\u8fbe\u5230\u672a\u6765\u72b6\u6001\u5417
    reputation_match:   float          # \u53cc\u65b9\u4fe1\u8a89\u517c\u5bb9\u6027

  # \u5386\u53f2\u5408\u4f5c
  existing_relationship: Optional[Dict]  # \u662f\u5426\u5df2\u6709\u5173\u7cfb
  relationship_stage:   string          # \u5f53\u524d\u9636\u6bb5
  relationship_trust:   float           # \u5173\u7cfb\u4fe1\u8a89

  # \u9884\u671f\u4ef7\u503c
  expected_value:
    capability_gain:    float           # \u80fd\u529b\u63d0\u5347\u9884\u4f30 (0-1)
    growth_acceleration: float          # \u6210\u957f\u52a0\u901f (0-1)
    strategic_value:    float           # \u6218\u7565\u4ef7\u503c (0-1)
    overall:            float           # \u7efc\u5408\u9884\u671f\u4ef7\u503c

  # \u98ce\u9669\u8bc4\u4f30
  risks:
    reputation_risk:    List[str]       # \u4fe1\u8a89\u98ce\u9669
    capability_risk:    List[str]       # \u80fd\u529b\u98ce\u9669
    relationship_risk:  List[str]       # \u5173\u7cfb\u98ce\u9669
    market_risk:        List[str]       # \u5e02\u573a\u98ce\u9669

  # \u5efa\u8bae\u884c\u52a8
  recommended_action:   string          # \u4e00\u53e5\u8bdd\u5efa\u8bae
  next_steps:           List[Dict]      # \u5177\u4f53\u6b65\u9aa4

  confidence:           float           # \u7efc\u5408\u7f6e\u4fe1\u5ea6 (0-1)
  generated_at:         datetime
`

---

## \u7b2c\u4e09\u7ae0\uff1aC4 \u2192 C5.2 \u2192 C5.3 \u878d\u5408\u63a5\u53e3

### 3.1 \u5347\u7ea7\u540e\u7684\u8fde\u63a5\u94fe\u8def

`
C4 Connection Engine
  discover_connections(node_id)
        |
        v
  ConnectionCandidate (\u521d\u6b65\u7b5b\u9009)
        |
        v
C5.3 Relationship Intelligence
  evaluate_opportunity(candidate)
        |
        |  \u67e5\u8be2 C5.1 Reputation
        |  \u67e5\u8be2 C5.2 Relationship History
        |  \u67e5\u8be2 Possibility Graph
        |  \u8ba1\u7b97 Capability Gap
        |
        v
  RelationshipOpportunity (\u6df1\u5ea6\u8bc4\u4f30)
        |
        v
C5.2 Relationship Lifecycle
  create_relationship() \u2192 UNKNOWN
        |
        v
  State Machine \u2192 CONNECTED \u2192 ACTIVE \u2192 ...
`

### 3.2 RelationshipOpportunityScore

`
Opportunity Score =

  Capability Complementarity    \u00d7 0.30   (C4)
+ Future Path Alignment         \u00d7 0.20   (Possibility Graph)
+ Reputation Compatibility      \u00d7 0.20   (C5.1)
+ Relationship History Quality  \u00d7 0.15   (C5.2)
+ Strategic Value Potential     \u00d7 0.15   (C5.3 \u65b0\u589e)
`

### 3.3 \u98ce\u9669\u68c0\u6d4b\u89c4\u5219

`
IF candidate.reputation.status == "UNKNOWN":
    \u2192 risk: "insufficient_reputation_data"

IF existing_relationship AND existing_relationship.stage == "ENDED":
    \u2192 risk: "previous_relationship_ended", show reason

IF candidate.delivery_trust < 40:
    \u2192 risk: "low_delivery_trust"

IF relationship_history.failure_rate > 0.3:
    \u2192 risk: "high_historical_failure_rate"
`

---

## \u7b2c\u56db\u7ae0\uff1a\u6700\u5c0f\u7248\u672c\u8303\u56f4 (C5.3 Scope)

### 4.1 \u540e\u7aef

`
backend/app/universe/relationship_intelligence.py
`

- RelationshipOpportunity \u2014 \u6570\u636e\u7c7b
- OpportunityEvaluator \u2014 \u8bc4\u4f30\u5668
- RelationshipIntelligenceEngine \u2014 \u4e3b\u5f15\u64ce

### 4.2 API

`
POST /api/v1/universe/intelligence/evaluate
  \u8f93\u5165: {node_a_id, node_b_id}
  \u8f93\u51fa: RelationshipOpportunity

GET  /api/v1/universe/intelligence/opportunities/{node_id}
  \u8f93\u51fa: \u8282\u70b9\u7684\u6240\u6709\u5173\u7cfb\u673a\u4f1a
`

### 4.3 \u4e0d\u8fdb C5.3

- UI \u53ef\u89c6\u5316 \u2014 \u7559 C5.4 Universe Home
- \u4ea4\u6613\u95ed\u73af \u2014 \u7559 C6

---

## \u7b2c\u4e94\u7ae0\uff1a\u9a8c\u6536\u6807\u51c6

### \u8f93\u5165

`
\u8282\u70b9 A: \u661f\u8fb0AI\u8425\u9500\u79d1\u6280
  Context:  Active Provider, Capability\u7f3a Data
  Future:   180\u5929\u8fdb\u5165 GEO Authority
  Reputation: Capability A, Delivery B+

\u5019\u9009 B: \u67d0GEO\u6570\u636e\u670d\u52a1\u5546
  Context:  Established Provider
  Capability: Data Intelligence Lv4
  Reputation: Overall A, Delivery A
  History:   \u65e0

\u5019\u9009 C: \u67d0\u4f4e\u4fe1\u8a89\u670d\u52a1\u5546
  Reputation: UNKNOWN
`

### \u8f93\u51fa

`
RelationshipOpportunity (A-B):
  reasons:
    capability_gap: \u201cA\u7f3a Data\u5206\u6790\u80fd\u529b\uff0cB\u62e5\u6709 Data Lv4\u201d
    future_alignment: 0.88
    reputation_match: 0.85

  expected_value: 0.82
  risks: [\u201c\u7f3a\u5c11\u5386\u53f2\u5408\u4f5c\u201d]
  recommended_action: \u201c\u5efa\u8bae\u5efa\u7acb\u521d\u6b65\u5408\u4f5c\u5173\u7cfb\uff0c\u4ece\u5c0f\u9879\u76ee\u5f00\u59cb\u201d
  confidence: 0.78

RelationshipOpportunity (A-C):
  reputation_match: 0.0
  risks: [\u201c\u4fe1\u8a89\u6570\u636e\u4e0d\u8db3\u201d, \u201c\u65e0\u6cd5\u8bc4\u4f30\u80fd\u529b\u201d]
  recommended_action: \u201c\u5efa\u8bae\u7b49\u5f85\u66f4\u591a\u4fe1\u8a89\u6570\u636e\u201d
  confidence: 0.15
`

---

## \u7b2c\u516d\u7ae0\uff1aUniverse First Law Check

| # | \u68c0\u67e5\u9879 | \u6807\u51c6 |
|---|--------|------|
| 1 | **\u670d\u52a1\u54ea\u4e2a\u8282\u70b9\uff1f** | \u670d\u52a1\u4e8e\u53d1\u8d77\u8fde\u63a5\u7684\u8282\u70b9\uff0c\u5e2e\u52a9\u5b83\u5224\u65ad\u201c\u4e3a\u4ec0\u4e48\u8fd9\u4e2a\u8fde\u63a5\u503c\u5f97\u53d1\u751f\u201d |
| 2 | **\u5e2e\u8282\u70b9\u89e3\u51b3\u4ec0\u4e48\u95ee\u9898\uff1f** | \u4ece\u201c\u53ef\u80fd\u8fde\u63a5\u8c01\u201d\u5230\u201c\u5e94\u8be5\u8fde\u63a5\u8c01\u201d\u7684\u8d28\u53d8 |
| 3 | **\u589e\u52a0\u4e86\u4ec0\u4e48\u957f\u671f\u8bb0\u5fc6\uff1f** | \u6bcf\u6b21\u673a\u4f1a\u8bc4\u4f30\u7ed3\u679c\u53ef\u8ffd\u6eaf\uff0c\u5f62\u6210\u63a8\u8350\u5386\u53f2 |
| 4 | **\u662f\u5426\u589e\u5f3a\u672a\u6765\u8fde\u63a5\u80fd\u529b\uff1f** | \u673a\u4f1a\u8bc4\u4f30\u76f4\u63a5\u8f93\u5165 C5.2 \u5173\u7cfb\u521b\u5efa |

---

> **\u51bb\u7ed3\u58f0\u660e\uff1a** \u672c\u6587\u6863\u662f C5.3 \u7684\u8bbe\u8ba1\u5951\u7ea6\u3002\u5b9e\u73b0\u65f6\u5fc5\u987b\u8d2f\u7a7f C4 \u2192 C5.2 \u2192 C5.3 \u7684\u878d\u5408\u94fe\u8def\uff0c\u4e0d\u5f97\u72ec\u7acb\u5b9e\u73b0\u4e3a\u53e6\u4e00\u4e2a\u63a8\u8350\u7cfb\u7edf\u3002
'''

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'OK: 10_GEO_Universe_Relationship_Intelligence.md created')
print(f'Size: {len(content)} chars')
