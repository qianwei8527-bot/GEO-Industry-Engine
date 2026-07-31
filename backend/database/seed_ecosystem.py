"""GEO Universe Seed Ecosystem - Sprint 5.3-B: First Living Ecosystem.

Creates a complete GEO industry ecosystem with lifecycle data.
"""

import asyncio, sys, uuid
sys.path.insert(0, ".")
from datetime import date, timedelta
from sqlalchemy import select
from app.database import _get_session_factory
from app.models.entity import Entity
from app.models.company import Company
from app.models.provider import Provider
from app.models.industry import Industry
from app.models.capability import Capability
from app.models.relationship import Relationship
from app.models.identity_profile import IdentityProfile
from app.models.node_snapshot import NodeSnapshot
from app.models.reputation import Reputation
from app.models.geo_event import GeoEvent

COMPANIES = [
    {"name": "\u9f99\u817eAI\u79d1\u6280", "stage": "Established", "geo": 85, "trust": 88, "vis": 82, "cap_score": 90,
     "desc": "\u884c\u4e1a\u9f99\u5934\u4f01\u4e1a\uff0cGEO\u7efc\u5408\u8bc4\u5206\u6700\u9ad8\uff0c\u62e5\u6709\u5b8c\u6574\u7684AI\u53ef\u89c1\u5ea6\u4f18\u5316\u4f53\u7cfb",
     "evidence": 25, "certs": 4, "rels": 12, "comps": 5, "size": "500-1000\u4eba", "region": "\u5317\u4eac"},
    {"name": "\u667a\u6e90\u6570\u636e\u96c6\u56e2", "stage": "Established", "geo": 78, "trust": 82, "vis": 75, "cap_score": 80,
     "desc": "\u6570\u636e\u9a71\u52a8\u578b\u4f01\u4e1a\uff0c\u5728Evidence\u548cTrust\u7ef4\u5ea6\u8868\u73b0\u7a81\u51fa",
     "evidence": 22, "certs": 3, "rels": 10, "comps": 4, "size": "200-500\u4eba", "region": "\u4e0a\u6d77"},
    {"name": "\u661f\u8fb0AI\u8425\u9500\u79d1\u6280", "stage": "Active", "geo": 68, "trust": 70, "vis": 65, "cap_score": 72,
     "desc": "\u5feb\u901f\u6210\u957f\u7684AI\u8425\u9500\u4f01\u4e1a\uff0c\u8fc7\u53bb90\u5929GEO\u8bc4\u5206\u4e0a\u534728\u5206",
     "evidence": 10, "certs": 2, "rels": 5, "comps": 4, "size": "50-200\u4eba", "region": "\u6df1\u5733"},
    {"name": "\u6781\u5149\u667a\u80fd\u8425\u9500", "stage": "Active", "geo": 55, "trust": 58, "vis": 52, "cap_score": 60,
     "desc": "\u4e13\u6ce8AI\u641c\u7d22\u4f18\u5316\u7684\u6210\u957f\u578b\u4f01\u4e1a\uff0cTrust\u7ef4\u5ea6\u6709\u8f83\u5927\u63d0\u5347\u7a7a\u95f4",
     "evidence": 7, "certs": 1, "rels": 4, "comps": 3, "size": "20-50\u4eba", "region": "\u676d\u5dde"},
    {"name": "\u6570\u8054\u672a\u6765\u79d1\u6280", "stage": "Active", "geo": 52, "trust": 50, "vis": 55, "cap_score": 48,
     "desc": "\u4ee5\u6570\u636e\u76d1\u6d4b\u548c\u5206\u6790\u89c1\u957f\uff0cVisibility\u8868\u73b0\u4f18\u4e8eTrust",
     "evidence": 6, "certs": 1, "rels": 3, "comps": 3, "size": "20-50\u4eba", "region": "\u5e7f\u5dde"},
    {"name": "\u65b0\u9014AI", "stage": "Entry", "geo": 38, "trust": 35, "vis": 40, "cap_score": 42,
     "desc": "\u521d\u521b\u4f01\u4e1a\uff0c\u6709\u660e\u786e\u7684\u6280\u672f\u80fd\u529b\u4f46\u7f3a\u4e4f\u884c\u4e1a\u8ba4\u8bc1\u548c\u8bc1\u636e\u79ef\u7d2f",
     "evidence": 3, "certs": 0, "rels": 2, "comps": 2, "size": "10-20\u4eba", "region": "\u6210\u90fd"},
    {"name": "\u4e91\u5e06\u6570\u5b57", "stage": "Entry", "geo": 42, "trust": 40, "vis": 38, "cap_score": 45,
     "desc": "\u65b0\u8fdb\u5165\u8005\uff0cCapability\u80fd\u529b\u4e2d\u4e0a\u4f46Trust\u548cVisibility\u504f\u4f4e",
     "evidence": 2, "certs": 0, "rels": 1, "comps": 2, "size": "5-10\u4eba", "region": "\u6b66\u6c49"},
    {"name": "\u542f\u660e\u667a\u80fd", "stage": "Entry", "geo": 30, "trust": 28, "vis": 32, "cap_score": 35,
     "desc": "\u6700\u65b0\u8fdb\u5165GEO\u9886\u57df\u7684\u4f01\u4e1a\uff0c\u5404\u65b9\u9762\u90fd\u5904\u4e8e\u8d77\u6b65\u9636\u6bb5\uff0c\u589e\u957f\u7a7a\u95f4\u6700\u5927",
     "evidence": 1, "certs": 0, "rels": 1, "comps": 1, "size": "1-5\u4eba", "region": "\u897f\u5b89"},
]

