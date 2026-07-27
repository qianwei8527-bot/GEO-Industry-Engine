from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.context.engine import ContextEngine
from app.models.company import Company


class IndustryBenchmark:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.context = ContextEngine(db)

    async def compare_company(self, company_id: str) -> dict:
        ctx = await self.context.get_company_context(company_id)
        company = ctx.company
        vis_score = ctx.scoring.geo_score or 0
        trust_score = ctx.scoring.trust_score or 0

        if not company.id:
            return {"error": "Company not found"}

        # Find industry peers
        from app.models.industry import Industry
        from app.models.company import Company as CompanyModel
        stmt = select(CompanyModel).where(CompanyModel.industry_id.isnot(None))
        result = await self.db.execute(stmt)
        all_companies = list(result.scalars().all())

        if not all_companies:
            return {"company_score": vis_score, "industry_avg": vis_score, "percentile": "N/A"}

        avg_score = sum(c.geo_score or 0 for c in all_companies) / len(all_companies)
        ranked = sorted(all_companies, key=lambda c: c.geo_score or 0, reverse=True)
        position = next((i for i, c in enumerate(ranked) if str(c.id) == str(company.id)), -1)
        percentile = round((1 - (position + 1) / len(ranked)) * 100) if position >= 0 else 0

        return {
            "company_score": vis_score,
            "industry_avg": round(avg_score, 1),
            "trust_score": trust_score,
            "rank": position + 1 if position >= 0 else None,
            "total_companies": len(ranked),
            "percentile": f"top {percentile}%" if percentile > 0 else "bottom",
            "comparisons": {
                "visibility_vs_avg": round(vis_score - avg_score, 1),
                "strength": "above average" if vis_score > avg_score else "below average",
            },
        }
