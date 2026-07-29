from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Any, Dict, Optional
from app.database import get_db
from app.mcp.server import MCPServer
from app.mcp.tools.context_tool import ContextTool
from app.mcp.tools.decision_tool import DecisionTool

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])


class MCPCallRequest(BaseModel):
    tool: str
    params: Dict[str, Any] = {}


@router.get("/tools")
async def list_mcp_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {"name": "get_company_context", "description": "Get full company context", "params": ["company_id"]},
            {"name": "get_industry_context", "description": "Get industry context", "params": ["industry_id"]},
            {"name": "analyze_company", "description": "Analyze company performance", "params": ["company_id"]},
            {"name": "analyze_industry", "description": "Analyze industry", "params": ["industry_id"]},
            {"name": "assess_company", "description": "Get company assessment report", "params": ["company_id"]},
        ]
    }


@router.post("/call")
async def call_mcp_tool(request: MCPCallRequest, db: AsyncSession = Depends(get_db)):
    """Call an MCP tool by name"""
    server = MCPServer()
    ctx_tool = ContextTool(db)
    dec_tool = DecisionTool(db)

    server.register("get_company_context", ctx_tool.get_company_context)
    server.register("get_industry_context", ctx_tool.get_industry_context)
    server.register("analyze_company", dec_tool.analyze_company)
    server.register("analyze_industry", dec_tool.analyze_industry)
    server.register("assess_company", dec_tool.assess_company)

    try:
        result = await server.call(request.tool, request.params)
        return {"tool": request.tool, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
