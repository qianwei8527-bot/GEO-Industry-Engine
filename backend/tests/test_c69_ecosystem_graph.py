"""C6.9 Ecosystem Graph: structure, relation, causality, evolution, next connection."""

import sys
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

from app.universe.ecosystem_graph import EcosystemGraphEngine, get_ecosystem_graph_engine
from app.universe.reputation_engine import ReputationEngine, get_reputation_engine
from app.universe.memory_engine import MemoryEngine, get_memory_engine
from app.universe.relationship_engine import RelationshipEngine, get_relationship_engine
from app.universe.connection_engine import FutureConnectionEngine
from app.universe.possibility_engine import PossibilityEngine


class TestEcosystemGraph:
    def setup_method(self):
        EcosystemGraphEngine.reset()
        ReputationEngine.reset()
        MemoryEngine.reset()
        RelationshipEngine.reset()
        FutureConnectionEngine.reset()
        PossibilityEngine.reset()

    def _seed(self):
        re = get_reputation_engine()
        re.record_event("node-x", "company", "certification_passed",
                        "GEO certification passed", "government",
                        timestamp="2026-02-01T00:00:00+00:00")
        re.record_event("node-x", "company", "customer_success",
                        "Client project completed", "enterprise_customer",
                        timestamp="2026-04-01T00:00:00+00:00")
        re.record_event("node-x", "company", "relationship_strengthened",
                        "Strategic partner deepened", "partner",
                        timestamp="2026-06-01T00:00:00+00:00")
        re.recalculate("node-x", "company")
        mem = get_memory_engine()
        mem.record_fact(node_id="node-x", node_type="company",
                        statement="GEO certification passed", category="certification")
        rel = get_relationship_engine()
        rel.create_relationship("node-x", "node-y", relationship_type="partnership",
                                initiated_by="node-x")
        return {
            "name": "星辰AI营销科技",
            "industry_id": "geo_services",
            "industry_name": "GEO服务",
            "relationships_list": [
                {"node_id": "node-y", "type": "partners_with", "stage": "COLLABORATING",
                 "strength": 0.8, "direction": "bidirectional"}
            ],
        }

    def test_explain_returns_four_layers(self):
        extra = self._seed()
        report = get_ecosystem_graph_engine().explain("node-x", "company", extra)
        assert report["structure"]["identity"]["name"] == "星辰AI营销科技"
        assert report["structure"]["position"]["industry"] == "GEO服务"
        assert report["relations"]["total"] >= 1
        assert report["causality"]["available"] is True
        assert report["evolution"]["current_stage"] in ("entry", "active", "trusted")
        assert "needs" in report["next_connections"]

    def test_causality_chain_orders_events(self):
        extra = self._seed()
        report = get_ecosystem_graph_engine().explain("node-x", "company", extra)
        types = [e["event_type"] for e in report["causality"]["chain"]]
        assert "certification_passed" in types
        assert "relationship_strengthened" in types
        dates = [e["timestamp"] for e in report["causality"]["chain"]]
        assert dates == sorted(dates)

    def test_graph_projection_has_nodes_and_edges(self):
        extra = self._seed()
        graph = get_ecosystem_graph_engine().project_graph("node-x", "company", extra)
        node_ids = {n["node_id"] for n in graph["nodes"]}
        assert "node-x" in node_ids
        assert "node-y" in node_ids
        assert graph["edge_count"] >= 1
        types = {e["relation_type"] for e in graph["edges"]}
        assert "partnership" in types or "partners_with" in types
        assert graph["layers"]["structure"]["identity"]["name"] == "星辰AI营销科技"

    def test_empty_node_explains_without_fabrication(self):
        report = EcosystemGraphEngine().explain("fresh-node", "company", {})
        assert report["structure"]["identity"]["node_id"] == "fresh-node"
        assert report["causality"]["available"] is False
        assert report["evolution"]["current_stage"] == "entry"
        assert "needs" in report["next_connections"]
