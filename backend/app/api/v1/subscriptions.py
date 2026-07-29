from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionResponse,PlanInfo
router=APIRouter(prefix='/api/v1/subscriptions',tags=['subscriptions'])
@router.get('/me')
async def my_subscription(user_id:str,db:AsyncSession=Depends(get_db)):
    r=await db.execute(select(Subscription).where(Subscription.user_id==user_id).order_by(Subscription.created_at.desc()))
    sub=r.scalars().first()
    if not sub:raise HTTPException(404,'No subscription found')
    return SubscriptionResponse.model_validate(sub)
@router.get('/plans')
async def list_plans():
    import yaml,os;path=os.path.join(os.getcwd(),'config','pricing','plans.yaml')
    with open(path,'r',encoding='utf-8') as f:plans=yaml.safe_load(f)
    result=[]
    for tid,p in plans['plans'].items():result.append(PlanInfo(tier_id=tid,name=p['name'],price_monthly=p.get('price_monthly'),description=p['description'],features=p.get('features',[]),permissions=p.get('permissions',[]),limitations=p.get('limitations',[])))
    return result