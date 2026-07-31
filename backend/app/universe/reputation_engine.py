# GEO Universe Reputation Engine
# Phase C5.1 - Trust Physics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from functools import lru_cache
import uuid, math, os as _os, yaml

_loaded_config = None
def _load_config():
    global _loaded_config
    if _loaded_config: return _loaded_config
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))), 'config', 'universe', 'reputation.yaml')
    _loaded_config = yaml.safe_load(open(p, encoding='utf-8')) if _os.path.exists(p) else {}
    return _loaded_config

@dataclass
class ReputationEvent:
    event_id: str = ''
    node_id: str = ''
    node_type: str = ''
    event_type: str = ''
    dimension: str = ''
    impact: str = 'positive'
    base_weight: float = 0.0
    evidence_weight: float = 1.0
    source_type: str = 'self_report'
    source_id: str = ''
    source_weight: float = 0.3
    effective_weight: float = 0.0
    evidence_refs: List[str] = None
    description: str = ''
    timestamp: str = ''
    recorded_at: str = ''

    def __post_init__(self):
        if not self.event_id: self.event_id = str(uuid.uuid4())[:8]
        if not self.timestamp: self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.recorded_at: self.recorded_at = datetime.now(timezone.utc).isoformat()
        if self.evidence_refs is None: self.evidence_refs = []
        if self.effective_weight == 0.0:
            sign = -1 if self.impact == 'negative' else 1
            self.effective_weight = round(sign * self.base_weight * max(self.evidence_weight, 0.1) * max(self.source_weight, 0.1), 2)

    def to_dict(self):
        return {k: getattr(self, k) for k in ['event_id','node_id','node_type','event_type','dimension','impact','effective_weight','source_type','source_weight','description','timestamp']}

    @classmethod
    def from_external(cls, node_id, node_type, event_type, description, source_type='self_report', source_id='', evidence_refs=None, config=None):
        cfg = config or _load_config()
        ec = cfg.get('event_types',{}).get(event_type,{})
        dim = ec.get('dimension','capability')
        imp = ec.get('impact','positive')
        bw = abs(ec.get('base_weight',5.0))
        sw = cfg.get('source_reliability',{}).get(source_type,0.3)
        ew = cfg.get('evidence_weights',{}).get(event_type,0.7)
        return cls(node_id=node_id,node_type=node_type,event_type=event_type,dimension=dim,impact=imp,base_weight=bw,evidence_weight=ew,source_type=source_type,source_id=source_id,source_weight=sw,evidence_refs=evidence_refs or [],description=description)
print('Part 1 OK')


@dataclass
class DimensionScore:
    dimension: str = ''
    score: float = 0.0
    level: str = 'N/A'
    event_count: int = 0
    contributing_event_ids: List[str] = None
    last_updated: str = ''
    def __post_init__(self):
        if self.contributing_event_ids is None: self.contributing_event_ids = []
    def to_dict(self):
        return {'dimension':self.dimension,'score':round(self.score,1),'level':self.level,'event_count':self.event_count,'contributing_events':self.contributing_event_ids,'last_updated':self.last_updated}

@dataclass
class ReputationSnapshot:
    snapshot_id: str = ''
    node_id: str = ''
    node_type: str = ''
    algorithm_version: str = '1.0'
    dimensions: Dict = None
    overall_score: float = 0.0
    overall_level: str = 'N/A'
    status: str = 'UNKNOWN'
    trend: str = 'stable'
    trend_momentum: float = 0.0
    computed_at: str = ''
    event_range_start: str = ''
    event_range_end: str = ''
    total_events: int = 0
    is_current: bool = True
    def __post_init__(self):
        if not self.snapshot_id: self.snapshot_id = str(uuid.uuid4())[:8]
        if not self.computed_at: self.computed_at = datetime.now(timezone.utc).isoformat()
        if self.dimensions is None: self.dimensions = {}
    def to_dict(self):
        return {'snapshot_id':self.snapshot_id,'node_id':self.node_id,'node_type':self.node_type,'algorithm_version':self.algorithm_version,'status':self.status,'overall_score':round(self.overall_score,1),'overall_level':self.overall_level,'trend':self.trend,'trend_momentum':round(self.trend_momentum,2),'dimensions':{k:v.to_dict() for k,v in self.dimensions.items()},'computed_at':self.computed_at,'total_events':self.total_events,'is_current':self.is_current}

