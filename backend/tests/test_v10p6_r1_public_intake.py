"""V10.6-R1.1 public secure intake security and truth-state tests."""

import asyncio
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.database import _get_session_factory
from app.main import app
from app.models.entity import Entity
from app.models.company import Company
from app.models.governance import AuditLog, NodeMembership
from app.models.intake import ClientIntake, IntakeAnalysis
from app.models.realm import RealmDataAuthorization, RealmRegistry
from app.models.user import User, UserRole
from app.services.intake_rate_limiter import IntakeRateLimiter, MemoryRateLimitBackend
from app.services.intake_service import (
    MAX_FILE_BYTES,
    IntakeDuplicateError,
    IntakeRateLimitError,
    IntakeTokenError,
    get_intake_service,
)
from app.services.realm_service import get_realm_service


def make_user(db, email, role=UserRole.ENTERPRISE):
    user = User(email=email, password_hash="x", name="域主", role=role)
    db.add(user)
    return user


async def _setup_realm(db, user):
    ws = await get_realm_service().create_enterprise(db, user, {
        "name": f"V10.6-R1.1 {uuid.uuid4().hex[:6]}",
        "website": f"https://{uuid.uuid4().hex[:8]}.test",
    })
    entity_id = uuid.UUID(ws["identity"]["id"])
    registry = (await db.execute(
        select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
    )).scalars().first()
    return entity_id, registry.id


async def _cleanup(db, entity_ids, user_ids, intake_ids=(), auth_ids=()):
    for intake_id in intake_ids:
        await db.execute(delete(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake_id))
        await db.execute(delete(ClientIntake).where(ClientIntake.id == intake_id))
    for auth_id in auth_ids:
        await db.execute(delete(RealmDataAuthorization).where(RealmDataAuthorization.id == auth_id))
    for entity_id in entity_ids:
        registry = (await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == entity_id)
        )).scalars().first()
        if registry:
            intakes = (await db.execute(
                select(ClientIntake).where(ClientIntake.realm_id == registry.id)
            )).scalars().all()
            for intake in intakes:
                await db.execute(delete(IntakeAnalysis).where(IntakeAnalysis.intake_id == intake.id))
                await db.execute(delete(ClientIntake).where(ClientIntake.id == intake.id))
            await db.execute(delete(RealmDataAuthorization).where(RealmDataAuthorization.entity_id == entity_id))
            await db.execute(delete(RealmRegistry).where(RealmRegistry.entity_id == entity_id))
        await db.execute(delete(NodeMembership).where(NodeMembership.node_id == str(entity_id)))
        await db.execute(delete(Company).where(Company.id == entity_id))
        await db.execute(delete(Entity).where(Entity.id == entity_id))
    for user_id in user_ids:
        await db.execute(delete(User).where(User.id == user_id))
    await db.commit()


def _payload(**overrides):
    payload = {
        "enterprise_name": "深圳市恒域世界科技有限公司",
        "brand_name": "恒域世界",
        "product_or_project_name": "GEO 运营服务",
        "relationship": "企业自身",
        "problem": "从零开始建立 GEO 认知与转化路径",
        "website_url": "https://example.com",
        "pasted_text": "",
        "supplemental_notes": "客户已提供官网与工商信息",
        "consent_data_analysis": True,
        "consent_use_authorization": True,
        "server_staging_consent": True,
    }
    payload.update(overrides)
    return payload


async def _make_auth(db, owner, entity_id, **overrides):
    data = {
        "source_name": "公共资料提交入口",
        "source_type": "intake_submission_token",
        "use_scope": "intake_submission",
        "grantee_type": "anonymous_intake",
        "grantee_id": "public",
        "valid_until": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "sensitive_level": "medium",
        "data_scope": {"submitter": "anonymous_intake"},
        "metadata": {"token_kind": "public_intake_submission"},
    }
    data.update(overrides)
    return await get_realm_service().create_authorization(db, owner, str(entity_id), data)


