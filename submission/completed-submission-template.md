# FutureReady Project Submission

A completed project submission for the Aiversecity Future-Ready Workforce Domain preliminary round. Project details are filled from the current repository and live prototype. The official team name, member names, and contact address must be supplied by the team before final submission.

## Submission details

| Field | Completed submission |
| --- | --- |
| Project | FutureReady: AI-Ready Career Pathways |
| Challenge | Aiversecity Future-Ready Workforce Domain |
| Sponsor | Aiversecity |
| Team name and members | Team to complete before submission |
| Contact email | Team to complete before submission |
| Product stage | Working web prototype; public hosted demo uses synthetic profiles |
| GitHub repository | https://github.com/Honray-Yi/SDG_FutureReady_employment_website |
| Live prototype | https://future-ready-demo.onrender.com/ |
| Product demo video | To be added by the team in `submission/demo/youtube-demo-link.txt` |
| Replit utilization proof | To be uploaded in `submission/evidence/replit/` |
| RunPod utilization proof | Team to confirm. No RunPod configuration appears in the current source or Render deployment. If the team used RunPod separately, upload proof to `submission/evidence/runpod/` and update the declaration; otherwise mark this item not applicable. |

## Problem

Workers facing job change, recent graduates, and career switchers need to understand how their current experience relates to emerging AI-era roles. Job descriptions use specialized language, learning options are spread across providers, and an unexplained match score can be mistaken for proof of skill or likelihood of employment. A static skills list also cannot communicate how labor-market and research signals may change over time.

## Proposed solution

FutureReady is a bilingual career-exploration web application. A user starts from a synthetic skills profile or, in a properly provisioned local deployment, reviews text extracted from a resume. The application compares the confirmed profile or experience text with a catalogue of 65 AI-related occupations, explains relevant skill gaps, recommends learning resources, and shows potential SDG contributions. The interface keeps evidence, sources, dates, score meaning, and limitations visible so a person can make the final career decision.

## Target users

- Working adults considering a transition as job requirements change.
- Fresh graduates and career switchers deciding where to build experience.
- HR and learning-and-development managers planning reskilling support.
- TVET and university career centres advising learners.
- Career advisers and educators supporting human-led exploration.

## SDG alignment

SDG 4 is the primary alignment: target 4.4 concerns relevant skills for employment and decent work. SDG 8.5 is a supporting alignment for informed career preparation, not a claim that the product creates jobs. SDG 10.2 is a supporting design alignment for bilingual access and clear learning-cost information. Role and skill records also carry curated, conditional mappings to relevant goals such as SDGs 3, 4, 7, 8, 9, 10, 11, 12, and 16. These mappings are project interpretations, not UN endorsement or measured social impact.

## Scope and key features

| Required feature | Delivery in this project |
| --- | --- |
| Skills profile intake | Module 1 supports a synthetic profile and a structured skills questionnaire. The full local workflow supports text-based PDF/DOCX or pasted experience, extracted-text review, consent, and confirmed skill input. |
| AI-trend signal layer | Dated research and job-market snapshots have a source registry and evidence links. The UI exposes source and measurement dates; the project does not rely only on a fixed hand-written trend list. |
| Future-role matching | The engine ranks suitable roles and explains skill coverage and gaps. Resume-based semantic matching uses cosine similarity and a pinned multilingual E5 model in a properly provisioned local installation. Scores are not hiring probabilities or skill mastery. |
| Personalised reskilling pathway | Ordered course recommendations include available duration, prerequisites, cost conditions, rationale, provider links, and review metadata where recorded. |
| SDG mapping | Role and skill views display potential SDG mappings, targets, and conditional rationale with official UN links. |
| Handling uncertainty | Moderate and fast-disruption scenarios show alternative estimated outcomes. They are scenario comparisons, not certain forecasts. |

The public Render Free instance is configured for synthetic-profile demonstrations and matching. The full resume-embedding path is not provisioned on the hosted free instance; it requires the public model download and at least 4 GB of memory in a local setup. The application does not make hiring decisions, guarantee employment, perform OCR on scanned resumes, or retain resume files and extracted text as user history.

## Technical approach

The browser interface uses React, TypeScript, and Vite. FastAPI serves the API and production frontend. The full local resume workflow uses the pinned `intfloat/multilingual-e5-small` model in a quantized ONNX format for CPU inference; it does not call a generative AI API for matching. JSON/CSV snapshots provide the career, trend, course, source, and SDG context. The repository includes dependency locks, OpenAPI files, local setup steps, validation scripts, and GitHub Actions checks.

## Expected impact and measurement

The prototype is intended to give a person a transparent starting point for career exploration and reskilling. It has not been evaluated for employment outcomes, user adoption, recommendation accuracy in real-world settings, fairness across groups, or measured SDG impact. Those outcomes require separate evaluation with consent, representative data, and human oversight.

## Demo and supporting files

- Product: https://future-ready-demo.onrender.com/
- Source: https://github.com/Honray-Yi/SDG_FutureReady_employment_website
- Product requirements: `docs/deliverables/FutureReady-Product-Requirements-Document.docx`
- Pitch deck: `docs/deliverables/FutureReady-Project-Presentation.pptx`
- AI and technical tools declaration: `submission/tech-tools-declaration.docx`
- Replit evidence folder: `submission/evidence/replit/`
- Optional RunPod evidence folder: `submission/evidence/runpod/`
- YouTube link file: `submission/demo/youtube-demo-link.txt`

## Final team completion items

Before submitting, enter the official team name, member names, and contact email; upload Replit proof; add the YouTube demo URL; and confirm whether RunPod was used. If RunPod was not used, leave its evidence item marked not applicable. Do not upload API keys, passwords, real resumes, or private account data as evidence.
