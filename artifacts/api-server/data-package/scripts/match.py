"""Explainable, deterministic demo. No LLM, real CV or hard-coded job rankings."""
import argparse
import math
from refresh import read, write, now

def clip(v,lo=0,hi=1):
    return max(lo,min(hi,v))

def rank(profile,scenario="moderate",neutral_trend=False,signals=None):
    if not profile.get("is_synthetic"):
        raise ValueError("This demo accepts synthetic profiles only.")
    signals=read("data/trend_signals.json")["signals"] if signals is None else signals
    signal_by={s["skill_id"]:s for s in signals}
    settings=next(s for s in read("data/scenarios.json") if s["scenario_id"]==scenario)
    w=settings["signal_weight"]
    max_jobs=max(((s.get("job_snapshot_count") or 0) for s in signals),default=0) or 1
    results=[]
    for role in read("data/roles.json"):
        breakdown=[]
        for required in role["required_skills"]:
            sid=required["skill_id"]
            have=profile["skill_levels"].get(sid)
            target=required["target_level"]
            breakdown.append(dict(skill_id=sid,current_level=have,target_level=target,
                gap=None if have is None else max(0,target-have),coverage=None if have is None else min(have/target,1),weight=required["weight"]))
        total=sum(x["weight"] for x in breakdown)
        fit=sum((x["coverage"] or 0)*x["weight"] for x in breakdown)/total
        unknown_weight=sum(x["weight"] for x in breakdown if x['current_level'] is None)/total
        components=[]
        for sid in role["trend_skill_ids"]:
            s=signal_by.get(sid,{})
            usable=s.get("research_status")=="usable"
            value=s.get("research_share_relative_change") if usable else None
            momentum=0.5 if neutral_trend or value is None else 0.5+clip(value,-1,1)/2
            jobs=s.get("job_snapshot_count")
            demand=jobs/max_jobs if jobs is not None else 0.5
            components.append(dict(skill_id=sid,research_momentum=momentum,
                research_momentum_method="0.5 + clip(relative_share_change, -1, 1)/2; missing/low-count data neutral at 0.5; no 0.35 floor",
                trend_indicator=s.get("trend_indicator","not_measured"),
                seasonality_adjusted=s.get("seasonality_adjusted",False),
                seasonality_note=s.get("seasonality_note"),
                job_sample_prevalence_normalised=demand,
                research_status=s.get("research_status","not_measured"),
                research_growth_pct=s.get("research_growth_pct"),
                source_urls=s.get("source_urls",[]),
                job_source="https://www.arbeitnow.com/api/job-board-api",
                research_retrieved_at=s.get("research_retrieved_at"),
                job_retrieved_at=s.get("job_retrieved_at")))
        momentum=sum(c["research_momentum"] for c in components)/len(components) if components else 0.5
        demand=sum(c["job_sample_prevalence_normalised"] for c in components)/len(components) if components else 0.5
        signal_score=0.7*momentum+0.3*demand
        score=100*((1-w)*fit+w*signal_score)
        results.append(dict(role_id=role["role_id"],title=role["title"],focus_label=role["focus_label"],
            score=round(score,3),skill_fit=round(100*fit,3),
            score_upper_bound=round(score+100*(1-w)*unknown_weight,3),
            assessment_coverage=round(100*(1-unknown_weight),3),
            unknown_skill_ids=[x['skill_id'] for x in breakdown if x['current_level'] is None],
            unmapped_requirements=role.get('unmapped_requirements',[]),
            taxonomy_mapping_note=role.get('taxonomy_mapping_note'),
            research_component=round(100*momentum,3),job_sample_component=round(100*demand,3),
            signal_weight=w,scenario=scenario,neutral_trend_ablation=neutral_trend,
            skills_gap=breakdown,signal_evidence=components,
            role_source=role["source_url"],sdg_mappings=role["sdg_mappings"],
            malaysia_reference_codes=role.get("malaysia_reference_codes",[]),
            malaysia_mapping_status=role.get("malaysia_mapping_status"),
            malaysia_mappings=role.get("malaysia_mappings",[]),
            is_mycol_critical=role.get("is_mycol_critical"),
            mycol_status=role.get("mycol_status"),
            mycol_status_scope=role.get("mycol_status_scope"),
            salary_range_myr=role.get("salary_range_myr"),
            score_semantics="Provisional lower-bound heuristic over mapped requirements. Unknown levels remain null; upper bound assumes unknown requirements met. NOT employment probability.",
            eligibility_note=role["readiness_note"]))
    results.sort(key=lambda r:(-r["score"],r["role_id"]))
    for i,r in enumerate(results,1):r["rank"]=i
    return results

