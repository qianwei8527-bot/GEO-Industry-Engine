path = r'D:\GEO-Industry-Engine\backend\app\universe\relationship_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# ===== FIX 1: Add Relationship Identity fields =====
old = '''    relationship_type: str = 'partnership'
    stage: str = 'UNKNOWN'
    previous_stage: str = ''
    initiated_by: str = ''
    initiated_at: str = ''''''
    last_activity_at: str = ''''''
    stage_entered_at: str = ''''''
    created_at: str = ''''''
    relationship_trust: Dict = None'''
new = '''    relationship_type: str = 'partnership'
    stage: str = 'UNKNOWN'
    previous_stage: str = ''
    initiated_by: str = ''
    initiated_at: str = ''''''
    last_activity_at: str = ''''''
    stage_entered_at: str = ''''''
    created_at: str = ''''''
    purpose: str = ''
    industry: str = ''
    value_exchange: List = None
    relationship_trust: Dict = None'''
content = content.replace(old, new)

# Add value_exchange to __post_init__
old2 = '''if self.relationship_trust is None: self.relationship_trust = {'stability':0,'reciprocity':0,'outcome':0,'communication':0,'overall':0,'level':'N/A'}
        if self.metadata is None: self.metadata = {}'''
new2 = '''if self.relationship_trust is None: self.relationship_trust = {'stability':0,'reciprocity':0,'outcome':0,'communication':0,'value_creation':0,'overall':0,'level':'N/A'}
        if self.value_exchange is None: self.value_exchange = []
        if self.metadata is None: self.metadata = {}'''
content = content.replace(old2, new2)

# Update to_dict in Relationship
old3 = '''return {'relationship_id':self.relationship_id,'node_a_id':self.node_a_id,'node_b_id':self.node_b_id,'relationship_type':self.relationship_type,'stage':self.stage,'previous_stage':self.previous_stage,'relationship_trust':self.relationship_trust'''
new3 = '''return {'relationship_id':self.relationship_id,'node_a_id':self.node_a_id,'node_b_id':self.node_b_id,'relationship_type':self.relationship_type,'stage':self.stage,'previous_stage':self.previous_stage,'purpose':self.purpose,'industry':self.industry,'value_exchange':self.value_exchange,'relationship_trust':self.relationship_trust'''
content = content.replace(old3, new3)

# ===== FIX 2: Add Value Creation as 5th dimension =====
# Update _default_config reputation_dimensions
old4 = '''        'reputation_dimensions': [
            {'id':'stability','label':'Stability','weight':0.30},
            {'id':'reciprocity','label':'Reciprocity','weight':0.25},
            {'id':'outcome','label':'Outcome','weight':0.30},
            {'id':'communication','label':'Communication','weight':0.15},
        ],'''
new4 = '''        'reputation_dimensions': [
            {'id':'stability','label':'Stability','weight':0.20},
            {'id':'reciprocity','label':'Reciprocity','weight':0.20},
            {'id':'outcome','label':'Outcome','weight':0.25},
            {'id':'communication','label':'Communication','weight':0.10},
            {'id':'value_creation','label':'Value Creation','weight':0.25},
        ],'''
content = content.replace(old4, new4)

# Update RelationshipReputation dataclass to include value_creation
old5 = '''    communication: float = 0.0
    overall: float = 0.0'''
new5 = '''    communication: float = 0.0
    value_creation: float = 0.0
    overall: float = 0.0'''
content = content.replace(old5, new5)

# Update RelationshipReputation.to_dict
old6 = '''return {'relationship_id':self.relationship_id,'dimensions':{'stability':round(self.stability,1),'reciprocity':round(self.reciprocity,1),'outcome':round(self.outcome,1),'communication':round(self.communication,1)},'overall':round(self.overall,1),'level':self.level,'events_count':self.events_count}'''
new6 = '''return {'relationship_id':self.relationship_id,'dimensions':{'stability':round(self.stability,1),'reciprocity':round(self.reciprocity,1),'outcome':round(self.outcome,1),'communication':round(self.communication,1),'value_creation':round(self.value_creation,1)},'overall':round(self.overall,1),'level':self.level,'events_count':self.events_count}'''
content = content.replace(old6, new6)

# Update Calculator to include value_creation in scores
old7 = '''        scores = {'stability':stability,'reciprocity':reciprocity,
                  'outcome':outcome,'communication':comm}'''
new7 = '''        # Value Creation: derived from outcome success rate x reciprocity
        vc = min(100, (outcome * 0.6 + reciprocity * 0.4))
        scores = {'stability':stability,'reciprocity':reciprocity,
                  'outcome':outcome,'communication':comm,'value_creation':vc}'''
content = content.replace(old7, new7)

old8 = '''            stability=stability, reciprocity=reciprocity,
            outcome=outcome, communication=comm,'''
new8 = '''            stability=stability, reciprocity=reciprocity,
            outcome=outcome, communication=comm,
            value_creation=vc,'''
content = content.replace(old8, new8)

# Update _update_reputation to include value_creation
old9 = '''            'outcome': rep.outcome,
            'communication': rep.communication,'''
new9 = '''            'outcome': rep.outcome,
            'communication': rep.communication,
            'value_creation': rep.value_creation,'''
content = content.replace(old9, new9)

# ===== FIX 3: Add UniverseEventBus interface =====
# Append after the singleton accessor
old10 = '''@lru_cache()
def get_relationship_engine():
    return RelationshipEngine.get_instance()'''
new10 = '''class UniverseEventBus:
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
    return RelationshipEngine.get_instance()'''
content = content.replace(old10, new10)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('All 3 fixes applied')
