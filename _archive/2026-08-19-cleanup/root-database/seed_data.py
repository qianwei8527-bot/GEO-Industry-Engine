"""GEO-Industry-Engine Seed Data — joined-inheritance aware, all NOT NULL cols covered"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.config import settings
import uuid

COMPANIES=[
    {"name":"星辰AI营销科技","scope":"AI内容生成与GEO优化服务","size":"50-200","founded":2020,"hq":"深圳","emp":85,"rev":"5000万-1亿"},
    {"name":"鼎新云计算","scope":"AI算力基础设施与模型服务","size":"500+","founded":2015,"hq":"北京","emp":1200,"rev":"10亿+"},
    {"name":"未来教育科技","scope":"AI个性化学习平台","size":"10-50","founded":2022,"hq":"杭州","emp":28,"rev":"500万-1000万"},
    {"name":"博跃数字营销","scope":"数据驱动的GEO品牌策略","size":"50-200","founded":2018,"hq":"上海","emp":65,"rev":"3000万-5000万"},
    {"name":"锐思GEO","scope":"GEO技术研究与AI搜索优化","size":"10-50","founded":2021,"hq":"广州","emp":32,"rev":"1000万-3000万"},
    {"name":"智擎企业AI","scope":"企业级AI应用与自动化","size":"200-500","founded":2017,"hq":"成都","emp":350,"rev":"2亿-5亿"},
    {"name":"灵析数据科技","scope":"行业数据分析与AI预测","size":"50-200","founded":2019,"hq":"武汉","emp":78,"rev":"5000万-1亿"},
    {"name":"创维智能","scope":"智能制造与工业AI解决方案","size":"200-500","founded":2016,"hq":"苏州","emp":420,"rev":"5亿-10亿"},
    {"name":"星图导航","scope":"产业地图与市场洞察平台","size":"10-50","founded":2023,"hq":"南京","emp":22,"rev":"500万-1000万"},
    {"name":"汇智认证","scope":"AI搜索可信认证与审计","size":"10-50","founded":2021,"hq":"厦门","emp":18,"rev":"500万以下"},
    {"name":"天成交易","scope":"GEO产业供需匹配平台","size":"50-200","founded":2020,"hq":"天津","emp":55,"rev":"3000万-5000万"},
    {"name":"深蓝科技","scope":"海洋探测与水下AI机器人","size":"500+","founded":2014,"hq":"青岛","emp":800,"rev":"10亿+"},
    {"name":"量子互联","scope":"量子计算与AI算力加速","size":"50-200","founded":2022,"hq":"合肥","emp":45,"rev":"1000万-3000万"},
    {"name":"玄武安全","scope":"AI系统安全与数据隐私保护","size":"200-500","founded":2018,"hq":"西安","emp":280,"rev":"2亿-5亿"},
    {"name":"昆仑农业","scope":"智慧农业与精准种植AI","size":"50-200","founded":2019,"hq":"昆明","emp":92,"rev":"5000万-1亿"},
]
INDUSTRIES=[("ai_marketing","AI营销与GEO优化"),("enterprise_ai","企业AI应用与SaaS"),("cloud_infra","云计算与基础设施"),("smart_mfg","智能制造与工业AI"),("fintech","金融科技与数字资产")]
CAPS=["AI内容生成","GEO战略咨询","技术文档优化","AI搜索排名分析","行业知识图谱"]

async def seed():
    engine=create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as db:
        iids={}
        for code,name in INDUSTRIES:
            iid=uuid.uuid4();iids[code]=iid
            await db.execute(text("INSERT INTO industries (id,code,name,level,sort_order,created_at,updated_at) VALUES (:id,:code,:name,1,1,NOW(),NOW()) ON CONFLICT DO NOTHING"),{"id":iid,"code":code,"name":name})

        eids=[]
        for i,c in enumerate(COMPANIES):
            eid=uuid.uuid4();geo_id=f"GEO-COM-{uuid.uuid4().hex[:8].upper()}";eids.append(eid)
            await db.execute(text("INSERT INTO entities (id,geo_id,entity_type,name,description,is_verified,region,lang_tag,created_at,updated_at) VALUES (:id,:gid,'company',:nm,:dsc,false,'CN','zh',NOW(),NOW())"),{"id":eid,"gid":geo_id,"nm":c["name"],"dsc":c["scope"]})
            web=f"https://{c['name']}.example.com";email=f"contact@{c['name']}.example.com"
            ik=list(iids.keys())[i%len(iids)]
            await db.execute(text("INSERT INTO companies (id,industry_id,company_size,website,founded_year,headquarters,employee_count,annual_revenue,business_scope,contact_email,subscription_tier) VALUES (:id,:iid,:sz,:wb,:fd,:hq,:em,:rv,:sc,:eml,'free')"),{"id":eid,"iid":iids[ik],"sz":c["size"],"wb":web,"fd":c["founded"],"hq":c["hq"],"em":c["emp"],"rv":c["rev"],"sc":c["scope"],"eml":email})

        for eid in eids:
            for cap in CAPS[:3]:
                await db.execute(text("INSERT INTO capabilities (id,company_id,name,level,created_at,updated_at) VALUES (:id,:cid,:nm,3,NOW(),NOW())"),{"id":uuid.uuid4(),"cid":eid,"nm":cap})

        for eid in eids[:5]:
            for claim in ["官网SEO结构完善","被AI搜索引用","行业白皮书发布"]:
                await db.execute(text("INSERT INTO evidence (id,entity_id,entity_type,claim,source_url,confidence_level,verified,created_at,updated_at) VALUES (:id,:eid,'company',:cl,:url,0.7,false,NOW(),NOW())"),{"id":uuid.uuid4(),"eid":eid,"cl":claim,"url":f"https://evidence.example.com/{claim[:10]}"})

        for eid in eids[:8]:
            for et,en,im in [("product_launch","发布AI内容生成引擎v3.0","high"),("certification_achieved","获得GEO服务能力L3认证","high"),("partnership_formed","与头部AI搜索平台达成合作","medium")]:
                await db.execute(text("INSERT INTO events (id,entity_id,entity_type,event_type,title,event_date,impact,created_at,updated_at) VALUES (:id,:eid,'company',:et,:en,CURRENT_DATE,:im,NOW(),NOW())"),{"id":uuid.uuid4(),"eid":eid,"et":et,"en":en,"im":im})

        for eid in eids:
            await db.execute(text("INSERT INTO trust (id,entity_id,entity_type,trust_score,evidence_count,certification_level,created_at,updated_at) VALUES (:id,:eid,'company',50.0,3,'L0',NOW(),NOW())"),{"id":uuid.uuid4(),"eid":eid})

        for i in range(min(5,len(eids))):
            for j in range(i+1,min(i+3,len(eids))):
                await db.execute(text("INSERT INTO relationships (id,source_type,source_id,target_type,target_id,relation_type,weight,created_at,updated_at) VALUES (:id,'company',:src,'company',:tgt,:rel,0.5,NOW(),NOW())"),{"id":uuid.uuid4(),"src":eids[i],"tgt":eids[j],"rel":["partners_with","competitor_of","supplier_to"][(i+j)%3]})

        await db.commit()
        print(f"Seed done: {len(COMPANIES)} companies, {len(INDUSTRIES)} industries, {len(CAPS)*len(eids)//5} capabilities, {15} evidence, {24} events, {len(eids)} trust, ~10 relationships")

if __name__=="__main__":
    asyncio.run(seed())
