"""Versioned skill normalization and evidence-linked dictionary candidate extraction."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]/'data-package'
CATALOG=json.loads((ROOT/'data/skill_dictionary.json').read_text(encoding='utf-8'))
CATALOG_HASH=hashlib.sha256(json.dumps(CATALOG,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
IDS=[s['skill_id'] for s in CATALOG['skills']]
DEMOS=json.loads((ROOT/'data/demo_profiles.json').read_text(encoding='utf-8'))

def alias_pattern(alias):
    # Unicode word boundaries avoid ML inside HTML; allow Chinese-adjacent terms.
    escaped=re.escape(alias).replace(r'\ ',r'\s+')
    return re.compile(r'(?<![A-Za-z0-9_])'+escaped+r'(?![A-Za-z0-9_])', re.I)

PATTERNS={s['skill_id']:[(alias,alias_pattern(alias)) for alias in s['aliases']] for s in CATALOG['skills']}
NEGATION=re.compile(r'(?:\bno(?:\s+\w+){0,3}|\bnot(?:\s+\w+){0,3}|\bwithout(?:\s+\w+){0,2}|\bnever(?:\s+\w+){0,3}|不熟悉|不会|未掌握|没有.{0,8}经验|无.{0,8}经验)\s*$',re.I)
LEARNING=re.compile(r'(?:\blearning|\bstudying|\blearn|\binterested\s+in|\bplan\s+to\s+learn|正在学习|计划学习|想学习|希望学习)\s*$',re.I)

def candidates(pages):
    found=[]
    for skill in CATALOG['skills']:
        evidence=[]; seen=set()
        for page_no,text in enumerate(pages,1):
            for alias,pattern in PATTERNS[skill['skill_id']]:
                for m in pattern.finditer(text):
                    if alias=='机器人' and text[m.end():].startswith('流程自动化'):continue
                    # Unique occurrence offsets; cap each skill's response size.
                    if any(start<=m.start()<end for pn,start,end in seen if pn==page_no):continue
                    before=text[max(0,m.start()-60):m.start()]
                    kind='negated' if NEGATION.search(before) else 'learning' if LEARNING.search(before) else 'mention'
                    evidence.append(dict(page=page_no,start=m.start(),end=m.end(),matched_text=m.group(),alias=alias,
                        snippet=text[max(0,m.start()-55):min(len(text),m.end()+85)].strip(),mention_type=kind))
                    seen.add((page_no,m.start(),m.end()))
                    if len(evidence)>=5:break
                if len(evidence)>=5:break
            if len(evidence)>=5:break
        if evidence:
            found.append(dict(skill_id=skill['skill_id'],name_zh=skill['name_zh'],level=None,confirmed=False,evidence=evidence))
    return found

def normalize(rows):
    supplied={r['skill_id']:r for r in rows}
    skills=[supplied.get(sid,dict(skill_id=sid,level=None,source='unknown',confirmed=False,evidence=[])) for sid in IDS]
    levels=[r['level'] for r in skills]
    # None is deliberately preserved. Consumers must respect the mask.
    return dict(skills=skills,vectors=dict(skill_ids=IDS,levels=levels,
        known_mask=[v is not None for v in levels],
        binary_presence=[None if v is None else int(v>=1) for v in levels],
        binary_thresholds=[None if v is None else int(v>=t) for v in levels for t in (1,2,3)],
        threshold_feature_ids=[f'{sid}:ge{t}' for sid in IDS for t in (1,2,3)],
        semantics='Self-confirmed evidence, not externally assessed proficiency. null = unknown; 0 = explicitly not mastered.'))