PROVIDERS = [
    {"name": "\u5185\u5bb9\u5f15\u64ce\u5b9e\u9a8c\u5ba4", "desc": "\u4e13\u6ce8AI\u65f6\u4ee3\u5185\u5bb9\u7b56\u7565\u4e0e\u751f\u6210\uff0c\u5e2e\u52a9\u4f01\u4e1a\u6784\u5efa\u9ad8\u8d28\u91cf\u5185\u5bb9\u8d44\u4ea7",
     "capabilities": ["Content Engineering", "Entity Building"], "evidence": 15, "certs": 2, "region": "\u5317\u4eac"},
    {"name": "\u6570\u636e\u67b6\u6784\u5de5\u573a", "desc": "\u63d0\u4f9b\u7ed3\u6784\u5316\u6570\u636e\u548cSchema\u4f18\u5316\u670d\u52a1\uff0c\u63d0\u5347AI\u5bf9\u4f01\u4e1a\u7684\u7406\u89e3\u6df1\u5ea6",
     "capabilities": ["Entity Building", "Evidence Management"], "evidence": 12, "certs": 2, "region": "\u4e0a\u6d77"},
    {"name": "AI\u589e\u957f\u54a8\u8be2", "desc": "\u7efc\u5408GEO\u6218\u7565\u54a8\u8be2\uff0c\u8986\u76d6AI\u641c\u7d22\u4f18\u5316\u5168\u94fe\u8def",
     "capabilities": ["AI Visibility Optimization", "Authority Building"], "evidence": 18, "certs": 3, "region": "\u6df1\u5733"},
    {"name": "\u76d1\u6d4b\u5148\u950b\u79d1\u6280", "desc": "\u5b9e\u65f6\u76d1\u6d4b\u4f01\u4e1aGEO\u8868\u73b0\uff0c\u63d0\u4f9b\u6570\u636e\u5206\u6790\u548c\u6539\u8fdb\u5efa\u8bae",
     "capabilities": ["Monitoring Analytics", "AI Visibility Optimization"], "evidence": 8, "certs": 1, "region": "\u676d\u5dde"},
    {"name": "\u54c1\u724c\u6743\u5a01\u5efa\u8bbe", "desc": "\u5e2e\u52a9\u4f01\u4e1a\u5efa\u7acb\u884c\u4e1a\u6743\u5a01\u5ea6\u548c\u54c1\u724c\u4fe1\u4efb",
     "capabilities": ["Authority Building", "Content Engineering"], "evidence": 10, "certs": 2, "region": "\u5317\u4eac"},
    {"name": "GEO\u5b66\u9662", "desc": "GEO\u77e5\u8bc6\u57f9\u8bad\u548c\u80fd\u529b\u8ba4\u8bc1\uff0c\u57f9\u517b\u884c\u4e1a\u4eba\u624d",
     "capabilities": ["Monitoring Analytics", "Content Engineering"], "evidence": 6, "certs": 1, "region": "\u7ebf\u4e0a"},
]

