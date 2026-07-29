from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.analytics_event import AnalyticsEvent
from app.schemas.analytics import AnalyticsEventCreate,AnalyticsEventBatch,AnalyticsEventResponse,AnalyticsSummary
from datetime import datetime,timedelta

router = APIRouter(prefix='/api/v1/analytics',tags=['analytics'])

@router.post('/events',status_code=202)
async def track_event(data: AnalyticsEventCreate, db: AsyncSession = Depends(get_db)):
    event = AnalyticsEvent(**data.model_dump(),server_ts=datetime.utcnow())
    db.add(event);await db.commit()
    return {'status':'accepted'}

@router.post('/events/batch',status_code=202)
async def track_events_batch(data: AnalyticsEventBatch, db: AsyncSession = Depends(get_db)):
    now=datetime.utcnow()
    for e in data.events:
        event=AnalyticsEvent(**e.model_dump(),server_ts=now)
        db.add(event)
    await db.commit()
    return {'status':'accepted','count':len(data.events)}

@router.get('/events/summary')
async def get_summary(db: AsyncSession = Depends(get_db)):
    cutoff=datetime.utcnow()-timedelta(hours=24)
    q1=select(AnalyticsEvent.event_type,func.count().label('total')).group_by(AnalyticsEvent.event_type)
    r1=await db.execute(q1);totals={row[0]:row[1] for row in r1.all()}
    q2=select(AnalyticsEvent.event_type,func.count().label('recent')).where(AnalyticsEvent.server_ts>=cutoff).group_by(AnalyticsEvent.event_type)
    r2=await db.execute(q2);recents={row[0]:row[1] for row in r2.all()}
    return [{'event_type':k,'count':v,'last_24h':recents.get(k,0)} for k,v in totals.items()]