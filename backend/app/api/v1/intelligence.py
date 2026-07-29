from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate,CompetitorResponse
router=APIRouter(prefix='/api/v1/intelligence',tags=['competitive'])
@router.get('/competitors')
async def list_competitors(db:AsyncSession=Depends(get_db)):
    r=await db.execute(select(Competitor))
    return [CompetitorResponse.model_validate(c) for c in r.scalars().all()]
@router.post('/competitors',status_code=201)
async def add_competitor(data:CompetitorCreate,db:AsyncSession=Depends(get_db)):
    c=Competitor(**data.model_dump());db.add(c);await db.commit();await db.refresh(c)
    return CompetitorResponse.model_validate(c)
@router.get('/analysis')
async def get_analysis():
    import yaml,os;path=os.path.join(os.getcwd(),'config','competitive','competitors.yaml')
    with open(path,'r',encoding='utf-8') as f:return yaml.safe_load(f)