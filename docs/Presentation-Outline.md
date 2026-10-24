# FutureReady — Approved Presentation Outline

The ten-slide English copy below is the source of truth for the current presentation.

## FutureReady

From resume experience to career direction and credible learning resources.
- Local multilingual semantic matching
- 65 career descriptions, potential SDG contributions and source-reviewed courses

## The problem: career exploration is fragmented

- Students and career changers struggle to connect experience with technical role descriptions
- Learning resources are scattered across providers
- Unexplained scores and unclear course costs can mislead decisions
- Users need one transparent starting point—not an automated hiring verdict

## Who FutureReady is designed for

- Students and recent graduates exploring AI-related careers
- Early-career professionals and career changers comparing transferable experience
- Career advisers supporting authorized, human-led exploration
- English-first interface with an optional Chinese interface

## Scope: one connected exploration journey

- Upload a text-based PDF or DOCX, or paste experience text
- Review and edit the extracted text; inspect keyword evidence
- Compare the same input with all 65 role descriptions
- Select a career, read its SDG rationale and explore linked learning resources
- OCR, real-user accounts and hiring decisions are outside this demo

## How the matching works

- Local CPU inference with multilingual-e5-small
- Native 384-dimensional embeddings and cosine similarity
- Percentage = max(0, cosine) × 100; scores do not need to sum to 100%
- English or Chinese keyword recognition explains overlap without changing scores
- Match percentage is not hiring probability or skill mastery

## SDG alignment: learning, work and inclusion

- SDG 4.4: access to learning resources for job-relevant skills
- SDG 8.5: support informed career preparation—not guaranteed employment
- SDG 10.2: bilingual access and clearly stated learning costs
- All 65 roles also carry application-specific SDG goals, targets and source links
- Potential alignment is not UN endorsement or measured social impact

## A transparent full-stack architecture

- React + TypeScript + Vite for the interface
- WebGL/GLSL orb and Canvas 2D particle entrance
- FastAPI for document extraction, matching, courses and demo sessions
- JSON/CSV data snapshots and a locally generated career-vector index
- OpenAPI contracts and generated TypeScript clients; no SQL server required

## Sources and learning recommendations

- The project-owner-supplied CSV is the 65-role matching catalogue
- Courses link to official providers with reasons, cost conditions and review dates
- UN goal pages support curated role-level SDG explanations
- O*NET, BLS, arXiv and Malaysian sources remain separate historical reference data
- Provenance and redistribution caveats are recorded in README

## A working demo, with explicit safety boundaries

- Server-validated shared demo sign-in, session restoration and logout
- PBKDF2-HMAC-SHA256: 600,000 iterations and a random salt
- HttpOnly cookie, two-hour in-memory sessions and login rate limits
- Resume processing requires consent; files, extracted text and resume vectors are not retained
- Public demo identity is not production authentication or private-data authorization

## Verified delivery—and responsible use

- 65 backend regression tests passed
- Independent source-package installation, fresh model download and index creation passed
- Interface regeneration, TypeScript checks, production build and full HTTP workflow passed
- GitHub-ready source includes data, frontend, backend, interface definitions and setup instructions
- First setup needs internet; inference runs on the application backend, not in the browser
