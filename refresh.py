"""Fetch public data; keep successful caches on failure. Python 3.10+, standard library."""
import argparse
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
NS = {"a":"http://www.w3.org/2005/Atom", "o":"http://a9.com/-/spec/opensearch/1.1/"}
CATEGORY = "(cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.CV)"

def now():
    return dt.datetime.now(UTC).isoformat()

def read(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

def write(name, value):
    p=ROOT/name
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(tmp,p)

def fetch(url):
    # TLS validation is always enabled. Windows curl can use the system certificate store.
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"FutureWorkforceResearchDemo/1.0"})
        with urllib.request.urlopen(req,timeout=30) as r:
            return r.read()
    except Exception:
        curl=shutil.which("curl.exe" if os.name=="nt" else "curl")
        if not curl:
            raise
        result=subprocess.run([curl,"--fail","--silent","--show-error","--location",
            "--max-time","40","--user-agent","FutureWorkforceResearchDemo/1.0",url],
            capture_output=True,check=True,timeout=45)
        return result.stdout

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def arxiv_count(query,start,end):
    end_inclusive=end-dt.timedelta(minutes=1)
    keyword=f" AND ({query})" if query else ""
    full=f'{CATEGORY}{keyword} AND submittedDate:[{start:%Y%m%d%H%M} TO {end_inclusive:%Y%m%d%H%M}]'
    url="https://export.arxiv.org/api/query?"+urllib.parse.urlencode({
        "search_query":full,"start":0,"max_results":3,"sortBy":"submittedDate","sortOrder":"descending"})
    err=None
    for attempt in range(2):
        try:
            raw=fetch(url)
            root=ET.fromstring(raw)
            count=root.find("o:totalResults",NS)
            if count is None:
                raise ValueError("No totalResults in arXiv response")
            examples=[]
            for e in root.findall("a:entry",NS):
                ident=e.findtext("a:id","",NS)
                if "api/errors" in ident:
                    raise ValueError(e.findtext("a:title","arXiv error",NS))
                examples.append({"url":ident.replace("http://","https://"),
                    "title":" ".join(e.findtext("a:title","",NS).split()),
                    "published_at":e.findtext("a:published",None,NS)})
            return dict(query=full,request_url=url,total_results=int(count.text),
                retrieved_at=now(),window_start=start.isoformat(),window_end_exclusive=end.isoformat(),
                source_feed_updated_at=root.findtext("a:updated",None,NS),
                response_sha256=digest(raw),sample_records=examples)
        except Exception as exc:
            err=f"{type(exc).__name__}: {str(exc)[:180]}"
            time.sleep(4)
    raise RuntimeError(err)

def research(asof,days):
    end=dt.datetime.combine(asof-dt.timedelta(days=7),dt.time(),UTC)
    current=end-dt.timedelta(days=days)
    previous=current-dt.timedelta(days=days)
    records=[]
    for skill in read("data/skills.json"):
        if not skill["arxiv_query"]:
            continue
        pair={}
        for label,start,stop in [("previous",previous,current),("current",current,end)]:
            pair[label]=arxiv_count(skill["arxiv_query"],start,stop)
            print(skill["skill_id"],label,pair[label]["total_results"],flush=True)
            time.sleep(3.2)
        records.append(dict(skill_id=skill["skill_id"],**pair))
    denominator={}
    for label,start,stop in [("previous",previous,current),("current",current,end)]:
        denominator[label]=arxiv_count(None,start,stop)
        time.sleep(3.2)
    # Publish only a complete coherent refresh.
    data=dict(source_id="arxiv",retrieved_at=now(),as_of=asof.isoformat(),days_per_window=days,
        indexing_lag_days=7,category_filter=CATEGORY,denominator=denominator,records=records,
        limitations="Research-topic momentum, NOT job-demand growth. Queries overlap and do not cover all skill meanings.")
    write("data/research_counts.json",data)
    stamp=dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    write(f"evidence/research_{stamp}.json",data)

