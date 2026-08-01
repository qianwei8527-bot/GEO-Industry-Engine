# GEO Universe Relationship Lifecycle Engine
# Phase C5.2 — Relationship as a first-class Universe Entity.
#
# Relationship is NOT an edge. It is a living entity with its own:
#   - Identity (who are the two nodes)
#   - Lifecycle (state machine)
#   - Memory (event history)
#   - Reputation (independent from Node Reputation)
#
# Principle: Node Reputation != Relationship Reputation.
# Two high-reputation nodes can have a low-reputation relationship.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from functools import lru_cache
import uuid, math, os as _os, yaml

_loaded_config = None
def _load_config():
    global _loaded_config
    if _loaded_config: return _loaded_config
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))), 'config', 'universe', 'relationship.yaml')
    _loaded_config = yaml.safe_load(open(p, encoding='utf-8')) if _os.path.exists(p) else _default_config()
    return _loaded_config

def _default_config():
    return {
        'version': '1.0',
        'states': ['UNKNOWN','DISCOVERED','CONNECTED','ACTIVE','COLLABORATING','VERIFIED','TRUSTED','STRATEGIC','DORMANT','ENDED'],
        'transitions': {
            'UNKNOWN': ['DISCOVERED'],
            'DISCOVERED': ['CONNECTED','UNKNOWN'],
            'CONNECTED': ['ACTIVE','DORMANT','ENDED'],
            'ACTIVE': ['COLLABORATING','DORMANT','ENDED'],
            'COLLABORATING': ['VERIFIED','ACTIVE','DORMANT','ENDED'],
            'VERIFIED': ['TRUSTED','COLLABORATING','DORMANT','ENDED'],
            'TRUSTED': ['STRATEGIC','VERIFIED','DORMANT','ENDED'],
            'STRATEGIC': ['TRUSTED','DORMANT','ENDED'],
            'DORMANT': ['ACTIVE','ENDED'],
            'ENDED': [],
        },
        'reputation_dimensions': [
            {'id':'stability','label':'Stability','weight':0.20},
            {'id':'reciprocity','label':'Reciprocity','weight':0.20},
            {'id':'outcome','label':'Outcome','weight':0.25},
            {'id':'communication','label':'Communication','weight':0.10},
            {'id':'value_creation','label':'Value Creation','weight':0.25},
        ],
        'event_types': {
            'discovered': {'from_state':'UNKNOWN','to_state':'DISCOVERED'},
            'connected': {'from_state':'DISCOVERED','to_state':'CONNECTED'},
            'activated': {'from_state':'CONNECTED','to_state':'ACTIVE'},
            'collaboration_started': {'from_state':'ACTIVE','to_state':'COLLABORATING'},
            'collaboration_completed': {'from_state':'COLLABORATING','to_state':'VERIFIED'},
            'collaboration_failed': {'from_state':'COLLABORATING','to_state':'ACTIVE'},
            'trust_established': {'from_state':'VERIFIED','to_state':'TRUSTED'},
            'strategic_partnership': {'from_state':'TRUSTED','to_state':'STRATEGIC'},
            'went_dormant': {'to_state':'DORMANT'},
            'ended': {'to_state':'ENDED'},
            'feedback_positive': {},
            'feedback_negative': {},
        },
        'level_thresholds': {'A':85,'B':70,'C':55,'D':40,'E':0},
    }

print('Part 1 OK: Config and imports')


