"""Refresh aggregate Malaysia context separately from AI/skill demand."""
import hashlib
import json
from refresh import read,write,fetch,now

if __name__=="__main__":
    old=read("data/malaysia_context.json")
    raw=fetch(old["source_url"])
    data=json.loads(raw)
    records=[r for r in data if r.get("age")=="overall"]
    if not records:raise ValueError("No overall records; existing cache retained")
    old.update(records=records,retrieved_at=now(),
        response_sha256=hashlib.sha256(raw).hexdigest(),
        latest_period=max(r["date"] for r in records))
    write("data/malaysia_context.json",old)
    print("Refreshed",len(records),"aggregate records. Latest quarter start:",old["latest_period"])
