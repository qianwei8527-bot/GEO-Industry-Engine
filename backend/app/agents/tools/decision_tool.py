from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class DecisionTool:
    def __init__(self):
        self._db = None

    def set_db(self, db: AsyncSession):
        self._db = db

    async def get_geo_score(self, company_id: str) -> dict:
        from app.decision.engine import DecisionEngine
        try:
            engine = DecisionEngine(self._db)
            return await engine.analyze_company(company_id)
        except Exception as e:
            return {'error': str(e)}

    async def get_opportunity(self, company_id: str) -> dict:
        from app.decision.engine import DecisionEngine
        try:
            engine = DecisionEngine(self._db)
            result = await engine.analyze_company(company_id)
            return {'opportunities': result.get('recommendations', []), 'scores': result.get('scores', {})}
        except Exception as e:
            return {'error': str(e)}

    async def get_risk_assessment(self, company_id: str) -> dict:
        from app.decision.engine import DecisionEngine
        try:
            engine = DecisionEngine(self._db)
            result = await engine.analyze_company(company_id)
            scores = result.get('scores', {})
            return {
                'competitive_position': scores.get('competitive_position', {}),
                'company_growth': scores.get('company_growth', {}),
            }
        except Exception as e:
            return {'error': str(e)}

    async def get_roadmap(self, company_id: str) -> dict:
        from app.decision.engine import DecisionEngine
        try:
            engine = DecisionEngine(self._db)
            result = await engine.analyze_company(company_id)
            scores = result.get('scores', {})
            return {
                'roadmap': scores.get('roadmap', {}),
                'content_strategy': scores.get('content_strategy', {}),
                'market_connection': scores.get('market_connection', {}),
            }
        except Exception as e:
            return {'error': str(e)}

decision_tool = DecisionTool()