@dataclass
class Relationship:
    relationship_id: str = ''
    node_a_id: str = ''
    node_b_id: str = ''
    relationship_type: str = 'partnership'
    stage: str = 'UNKNOWN'
    previous_stage: str = ''
    initiated_by: str = ''
    initiated_at: str = ''
    last_activity_at: str = ''
    stage_entered_at: str = ''
    created_at: str = ''
    relationship_trust: Dict = None
    total_interactions: int = 0
    total_projects: int = 0
    successful_projects: int = 0
    duration_days: int = 0
    purpose: str = ''
    industry: str = ''
    value_exchange: List = field(default_factory=list)
    metadata: Dict = None
    def __post_init__(self):
        if not self.relationship_id: self.relationship_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at: self.created_at = now
        if not self.stage_entered_at: self.stage_entered_at = now
        if not self.last_activity_at: self.last_activity_at = now
        if self.relationship_trust is None: self.relationship_trust = {'stability':0,'reciprocity':0,'outcome':0,'communication':0,'value_creation':0,'overall':0,'level':'N/A'}
        if self.value_exchange is None: self.value_exchange = []
        if self.metadata is None: self.metadata = {}
    def to_dict(self):
        return {'relationship_id':self.relationship_id,'node_a_id':self.node_a_id,'node_b_id':self.node_b_id,'relationship_type':self.relationship_type,'stage':self.stage,'previous_stage':self.previous_stage,'purpose':self.purpose,'industry':self.industry,'value_exchange':self.value_exchange,'relationship_trust':self.relationship_trust,'total_interactions':self.total_interactions,'total_projects':self.total_projects,'successful_projects':self.successful_projects,'duration_days':self.duration_days,'last_activity_at':self.last_activity_at,'created_at':self.created_at}

@dataclass
class RelationshipEvent:
    event_id: str = ''
    relationship_id: str = ''
    event_type: str = ''
    actor_id: str = ''
    from_stage: str = ''
    to_stage: str = ''
    description: str = ''
    reputation_impact: Dict = None
    outcome_score: float = 0.0
    timestamp: str = ''
    def __post_init__(self):
        if not self.event_id: self.event_id = str(uuid.uuid4())[:8]
        if not self.timestamp: self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.reputation_impact is None: self.reputation_impact = {}
    def to_dict(self):
        return {'event_id':self.event_id,'relationship_id':self.relationship_id,'event_type':self.event_type,'actor_id':self.actor_id,'from_stage':self.from_stage,'to_stage':self.to_stage,'description':self.description,'reputation_impact':self.reputation_impact,'outcome_score':self.outcome_score,'timestamp':self.timestamp}

@dataclass
class RelationshipReputation:
    relationship_id: str = ''
    node_pair: Tuple = ()
    stability: float = 0.0
    reciprocity: float = 0.0
    outcome: float = 0.0
    communication: float = 0.0
    value_creation: float = 0.0
    overall: float = 0.0
    level: str = 'N/A'
    events_count: int = 0
    last_evaluated_at: str = ''
    def __post_init__(self):
        if not self.last_evaluated_at: self.last_evaluated_at = datetime.now(timezone.utc).isoformat()
        if self.node_pair == (): self.node_pair = ('','')
    def to_dict(self):
        return {'relationship_id':self.relationship_id,'dimensions':{'stability':round(self.stability,1),'reciprocity':round(self.reciprocity,1),'outcome':round(self.outcome,1),'communication':round(self.communication,1),'value_creation':round(self.value_creation,1)},'overall':round(self.overall,1),'level':self.level,'events_count':self.events_count}
print('Part 2 appended')


class RelationshipStateMachine:
    def __init__(self, config=None):
        self.config = config or _load_config()
        self._transitions = self.config.get('transitions', {})
    def can_transition(self, from_stage, to_stage):
        return to_stage in self._transitions.get(from_stage, [])
    def get_allowed_transitions(self, stage):
        return self._transitions.get(stage, [])
    def transition(self, rel, to_stage, event_type='', actor_id=''):
        if not self.can_transition(rel.stage, to_stage):
            allowed = self.get_allowed_transitions(rel.stage)
            raise ValueError('Invalid transition: ' + rel.stage + ' -> ' + to_stage + '. Allowed: ' + str(allowed))
        prev = rel.stage
        rel.previous_stage = prev
        rel.stage = to_stage
        rel.stage_entered_at = datetime.now(timezone.utc).isoformat()
        rel.last_activity_at = datetime.now(timezone.utc).isoformat()
        rel.total_interactions += 1
        now = datetime.now(timezone.utc)
        if rel.initiated_at:
            try:
                start = datetime.fromisoformat(rel.initiated_at.replace('Z','+00:00'))
                rel.duration_days = (now - start).days
            except: pass
        return RelationshipEvent(
            relationship_id=rel.relationship_id,
            event_type=event_type or 'stage_' + to_stage.lower(),
            actor_id=actor_id, from_stage=prev, to_stage=to_stage,
            description=prev + ' -> ' + to_stage
        )
    @classmethod
    def reset(cls): pass

