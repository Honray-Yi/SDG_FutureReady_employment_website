"""Offline validation for the authoritative Module 1 taxonomy."""
import hashlib, json
from refresh import read, write, now
from match import rank, pathway, demo

def check():
    checks=[]
    def ok(value,name):
        if not value:raise AssertionError(name)
        checks.append(name)
    catalog=read('data/skill_dictionary.json');skills=read('data/skills.json')
    ids=[s['skill_id'] for s in catalog['skills']];known=set(ids)
    ok(len(ids)==len(known)==20,'20 canonical dimensions')
    ok([s['skill_id'] for s in skills]==ids,'Canonical ordering')
    for c,s in zip(catalog['skills'],skills):ok(all(s[k]==v for k,v in c.items()),'Definition '+c['skill_id'])
    roles=read('data/roles.json');courses=read('data/courses.json');profiles=read('data/synthetic_profiles.json')
    course_by={c['course_id']:c for c in courses}
    ok(len(roles)==12 and len(courses)==22,'12 roles and 22 resources')
    for r in roles:
        ok(bool(r['required_skills']) and all(s['skill_id'] in known for s in r['required_skills']),'Role '+r['role_id'])
        ok(set(r['trend_skill_ids'])<=known,'Trend '+r['role_id'])
    for c in courses:ok(set(c['skill_ids'])<=known and set(c['prerequisite_course_ids'])<=set(course_by),'Course '+c['course_id'])
    ok([s['skill_id'] for s in read('data/trend_signals.json')['signals']]==ids,'Signals order')
    for r in read('data/research_counts.json')['records']:ok(r['skill_id'] in known,'Research '+r['skill_id'])
    for j in read('data/jobs_snapshot.json')['records']:ok(set(j['skill_matches'])<=known,'Job '+j['job_id'])
    ok(len(profiles)==3,'Three Module 1 demos')
    for p in profiles:
        ok(p['is_synthetic'] is True and set(p['skill_levels'])==known,'Profile '+p['profile_id'])
        ok(all(v is None or type(v) is int and 0<=v<=3 for v in p['skill_levels'].values()),'Nullable levels '+p['profile_id'])
        for scenario in ('moderate','fast'):
            ranked=rank(p,scenario);ok(len(ranked)==12,'Rank completeness')
            for r in ranked:
                ok(0<=r['score']<=r['score_upper_bound']<=100,'Score interval '+r['role_id'])
                plan=pathway(p,r['role_id']);seen=set()
                ok(not(set(plan['unknown_skill_ids'])&set(plan['gaps'])),'Unknown is not gap')
                for step in plan['steps']:
                    c=course_by[step['course_id']];ok(set(c['prerequisite_course_ids'])<=seen,'Prerequisites '+c['course_id']);seen.add(c['course_id'])
    report={'checked_at':now(),'schema_version':'module1-aligned-1.0','status':'passed','checks_passed':len(checks),'checks':checks,'dictionary_hash':hashlib.sha256(json.dumps(catalog,sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
    write('reports/validation.json',report);demo();return report
if __name__=='__main__':print('PASS',check()['checks_passed'],'checks')
