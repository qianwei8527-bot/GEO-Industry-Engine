# 参考: Dialogflow Intent Routing + Rasa NLU
from typing import Tuple
from app.agents.core.base_agent import AgentContext

INTENT_PATTERNS = {
    'company': ['企业','公司','品牌','集团','科技'],
    'industry': ['行业','产业','市场','赛道','趋势'],
    'geo_growth': ['优化','增长','提升','可见度','排名'],
    'analyze': ['分析','评估','报告','检测','扫描','诊断'],
}

class IntentRouter:
    def route(self, query: str) -> Tuple[str, float]:
        scores = {}
        for intent, keywords in INTENT_PATTERNS.items():
            score = sum(1 for kw in keywords if kw in query)
            if score > 0: scores[intent] = score / len(keywords)
        if not scores: return ('analyze', 0.3)
        best = max(scores, key=scores.get)
        return (best, scores[best])

    def build_context(self, query: str, params: dict = None) -> AgentContext:
        intent, confidence = self.route(query)
        return AgentContext(intent=intent, input_query=query, params=params or {})

intent_router = IntentRouter()