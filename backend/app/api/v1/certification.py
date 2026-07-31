from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.certification import Certification,CertStatus,CertLevel
from app.models.evidence import Evidence
from app.schemas.certification import CertificationApply,CertificationReview,CertificationResponse
from datetime import datetime,timedelta
import uuid

router = APIRouter(prefix='/api/v1/certification',tags=['certification'])

@router.post('/apply',status_code=201)
async def apply_cert(data:CertificationApply,db:AsyncSession=Depends(get_db)):
    cert=Certification(entity_id=data.entity_id,entity_type=data.entity_type.value,level=data.target_level.value,cert_type=data.cert_type,status=CertStatus.PENDING,evidence_ids=data.evidence_ids)
    db.add(cert);await db.commit();await db.refresh(cert)
    return CertificationResponse.model_validate(cert)

@router.get('/levels')
async def list_cert_levels():
    return {"levels": [
        {"level": "L0", "name": "未认证", "unlocks": ["基础搜索"]},
        {"level": "L1", "name": "基础身份认证", "unlocks": ["信息展示", "基础评分"]},
        {"level": "L2", "name": "GEO生态认证", "unlocks": ["产业导航", "关系网络"]},
        {"level": "L3", "name": "专业能力认证", "unlocks": ["高级分析", "Agent服务"]},
        {"level": "L4", "name": "行业权威认证", "unlocks": ["生态治理", "交易优先"]},
    ]}

@router.get('/status/{entity_id}')
async def get_cert_status(entity_id:str,db:AsyncSession=Depends(get_db)):
    r=await db.execute(select(Certification).where(Certification.entity_id==entity_id).order_by(Certification.applied_at.desc()))
    certs=r.scalars().all()
    return [CertificationResponse.model_validate(c) for c in certs]

@router.get('/review/pending')
async def list_pending_reviews(db:AsyncSession=Depends(get_db)):
    r=await db.execute(select(Certification).where(Certification.status.in_([CertStatus.PENDING,CertStatus.AI_REVIEW,CertStatus.HUMAN_REVIEW])).order_by(Certification.applied_at))
    return [CertificationResponse.model_validate(c) for c in r.scalars().all()]

@router.put('/review/{cert_id}')
async def review_cert(cert_id:str,data:CertificationReview,db:AsyncSession=Depends(get_db)):
    r=await db.execute(select(Certification).where(Certification.id==cert_id))
    cert=r.scalar_one_or_none()
    if not cert:raise HTTPException(404,'Certification not found')
    if data.action=='approve':
        cert.status=CertStatus.APPROVED
        cert.issued_at=datetime.utcnow()
        cert.expires_at=datetime.utcnow()+timedelta(days=730)
        evidence=Evidence(
            entity_id=cert.entity_id,
            entity_type=cert.entity_type.value if hasattr(cert.entity_type,'value') else str(cert.entity_type),
            claim="GEO认证通过: "+str(cert.level.value if hasattr(cert.level,'value') else cert.level)+"级",
            source_url="/certification/"+str(cert.id),
            confidence_level=1.0,
            source_type="certification",
            verified=True,
            verified_by=cert.reviewer_id,
            verified_at=datetime.utcnow()
        )
        db.add(evidence)
    elif data.action=='reject':
        cert.status=CertStatus.REJECTED
    elif data.action=='request_more':
        cert.status=CertStatus.PENDING
    cert.reviewer_id=uuid.uuid4();cert.review_comment=data.comment;cert.reviewed_at=datetime.utcnow()
    await db.commit();await db.refresh(cert)
    return CertificationResponse.model_validate(cert)