def pathway(profile,role_id):
    role=next(r for r in read("data/roles.json") if r["role_id"]==role_id)
    courses={c["course_id"]:c for c in read("data/courses.json")}
    unknown=[r['skill_id'] for r in role['required_skills'] if profile['skill_levels'].get(r['skill_id']) is None]
    gaps={r["skill_id"]:r["target_level"]-profile["skill_levels"][r["skill_id"]]
          for r in role["required_skills"] if profile['skill_levels'].get(r['skill_id']) is not None and r["target_level"]>profile["skill_levels"][r["skill_id"]]}
    pending=set(gaps)
    selected=set()
    # Prefer broad coverage then lower stage. Hours are not evidence of skill mastery.
    eligible=[c for c in courses.values() if c.get("default_recommendation_eligible",False)]
    while pending:
        options=[c for c in eligible if set(c["skill_ids"]) & pending and c["course_id"] not in selected]
        if not options:break
        options.sort(key=lambda c:(-len(set(c["skill_ids"]) & pending),c["pathway_stage"],c["estimated_hours"],c["course_id"]))
        best=options[0];selected.add(best["course_id"]);pending-=set(best["skill_ids"])
    ordered=[]
    visiting=set()
    def visit(cid):
        if cid in ordered:return
        if cid in visiting:raise ValueError("Course prerequisite cycle")
        visiting.add(cid)
        for pre in courses[cid]["prerequisite_course_ids"]:visit(pre)
        visiting.remove(cid);ordered.append(cid)
    for cid in sorted(selected,key=lambda x:(courses[x]["pathway_stage"],x)):visit(cid)
    steps=[]
    hours=0
    for cid in ordered:
        c=courses[cid]
        hours+=c["estimated_hours"]
        steps.append(dict(step=len(steps)+1,course_id=cid,title=c["title"],url=c["url"],
            skill_ids=c["skill_ids"],addresses_gap_skill_ids=sorted(set(c["skill_ids"]) & set(gaps)),
            prerequisite_for_selected_course=cid not in selected,
            estimated_hours=c["estimated_hours"],duration_basis=c["duration_basis"],
            difficulty_level=c.get("difficulty_level"),
            difficulty_basis=c.get("difficulty_basis"),
            pathway_stage=c["pathway_stage"],
            pathway_stage_label=c.get("pathway_stage_label"),
            language_support=c.get("language_support",[]),
            subtitle_languages_verified=c.get("subtitle_languages_verified",[]),
            subtitle_verification_status=c.get("subtitle_verification_status"),
            resource_format=c.get("resource_format",[]),
            low_bandwidth_access=c.get("low_bandwidth_access"),
            recommended_preparation_course_ids=c.get("recommended_preparation_course_ids",[]),
            preparation_note=c.get("preparation_note"),
            cost_access=c["cost_access"],price_scope=c.get("price_scope"),
            completion_week=math.ceil(hours/profile["hours_per_week"]),
            practice_note="Use only synthetic projects. Demonstrate competence with an assessed portfolio task."))
    skill_by={s["skill_id"]:s for s in read("data/skills.json")}
    return dict(profile_id=profile["profile_id"],role_id=role_id,role_source=role["source_url"],
        steps=steps,estimated_course_hours=round(hours,2),
        estimated_course_weeks=math.ceil(hours/profile["hours_per_week"]),
        uncovered_skill_ids=sorted(pending),gaps=gaps,unknown_skill_ids=unknown,
        accessibility_note="Language and text-access metadata support user choice; current planner does not filter by language or guarantee offline labs.",
        gap_sdg_mappings={s:skill_by[s]["sdg_mappings"] for s in gaps},
        limitations="Introductory learning sequence only. Hours exclude substantial practice and prerequisites outside this catalogue. Courses do not automatically close proficiency gaps.")

def demo():
    reports=[]
    for p in read("data/synthetic_profiles.json"):
        for scenario in read("data/scenarios.json"):
            sid=scenario["scenario_id"]
            observed=rank(p,sid)
            neutral=rank(p,sid,True)
            base={r["role_id"]:r for r in neutral}
            changes=[dict(role_id=r["role_id"],neutral_rank=base[r["role_id"]]["rank"],observed_rank=r["rank"],
                neutral_score=base[r["role_id"]]["score"],observed_score=r["score"],
                delta=round(r["score"]-base[r["role_id"]]["score"],3)) for r in observed]
            reports.append(dict(profile_id=p["profile_id"],scenario=sid,ranked_roles=observed,
                neutral_ablation_comparison=changes,
                target_pathway=pathway(p,p["target_role_id"])))
    out=dict(computed_at=now(),experiment="Observed research momentum versus neutral-momentum ablation; job sample and profile held fixed.",
        warning="The neutral variant is a model ablation, not a second observed market snapshot.",
        results=reports)
    write("reports/matching_demo.json",out)
    return out

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--profile",default=None)
    ap.add_argument("--scenario",choices=["moderate","fast"],default="moderate")
    args=ap.parse_args()
    if args.profile:
        p=next(p for p in read("data/synthetic_profiles.json") if p["profile_id"]==args.profile)
        import json
        print(json.dumps({"roles":rank(p,args.scenario),"target_pathway":pathway(p,p["target_role_id"])},ensure_ascii=True,indent=2))
    else:
        out=demo()
        print("Saved reports/matching_demo.json;",len(out["results"]),"profile/scenario combinations.")
