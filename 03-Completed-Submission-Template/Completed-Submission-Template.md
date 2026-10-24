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
| Product demo video | To be added by the team in `06-YouTube-Product-Demo/youtube-demo-link.txt` |
| Replit utilization proof | To be uploaded in `01-Replit-Utilization-Proof/` |
| RunPod utilization proof | Team to confirm. No RunPod configuration appears in the current source or Render deployment. If the team used RunPod separately, upload proof to `02-RunPod-Utilization-Proof/` and update the declaration; otherwise mark this item not applicable. |

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
- AI and technical tools declaration: `04-Completed-Tech-Tools-Declaration/Completed-Tech-Tools-Declaration.docx`
- Replit evidence folder: `01-Replit-Utilization-Proof/`
- Optional RunPod evidence folder: `02-RunPod-Utilization-Proof/`
- YouTube link file: `06-YouTube-Product-Demo/youtube-demo-link.txt`

## Final team completion items

Before submitting, enter the official team name, member names, and contact email; upload Replit proof; add the YouTube demo URL; and confirm whether RunPod was used. If RunPod was not used, leave its evidence item marked not applicable. Do not upload API keys, passwords, real resumes, or private account data as evidence.


---

---

## Copy-ready answers for the SDC form

# 2. Executive Summary & Problem Statement

## 2.1 The Problem Context

AI is changing the tasks and skills required across many occupations, while career guidance, job-market information, and affordable learning options are often spread across different sources. Working adults whose roles are changing, recent graduates, and career switchers can struggle to see how their existing experience transfers to emerging roles or which skills to build next. This can lead to costly or poorly targeted training decisions and make career transitions harder, especially for people with limited access to personalized guidance. Employers, educators, and career services also need clearer ways to discuss changing skill needs without treating uncertain forecasts as guarantees. FutureReady addresses this information and navigation gap. It is a career-exploration aid: it helps people compare skills, roles, evidence, and learning options, while leaving decisions about training and employment to the person and their advisers.

## 2.2 The Proposed AI Solution

FutureReady is a bilingual web application that takes a user from a skills profile to explainable future-role suggestions and an ordered reskilling pathway. Users can explore with synthetic profiles in the public demo. In a properly provisioned local deployment, they can provide resume text or a text-based PDF/DOCX, review the extracted text, and confirm the skills used. The local matching workflow uses a pinned, quantized multilingual E5 model in ONNX format to compare profile text with a catalogue of 65 occupations; it reports similarity scores and skill gaps, not hiring probabilities. Dated job-market and research snapshots provide trend context, with visible sources and dates. The app also links roles and skills to SDGs, recommends learning resources, and compares moderate and faster-disruption scenarios. The prototype uses React, TypeScript, Vite, Python, FastAPI, OpenAPI, structured JSON/CSV data, GitHub version control and Actions, Docker, and Render hosting. The matching model is not a generative AI service. The current project does not use an official SDC sponsor-provided GenAI API or cloud platform.

# 3. Technical Architecture & Implementation Plan

## 3.1 Conceptual Tech Stack

**Frontend:** React, TypeScript, and Vite provide the bilingual browser interface and profile review flow.

**API and application logic:** Python with FastAPI, Uvicorn, and OpenAPI provides the API, intake, role matching, pathway, SDG, and scenario features.

**AI / matching:** The full local resume-text workflow uses intfloat/multilingual-e5-small in quantized ONNX format for CPU embeddings and cosine-similarity matching. The hosted free demo uses synthetic profiles and does not provide the full resume model workflow.

**Data and storage:** Versioned JSON/CSV snapshots hold role, skill, trend, source, course, scenario, and SDG mapping data. The current prototype has no SQL database and does not retain uploaded resumes as user history.

**Build and deployment:** Docker packages the app; GitHub Actions runs repository checks; Render Free hosts the synthetic-profile demonstration.

**System flow:**

```text
User
  ↓
React / TypeScript / Vite (profile entry and review)
  ↓
FastAPI application
  ↓
Matching and pathway logic ← dated JSON/CSV role, trend, course, source, and SDG data
  ↑
Local E5 ONNX embeddings (full local resume workflow only)
  ↓
Ranked roles, skill gaps, evidence, learning options, SDG links, and scenarios
```

**SDC sponsor-provided services:** No official SDC sponsor-provided GenAI API or cloud platform is used in the current prototype. Render is a third-party hosting provider. ChatGPT/Codex assisted development and documentation only; neither is called by the deployed application for runtime matching.

## 3.2 Design-Thinking & Deployment Strategy

We shaped the prototype around the user journey in the project brief: describe current skills, understand changing opportunities, compare suitable roles, and choose a practical learning path. The interface explains match evidence, data sources and dates, skill gaps, SDG links, and scenario assumptions so users can question recommendations rather than treat them as decisions. Synthetic profiles support a privacy-conscious public demonstration; the local resume workflow includes text review and user confirmation before matching. Technical feasibility is supported by the working web/API architecture, repository automation, and a hosted synthetic demo. Before deploying resume analysis for real users, Phase 2 should test usability and accessibility with intended users, review privacy and data-retention controls, validate data rights and source freshness, and evaluate recommendation quality and potential bias. No formal user study, fairness assessment, or employment-impact measurement has yet been completed.


# 4. Preliminary Environmental & SDG Impact Framework

**Metric Category:** Career skills navigation and reskilling readiness (social/economic impact). FutureReady has no measured direct environmental benefit; no emissions or resource savings are claimed.

