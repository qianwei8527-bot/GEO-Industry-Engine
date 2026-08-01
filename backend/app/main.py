from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import agent, universe, auth, users, entities, companies, industries, relationships, evidence, context, decision, admin, mcp_router, analytics, certification, subscriptions, marketplace, intelligence, payments, providers, assets, graph, identity, observation, knowledge, onboarding, learning, observation_external, geo, memory_universe
from app.core.config import settings

from app.services.observation_scheduler import get_observation_scheduler

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(entities.router)
app.include_router(companies.router)
app.include_router(industries.router)
app.include_router(relationships.router)
app.include_router(evidence.router)
app.include_router(context.router)
app.include_router(decision.router)
app.include_router(agent.router)
app.include_router(admin.router)
app.include_router(mcp_router.router)
app.include_router(analytics.router)
app.include_router(certification.router)
app.include_router(subscriptions.router)
app.include_router(marketplace.router)
app.include_router(providers.router)
app.include_router(assets.router)
app.include_router(graph.router)
app.include_router(intelligence.router)
app.include_router(payments.router)
app.include_router(universe.router)


app.include_router(learning.router)
app.include_router(observation_external.router)
app.include_router(geo.router)
app.include_router(memory_universe.router)
app.include_router(onboarding.router)
app.include_router(identity.router)
app.include_router(observation.router)
app.include_router(knowledge.router)

@app.on_event("startup")
async def _start_scheduler():
    get_observation_scheduler().start()


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}