class RelationshipEventStore:
    _instance = None
    def __init__(self):
        self._events = {}
    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def append(self, event):
        self._events.setdefault(event.relationship_id, []).append(event)
        return event
    def get_events(self, relationship_id, since=None):
        events = self._events.get(relationship_id, [])
        if since: events = [e for e in events if e.timestamp >= since]
        return sorted(events, key=lambda e: e.timestamp)
    def get_event_count(self, relationship_id):
        return len(self._events.get(relationship_id, []))
    @classmethod
    def reset(cls): cls._instance = None

class RelationshipReputationCalculator:
    def __init__(self, config=None):
        self.config = config or _load_config()
    def calculate(self, relationship_id, events):
        if not events:
            return RelationshipReputation(relationship_id=relationship_id)
        now = datetime.now(timezone.utc)
        cfg = self.config
        dims = cfg.get('reputation_dimensions', [])
        weights = {d['id']: d['weight'] for d in dims}
        today = now.date()
        first_event_date = datetime.fromisoformat(
            events[0].timestamp.replace('Z','+00:00')
        ).date()
        stability = min(100, (today - first_event_date).days / 365.0 * 100)
        reciprocity = 0
        outcome = 0; outcome_count = 0
        comm = 50
        actors = set()
        for e in events:
            if e.actor_id:
                actors.add(e.actor_id)
            if e.outcome_score != 0:
                outcome += (e.outcome_score + 1) / 2 * 100
                outcome_count += 1
            if e.event_type in ('connected','activated'):
                comm = min(100, comm + 10)
            if 'feedback' in e.event_type:
                if 'positive' in e.event_type:
                    comm = min(100, comm + 5)
                else:
                    comm = max(0, comm - 5)
        reciprocity = min(100, len(actors) * 35)
        if outcome_count > 0:
            outcome /= outcome_count
        else:
            outcome = 30
        scores = {'stability': stability, 'reciprocity': reciprocity,
                  'outcome': outcome, 'communication': comm}
        overall = sum(scores.get(d['id'], 0) * d['weight'] for d in dims)
        level = self._score_to_level(overall)
        return RelationshipReputation(
            relationship_id=relationship_id,
            stability=stability, reciprocity=reciprocity,
            outcome=outcome, communication=comm,
            value_creation=outcome,
            overall=round(overall, 1), level=level,
            events_count=len(events)
        )
    def _score_to_level(self, score):
        th = self.config.get('level_thresholds',{})
        for lvl, t in sorted(th.items(), key=lambda x: x[1], reverse=True):
            if score >= t: return lvl
        return 'E'
    @classmethod
    def reset(cls): pass
print('Part 3 appended')