CAPABILITIES = ["Entity Building", "Evidence Management", "Content Engineering",
                "AI Visibility Optimization", "Authority Building", "Monitoring Analytics"]

SNAPSHOT_TEMPLATES = {
    "Established": [
        {"days_ago": 180, "geo_delta": -30, "trust_delta": -28, "vis_delta": -25, "cap_delta": -25},
        {"days_ago": 120, "geo_delta": -15, "trust_delta": -15, "vis_delta": -15, "cap_delta": -15},
        {"days_ago": 60, "geo_delta": -5, "trust_delta": -5, "vis_delta": -5, "cap_delta": -5},
    ],
    "Active": [
        {"days_ago": 90, "geo_delta": -25, "trust_delta": -22, "vis_delta": -20, "cap_delta": -20},
        {"days_ago": 45, "geo_delta": -10, "trust_delta": -8, "vis_delta": -10, "cap_delta": -8},
    ],
    "Entry": [
        {"days_ago": 45, "geo_delta": -15, "trust_delta": -15, "vis_delta": -15, "cap_delta": -15},
    ],
}

REPUTATION_LEVELS = {"Established": "AA", "Active": "A", "Entry": "B"}


async def seed_ecosystem():
    factory = _get_session_factory()
    async with factory() as db:
        print("=== GEO Universe First Living Ecosystem ===\\n")
        today = date.today()

        # [1/7] Industry
        print("[1/7] Creating industry...")
        existing_ind = (await db.execute(
            select(Industry).where(Industry.code == "GEO")
        )).scalars().first()
        if existing_ind:
            ind_id = existing_ind.id
            print(f"  Using existing: {existing_ind.name}")
        else:
            industry = Industry(
                id=uuid.uuid4(), name="GEO\u4ea7\u4e1a", code="GEO",
                description="\u751f\u6210\u5f0f\u5f15\u64ce\u4f18\u5316\u4ea7\u4e1a\u2014\u2014\u6db5\u76d6AI\u641c\u7d22\u4f18\u5316\u3001\u4f01\u4e1aAI\u53ef\u89c1\u5ea6\u3001AI\u5185\u5bb9\u751f\u6001\u3001AI\u77e5\u8bc6\u8d44\u4ea7\u548cGEO\u6280\u672f\u670d\u52a1\u4e94\u5927\u5b50\u8d5b\u9053",
                level=0,
            )
            db.add(industry)
            await db.flush()
            ind_id = industry.id
            print(f"  Created: {industry.name}")

        # [2/7] Companies
        print("\\n[2/7] Creating companies...")
        company_map = {}
        for c in COMPANIES:
            existing = (await db.execute(
                select(Company).where(Company.name == c["name"])
            )).scalars().first()
            if existing:
                company_map[c["name"]] = existing
                print(f"  Using existing: {c['name']} (Stage: {c['stage']})")
                continue
            comp = Company(
                id=uuid.uuid4(), name=c["name"], entity_type="company",
                geo_id=f"GEO-COMP-{uuid.uuid4().hex[:8].upper()}",
                description=c["desc"], industry_id=ind_id,
                geo_score=c["geo"], company_size=c["size"],
                headquarters=c["region"], region=c["region"],
            )
            db.add(comp)
            company_map[c["name"]] = comp
            print(f"  Created: {c['name']} (Stage: {c['stage']}, GEO: {c['geo']})")
        await db.flush()

        # [3/7] Capabilities (attached to anchor company for FK requirement)
        print("\\n[3/7] Creating capabilities...")
        cap_map = {}
        anchor = list(company_map.values())[0]
        print(f"  Anchor company: {anchor.name}")
        for cname in CAPABILITIES:
            existing = (await db.execute(
                select(Capability).where(Capability.name == cname)
            )).scalars().first()
            if existing:
                cap_map[cname] = existing.id
                print(f"    Using existing: {cname}")
                continue
            cap = Capability(
                id=uuid.uuid4(), name=cname,
                description=f"GEO\u4ea7\u4e1a\u6838\u5fc3\u80fd\u529b: {cname}",
                company_id=anchor.id, level=1,
            )
            db.add(cap)
            cap_map[cname] = cap.id
            print(f"    Created: {cname}")
        await db.flush()

        # [4/7] Providers
        print("\\n[4/7] Creating providers...")
        provider_map = {}
        for p in PROVIDERS:
            existing = (await db.execute(
                select(Provider).join(Entity, Provider.entity_id == Entity.id)
                .where(Entity.name == p["name"])
            )).scalars().first()
            if existing:
                provider_map[p["name"]] = existing
                print(f"  Using existing: {p['name']}")
                continue
            entity = Entity(
                id=uuid.uuid4(), entity_type="provider",
                name=p["name"], description=p["desc"],
                geo_id=f"GEO-PROV-{uuid.uuid4().hex[:8].upper()}",
                region=p["region"],
            )
            db.add(entity)
            await db.flush()
            prov = Provider(
                id=uuid.uuid4(), entity_id=entity.id,
                provider_type="company",
                trust_score=p["certs"] * 15.0,
                geo_score=p["evidence"] * 3.0,
                verification_status="verified",
            )
            db.add(prov)
            provider_map[p["name"]] = prov
            print(f"  Created: {p['name']}")
        await db.flush()

        # [5/7] Relationships
        print("\\n[5/7] Creating relationships...")
        rel_count = 0

        def add_rel(src_type, src_id, tgt_type, tgt_id, rel_type, weight=1.0, desc=None):
            nonlocal rel_count
            rel = Relationship(
                source_type=src_type, source_id=src_id,
                target_type=tgt_type, target_id=tgt_id,
                relation_type=rel_type, weight=weight, description=desc,
            )
            db.add(rel)
            rel_count += 1

        comp_list = list(company_map.values())
        prov_list = list(provider_map.values())

        # Competition among companies
        for i in range(len(comp_list)):
            for j in range(i + 1, min(i + 3, len(comp_list))):
                add_rel("company", comp_list[i].id, "company", comp_list[j].id,
                        "competition", 0.7)

        # Cooperation: companies -> providers
        for ci, comp in enumerate(comp_list):
            for pi in range(min(3, len(prov_list))):
                add_rel("company", comp.id, "provider", prov_list[pi].id,
                        "cooperation", 0.8,
                        f"{COMPANIES[ci]['name']} - {PROVIDERS[pi]['name']} \u5408\u4f5c\u5173\u7cfb")

        # Provider capability linking
        for pi, pdata in enumerate(PROVIDERS):
            prov = prov_list[pi]
            for cname in pdata["capabilities"]:
                if cname in cap_map:
                    add_rel("provider", prov.entity_id, "capability", cap_map[cname],
                            "capability", 1.0)

        print(f"  Created {rel_count} relationships")

        # [6/7] IdentityProfile + Snapshots + Reputation
        print("\\n[6/7] Creating IdentityProfiles, Snapshots, and Reputation...")
        snapshot_count = 0

        for cdata in COMPANIES:
            comp = company_map[cdata["name"]]
            comp_id = comp.id

            # IdentityProfile
            existing_ip = (await db.execute(
                select(IdentityProfile).where(
                    IdentityProfile.entity_id == comp_id,
                    IdentityProfile.is_primary == True
                )
            )).scalars().first()
            if not existing_ip:
                ip = IdentityProfile(
                    entity_id=comp_id,
                    identity_type="\u4f01\u4e1a",
                    display_name=cdata["name"],
                    industry_context="GEO\u4ea7\u4e1a",
                    growth_stage=cdata["stage"],
                    reputation_level=REPUTATION_LEVELS[cdata["stage"]],
                    geo_score=cdata["geo"],
                    visibility_score=cdata["vis"],
                    trust_score=cdata["trust"],
                    capability_score=cdata["cap_score"],
                    evidence_count=cdata["evidence"],
                    certification_count=cdata["certs"],
                    relationship_count=cdata["rels"],
                )
                db.add(ip)

            # NodeSnapshots - current state
            snap = NodeSnapshot(
                entity_id=comp_id, snapshot_date=today,
                snapshot_type="daily",
                trigger_event=f"Current state - {cdata['stage']} stage",
                growth_stage=cdata["stage"],
                geo_score=cdata["geo"], visibility_score=cdata["vis"],
                trust_score=cdata["trust"], capability_score=cdata["cap_score"],
                evidence_count=cdata["evidence"],
                certification_count=cdata["certs"],
                relationship_count=cdata["rels"],
                competitor_count=cdata["comps"],
                change_summary=f"\u5f53\u524d\u72b6\u6001: {cdata['stage']}\u9636\u6bb5",
            )
            db.add(snap)
            snapshot_count += 1

            # Historical snapshots
            for tmpl in SNAPSHOT_TEMPLATES.get(cdata["stage"], []):
                days = tmpl["days_ago"]
                if days > 90:
                    hist_stage = "Entry"
                elif days > 45:
                    hist_stage = "Active"
                else:
                    hist_stage = cdata["stage"]
                hist = NodeSnapshot(
                    entity_id=comp_id,
                    snapshot_date=today - timedelta(days=days),
                    snapshot_type="event",
                    trigger_event="\u9636\u6bb5\u53d8\u5316\u4e0e\u80fd\u529b\u79ef\u7d2f",
                    growth_stage=hist_stage,
                    geo_score=cdata["geo"] + tmpl["geo_delta"],
                    visibility_score=cdata["vis"] + tmpl["vis_delta"],
                    trust_score=cdata["trust"] + tmpl["trust_delta"],
                    capability_score=cdata["cap_score"] + tmpl["cap_delta"],
                    evidence_count=max(1, cdata["evidence"] - 3),
                    certification_count=max(0, cdata["certs"] - 1),
                    relationship_count=max(1, cdata["rels"] - 2),
                    change_summary="\u65e9\u671f\u6210\u957f\u8bb0\u5f55",
                )
                db.add(hist)
                snapshot_count += 1

            # Reputation (correct field names)
            existing_rep = (await db.execute(
                select(Reputation).where(Reputation.node_id == comp_id)
            )).scalars().first()
            if not existing_rep:
                rep = Reputation(
                    node_id=comp_id, node_type="company",
                    reputation_level=REPUTATION_LEVELS[cdata["stage"]],
                    total_score=float(cdata["trust"]),
                    evidence_count=cdata["evidence"],
                )
                db.add(rep)

        print(f"  Created {snapshot_count} snapshots across all nodes")

        # [7/7] GeoEvents
        print("\\n[7/7] Creating GeoEvents...")
        geo_events = [
            {"type": "industry_growth", "title": "GEO\u4ea7\u4e1a\u52a0\u901f\u589e\u957f",
             "desc": "\u8fc7\u53bb6\u4e2a\u6708\uff0cGEO\u4ea7\u4e1a\u4f01\u4e1a\u6570\u91cf\u589e\u957f40%\uff0cAI\u641c\u7d22\u4f18\u5316\u6210\u4e3a\u6838\u5fc3\u8d5b\u9053",
             "impact": "high"},
            {"type": "new_capability", "title": "AI Agent\u80fd\u529b\u5174\u8d77",
             "desc": "AI Agent\u4f5c\u4e3a\u65b0\u7684GEO\u80fd\u529b\u7ef4\u5ea6\u6b63\u5728\u5f62\u6210\uff0c\u9884\u8ba1\u5c06\u6210\u4e3a\u4e0b\u4e00\u9636\u6bb5\u7ade\u4e89\u7126\u70b9",
             "impact": "medium"},
            {"type": "certification", "title": "\u9f99\u817eAI\u79d1\u6280\u83b7\u5f97AAA\u7ea7\u8ba4\u8bc1",
             "desc": "\u884c\u4e1a\u9996\u5bb6\u83b7\u5f97\u6700\u9ad8\u7ea7\u522bGEO\u80fd\u529b\u8ba4\u8bc1\u7684\u4f01\u4e1a",
             "impact": "high"},
        ]
        for ge in geo_events:
            event = GeoEvent(
                event_type=ge["type"], title=ge["title"],
                description=ge["desc"], impact_level=ge["impact"],
                impact_score={"high": 0.8, "medium": 0.5, "low": 0.3}.get(ge["impact"], 0.5),
                is_processed=True,
            )
            db.add(event)
        print(f"  Created {len(geo_events)} GeoEvents")

        await db.commit()
        print(f"\\n=== Ecosystem seed complete! ===")
        print(f"Industry: 1 | Companies: {len(company_map)} | Providers: {len(provider_map)}")
        print(f"Capabilities: {len(cap_map)} | Relationships: {rel_count} | Snapshots: {snapshot_count}")
        print(f"IdentityProfiles + Reputation: created for all nodes")


if __name__ == "__main__":
    asyncio.run(seed_ecosystem())
