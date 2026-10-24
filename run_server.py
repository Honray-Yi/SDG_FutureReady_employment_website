"""Run the existing FastAPI backend using the artifact-managed port."""
import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ["PORT"]), access_log=False)
