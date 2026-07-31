import pathlib

BASE = pathlib.Path('D:/GEO-Industry-Engine/backend/tests')

f1 = BASE / 'test_agent_eval.py'
c1 = f1.read_text('utf-8')

helper = 'def _agent_payload(cid, query):\n    return {"query": query, "params": {"company_id": cid}}\n\n'
c1 = c1.replace('def test_agent_post_returns_200', helper + 'def test_agent_post_returns_200')

for old, new in [
    ('json={"entity_type":"company","entity_id":cid,"query":', 'json=_agent_payload(cid, '),
    ('json={"entity_type":"company","entity_id":fake_id,"query":', 'json=_agent_payload(fake_id, '),
]:
    c1 = c1.replace(old, new)

c1 = c1.replace('\"})', '\"]0'
f1.write_text(c1, 'utf-8')
print('[OK] Patched test_agent_eval.py')
