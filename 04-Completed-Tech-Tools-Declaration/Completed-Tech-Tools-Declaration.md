# FutureReady Technical Tools Declaration

This declaration records the tools and services evident in the current source repository and deployment. It distinguishes development assistance from tools used by the product at runtime. The team must confirm its names and any separate RunPod activity before signing.

## Project and declaration details

| Field | Value |
| --- | --- |
| Project | FutureReady: AI-Ready Career Pathways |
| Repository | https://github.com/Honray-Yi/SDG_FutureReady_employment_website |
| Live prototype | https://future-ready-demo.onrender.com/ |
| Team and members | Team to complete before submission |
| Declaring representative | Team to complete before submission |
| Declaration date | 2026-10-25 |

## Development and runtime tools

| Category | Tool | Declared use |
| --- | --- | --- |
| AI-assisted development and writing | OpenAI ChatGPT and Codex | Assisted with code changes, debugging, project documentation, the product requirements document, pitch deck content, and submission materials. AI assistance is disclosed; the project team remains responsible for checking the work and all claims before submission. |
| Product embedding model | `intfloat/multilingual-e5-small`, using the pinned Xenova quantized ONNX distribution | Used by the full local resume-matching workflow for CPU text embeddings. It is not a generative model and does not generate job or course facts. Model revision, hashes, and MIT notice are in `docs/model-notice.md`. |
| Product inference service | None | The application does not call OpenAI or another external generative AI API for profile analysis or matching. The hosted free demo is configured for synthetic profiles; the local E5 workflow requires model assets and at least 4 GB memory. |
| Frontend | React, TypeScript, Vite, CSS, and WebGL/Canvas | User interface, visualizations, and browser interactions. Dependencies are declared in the workspace manifests and `pnpm-lock.yaml`. |
| Backend | Python, FastAPI, Uvicorn, NumPy, ONNX Runtime, and Tokenizers | API, document text extraction, matching and course-pathway logic. Python dependencies are locked in `uv.lock` and `requirements.lock`. |
| Prototype environment | Replit | Used during project prototyping/development. Proof is to be uploaded by the team in `01-Replit-Utilization-Proof/`. No Replit secret or credential is included in this repository. |
| Source control | GitHub | Public project repository and source history. The repository contains the complete application source, data package, documentation, and setup files. |
| Public hosting | Render Free | Hosts the synthetic-profile demonstration at the link above. It is not provisioned for full E5 resume inference. |
| RunPod | Not used in the current codebase or Render deployment record | This is marked not applicable based on available project records. If the team separately used RunPod for development or model work, update this row and place non-sensitive proof in `02-RunPod-Utilization-Proof/`. |

## Data, model, and privacy disclosures

The repository includes synthetic demonstration profiles and curated public-source snapshots with provenance and dates recorded in the data package. The 65-role matching catalogue is supplied/project-maintained input; its upstream redistribution rights should be confirmed independently. Third-party libraries, public datasets, course metadata, model assets, fonts, and supplied challenge materials keep their own applicable terms. See `NOTICE`, `artifacts/api-server/data-package/ATTRIBUTION_AND_USE.md`, and `docs/model-notice.md`.

The hosted demo is for synthetic profiles. In a properly provisioned local run, a user may submit a text-based resume for transient backend processing after reviewing the extracted text and giving consent. The project does not save resume files, extracted text, or vectors as persistent user history. Users should not upload real resumes to the public free demo.

## Declaration and signature

We disclose the development assistance, runtime model, software stack, data boundaries, and hosting environment listed above. We understand that AI-assisted output must be reviewed by the submitting team, and that similarity scores and SDG mappings are not employment outcomes, competency certifications, or measured social impact. We will update this declaration if the team confirms any additional tool usage, including RunPod.

| Sign-off | Complete before submission |
| --- | --- |
| Team representative name | __________________________________________ |
| Signature | __________________________________________ |
| Date | __________________________________________ |

## Evidence locations

- Replit utilization evidence: `01-Replit-Utilization-Proof/`
- RunPod utilization evidence, if applicable: `02-RunPod-Utilization-Proof/`
- Public demo URL: `06-YouTube-Product-Demo/youtube-demo-link.txt` (paste the YouTube URL after uploading the video)
