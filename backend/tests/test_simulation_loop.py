"""Simulation closed-loop infrastructure tests."""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from sqlalchemy import delete, select

from app.database import _get_session_factory
from app.models.entity import Entity
from app.models.company import Company
from app.models.evidence import Evidence
from app.models.geo_project import GeoProject, ProjectWorkItem
from app.models.governance import AuditLog, NodeMembership
from app.models.intake import ClientIntake, IntakeAnalysis
from app.models.realm import RealmRegistry
from app.models.user import User, UserRole
from app.services.realm_service import get_realm_service
from app.services.simulation_loop_service import get_simulation_loop_service


def make_user(db, email, role=UserRole.ENTERPRISE):
    user = User(email=email, password_hash="x", name="域主", role=role)
    db.add(user)
    return user


async def _setup_realm(db, user):
    ws = await get_realm_service().create_enterprise(db, user, {
        "name": f"Simulation {uuid.uuid4().hex[:6]}",
        "website": f"https://{uuid.uuid4().hex[:8]}.test",
    })
    entity_id = uuid.UUID(ws["identity"]["id"])
    registry = (await db.execute(
        select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
    )).scalars().first()
    return entity_id, registry.id


async def _cleanup(db, entity_id, user_id, project_ids=(), intake_ids=()):
    for project_id in project_ids:
        await db.execute(delete(ProjectWorkItem).where(ProjectWorkItem.project_id == project_id))
        await db.execute(delete(GeoProject).where(GeoProject.id == project_id))
    for intake_id in intake_ids:
        await db.execute(delete(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake_id))
        await db.execute(delete(ClientIntake).where(ClientIntake.id == intake_id))
    await db.execute(delete(Evidence).where(Evidence.entity_id == entity_id))
    await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(entity_id)))
    await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == entity_id))
    await db.execute(delete(Company).where(Company.id == entity_id))
    await db.execute(delete(Entity).where(Entity.id == entity_id))
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()


class TestSimulationLoop:
    async def test_simulation_loop_marks_everything_simulation_and_builds_plan(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"sim-loop-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            project_ids = []
            intake_ids = []
            try:
                result = await get_simulation_loop_service().run(
                    db, owner, str(entity_id)
                )
                project_ids.append(uuid.UUID(result["project"]["id"]))
                intake_ids.append(uuid.UUID(result["intake"]["id"]))
                assert result["simulation"] is True
                assert result["intake"]["source_truth_status"] == "simulation"
                assert result["analysis"]["unknown_count"] > 0
                assert result["evidence"]["truth_status"] == "synthetic"
                assert result["project"]["truth_status"] == "synthetic"
                assert result["plan"]["simulation"] is True
                assert result["plan"]["work_item_count"] >= 8

                project_id = uuid.UUID(result["project"]["id"])
                intake_id = uuid.UUID(result["intake"]["id"])
                work_items = (await db.execute(
                    select(ProjectWorkItem).where(ProjectWorkItem.project_id == project_id)
                )).scalars().all()
                assert len(work_items) >= 8
                assert all(item.truth_status == "synthetic" for item in work_items)
                assert all((item.metadata_json or {}).get("simulation") is True for item in work_items)

                evidence = (await db.execute(
                    select(Evidence).where(Evidence.entity_id == entity_id)
                )).scalars().first()
                assert evidence is not None
                assert evidence.is_synthetic is True
                assert evidence.may_affect_real_metrics is False

                audit = (await db.execute(
                    select(AuditLog).where(
                        AuditLog.action == "simulation_loop_run",
                        AuditLog.target_id == result["intake"]["id"],
                    )
                )).scalars().first()
                assert audit is not None
                assert audit.metadata_json["simulation"] is True

                latest = await get_simulation_loop_service().latest(db, owner, str(entity_id))
                assert latest["latest"]["intake_code"] == result["intake"]["intake_code"]
            finally:
                await _cleanup(
                    db,
                    entity_id,
                    owner.id,
                    project_ids=project_ids,
                    intake_ids=intake_ids,
                )

    async def test_simulation_loop_requires_owner(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"sim-owner-{uuid.uuid4().hex[:8]}@x.com")
            outsider = make_user(db, f"sim-out-{uuid.uuid4().hex[:8]}@x.com")
            db.add_all([owner, outsider])
            await db.commit()
            await db.refresh(owner)
            await db.refresh(outsider)
            entity_id, _ = await _setup_realm(db, owner)
            try:
                with pytest.raises(PermissionError):
                    await get_simulation_loop_service().run(db, outsider, str(entity_id))
            finally:
                await _cleanup(db, entity_id, owner.id)
                await db.execute(delete(User).where(User.id == outsider.id))
                await db.commit()
