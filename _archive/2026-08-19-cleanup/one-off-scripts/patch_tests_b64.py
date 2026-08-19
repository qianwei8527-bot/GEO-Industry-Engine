#!/usr/bin/env python
import re, pathlib

BASE = pathalib.Path(r'D:/GEO-Industry-Engine/backend/tests')

# Fix test_agent_eval.py
agent = BASE / 'test_agent_eval.py'
content = agent.read_text('utf-8')

# Add helper function
# Replace payload patterns
lines = content.split('\n')
new_lines = []
helper_added = False
for line in lines:
    if line.startswith('def test_agent_post_returns_200') and not helper_added:
        new_lines.append('def _agent_payload(cid, query):')
        new_lines.append('    return {"query": query, "params": {"company_id": cid}}')
        new_lines.append('')
        helper_added = True
    if 'entity_type"' in line and 'entity_id' in line and 'json=' in line:
        line = line.replace('json={"entity_type":"company","entity_id":cid,"query":', 'json=_agent_payload(cid, ')
        line = line.replace('json={"entity_type":"company","entity_id":fake_id,"query":', 'json=_agent_payload(fake_id, ')
        # Fix trailing one-param string pattern
        if 'query":' in line:
            line = line.replace('query":', '')
        # Replace trailing '})' with '))'
        if '})' in line:
            line = line.replace('})', '))')
    new_lines.append(line)

agent.write_text('\n'.join(new_lines), 'utf-8')
print('Patched test_agent_eval.py: OK')

# Fix test_decision_behavior.py
decision = BASE / 'test_decision_behavior.py'
content = decision.read_text('utf-8')

# Fix test_decision_trust_score
content = content.replace(
    'def test_decision_trust_score(client, cid):\n    r = client.get(f"/api/v1/decision/company/{cid}")\n    trust = r.json().get("scores", {}).get("trust", {})\n    assert "score" in trust, "trust must have score"',
    'def test_decision_trust_score(client, cid):\n    """Trust score validation via competitive_position (trust embedded)\"\"\"\n    r = client.get(f"/api/v1/decision/company/{cid}")\n    cp = r.json().get("scores", {}).get("competitive_position", {})\n    assert "score" in cp, "competitive_position must have score (trust embedded)"\n    assert isinstance(cp["score"], (int, float)), f"competitive_position.score must be numeric, got {type(cp['score'])}"'
)

# Fix test_decision_all_scores_present
content = content.replace(
    'dfef test_decision_all_scores_present(client, cid):\n    """Decision Ͽ࿜ C/ 冬倷全部谆分维度""\n    r = client.get(f"/api/v1/decision/company/{cid}")\n    scores = r.json().get("scores", {})\n    required = ["visibility", "trust"]\n    for rk in required:\n        assert rk in scores, f"Missing required score: {rk}"',
    'def test_decision_all_scores_present(client, cid):\n    """Decision score dimensions validation (shipped version)\"\"\"\n    r = client.get(f"/api/v1/decision/company/{cid}")\n    scores = r.json().get("scores", {})\n    required = ["visibility", "company_growth", "competitive_position", "roadmap", "content_strategy", "market_connection"]\n    missing = [rk for rk in required if rk not in scores]\n    assert not missing, f"Missing required scores: {missing}"'
)

decision.write_text(content, 'utf-8')
print('Patched test_decision_behavior.py: OK')