@dataclass
class ReputationExplanation:
    node_id: str = ''
    status: str = 'UNKNOWN'
    overall_score: float = 0.0
    overall_level: str = 'N/A'
    summary: str = ''
    dimensions: Dict = None
    trajectory: List = None
    risk_signals: List = None
    recommendations: List = None
    generated_at: str = ''
    def __post_init__(self):
        if self.dimensions is None: self.dimensions = {}
        if self.trajectory is None: self.trajectory = []
        if self.risk_signals is None: self.risk_signals = []
        if self.recommendations is None: self.recommendations = []
        if not self.generated_at: self.generated_at = datetime.now(timezone.utc).isoformat()
    def to_dict(self):
        return {'node_id':self.node_id,'overview':{'status':self.status,'status_label':self.status,'level':self.overall_level,'summary':self.summary},'dimension_breakdown':self.dimensions,'trajectory':self.trajectory,'risk_signals':self.risk_signals,'recommendations':self.recommendations,'generated_at':self.generated_at}
print('Part 2 appended')


class EventStore:
    _instance = None
    def __init__(self):
        self._events = {}
    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def append(self, event):
        self._events.setdefault(event.node_id, []).append(event)
        return event
    def get_events(self, node_id, since=None, dimensions=None):
        events = self._events.get(node_id, [])
        if since: events = [e for e in events if e.timestamp >= since]
        if dimensions: events = [e for e in events if e.dimension in dimensions]
        return sorted(events, key=lambda e: e.timestamp)
    def get_event_count(self, node_id, dimension=None):
        events = self._events.get(node_id,[])
        if dimension: events = [e for e in events if e.dimension == dimension]
        return len(events)
    def get_all_node_ids(self):
        return list(self._events.keys())
    @classmethod
    def reset(cls): cls._instance = None

class ReputationCalculator:
    def __init__(self, config=None):
        self.config = config or _load_config()
        self._event_store = EventStore.get_instance()
    def _calculate_decay(self, event, now):
        cfg = self.config.get('time_decay',{})
        ed = cfg.get(event.event_type, cfg.get('project_success',{'half_life_days':365}))
        hl = ed.get('half_life_days', 365)
        try:
            et = datetime.fromisoformat(event.timestamp.replace('Z','+00:00'))
            if et.tzinfo is None: et = et.replace(tzinfo=timezone.utc)
            if now.tzinfo is None: now = now.replace(tzinfo=timezone.utc)
            age = max(0, (now - et).days)
            if age <= 0: return 1.0
            return math.exp(-math.log(2) / hl * age)
        except: return 1.0
    def _score_to_level(self, score):
        th = self.config.get('level_thresholds',{})
        for lvl, t in sorted(th.items(), key=lambda x: x[1], reverse=True):
            if score >= t:
                return lvl.replace('_plus','+').replace('_minus','-').upper()
        return 'N/A'
    def calculate_dimension(self, node_id, dimension_id, events=None):
        if events is None: events = self._event_store.get_events(node_id, dimensions=[dimension_id])
        if not events: return DimensionScore(dimension=dimension_id, score=0.0, level='N/A')
        total = 0.0; cids = []; now = datetime.now(timezone.utc)
        for e in events:
            d = self._calculate_decay(e, now)
            w = e.effective_weight * d
            total += w
            if e.impact != 'neutral': cids.append(e.event_id)
        score = max(0.0, min(100.0, total))
        return DimensionScore(dimension=dimension_id, score=round(score,1), level=self._score_to_level(score), event_count=len(events), contributing_event_ids=cids[-5:], last_updated=events[-1].timestamp if events else '')
    def calculate_all_dimensions(self, node_id):
        all_ev = self._event_store.get_events(node_id)
        res = {}
        for dc in self.config.get('dimensions',[]):
            did = dc['id']
            res[did] = self.calculate_dimension(node_id, did, [e for e in all_ev if e.dimension == did])
        return res
    def calculate_overall(self, dims):
        total = 0.0
        dcfg = {d['id']:d for d in self.config.get('dimensions',[])}
        active = 0.0
        for did, ds in dims.items():
            w = dcfg.get(did,{}).get('aggregation_weight',0.10)
            if ds.level != 'N/A':
                total += ds.score * w
                active += w
        overall = total / max(active, 0.01)
        overall = max(0.0, min(100.0, overall))
        return round(overall,1), self._score_to_level(overall)
    def determine_status(self, dims, overall):
        te = sum(ds.event_count for ds in dims.values())
        levels = self.config.get('reputation_status',{}).get('levels',[])
        for lc in sorted(levels, key=lambda x: x.get('min_overall',0), reverse=True):
            if te >= lc.get('min_events',0) and overall >= lc.get('min_overall',0):
                return lc['id']
        return 'UNKNOWN'
    def calculate_trend(self, node_id, dims):
        events = self._event_store.get_events(node_id)
        if len(events) < 2: return 'stable', 0.0
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(days=90)).isoformat()
        recent = [e for e in events if e.timestamp >= cutoff]
        older = [e for e in events if e.timestamp < cutoff]
        rw = sum(e.effective_weight for e in recent) if recent else 0
        ow = sum(e.effective_weight for e in older) if older else 0.01
        m = (rw - ow) / max(abs(ow), 1.0)
        m = max(-1.0, min(1.0, m))
        if m > 0.15: return 'rising', round(m,2)
        elif m < -0.15: return 'declining', round(m,2)
        return 'stable', round(m,2)
    @classmethod
    def reset(cls): pass