def term_matches(text,terms):
    return [t for t in terms if re.search(r"(?<!\w)"+re.escape(t)+r"(?!\w)",text,re.I)]

def jobs(pages,seed=None):
    skills=read("data/skills.json")
    records={}
    page_evidence=[]
    for page in range(1,pages+1):
        url=f"https://www.arbeitnow.com/api/job-board-api?page={page}"
        seeded=bool(seed and page==1)
        raw=Path(seed).read_bytes() if seeded else fetch(url)
        payload=json.loads(raw)
        if not isinstance(payload.get("data"),list):
            raise ValueError("Unexpected Arbeitnow response")
        captured=dt.datetime.fromtimestamp(Path(seed).stat().st_mtime,UTC).isoformat() if seeded else now()
        page_evidence.append(dict(url=url,retrieved_at=captured,response_sha256=digest(raw),
            capture_time_basis="predownloaded_seed_file_mtime" if seeded else "http_response_completed",
            count=len(payload["data"]),meta=payload.get("meta")))
        for j in payload["data"]:
            text=html.unescape(re.sub("<[^>]+>"," ",j.get("description","")))
            text=" ".join([j.get("title",""),text," ".join(j.get("tags",[]))])
            matched={s["skill_id"]:term_matches(text,s["job_terms"]) for s in skills}
            matched={k:v for k,v in matched.items() if v}
            # Do not persist descriptions, contact persons, email, phones, CVs or author details.
            rec=dict(job_id=j["slug"],title=j["title"],url=j["url"],location=j.get("location"),
                remote=j.get("remote"),published_at=dt.datetime.fromtimestamp(j["created_at"],UTC).isoformat(),
                skill_matches=matched,source_id="arbeitnow")
            records[rec["job_id"]]=rec
        time.sleep(1)
    data=dict(source_id="arbeitnow",retrieved_at=now(),geography="Europe-oriented; not Malaysia",
        sampling="First N API pages sorted by created_at; not a representative labour-market sample",
        measured_skill_ids=[s['skill_id'] for s in skills],
        pages_requested=pages,records=list(records.values()),page_evidence=page_evidence,
        privacy="Full descriptions and all contact-person fields omitted.",
        attribution="Source: Arbeitnow; preserve each listing URL in any displayed listing.",
        observed_hiring_growth_pct=None,
        growth_note="One active-listing snapshot cannot establish historical hiring growth.")
    write("data/jobs_snapshot.json",data)
    stamp=dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    write(f"evidence/jobs_{stamp}.json",data)
    print("jobs",len(records),flush=True)

