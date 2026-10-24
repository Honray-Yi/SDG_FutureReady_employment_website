"""Display-only English summaries; canonical embedding documents stay unchanged."""
from functools import lru_cache
import json
from pathlib import Path
from semantic_catalogue import normalize_text


@lru_cache(maxsize=1)
def translations():
    rows = json.loads((Path(__file__).resolve().parents[1] / "catalogue/job_english.json").read_text())
    return {normalize_text(name): value for name, value in rows.items()}


def display_fields(job):
    name, description = translations()[job["job_name"]]
    return {"job_name_en": name, "job_text_en": description}


def public_job(job):
    from sdg_mapping import sdgs_for_job
    return {**job, **display_fields(job), "sdg_contributions": sdgs_for_job(job)}