print('Part 3 appended')


class SnapshotManager:
    _instance = None
    def __init__(self, config=None):
        self.config = config or _load_config()
        self._snapshots = {}
        self._idx = {}
    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def create_snapshot(self, node_id, node_type, dimensions, overall_score, overall_level, status, trend, trend_momentum, total_events, event_range_start='', event_range_end=''):
        existing = self._snapshots.get(node_id, [])
        for s in existing: s.is_current = False
        av = self.config.get('snapshot',{}).get('algorithm_version','1.0')
        snap = ReputationSnapshot(node_id=node_id, node_type=node_type, algorithm_version=av, dimensions=dimensions, overall_score=overall_score, overall_level=overall_level, status=status, trend=trend, trend_momentum=trend_momentum, event_range_start=event_range_start, event_range_end=event_range_end, total_events=total_events, is_current=True)
        self._snapshots.setdefault(node_id, []).append(snap)
        self._idx[snap.snapshot_id] = snap
        return snap
    def get_current_snapshot(self, node_id):
        for s in reversed(self._snapshots.get(node_id, [])):
            if s.is_current: return s
        return None
    def archive_all(self, node_id):
        for snap in self._snapshots.get(node_id, []):
            snap.is_current = False

    def get_snapshot_history(self, node_id):
        return list(reversed(self._snapshots.get(node_id, [])))
    @classmethod
    def reset(cls): cls._instance = None