def derive():
    research_data=read("data/research_counts.json") if (ROOT/"data/research_counts.json").exists() else None
    job_data=read("data/jobs_snapshot.json") if (ROOT/"data/jobs_snapshot.json").exists() else None
    research_by={r["skill_id"]:r for r in research_data["records"]} if research_data else {}
    signals=[]
    for s in read("data/skills.json"):
        r=research_by.get(s["skill_id"])
        item=dict(skill_id=s["skill_id"],research_growth_pct=None,research_share_change_pp=None,
            research_previous_count=None,research_current_count=None,research_status="not_measured",
            job_snapshot_count=None,job_snapshot_share_pct=None,job_growth_pct=None)
        if r:
            p,c=r["previous"]["total_results"],r["current"]["total_results"]
            pd,cd=[research_data["denominator"][k]["total_results"] for k in ["previous","current"]]
            growth=(c-p)/p*100 if p else None
            # Primary matching signal: change in share, normalised by prior share.
            sp=p/pd if pd else None
            sc=c/cd if cd else None
            relative=(sc-sp)/sp if sp else None
            item.update(research_previous_count=p,research_current_count=c,
                research_growth_pct=round(growth,3) if growth is not None else None,
                research_share_change_pp=round(100*(sc-sp),4) if sp is not None and sc is not None else None,
                research_share_relative_change=relative,
                research_status="usable" if p>=10 and c>=10 and relative is not None else "low_count_or_zero_baseline",
                research_windows={k:{"start":r[k]["window_start"],"end_exclusive":r[k]["window_end_exclusive"]} for k in ["previous","current"]},
                source_urls=[r[k]["request_url"] for k in ["previous","current"]],
                research_retrieved_at=research_data["retrieved_at"])
        if job_data:
            item.update(job_sample_size=len(job_data['records']),job_retrieved_at=job_data['retrieved_at'])
        if job_data and s['skill_id'] in job_data.get('measured_skill_ids', [s['skill_id']]):
            n=len(job_data["records"])
            count=sum(s["skill_id"] in j["skill_matches"] for j in job_data["records"])
            item.update(job_snapshot_count=count,job_snapshot_share_pct=round(count/n*100,3) if n else None,
                job_sample_size=n,job_retrieved_at=job_data["retrieved_at"])
        item.update(measurement_scope=s.get('measurement_scope'),research_proxy_legacy_id=s.get('research_proxy_legacy_id'),
            signal_scope="Research-topic attention and Europe-oriented job sample; not Malaysia hiring growth.",
            industry_demand_level=None,
            industry_demand_status="not_established_from_available_sources",
            seasonality_adjusted=False,
            seasonality_note="Short windows may reflect submission timing, keyword changes and indexing effects. "
                "Seasonality has NOT been estimated, and the cause of a decline is unknown. Research decline is not evidence of hiring decline.",
            uncertainty_flags=["keyword_proxy","nonrepresentative_job_sample","no_causal_attribution"],
            trend_indicator_basis="Sign of measured relative topic-share change; descriptive, not a forecast.",
            research_momentum_floor_applied=False)
        value=item.get("research_share_relative_change")
        if item["research_status"]=="not_measured":
            indicator="not_measured"
            label="未测量研究趋势"
        elif item["research_status"]!="usable" or value is None:
            indicator="insufficient_research_evidence"
            label="研究计数不足，暂不判断方向"
        elif value>0:
            indicator="research_share_increasing"
            label="研究主题占比上升（不等于招聘增长）"
        elif value<0:
            indicator="research_share_decreasing"
            label="研究主题占比下降（不等于招聘下降）"
        else:
            indicator="research_share_unchanged"
            label="研究主题占比未变"
        item.update(trend_indicator=indicator,trend_indicator_label_zh=label)
        signals.append(item)
    write("data/trend_signals.json",dict(computed_at=now(),signals=signals,
        semantics="Research growth, active-job prevalence and employment projections are distinct metrics.",
        cache_policy="Show source retrieval times; computed_at does not mean source refreshed.",
        schema_version="2.0",
        methodology_note="Raw counts and signs are retained. No assumed high-demand labels, causal seasonal corrections or 0.35 momentum floor."))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",choices=["all","research","jobs","derive"],default="all")
    ap.add_argument("--as-of",default=dt.datetime.now(UTC).date().isoformat())
    ap.add_argument("--days",type=int,default=90)
    ap.add_argument("--pages",type=int,default=3)
    ap.add_argument("--seed-first-job-page",help="Optional already downloaded API response")
    args=ap.parse_args()
    if args.days<=0 or not 1<=args.pages<=10:
        ap.error("days must be positive; pages must be 1..10")
    errors=[]
    successful_sources=[]
    if args.source in ("all","research"):
        try:
            research(dt.date.fromisoformat(args.as_of),args.days)
            successful_sources.append("research")
        except Exception as e: errors.append({"source":"research","error":str(e),"failed_at":now()})
    if args.source in ("all","jobs"):
        try:
            jobs(args.pages,args.seed_first_job_page)
            successful_sources.append("jobs")
        except Exception as e: errors.append({"source":"jobs","error":str(e),"failed_at":now()})
    derive()
    write("reports/last_refresh.json",dict(attempted_at=now(),errors=errors,
        operation=args.source,successful_sources=successful_sources,
        source_refresh_performed=bool(successful_sources),
        status="failed_refresh_existing_cache_preserved" if errors else "success"))
    if errors:
        print(json.dumps(errors,ensure_ascii=False))
        raise SystemExit(1)
