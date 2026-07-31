-- Sprint 3.1 Phase A: Provider Ecosystem Seed Data
-- Insert providers (sample GEO service companies)
INSERT INTO providers (id, entity_id, provider_type, trust_score, geo_score, verification_status, is_verified, is_active, completed_orders, avg_rating, pricing_model, created_at, updated_at)
SELECT gen_random_uuid(), e.id, 'company', 82.5, 78.0, 'verified', true, true, 15, 4.5, '{"model":"project","range_min":5000,"range_max":50000}'::jsonb, NOW(), NOW()
FROM entities e WHERE e.entity_type = 'company' LIMIT 1;

INSERT INTO providers (id, entity_id, provider_type, trust_score, geo_score, verification_status, is_verified, is_active, completed_orders, avg_rating, pricing_model, created_at, updated_at)
SELECT gen_random_uuid(), e.id, 'company', 65.0, 55.5, 'pending', false, true, 3, 3.8, '{"model":"hourly","rate":300}'::jsonb, NOW(), NOW()
FROM entities e WHERE e.entity_type = 'company' LIMIT 1 OFFSET 1;

INSERT INTO providers (id, entity_id, provider_type, trust_score, geo_score, verification_status, is_verified, is_active, completed_orders, avg_rating, pricing_model, created_at, updated_at)
SELECT gen_random_uuid(), e.id, 'company', 91.0, 85.3, 'verified', true, true, 42, 4.9, '{"model":"fixed","range_min":10000,"range_max":100000}'::jsonb, NOW(), NOW()
FROM entities e WHERE e.entity_type = 'company' LIMIT 1 OFFSET 2;

-- Link capabilities
INSERT INTO provider_capabilities (id, provider_id, capability_id, level, verified, experience_years, created_at)
SELECT gen_random_uuid(), p.id, c.id, 4, true, 3.5, NOW()
FROM providers p, capabilities c WHERE c.name LIKE '%GEO%' OR c.name LIKE '%AI%' OR c.name LIKE '%content%' LIMIT 5;

-- Create demands
INSERT INTO market_demands (id, publisher_id, demand_type, title, description, category, industry_id, urgency_level, budget_min, budget_max, timeline_days, requirements, status, created_at)
SELECT gen_random_uuid(), e.id, 'demand', '提升AI搜索可见度', '需要专业的GEO优化服务，提升在AI搜索引擎中的曝光率和排名', 'service',
(SELECT id FROM industries LIMIT 1), 'high', 5000, 20000, 60, '{"keywords":["GEO优化","AI搜索"]}'::jsonb, 'open', NOW()
FROM entities e WHERE e.entity_type = 'company' LIMIT 1;

INSERT INTO market_demands (id, publisher_id, demand_type, title, description, category, industry_id, urgency_level, budget_min, budget_max, timeline_days, requirements, status, created_at)
SELECT gen_random_uuid(), e.id, 'demand', '企业AI数据训练服务', '需要数据标注和AI模型微调服务', 'data',
(SELECT id FROM industries LIMIT 1 OFFSET 1), 'normal', 20000, 80000, 90, '{"data_type":["文本"]}'::jsonb, 'open', NOW()
FROM entities e WHERE e.entity_type = 'company' LIMIT 1 OFFSET 1;