class TestPublicSecureIntake:
    async def test_context_draft_submit_duplicate_and_audit(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            intake_ids = []
            auth_ids = []
            try:
                auth = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(auth["id"]))
                token = auth["authorization_code"]
                assert len(token) >= 40
                assert token.startswith("AUTH-")

                svc = get_intake_service()
                context = await svc.get_public_context(db, token)
                assert context["token_status"] == "valid"
                assert "entity_id" not in context["realm"]
                assert context["latest_draft"] is None
                workspace = await get_realm_service().get_workspace(db, owner, str(entity_id))
                auth_item = next(
                    item for item in workspace["authorizations"] if item["id"] == auth["id"]
                )
                assert "authorization_code" not in auth_item
                assert auth_item["authorization_code_masked"]
                assert token not in auth_item["authorization_code_masked"]

                draft = await svc.save_public_draft(db, token, _payload(), [])
                intake_ids.append(uuid.UUID(draft["id"]))
                assert draft["status"] == "draft"
                assert "metadata_json" not in draft

                cleared = await svc.save_public_draft(
                    db, token, _payload(relationship="", pasted_text=""), []
                )
                assert cleared["relationship"] is None
                assert cleared["form"]["relationship"] == ""

                submitted = await svc.submit_public_intake(db, token, _payload(), [])
                assert submitted["status"] == "needs_confirmation"
                assert submitted["processing_status"] == "completed"
                assert submitted["latest_analysis"] is not None
                assert "analysis_json" not in submitted["latest_analysis"]
                assert len([
                    field for field in submitted["latest_analysis"]["fields"]
                    if field["status"] == "unknown"
                ]) > 0
                assert "metadata_json" not in submitted

                context_after = await svc.get_public_context(db, token)
                public_submission = context_after["latest_submission"]
                assert public_submission["latest_analysis"] is not None
                assert public_submission["file_manifest"] == []
                assert "extracted_text" not in str(public_submission)
                assert "metadata_json" not in public_submission

                with pytest.raises(IntakeDuplicateError):
                    await svc.submit_public_intake(db, token, _payload(), [])

                audit = (await db.execute(
                    select(AuditLog).where(
                        AuditLog.action == "public_intake_submission_created",
                        AuditLog.actor_label == f"intake_authorization:{auth['id']}",
                    )
                )).scalars().first()
                assert audit is not None
                assert "AUTH-" not in audit.actor_label
                assert "problem" not in audit.metadata_json
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, auth_ids)

    async def test_token_lifecycle_consent_and_strength(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1b-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            auth_ids = []
            try:
                with pytest.raises(ValueError, match="requires valid_until"):
                    await _make_auth(db, owner, entity_id, valid_until=None)

                not_yet = await _make_auth(
                    db, owner, entity_id,
                    valid_from=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                )
                auth_ids.append(uuid.UUID(not_yet["id"]))
                with pytest.raises(IntakeTokenError) as pending:
                    await get_intake_service().get_public_context(db, not_yet["authorization_code"])
                assert pending.value.code == "token_not_yet_valid"

                expired = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(expired["id"]))
                row = await db.get(RealmDataAuthorization, uuid.UUID(expired["id"]))
                row.valid_until = datetime.now(timezone.utc) - timedelta(hours=1)
                await db.commit()
                with pytest.raises(IntakeTokenError) as expired_error:
                    await get_intake_service().get_public_context(db, expired["authorization_code"])
                assert expired_error.value.code == "token_expired"

                active = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(active["id"]))
                await get_realm_service().revoke_authorization(
                    db, owner, str(entity_id), active["id"], reason="test revoke"
                )
                with pytest.raises(IntakeTokenError) as revoked_error:
                    await get_intake_service().get_public_context(db, active["authorization_code"])
                assert revoked_error.value.code == "token_revoked"

                no_consent = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(no_consent["id"]))
                with pytest.raises(ValueError, match="服务器暂存授权为必填"):
                    await get_intake_service().save_public_draft(
                        db,
                        no_consent["authorization_code"],
                        _payload(server_staging_consent=False),
                        [],
                    )
            finally:
                await _cleanup(db, [entity_id], [owner.id], auth_ids=auth_ids)

    async def test_file_rejection_is_real_and_not_fabricated(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1c-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            auth_ids = []
            intake_ids = []
            try:
                auth = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(auth["id"]))
                submitted = await get_intake_service().submit_public_intake(
                    db,
                    auth["authorization_code"],
                    _payload(),
                    [{"filename": "malware.exe", "content_type": "application/octet-stream", "content": b"MZ"}],
                )
                intake_ids.append(uuid.UUID(submitted["id"]))
                manifest = submitted["file_manifest"]
                assert manifest[0]["parse_status"] == "rejected"
                assert manifest[0]["parse_error"] == "unsupported_type"
                assert "extracted_text" not in manifest[0]
                assert "sha256" not in manifest[0]
                assert "metadata_json" not in submitted
                assert submitted["processing_status"] == "completed"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, auth_ids)

    async def test_draft_cumulative_file_limit(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1d-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            auth_ids = []
            intake_ids = []
            try:
                auth = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(auth["id"]))
                svc = get_intake_service()
                files_a = [
                    {"filename": f"a{i}.txt", "content_type": "text/plain", "content": b"a"}
                    for i in range(3)
                ]
                files_b = [
                    {"filename": f"b{i}.txt", "content_type": "text/plain", "content": b"b"}
                    for i in range(3)
                ]
                draft = await svc.save_public_draft(db, auth["authorization_code"], _payload(), files_a)
                intake_ids.append(uuid.UUID(draft["id"]))
                assert len(draft["file_manifest"]) == 3
                with pytest.raises(ValueError, match="maximum of 5 files"):
                    await svc.save_public_draft(
                        db, auth["authorization_code"], _payload(), files_b
                    )
                context = await svc.get_public_context(db, auth["authorization_code"])
                assert len(context["latest_draft"]["file_manifest"]) == 3
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, auth_ids)

    async def test_rate_limiter_allows_five_and_rejects_sixth(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1f-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            auth_ids = []
            try:
                auth = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(auth["id"]))
                svc = get_intake_service()
                svc.rate_limiter = IntakeRateLimiter(MemoryRateLimitBackend())
                for _ in range(5):
                    await svc.check_public_rate(
                        db, "submit", auth["authorization_code"], "127.0.0.1"
                    )
                with pytest.raises(IntakeRateLimitError):
                    await svc.check_public_rate(
                        db, "submit", auth["authorization_code"], "127.0.0.1"
                    )

                svc.rate_limiter = IntakeRateLimiter(MemoryRateLimitBackend())
                for _ in range(5):
                    with pytest.raises(IntakeTokenError):
                        await svc.check_public_rate(
                            db, "submit", "AUTH-INVALID-TOKEN", "9.9.9.9"
                        )
                with pytest.raises(IntakeRateLimitError):
                    await svc.check_public_rate(
                        db, "submit", "AUTH-INVALID-TOKEN", "9.9.9.9"
                    )
            finally:
                await _cleanup(db, [entity_id], [owner.id], auth_ids=auth_ids)

    async def test_oversized_upload_returns_413_and_not_saved(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1g-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            auth_ids = []
            try:
                auth = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(auth["id"]))
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    response = await client.post(
                        f"/api/v1/intakes/public/{auth['authorization_code']}/draft",
                        data={
                            "enterprise_name": "超大文件测试企业",
                            "server_staging_consent": "true",
                        },
                        files={
                            "files": (
                                "big.txt",
                                b"x" * (MAX_FILE_BYTES + 1),
                                "text/plain",
                            )
                        },
                    )
                    assert response.status_code == 413
                context = await get_intake_service().get_public_context(
                    db, auth["authorization_code"]
                )
                assert context["latest_draft"] is None
            finally:
                await _cleanup(db, [entity_id], [owner.id], auth_ids=auth_ids)

    async def test_draft_stored_file_submit_does_not_duplicate(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1h-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            auth_ids = []
            intake_ids = []
            try:
                auth = await _make_auth(db, owner, entity_id)
                auth_ids.append(uuid.UUID(auth["id"]))
                svc = get_intake_service()
                draft = await svc.save_public_draft(
                    db,
                    auth["authorization_code"],
                    _payload(),
                    [{"filename": "profile.txt", "content_type": "text/plain", "content": b"profile"}],
                )
                intake_ids.append(uuid.UUID(draft["id"]))
                assert len(draft["file_manifest"]) == 1
                submitted = await svc.submit_public_intake(
                    db,
                    auth["authorization_code"],
                    _payload(),
                    [{"filename": "new.txt", "content_type": "text/plain", "content": b"new"}],
                )
                names = [item["file_name"] for item in submitted["file_manifest"]]
                ids = [item["file_id"] for item in submitted["file_manifest"]]
                assert names == ["profile.txt", "new.txt"]
                assert len(ids) == len(set(ids))
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, auth_ids)

    async def test_multiple_tokens_are_independent(self):
        factory = _get_session_factory()
        async with factory() as db:
            owner = make_user(db, f"v106r1i-{uuid.uuid4().hex[:8]}@x.com")
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
            entity_id, _ = await _setup_realm(db, owner)
            auth_ids = []
            intake_ids = []
            try:
                auth_a = await _make_auth(db, owner, entity_id, source_name="客户 A")
                auth_b = await _make_auth(db, owner, entity_id, source_name="客户 B")
                auth_ids.extend([uuid.UUID(auth_a["id"]), uuid.UUID(auth_b["id"])])
                svc = get_intake_service()
                submitted = await svc.submit_public_intake(db, auth_a["authorization_code"], _payload(), [])
                intake_ids.append(uuid.UUID(submitted["id"]))
                context_b = await svc.get_public_context(db, auth_b["authorization_code"])
                assert context_b["token_status"] == "valid"
                await get_realm_service().revoke_authorization(
                    db, owner, str(entity_id), auth_b["id"], reason="independent revoke"
                )
                with pytest.raises(IntakeTokenError) as revoked:
                    await svc.get_public_context(db, auth_b["authorization_code"])
                assert revoked.value.code == "token_revoked"
                context_a = await svc.get_public_context(db, auth_a["authorization_code"])
                assert context_a["latest_submission"]["status"] == "needs_confirmation"
            finally:
                await _cleanup(db, [entity_id], [owner.id], intake_ids, auth_ids)

    async def test_concurrent_double_submit_only_one_succeeds(self):
        factory = _get_session_factory()
        async with factory() as db1:
            owner = make_user(db1, f"v106r1e-{uuid.uuid4().hex[:8]}@x.com")
            db1.add(owner)
            await db1.commit()
            await db1.refresh(owner)
            entity_id, _ = await _setup_realm(db1, owner)
            auth = await _make_auth(db1, owner, entity_id)
            auth_id = uuid.UUID(auth["id"])
            token = auth["authorization_code"]
            try:
                async with factory() as db2:
                    async def run(db):
                        return await get_intake_service().submit_public_intake(db, token, _payload(), [])

                    results = await asyncio.gather(run(db1), run(db2), return_exceptions=True)
                    successes = [result for result in results if not isinstance(result, Exception)]
                    errors = [result for result in results if isinstance(result, Exception)]
                    assert len(successes) == 1
                    assert any(isinstance(error, IntakeDuplicateError) for error in errors)
            finally:
                await _cleanup(db1, [entity_id], [owner.id], auth_ids=[auth_id])