class ExplanationBuilder:
    def __init__(self, config=None):
        self.config = config or _load_config()
        self._event_store = EventStore.get_instance()
        self._snapshot_manager = SnapshotManager.get_instance()
    def build(self, node_id, snapshot=None):
        if snapshot is None: snapshot = self._snapshot_manager.get_current_snapshot(node_id)
        if snapshot is None: return ReputationExplanation(node_id=node_id, status='UNKNOWN', summary='No reputation data.')
        dim_breakdown = {}
        events = self._event_store.get_events(node_id)
        dcfg = {d['id']:d for d in self.config.get('dimensions',[])}
        for did, ds in snapshot.dimensions.items():
            de = sorted([e for e in events if e.dimension == did and e.impact != 'neutral'], key=lambda e: abs(e.effective_weight), reverse=True)
            dc = dcfg.get(did, {})
            dim_breakdown[did] = {
                'score': ds.score, 'level': ds.level, 'label': dc.get('label',did), 'label_en': dc.get('label_en',did),
                'top_contributors': [{'event_id':e.event_id,'description':e.description,'impact':('+' if e.impact=='positive' else '')+str(int(e.effective_weight)),'date':e.timestamp[:10] if e.timestamp else ''} for e in de[:3]],
                'risk_flags': self._dim_risks(ds, de),
            }
        trajectory = [{'date':e.timestamp[:10] if e.timestamp else '','event':e.description,'change':('+' if e.impact=='positive' else '')+str(int(e.effective_weight))} for e in sorted(events, key=lambda x: x.timestamp)[-10:]]
        risks = self._detect_risks(node_id, snapshot, events)
        recs = self._gen_recs(snapshot)
        summary = self._build_summary(snapshot, risks)
        return ReputationExplanation(node_id=node_id, status=snapshot.status, overall_score=snapshot.overall_score, overall_level=snapshot.overall_level, summary=summary, dimensions=dim_breakdown, trajectory=trajectory, risk_signals=risks, recommendations=recs)
    def _build_summary(self, snap, risks):
        dcfg = {d['id']:d for d in self.config.get('dimensions',[])}
        strong = []; weak = []
        for did, ds in snap.dimensions.items():
            lb = dcfg.get(did,{}).get('label',did)
            if ds.level in ('A+','A','A-'): strong.append(lb)
            elif ds.level in ('C','D','E','N/A'): weak.append(lb)
        p = []
        if strong: p.append(','.join(strong[:2])+chr(34920)+chr(29616)+chr(20248)+chr(31168))
        if weak: p.append(','.join(weak[:2])+chr(26377)+chr(24453)+chr(25552)+chr(21319))
        if snap.trend == 'rising': p.append(chr(36235)+chr(21183)+chr(19978)+chr(21319))
        elif snap.trend == 'declining': p.append(chr(36235)+chr(21183)+chr(19979)+chr(38477))
        return chr(12290).join(p) if p else chr(25968)+chr(25454)+chr(31215)+chr(32047)+chr(20013)
    def _detect_risks(self, node_id, snap, events):
        risks = []
        recent = [e for e in events if e.timestamp >= (datetime.now(timezone.utc)-timedelta(days=180)).isoformat()]
        if not recent and events: risks.append({'signal':chr(36817)+' 180 '+chr(22825)+chr(32570)+chr(23569)+chr(26032)+chr(35777)+chr(25454),'severity':'medium'})
        if snap.trend == 'declining': risks.append({'signal':chr(20449)+chr(35465)+chr(36235)+chr(21183)+chr(19979)+chr(38477),'severity':'high' if snap.trend_momentum < -0.3 else 'medium'})
        return risks
    def _dim_risks(self, ds, events):
        f = []
        if ds.level == 'N/A': f.append(chr(35813)+chr(32500)+chr(24230)+chr(26242)+chr(26080)+chr(25968)+chr(25454))
        if ds.event_count > 0 and ds.level in ('D','E'): f.append(chr(35813)+chr(32500)+chr(24230)+chr(20449)+chr(35465)+chr(20559)+chr(20302))
        return f
    def _gen_recs(self, snap):
        recs = []
        dcfg = {d['id']:d for d in self.config.get('dimensions',[])}
        for did, ds in snap.dimensions.items():
            lb = dcfg.get(did,{}).get('label',did)
            if ds.level in ('N/A','D','E'): recs.append({'action':chr(24314)+chr(35758)+chr(34917)+chr(51473)+' '+lb+chr(30456)+chr(20851)+chr(35777)+chr(25454),'target_dimension':did})
        return recs
    @classmethod
    def reset(cls): pass
print('Part 4-5 appended')


class TrustPropagator:
    def __init__(self, config=None):
        self.config = config or _load_config()
        self._pc = self.config.get('trust_propagation',{})
    @property
    def enabled(self):
        return self._pc.get('enabled', False)
    def propagate(self, src_id, tgt_id, src_snap, tgt_snap, rel_strength=0.5):
        if not self.enabled: return None
        if rel_strength < self._pc.get('min_relationship_strength',0.3): return None
        damp = self._pc.get('damping_factor',0.5)
        allowed = self._pc.get('allowed_transfers',{})
        adj = {}
        for did, ds in src_snap.dimensions.items():
            if ds.level == 'N/A': continue
            for td in allowed.get(did,[]):
                adj[td] = ds.score * rel_strength * damp * 0.1
        return adj if adj else None
    @classmethod
    def reset(cls): pass

