from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from typing import Dict,Any,List,Optional
import os,yaml,datetime
from sqlalchemy import text,select,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.company import Company
from app.models.entity import Entity
from app.models.industry import Industry
from app.models.evidence import Evidence
from app.models.event import Event
from app.models.trust import Trust
from app.models.capability import Capability
from app.models.relationship import Relationship

router=APIRouter(prefix="/api/v1/admin",tags=["admin"])

PROJECT_ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","..","..")
CONFIG_BASE=os.path.join(PROJECT_ROOT,"config")
CONFIG_CATEGORIES={
    "scoring":"scoring",
    "analytics":"analytics",
    "certification":"certification",
    "pricing":"pricing",
    "marketplace":"marketplace",
    "competitive":"competitive",
}

@router.get("/configs")
async def list_all_configs():
    result={}
    for cat,dirname in CONFIG_CATEGORIES.items():
        cat_path=os.path.join(CONFIG_BASE,dirname)
        if os.path.isdir(cat_path):
            files=[f for f in os.listdir(cat_path) if f.endswith(".yaml")]
            result[cat]=files
    return result

@router.get("/configs/{category}/{name}")
async def get_config(category:str,name:str):
    if category not in CONFIG_CATEGORIES:raise HTTPException(404,"Category not found")
    cat_path=os.path.join(CONFIG_BASE,CONFIG_CATEGORIES[category])
    path=os.path.join(cat_path,f"{name}.yaml")
    if not os.path.exists(path):raise HTTPException(404,"Config not found")
    with open(path,"r",encoding="utf-8") as f:return yaml.safe_load(f)

class ConfigUpdate(BaseModel):
    data:Dict[str,Any]

@router.put("/configs/{category}/{name}")
async def update_config(category:str,name:str,body:ConfigUpdate):
    if category not in CONFIG_CATEGORIES:raise HTTPException(404,"Category not found")
    cat_path=os.path.join(CONFIG_BASE,CONFIG_CATEGORIES[category])
    path=os.path.join(cat_path,f"{name}.yaml")
    if not os.path.exists(path):raise HTTPException(404,"Config not found")
    with open(path,"w",encoding="utf-8") as f:yaml.safe_dump(body.data,f,allow_unicode=True,sort_keys=False)
    return {"status":"updated","category":category,"name":name}

@router.get("/stats")
async def get_stats():
    total=0
    for d in CONFIG_CATEGORIES.values():
        p=os.path.join(CONFIG_BASE,d)
        if os.path.isdir(p):total+=len([f for f in os.listdir(p) if f.endswith(".yaml")])
    return {"total_configs":total,"categories":len(CONFIG_CATEGORIES),"version":"1.0"}

@router.get("/db-stats")
async def get_db_stats(db:AsyncSession=Depends(get_db)):
    tables=["entities","companies","industries","capabilities","evidence","events","relationships","trust"]
    counts={}
    for t in tables:
        r=await db.execute(text(f"SELECT COUNT(*) FROM {t}"))
        counts[t]=r.scalar()
    return {"counts":counts,"total":sum(counts.values()),"timestamp":datetime.datetime.utcnow().isoformat()}

@router.get("/companies")
async def list_all_companies(db:AsyncSession=Depends(get_db),skip:int=0,limit:int=50):
    result=await db.execute(select(Company).offset(skip).limit(limit))
    companies=result.scalars().all()
    return [{"id":str(c.id),"name":c.name,"geo_id":c.geo_id,"industry_id":str(c.industry_id) if c.industry_id else None,"is_verified":c.is_verified,"geo_score":c.geo_score,"subscription_tier":c.subscription_tier,"created_at":c.created_at.isoformat() if c.created_at else None} for c in companies]

@router.get("/industries")
async def list_all_industries(db:AsyncSession=Depends(get_db)):
    result=await db.execute(select(Industry).order_by(Industry.sort_order))
    industries=result.scalars().all()
    return [{"id":str(i.id),"name":i.name,"code":i.code,"level":i.level,"parent_id":str(i.parent_id) if i.parent_id else None,"sort_order":i.sort_order} for i in industries]

class EntityUpdate(BaseModel):
    name:Optional[str]=None
    description:Optional[str]=None
    is_verified:Optional[bool]=None

@router.put("/companies/{company_id}")
async def update_company(company_id:str,body:EntityUpdate,db:AsyncSession=Depends(get_db)):
    result=await db.execute(select(Company).where(Company.id==company_id))
    c=result.scalar_one_or_none()
    if not c:raise HTTPException(404,"Company not found")
    if body.name is not None:c.name=body.name
    if body.description is not None:c.description=body.description
    if body.is_verified is not None:c.is_verified=body.is_verified
    await db.commit()
    return {"status":"updated","id":company_id}

@router.get("/health")
async def health_check():
    return {"status":"ok","backend":"running","timestamp":datetime.datetime.utcnow().isoformat()}