**Target SDG Sub-Target(s):** Primary: SDG 4, Target 4.4 — “By 2030, substantially increase the number of youth and adults who have relevant skills, including technical and vocational skills, for employment, decent jobs and entrepreneurship.” Supporting: SDG 8, Target 8.5 — “By 2030, achieve full and productive employment and decent work for all women and men, including for young people and persons with disabilities, and equal pay for work of equal value.” The prototype supports career exploration and skills planning; it does not claim to deliver employment outcomes.

**Current Problem Baseline:** The World Economic Forum’s 2025 survey of employers found that 63% identified skills gaps as a major barrier to business transformation; employers also expect 39% of workers’ core skills to change by 2030. These are global employer expectations, not Malaysia-specific worker outcomes. FutureReady has not yet collected a participant baseline; the Phase 2 pilot will record the same task measure before product use.

**Core Measurable KPI:** Percentage-point change in pilot participants who can complete a short, scored task: explain one recommended role, identify one skill gap, and select one linked learning option. Use the same assessment before and after using FutureReady; report numerator, denominator, and completion time.

**Phase 2 Impact Target:** In a small pilot of at least 10 consenting adult participants, achieve at least a 20-percentage-point improvement over the pre-use task pass rate and at least an 80% post-use pass rate. Treat this as an early usability and career-navigation signal, not proof of improved employment or SDG outcomes. Disaggregate results only where consent and sample size protect privacy.

**Sources:** World Economic Forum, The Future of Jobs Report 2025, skills outlook and workforce strategies, published 7 January 2025: https://www.weforum.org/publications/the-future-of-jobs-report-2025/3-skills-outlook/ and https://www.weforum.org/publications/the-future-of-jobs-report-2025/in-full/4-workforce-strategies/ . United Nations, SDG Goal 4, Target 4.4: https://sdgs.un.org/goals/goal4 . United Nations, SDG Goal 8, Target 8.5: https://sdgs.un.org/goals/goal8 .

# 5. Eligibility & Readiness Checklist

- [ ] All team members have completed the mandatory GenAI, Database, and Cloud Deployment upskilling workshops. Team leader: confirm attendance before ticking.
- [x] The project concept addresses a documented real-world problem and maps directly to SDG Targets 4.4 and 8.5 (see Section 4 and cited sources).
- [x] The proposed solution is a functional, deployed application. The public Render demo is configured for synthetic profiles; full resume-model analysis requires a properly provisioned local setup.
- [ ] All fields in this template have been completed within the stated word limits. Leave unchecked until team-specific declarations, sign-off, and remaining submission materials are completed.

# 6. IP & Originality Declaration

## 6.1 Pre-Existing / Prior-Owned Work

**Selection:** [TEAM LEADER MUST CONFIRM — tick Yes or No only after checking the official hackathon start date and project history.]

The FutureReady source repository, interface, data package, and prototype were already present when this submission form was prepared. The team must compare the creation dates of each item with the official hackathon start date and list the actual team member(s) who created or owned any pre-existing work. If applicable, disclose the relevant code, design, research, prototype, and documentation rather than describing the whole project as newly created.

## 6.2 Third-Party Code, Datasets, or Models

**Selection:** YES

| Name | Type | License / terms |
| --- | --- | --- |
| React, TypeScript, Vite, FastAPI, Uvicorn, NumPy, ONNX Runtime, Tokenizers, and other locked dependencies | Open-source code libraries and frameworks | Mixed; each package retains its own upstream license. See package.json, pnpm-lock.yaml, pyproject.toml, uv.lock, and requirements.lock. |
| intfloat/multilingual-e5-small and pinned Xenova/multilingual-e5-small quantized ONNX assets | Pre-trained embedding model | MIT; model revision and asset hashes are recorded in docs/model-notice.md. |
| Department of Statistics Malaysia / data.gov.my labour-force skills-related underemployment data | Public dataset | CC BY 4.0 as recorded in the project attribution file; retain attribution. |
| O*NET, U.S. Bureau of Labor Statistics, TalentCorp MYCOL, Arbeitnow job postings, and arXiv metadata | Public occupational, forecast, job-posting, or research-source facts/metadata | Source-specific terms apply. Attribution and reuse notes are in artifacts/api-server/data-package/ATTRIBUTION_AND_USE.md; public access does not imply unrestricted redistribution. |
| Course/provider catalogue metadata and United Nations SDG references | Third-party metadata and public reference text | Provider/source terms apply. The project stores selected metadata and links, not course content. |
| Project-supplied 65-role catalogue | Role and skill dataset | Upstream redistribution terms were not supplied with the repository; the team must confirm the catalogue owner’s license/permission before external redistribution. |

The project root Apache License 2.0 covers original FutureReady code and documentation only where no separate notice applies. It does not override third-party terms. See NOTICE, docs/model-notice.md, and the data-package attribution file.

## 6.3 Employment-Related IP Conflicts

**Selection:** [EACH TEAM MEMBER MUST CONFIRM — tick Yes or No after checking applicable employment, internship, and consulting agreements.]

If Yes, identify the affected member(s) and describe the relevant agreement or potential ownership claim. Do not include confidential contract text. If none of the team members is subject to such a claim, tick No.

# 7. Declaration

By submitting this proposal, the team leader confirms that the information provided is accurate to the best of the team’s knowledge and that the project is original work created during the SDC 2026 hackathon period. The team leader must verify the originality statement against the project history and the official hackathon dates before signing.

**Signature:** ____________________________________

**Name:** ________________________________________

**Date:** _________________________________________

