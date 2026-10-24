"""Original five synthetic scenarios, isolated from both newer skill taxonomies."""
import copy,hashlib,importlib.util,json,math
from pathlib import Path
from types import FunctionType
from typing import Literal
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,ConfigDict,Field
ROOT=Path(__file__).resolve().parents[1]/'legacy-package'
router=APIRouter(prefix='/api/legacy')
spec=importlib.util.spec_from_file_location('legacy_engine',ROOT.parent/'data-package/scripts/match.py');engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
def values():return {'data/'+p.name:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'data').glob('*.json')}
def bound(fn,data):return FunctionType(fn.__code__,{**fn.__globals__,'read':lambda name:data[name]},fn.__name__,fn.__defaults__)
def metadata(v):
    research=v['data/research_counts.json'];signals=v['data/trend_signals.json']
    return {'snapshot_id':hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()[:12],'mode':'archived_legacy_taxonomy','model':'Original deterministic trend-weighted ranking','research_retrieved_at':research.get('retrieved_at'),'jobs_retrieved_at':next((r.get('job_retrieved_at') for r in signals['signals']),None),'signals_computed_at':signals.get('computed_at'),'job_sample_size':max((r.get('job_sample_size',0) for r in signals['signals']),default=0),'research_windows':{p:{k:research['denominator'][p][k] for k in ('window_start','window_end_exclusive','total_results')} for p in ('previous','current')},'research_scope':'Archived global research counts','jobs_scope':'Archived Europe-oriented Arbeitnow sample','taxonomy_note':'Original five scenarios, historical 20-topic taxonomy. No conversion to leaf-80-v1.'}
@router.get('/bootstrap')
def bootstrap():
    v=values();return {'profiles':v['data/synthetic_profiles.json'],'skills':v['data/skills.json'],'roles':v['data/roles.json'],'scenarios':v['data/scenarios.json'],'signals':v['data/trend_signals.json']['signals'],'sources':v['data/source_registry.json'],'metadata':metadata(v)}
class Body(BaseModel):
    model_config=ConfigDict(extra='forbid')
    profile_id:str=Field(max_length=80)
    scenario:Literal['moderate','fast']='moderate'
    hours_per_week:int|None=Field(default=None,ge=1,le=40,strict=True)
@router.post('/match')
def match(body:Body):
    v=values();p=next((copy.deepcopy(p) for p in v['data/synthetic_profiles.json'] if p['profile_id']==body.profile_id),None)
    if p is None or p.get('is_synthetic') is not True:raise HTTPException(422,'Choose an original synthetic scenario.')
    if body.hours_per_week is not None:p['hours_per_week']=body.hours_per_week
    rank=bound(engine.rank,v);pathway=bound(engine.pathway,v);roles=rank(p,body.scenario);neutral={r['role_id']:r for r in rank(p,body.scenario,neutral_trend=True)};paths={};courses={c['course_id']:c for c in v['data/courses.json']}
    for r in roles:
        n=neutral[r['role_id']];r['comparison']={'neutral_rank':n['rank'],'neutral_score':n['score'],'rank_change':n['rank']-r['rank'],'score_change':round(r['score']-n['score'],3)}
        path=pathway(p,r['role_id'])
        for step in path['steps']:step.update({k:courses[step['course_id']].get(k) for k in ['provider','prerequisite_course_ids','checked_at','extra_cost_note']})
        paths[r['role_id']]=path
    return {'profile':p,'scenario':body.scenario,'roles':roles,'pathways':paths,'metadata':metadata(v)}
