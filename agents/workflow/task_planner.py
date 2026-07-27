from typing import Any


class TaskPlanner:
    @staticmethod
    def plan(agent_name: str, params: dict) -> list:
        steps = [{"agent": agent_name, "params": params}]
        if agent_name == "industry_agent":
            steps = [
                {"action": "get_industry_context", "target": "industry_id"},
                {"action": "analyze_industry", "target": "industry_id"},
                {"action": "format_report", "target": "result"},
            ]
        elif agent_name == "company_agent":
            steps = [
                {"action": "get_company_context", "target": "company_id"},
                {"action": "analyze_company", "target": "company_id"},
                {"action": "format_report", "target": "result"},
            ]
        elif agent_name == "geo_growth_agent":
            steps = [
                {"action": "get_company_context", "target": "company_id"},
                {"action": "analyze_company", "target": "company_id"},
                {"action": "generate_roadmap", "target": "result"},
            ]
        return steps
