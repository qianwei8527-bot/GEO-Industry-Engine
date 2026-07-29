from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import select,desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.market_demand import MarketDemand
from app.models.transaction_review import TransactionReview
from app.schemas.marketplace import MarketDemandCreate,MarketDemandResponse,ReviewCreate
router=APIRouter(prefix='/api/v1/marketplace',tags=['marketplace'])
@router.post('/demands',status_code=201)
async def create_demand(data:MarketDemandCreate,db:AsyncSession=Depends(get_db)):
    d=MarketDemand(**data.model_dump());db.add(d);await db.commit();await db.refresh(d)
    return MarketDemandResponse.model_validate(d)
@router.get('/demands')
async def list_demands(category:str=Query(None),skip:int=0,limit:int=50,db:AsyncSession=Depends(get_db)):
    stmt=select(MarketDemand).order_by(desc(MarketDemand.created_at)).offset(skip).limit(limit)
    if category:stmt=stmt.where(MarketDemand.category==category)
    r=await db.execute(stmt)
    return [MarketDemandResponse.model_validate(d) for d in r.scalars().all()]
@router.post('/reviews',status_code=201)
async def create_review(data:ReviewCreate,db:AsyncSession=Depends(get_db)):
    r=TransactionReview(**data.model_dump());db.add(r);await db.commit();await db.refresh(r)
    return {'id':str(r.id),'status':r.status}