class RelationshipEngine:
    _instance = None
    def __init__(self, config=None):
        self.config = config or _load_config()
        self._relationships = {}
        self._lookup = {}
        self.event_store = RelationshipEventStore.get_instance()
        self.state_machine = RelationshipStateMachine(self.config)
        self.rep_calc = RelationshipReputationCalculator(self.config)
    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def _make_key(self, a, b):
        return tuple(sorted([a, b]))
    def create_relationship(self, node_a_id, node_b_id, relationship_type='partnership', initiated_by=''):
        key = self._make_key(node_a_id, node_b_id)
        if key in self._lookup:
            return self._lookup[key]
        rel = Relationship(node_a_id=node_a_id, node_b_id=node_b_id, relationship_type=relationship_type, initiated_by=initiated_by, initiated_at=datetime.now(timezone.utc).isoformat())
        self._relationships[rel.relationship_id] = rel
        self._lookup[key] = rel
        return rel
    def get_relationship(self, node_a_id, node_b_id):
        key = self._make_key(node_a_id, node_b_id)
        return self._lookup.get(key)
    def get_relationship_by_id(self, relationship_id):
        return self._relationships.get(relationship_id)
    def get_node_relationships(self, node_id):
        results = []
        for key, rel in self._lookup.items():
            if node_id in key:
                results.append(rel)
        return results
    def transition(self, relationship_id, to_stage, event_type='', actor_id='', outcome_score=0.0):
        rel = self._relationships.get(relationship_id)
        if not rel:
            raise ValueError('Relationship not found: ' + relationship_id)
        event = self.state_machine.transition(rel, to_stage, event_type, actor_id)
        if outcome_score != 0:
            event.outcome_score = outcome_score
        self.event_store.append(event)
        self._update_reputation(rel)
        return event
    def record_event(self, relationship_id, event_type, actor_id='', description='', outcome_score=0.0):
        rel = self._relationships.get(relationship_id)
        if not rel:
            raise ValueError('Relationship not found: ' + relationship_id)
        event = RelationshipEvent(relationship_id=relationship_id, event_type=event_type, actor_id=actor_id, description=description, outcome_score=outcome_score)
        rel.last_activity_at = datetime.now(timezone.utc).isoformat()
        rel.total_interactions += 1
        self.event_store.append(event)
        self._update_reputation(rel)
        return event
    def _update_reputation(self, rel):
        events = self.event_store.get_events(rel.relationship_id)
        rep = self.rep_calc.calculate(rel.relationship_id, events)
        rel.relationship_trust = {
            'stability': rep.stability,
            'reciprocity': rep.reciprocity,
            'outcome': rep.outcome,
            'communication': rep.communication,
            'value_creation': rep.value_creation,
            'overall': rep.overall,
            'level': rep.level,
        }
        return rep
    def get_reputation(self, relationship_id):
        rel = self._relationships.get(relationship_id)
        if not rel: return None
        events = self.event_store.get_events(relationship_id)
        return self.rep_calc.calculate(relationship_id, events)
    def get_history(self, relationship_id):
        return [e.to_dict() for e in self.event_store.get_events(relationship_id)]
    def get_stage_summary(self, relationship_id):
        rel = self._relationships.get(relationship_id)
        if not rel: return None
        return {
            'relationship_id': rel.relationship_id,
            'node_a': rel.node_a_id, 'node_b': rel.node_b_id,
            'stage': rel.stage, 'previous_stage': rel.previous_stage,
            'type': rel.relationship_type,
            'trust': rel.relationship_trust,
            'projects': {'total': rel.total_projects, 'successful': rel.successful_projects},
            'interactions': rel.total_interactions,
            'duration_days': rel.duration_days,
            'created_at': rel.created_at,
        }
    @classmethod
    def reset(cls):
        cls._instance = None
        RelationshipEventStore.reset()
        RelationshipStateMachine.reset()
        RelationshipReputationCalculator.reset()

class UniverseEventBus:
    """Unified event bus. All Universe events (Node, Relationship, Knowledge) emit here.
    
    v1.0: Pass-through to existing event stores. Future: single unified store.
    """
    _instance = None
    
    def __init__(self):
        self._listeners = []
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    
    def emit(self, event_type, event_data):
        """Emit any Universe event. Subscribers receive all events."""
        payload = {'event_type': event_type, 'data': event_data,
                   'timestamp': datetime.now(timezone.utc).isoformat()}
        for listener in self._listeners:
            try: listener(payload)
            except: pass
        return payload
    
    def subscribe(self, callback):
        self._listeners.append(callback)
    
    @classmethod
    def reset(cls): cls._instance = None

@lru_cache()
def get_relationship_engine():
    return RelationshipEngine.get_instance()
