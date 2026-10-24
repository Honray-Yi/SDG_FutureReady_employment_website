# FutureReady

> **Live prototype:** [Open FutureReady](https://future-ready-demo.onrender.com/) — a free synthetic-profile demo. Do not upload a real résumé. The full local résumé-embedding workflow requires the pinned model download and at least 4 GB of memory.

FutureReady is a bilingual career-exploration application that helps learners connect experience and skills to AI-era roles, compare skills gaps, explore dated workforce signals, follow learning pathways, and understand potential Sustainable Development Goal (SDG) contributions. It supports human-led exploration; it does not make hiring decisions or guarantee employment.

## What is included

- **Skills intake:** synthetic Module 1 profiles and structured skill confirmation; local setup also supports text-based PDF/DOCX or pasted experience with review and consent.
- **Trend evidence:** dated research and job-market snapshots with a source registry and links.
- **Future-role matching:** 65 occupations, explainable fit and skills gaps; local résumé matching uses a pinned multilingual E5 embedding model.
- **Reskilling pathways:** ordered course suggestions with duration, prerequisites, cost conditions, provider links, and review metadata where available.
- **SDG mapping:** role and skill mappings include targets, conditional rationales, and official UN links.
- **Uncertainty:** moderate and fast-disruption scenarios display estimates rather than a single certain prediction.

The hosted Render Free instance is configured for synthetic profiles and career matching. The complete model-backed résumé workflow is intended for a properly provisioned local deployment. Matching scores are similarity estimates, not hiring probabilities or skill certifications. The app does not retain uploaded résumé files, extracted text, or vectors as user history.

## Technology

| Layer | Stack |
|---|---|
| Frontend | React, TypeScript, Vite, CSS, WebGL and Canvas |
| API | Python, FastAPI and Uvicorn |
| Semantic matching | `intfloat/multilingual-e5-small` via pinned quantized ONNX assets, CPU inference |
| Data | JSON/CSV snapshots with source, date, and usage notes |
| Workspace | pnpm, uv, OpenAPI, GitHub Actions, Docker |
| Hosted demo | Render Free, Singapore region |

## Run locally

Requirements: Node.js 22.12+, pnpm 10, Python 3.13, uv, approximately 4 GB available memory and 2 GB disk space. The first setup downloads the pinned public model assets.

```bash
pnpm install --frozen-lockfile
uv sync --frozen --no-dev --no-install-project
uv run --no-sync python artifacts/api-server/backend/local_model_assets.py --from-hub
uv run --no-sync python artifacts/api-server/backend/build_job_index.py
uv run --no-sync python scripts/dev_local.py
```

Open `http://localhost:5173`. Use the public demo credentials shown in the application README. No SQL database or external inference API key is required.

## Submission package

| Item | Location and status |
|---|---|
| Complete codebase | Repository root, including frontend, FastAPI backend, data, lockfiles, setup scripts, and verification workflow. |
| Replit utilization proof | [01-Replit-Utilization-Proof](01-Replit-Utilization-Proof/); upload evidence here. |
| RunPod utilization proof | [02-RunPod-Utilization-Proof](02-RunPod-Utilization-Proof/); upload if applicable and confirm the declaration. |
| Completed submission template | [03-Completed-Submission-Template](03-Completed-Submission-Template/); team identity fields remain to be entered. |
| Tech tools declaration | [04-Completed-Tech-Tools-Declaration](04-Completed-Tech-Tools-Declaration/); confirm RunPod use and add signatures. |
| Pitch deck | [05-Pitch-Deck-Slides](05-Pitch-Deck-Slides/). |
| YouTube demo link | [06-YouTube-Product-Demo](06-YouTube-Product-Demo/); add the URL after uploading. |
| README summary | [07-README-Summary](07-README-Summary/). |
| Apache License 2.0 | [08-Apache-License-2.0](08-Apache-License-2.0/) and root [`LICENSE`](LICENSE). |
| Product requirements document | [`docs/deliverables/FutureReady-Product-Requirements-Document.docx`](docs/deliverables/FutureReady-Product-Requirements-Document.docx). |
| Live prototype | https://future-ready-demo.onrender.com/ |

The only remaining submission inputs are the team name, member names and contact, signatures, the Replit proof, the YouTube URL, and confirmation of RunPod usage. The RunPod item may be marked not applicable if it was not used.

## Data, privacy, and license

The live demo uses synthetic profiles. In a local model-backed run, résumé text is sent to the application backend for temporary processing after review and consent; it is not browser-only offline analysis. Do not upload real résumés to the public demo.

Original project code and project-authored documentation are licensed under Apache-2.0. Third-party data, model files, dependencies, fonts, images, logos, and challenge materials retain their own terms. The upstream redistribution license for the supplied 65-role catalogue was not provided and must be confirmed by its owner before redistribution. See [`NOTICE`](NOTICE), [`docs/model-notice.md`](docs/model-notice.md), and [`artifacts/api-server/data-package/ATTRIBUTION_AND_USE.md`](artifacts/api-server/data-package/ATTRIBUTION_AND_USE.md).