class ReputationEngine:
    _instance = None
    def __init__(self, config=None):
        self.config = config or _load_config()
        self.event_store = EventStore.get_instance()
        self.calculator = ReputationCalculator(self.config)
        self.snapshot_manager = SnapshotManager.get_instance()
        self.explanation_builder = ExplanationBuilder(self.config)
        self.trust_propagator = TrustPropagator(self.config)
    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def record_event(self, node_id, node_type, event_type, description, source_type='self_report', source_id='', evidence_refs=None, timestamp=None):
        event = ReputationEvent.from_external(node_id, node_type, event_type, description, source_type, source_id, evidence_refs, self.config)
        if timestamp: event.timestamp = timestamp
        self.event_store.append(event)
        return event
    def get_profile(self, node_id):
        snap = self.snapshot_manager.get_current_snapshot(node_id)
        return snap if snap else self.recalculate(node_id)
    def get_explanation(self, node_id):
        return self.explanation_builder.build(node_id, self.get_profile(node_id))
    def recalculate(self, node_id, node_type='company'):
        events = self.event_store.get_events(node_id)
        if not events:
            dims = {}
            for dc in self.config.get('dimensions',[]):
                dims[dc['id']] = DimensionScore(dimension=dc['id'], score=0.0, level='N/A')
            return self.snapshot_manager.create_snapshot(node_id=node_id, node_type=node_type, dimensions=dims, overall_score=0.0, overall_level='N/A', status='UNKNOWN', trend='stable', trend_momentum=0.0, total_events=0)
        dims = self.calculator.calculate_all_dimensions(node_id)
        overall, level = self.calculator.calculate_overall(dims)
        status = self.calculator.determine_status(dims, overall)
        trend, momentum = self.calculator.calculate_trend(node_id, dims)
        return self.snapshot_manager.create_snapshot(node_id=node_id, node_type=node_type, dimensions=dims, overall_score=overall, overall_level=level, status=status, trend=trend, trend_momentum=momentum, total_events=len(events), event_range_start=events[0].timestamp if events else '', event_range_end=events[-1].timestamp if events else '')
    def get_history(self, node_id):
        return [e.to_dict() for e in self.event_store.get_events(node_id)]
    def archive_all(self, node_id):
        for snap in self._snapshots.get(node_id, []):
            snap.is_current = False

    def get_snapshot_history(self, node_id):
        return [s.to_dict() for s in self.snapshot_manager.get_snapshot_history(node_id)]
    def get_reputation_for_connection(self, node_ids):
        return {nid: self.get_profile(nid) for nid in node_ids}
    def propagate_trust(self, src, tgt, strength=0.5):
        if not self.trust_propagator.enabled: return None
        return self.trust_propagator.propagate(src, tgt, self.get_profile(src), self.get_profile(tgt), strength)
    def seed_sample_data(self, node_id='comp-seed', node_type='company'):
        samples = [
            ('certification_passed', chr(33719)+chr(24471)+' ISO 9001 '+chr(35748)+chr(35777), 'government'),
            ('customer_success', chr(23436)+chr(25104)+' GEO '+chr(20248)+chr(21270)+chr(39033)+chr(30446)+chr(20132)+chr(20184), 'enterprise_customer'),
            ('customer_success', chr(23436)+chr(25104)+' AI '+chr(20869)+chr(23481)+chr(31574)+chr(30053)+chr(21672)+chr(35810), 'enterprise_customer'),
            ('peer_endorsement', chr(33719)+chr(34892)+chr(19994)+chr(21516)+chr(34892)+chr(25512)+chr(33616), 'partner'),
            ('innovation_release', chr(21457)+chr(24067)+' AI Agent '+chr(33258)+chr(21160)+chr(26816)+chr(27979)+chr(24037)+chr(20855), 'self_report'),
            ('industry_citation', chr(34987)+chr(34892)+chr(19994)+chr(30333)+chr(30382)+chr(20070)+chr(24341)+chr(29992), 'association'),
            ('compliance_audit_passed', chr(36890)+chr(36807)+chr(24180)+chr(24230)+chr(21512)+chr(35268)+chr(23457)+chr(26597), 'government'),
            ('negative_feedback', chr(19968)+chr(27425)+chr(39033)+chr(30446)+chr(24310)+chr(26399)+chr(20132)+chr(20184)+chr(65288)+chr(24050)+chr(34917)+chr(25937)+chr(65289), 'enterprise_customer'),
            ('relationship_strengthened', chr(19982)+chr(25112)+chr(30053)+chr(20249)+chr(20276)+chr(32493)+chr(32422)+' 2 '+chr(24180), 'partner'),
            ('ai_agent_cited', chr(34987)+chr(22810)+chr(20010)+' AI Agent '+chr(25512)+chr(33616)+chr(24341)+chr(29992), 'ai_observation'),
        ]
        bt = datetime.now(timezone.utc) - timedelta(days=365)
        for i, (et, desc, st) in enumerate(samples):
            ts = (bt + timedelta(days=i*35)).isoformat()
            self.record_event(node_id=node_id, node_type=node_type, event_type=et, description=desc, source_type=st, timestamp=ts)
        return self.recalculate(node_id, node_type)
    @classmethod
    def reset(cls):
        cls._instance = None
        EventStore.reset()
        SnapshotManager.reset()
        ReputationCalculator.reset()
        ExplanationBuilder.reset()
        TrustPropagator.reset()

@lru_cache()
def get_reputation_engine():
    return ReputationEngine.get_instance()
print('Part 6-7 complete')
