"""Module 1 intake contracts and nullable-aware matching over one data snapshot."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import logging
import os
from pathlib import Path
import sys
from threading import RLock
from types import FunctionType
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from intake.app import app as intake_app, ProfileInput, profile as normalize_profile
from intake.engine import CATALOG, CATALOG_HASH, IDS
from explorer_api import router as explorer_router

BASE = Path(__file__).resolve().parents[1]
DATA_PACKAGE = Path(os.environ.get("FUTURE_WORKFORCE_DATA", BASE / "data-package")).resolve()
sys.path.insert(0, str(DATA_PACKAGE / "scripts"))
spec = importlib.util.spec_from_file_location("workforce_engine", DATA_PACKAGE / "scripts/match.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
logger = logging.getLogger(__name__)
from legacy_api import router as legacy_router


class Dataset:
    """Invalidate on file changes; reject a refresh observed partway through reading."""
    def __init__(self, root: Path):
        self.root, self.lock = root, RLock()
        self.signature, self.cached = None, None

    def load(self):
        with self.lock:
            for _ in range(3):
                files = sorted((self.root / "data").glob("*.json"))
                signature = tuple((p.name, p.stat().st_mtime_ns, p.stat().st_size) for p in files)
                if self.cached is not None and signature == self.signature:
                    return self.cached
                raw = {"data/" + p.name: p.read_bytes() for p in files}
                after = tuple((p.name, p.stat().st_mtime_ns, p.stat().st_size) for p in files)
                if signature != after:
                    continue
                values = {name: json.loads(content) for name, content in raw.items()}
                for name in ("skills", "roles", "courses", "synthetic_profiles", "scenarios", "trend_signals", "research_counts", "jobs_snapshot", "source_registry"):
                    if "data/" + name + ".json" not in values:
                        raise ValueError("Missing required dataset: " + name)
                canonical=values['data/skill_dictionary.json']
                if hashlib.sha256(json.dumps(canonical,sort_keys=True,ensure_ascii=False).encode()).hexdigest()!=CATALOG_HASH:
                    raise ValueError('Dictionary changed; restart the service to reload intake and matching together')
                if [s['skill_id'] for s in values['data/skills.json']]!=IDS:
                    raise ValueError('Derived skill index must use Module 1 order')
                if any(any(derived.get(k)!=v for k,v in original.items()) for original,derived in zip(canonical['skills'],values['data/skills.json'])):
                    raise ValueError('Derived skill definitions differ from the authoritative dictionary')
                if not all(p.get("is_synthetic") is True and not p.get("personal_identifiers_included") for p in values["data/synthetic_profiles.json"]):
                    raise ValueError("Only synthetic profiles are supported")
                digest = hashlib.sha256()
                for name, content in raw.items():
                    digest.update(name.encode())
                    digest.update(content)
                self.cached = (values, digest.hexdigest()[:12])
                self.signature = signature
                return self.cached
            raise ValueError("Dataset is being updated; retry shortly")


dataset = Dataset(DATA_PACKAGE)
app = FastAPI(title="FutureReady API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # FastAPI's default error includes rejected input (possibly the whole resume).
    return JSONResponse(status_code=422, content={"detail": [
        {key: item[key] for key in ("loc", "msg", "type")}
        for item in exc.errors()
    ]})


app.include_router(explorer_router)
app.include_router(legacy_router)
# Reuse the Module 1 contracts, excluding its colliding health/root/docs routes.
for route in intake_app.routes:
    if route.path in ('/api/skills','/api/demo-profiles','/api/profile','/api/profile/parse'):
        app.router.routes.append(route)


@app.middleware("http")
async def security_headers(request, call_next):
    if request.url.path == "/api/explorer/match" and request.method == "POST":
        # Bound even chunked bodies before Pydantic/JSON parsing; never trust only
        # Content-Length. 512 KiB accommodates 100k UTF-8 characters plus JSON.
        payload = bytearray()
        async for chunk in request.stream():
            if len(payload) + len(chunk) > 512 * 1024:
                return JSONResponse(
                    status_code=413,
                    content={"detail": {"code": "body_too_large", "message": "分析请求超过大小限制。"}},
                    headers={"Cache-Control": "no-store"},
                )
            payload.extend(chunk)
        request._body = bytes(payload)
        payload.clear()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    return response


def load():
    try:
        return dataset.load()
    except (OSError, ValueError, KeyError) as exc:
        logger.warning("Dataset unavailable: %s", exc)
        raise HTTPException(503, "The data snapshot is unavailable. Restore the data package or retry after a refresh.") from exc


def bind(function, values):
    # The original function bytecode is reused; only its data reader is bound.
    # This avoids global monkeypatching and keeps concurrent requests isolated.
    namespace = {**function.__globals__, "read": lambda path: values[path]}
    return FunctionType(function.__code__, namespace, function.__name__, function.__defaults__, function.__closure__)


def metadata(values, version):
    research = values["data/research_counts.json"]
    jobs = values["data/jobs_snapshot.json"]
    return {
        "snapshot_id": version,
        "mode": "cached_public_observations",
        "research_retrieved_at": research.get("retrieved_at"),
        "jobs_retrieved_at": jobs.get("retrieved_at"),
        "signals_computed_at": values["data/trend_signals.json"].get("computed_at"),
        "research_windows": {period: {key: research["denominator"][period][key] for key in ("window_start", "window_end_exclusive", "total_results")} for period in ("previous", "current")},
        "job_sample_size": next((s.get("job_sample_size") for s in values["data/trend_signals.json"]["signals"] if s.get("job_sample_size") is not None), len(jobs.get("records", []))),
        "research_scope": "Global research attention; topic queries may overlap.",
        "jobs_scope": "Europe-oriented Arbeitnow sample; not Malaysia hiring growth.",
        "model": "Deterministic heuristic; no LLM is used.",
        "skill_dictionary_version": CATALOG['version'],
        "dictionary_hash": CATALOG_HASH,
        "taxonomy_note": "Module 1 taxonomy; historical topic proxies cover only subsets. Unknown proficiency remains null.",
    }


@app.get("/api/health")
def health():
    _, version = load()
    return {"status": "ok", "snapshot_id": version, "module":"skills-intake-and-matching", "dictionary_version":CATALOG['version'], "dictionary_hash":CATALOG_HASH}


@app.get("/api/bootstrap")
def bootstrap():
    values, version = load()
    return {"profiles": values["data/synthetic_profiles.json"], "skills": values["data/skills.json"],
            "roles": values["data/roles.json"], "scenarios": values["data/scenarios.json"],
            "signals": values["data/trend_signals.json"]["signals"],
            "sources": values["data/source_registry.json"], "metadata": metadata(values, version)}


class MatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_id: str | None = Field(default=None, max_length=80)
    profile: dict | None = None
    scenario: Literal["moderate", "fast"] = "moderate"
    hours_per_week: int | None = Field(default=None, ge=1, le=40, strict=True)


@app.post("/api/match")
def match(request: MatchRequest):
    values, version = load()
    if (request.profile_id is None)==(request.profile is None):
        raise HTTPException(422, 'Supply exactly one of profile_id or a Module 1 profile.')
    profile = next((p for p in values["data/synthetic_profiles.json"] if p["profile_id"] == request.profile_id), None)
    if request.profile is not None:
        from pydantic import ValidationError
        allowed=set(ProfileInput.model_fields)|{'profile_id','created_at','assessment_status','storage','summary','vectors'}
        if set(request.profile)-allowed:
            raise HTTPException(422,'Unexpected profile fields')
        try:
            body=ProfileInput.model_validate({k:v for k,v in request.profile.items() if k in ProfileInput.model_fields})
        except ValidationError:
            raise HTTPException(422,'Invalid Module 1 profile: use confirmed synthetic skills and the current dictionary.')
        normalized=normalize_profile(body)
        # Recompute redundant vectors; never trust client-supplied levels or mask.
        if 'vectors' in request.profile and request.profile['vectors']!=normalized['vectors']:
            raise HTTPException(422,'Profile vectors do not match confirmed skills.')
        profile={**normalized,'skill_levels':dict(zip(IDS,normalized['vectors']['levels'])),
                 'current_role':body.display_name,'hours_per_week':8,'interests':[],'target_role_id':'R05'}
    if profile is None:
        raise HTTPException(422, "Choose one of the supplied synthetic demo profiles.")
    profile = copy.deepcopy(profile)
    if request.hours_per_week is not None:
        profile["hours_per_week"] = request.hours_per_week
    rank = bind(engine.rank, values)
    pathway = bind(engine.pathway, values)
    observed = rank(profile, request.scenario)
    neutral = {r["role_id"]: r for r in rank(profile, request.scenario, neutral_trend=True)}
    courses = {c["course_id"]: c for c in values["data/courses.json"]}
    paths = {}
    for role in observed:
        n = neutral[role["role_id"]]
        role["comparison"] = {"neutral_rank": n["rank"], "neutral_score": n["score"], "rank_change": n["rank"] - role["rank"], "score_change": round(role["score"] - n["score"], 3)}
        path = pathway(profile, role["role_id"])
        for step in path["steps"]:
            source = courses[step["course_id"]]
            step.update({key: source.get(key) for key in ("provider", "prerequisite_course_ids", "checked_at", "extra_cost_note")})
        paths[role["role_id"]] = path
    return {"profile": profile, "scenario": request.scenario, "roles": observed,
            "pathways": paths, "metadata": metadata(values, version)}


DIST = BASE / "frontend" / "dist"
app.mount('/intake-static',StaticFiles(directory=BASE/'module1-web'),name='intake-static')

@app.get('/intake', include_in_schema=False)
def intake_page():
    return FileResponse(BASE/'module1-web/index.html')
if (DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")


@app.get("/", include_in_schema=False)
def index():
    if not (DIST / "index.html").is_file():
        raise HTTPException(503, "Build the frontend first, or use the Vite development server.")
    return FileResponse(DIST / "index.html")
