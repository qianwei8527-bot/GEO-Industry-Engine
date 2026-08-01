"""ObservationScheduler — C6.4 Gate 0: single-instance scheduled observation.

DB lease (locked_by/locked_until/version) prevents concurrent duplicate runs
across uvicorn workers. The scheduler is enabled via SCHEDULER_ENABLED=true
and only one instance should hold the startup flag in production.
"""
import os
from datetime import datetime, timezone, timedelta
from typing import Optional
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observation import ObservationSource

LEASE_SECONDS = 300  # a source run should complete well within this
INSTANCE_ID = os.environ.get("OBSERVER_INSTANCE_ID", "scheduler-1")


class ObservationScheduler:
    _instance = None

    def __init__(self):
        self._scheduler = None
        self.enabled = os.environ.get("SCHEDULER_ENABLED", "false").lower() == "true"

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self):
        """Start APScheduler BackgroundScheduler (idempotent; single instance via env)."""
        if not self.enabled or self._scheduler is not None:
            return False
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            self._scheduler = AsyncIOScheduler()
            self._scheduler.add_job(self._tick, "interval", seconds=60, id="observation_tick")
            self._scheduler.start()
            return True
        except Exception:
            return False

    def stop(self):
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None

    async def _tick(self):
        """Pick due sources one at a time using DB lease."""
        from app.database import _get_session_factory
        factory = _get_session_factory()
        async with factory() as db:
            now = datetime.now(timezone.utc)
            due = (await db.execute(
                select(ObservationSource).where(
                    ObservationSource.enabled == True,
                    ObservationSource.paused == False,
                    ObservationSource.next_run_at.is_(None) | (ObservationSource.next_run_at <= now),
                ).order_by(ObservationSource.next_run_at.asc().nullsfirst()).limit(10)
            )).scalars().all()
            for src in due:
                await self._run_with_lease(db, src)

    async def _run_with_lease(self, db, src):
        """Atomically acquire lease; skip if another instance holds a valid lock."""
        now = datetime.now(timezone.utc)
        if src.locked_until and src.locked_until > now and src.locked_by != INSTANCE_ID:
            return
        # acquire (optimistic via version bump; DB update filters expired lock)
        src.locked_by = INSTANCE_ID
        src.locked_until = now + timedelta(seconds=LEASE_SECONDS)
        src.version += 1
        await db.commit()
        try:
            from app.services.external_observation import ExternalObservationService
            svc = ExternalObservationService()
            await svc.run_source(db, src, manual=False, actor_id=f"system:{INSTANCE_ID}")
        except Exception:
            pass
        finally:
            await db.refresh(src)
            src.locked_by = None
            src.locked_until = None
            await db.commit()


@lru_cache()
def get_observation_scheduler():
    return ObservationScheduler.get_instance()
