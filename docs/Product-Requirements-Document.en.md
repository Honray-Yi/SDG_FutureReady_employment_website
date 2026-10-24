# Product Requirements Document — FutureReady

English submission edition | Current implemented demo

## 1. Problem

Students, recent graduates and career changers often struggle to connect their experience with AI-related career descriptions. Technical terminology makes comparison difficult, while learning resources are scattered across providers with different costs and prerequisites. Unexplained match scores can also be mistaken for hiring probability or a complete assessment of ability.

FutureReady provides one connected starting point: upload or paste a resume, inspect the extracted text, compare it with career descriptions, then explore source-reviewed learning resources associated with a selected career.

The primary user need is: “Help me understand what the system read, which careers are semantically related to my experience, and where I can begin learning.”

The product supports human-led exploration. It does not make recruitment decisions, guarantee employment or certify skill mastery.

### Product objective and success criteria

- Complete resume upload → text review → local semantic analysis → ranked careers and percentages → selected-career courses without switching to unrelated synthetic results.
- Make score meaning, data provenance, course access conditions and potential SDG contributions visible.
- Provide a reproducible GitHub setup without Replit-only services, a SQL database or an external inference API key.
- Evaluate operation through automated checks and end-to-end smoke tests. Recommendation accuracy and employment impact require separate human evaluation; neither has been measured here.

## 2. SDG Alignment

### SDG 4 — Quality Education

Target 4.4 concerns skills relevant to employment, decent jobs and entrepreneurship. FutureReady supports this direction through official learning links, explanations of relevance and clear access conditions. It helps users find a starting point; it does not award qualifications or verify learning outcomes.

Official reference: https://sdgs.un.org/goals/goal4

### SDG 8 — Decent Work and Economic Growth

Target 8.5 concerns productive employment and decent work. Comparing experience with role descriptions can support informed career preparation and transition. Semantic similarity is not evidence that the product increases employment, pay or job quality.

Official reference: https://sdgs.un.org/goals/goal8

### SDG 10 — Reduced Inequalities

Target 10.2 concerns social and economic inclusion. English/Chinese access and transparent learning costs can reduce information barriers. This is a design alignment, not a measured reduction in inequality or proof of model fairness.

Official reference: https://sdgs.un.org/goals/goal10

### Occupation-specific SDG contributions

All 65 occupations include curated potential SDG mappings. Career catalogue and ranking entries show goal badges; details include goal names, target identifiers, conditional explanations and official UN source links. The interface defaults to English and translates these explanations when Chinese is selected.

Mappings cover goals 3, 4, 7, 8, 9, 10, 11, 12 and 16 where appropriate to the occupation. For example, healthcare applications may support SDG 3, while responsible technical innovation may support SDG 9. A role title alone does not establish positive impact: the application, governance and implementation matter.

These are project-authored interpretations of potential alignment, not UN endorsement, certification or measured impact.

## 3. Target Users

- Students and recent graduates: explore how coursework, projects and internships relate to AI-related careers.
- Early-career professionals and career changers: compare existing experience with a defined role catalogue and identify learning starting points.
- Career advisers and educators: support authorized, human-led exploration and explain the limitations of scores and sources.

Users need a modern browser, access to the running application and a text-based PDF/DOCX resume or experience text. They must have permission to process the submitted material and consent to temporary backend processing. The demo is not intended for confidential or third-party personal records.

These are intended user groups, not claims of validated adoption or measured satisfaction.

## 4. Scope

### Included in the current demo

- A working public shared demo sign-in on the welcome page, session restoration and logout.
- Text-based PDF and DOCX upload, or direct text entry; extraction, editable text review, consent and explicit error states.
- Backend CPU inference using a pinned quantized multilingual-e5-small model with native 384-dimensional embeddings.
- Semantic comparison with all 65 catalogue occupations, sorted career results, raw cosine values and one-decimal match percentages.
- Independent interface-language and keyword-recognition settings: English defaults, with Chinese options.
- Keyword evidence and overlap explanations from a controlled bilingual glossary; these do not change the semantic scores.
- Career-specific potential SDG badges, rationales, target identifiers and official references.
- Course recommendations based on explicit themes in the selected career description, with official links, reasons, costs, prerequisites and review metadata where recorded.
- Clear loading, unavailable-model, invalid-document and resource-limit states; no fabricated-score fallback.
- GitHub-ready frontend, backend, interface definitions, data snapshots, lockfiles, setup scripts and verification instructions.

### Resource limits

- Maximum upload: 8 MB; maximum PDF length: 20 pages.
- Maximum extracted text: 100,000 characters; maximum model input: 12,000 tokens.
- Inputs exceeding supported limits are rejected explicitly rather than silently treated as complete.
- CPU capacity, latency and concurrent availability depend on the host. No universal response-time guarantee is claimed.

### Excluded from this demo

- OCR for scanned or image-only resumes, handwriting recognition and arbitrary document formats.
- Private real-user accounts, registration, email verification, password reset, MFA, persistent user histories and cross-device resume storage.
- Automated hiring decisions, skill-mastery assessment, clinically or legally authoritative advice, and guaranteed career outcomes.
- A measured probability model for employment, a diagnosis of individual skill gaps or a complete prerequisite learning plan for every occupation.
- Live job placement, application submission, course checkout, certificates and real-time labour-market coverage.
- External analysis services such as OpenAI. No inference API key is required.
- Production private-data authorization and a production privacy/compliance programme.

Historical synthetic dashboard, radar and learning-path pages remain separate reference demonstrations. Their illustrative metrics are not outputs of the resume-matching workflow.

## 5. Key Features

### F1. Public demo access

The main welcome form validates the public shared demo credentials on the backend. Incorrect credentials receive a generic error. Valid access retains the particle entrance, restores the session after refresh and provides logout.

The account exists to demonstrate a login flow, not to identify a private user. The public credentials and complete explanation are in README; users should not enter personal passwords.

### F2. Resume intake and review

The application extracts document body text and allows the user to inspect and edit it before analysis. Processing requires explicit consent for real input. Invalid, unsupported, image-only or oversized documents fail clearly.

Text extraction does not imply structured extraction of a person's name, education, experience and skill proficiency. Supported glossary terms are evidence, not a full resume parser.

### F3. Local semantic comparison

Both resume and career descriptions use the same multilingual embedding pipeline: normalization, tokenization, bounded chunks, attention-mask mean pooling and vector normalization. Long-input chunk vectors are combined using content-token weights.

The pinned intfloat/multilingual-e5-small model uses quantized ONNX weights for CPU inference. The backend—not the browser—runs the model. First setup downloads public model assets; resume inference does not call an external analysis API.

Careers are ranked by cosine similarity. Displayed percentage is max(0, cosine) × 100, rounded to one decimal, using the API's rounded cosine value. The percentages need not sum to 100. They are not accuracy, hiring probability or skill mastery.

Missing assets or an unavailable model generate explicit errors. The system does not substitute fixed demo numbers.

### F4. Independent bilingual settings and evidence

The interface defaults to English and can switch to Chinese. Keyword recognition separately defaults to English and can switch to Chinese aliases. Interface translation does not change an existing semantic score. Changing keyword mode clears stale analysis and requires a new analysis.

The glossary handles known aliases, English boundaries and evidence locations. It does not claim unrestricted recognition of every technical term. Language preferences may be stored locally in the browser; resume text is not stored there by this flow.

### F5. Career results and SDG explanations

Ranked results and the occupation catalogue expose role names, descriptions and curated SDG badges. Selecting a role opens its explanations and learning resources. The selected stable role identifier links result details and course requests; the interface does not redirect to a disconnected synthetic persona.

English display names are a presentation layer. The canonical occupation descriptions used for embeddings remain unchanged.

### F6. Source-reviewed courses

The course dataset contains 22 source-reviewed records. Recommendation rules use the eligible reviewed subset; this does not mean that every record is recommended for every career.

Selected-career recommendations explain a relevant theme and link to the official provider. Recorded access conditions distinguish free learning material from paid certificates, compute, APIs or other optional costs. Recommendations are foundations related to role descriptions, not proof of a user's missing skills or guaranteed advanced specialization.

Source review dates are snapshots. Provider availability, prices and prerequisites can change; users must verify the official page before enrolling.

### F7. Consistent states and data flow

The same submitted input drives extraction and analysis. Results identify a selected career; that identifier drives the course request. Editing input or changing analysis settings invalidates stale results. Loading, consent, errors, empty states and unavailable services are surfaced instead of displaying unrelated fallback scores.

## 6. Architecture and Interfaces

- Frontend: React, TypeScript and Vite; CSS for responsive layout.
- Visual entrance: WebGL and GLSL for the rotating orb and lighting; Canvas 2D for the FutureReady particle entrance.
- Backend: Python and FastAPI for document extraction, local matching, course data and demo login.
- Interface contract: OpenAPI definitions with generated TypeScript clients and schemas.
- Data: versioned CSV/JSON snapshots and a generated local career-vector index. The main workflow requires no SQL server.
- Local orchestration: scripts/dev_local.py starts the frontend and FastAPI with a same-origin frontend proxy.
- Presentation: a separate React slides package with ten approved English slides; it does not alter the main website.

Source is separated into frontend pages/components, backend services, interface definitions, catalogue/data packages and documentation. README identifies the files to edit for individual visual, backend, course and SDG changes.

## 7. Data Sources, Rights and Reproducibility

- Career matching catalogue: the project-owner-supplied 65-row CSV. Its upstream redistribution licence was not supplied; the owner must establish rights before public redistribution.
- English occupation labels and summaries: project-authored display material, separate from the canonical vector corpus.
- Learning resources: project-curated metadata and official provider links; no full third-party course material is bundled.
- SDG explanations: project-authored conditional mappings linked to https://sdgs.un.org/goals .
- Model: intfloat/multilingual-e5-small and the Xenova quantized ONNX distribution; pinned revision, hashes, MIT notices and download instructions are documented.
- Historical references: O*NET, BLS, arXiv, Arbeitnow, Malaysian DOSM/data.gov.my, MyCOL, MASCO and official programme records have individual provenance and use caveats in README and the data package. They are not substitutes for the canonical 65-role embedding catalogue.
- Synthetic profiles, scenarios and derived trend data are labelled reference material, not observed user outcomes.

Runtime model files, generated indexes, account caches, secrets and sessions are excluded from GitHub source. Setup regenerates necessary caches. Lack of model files in the source ZIP is intentional, not a missing database.

The root Apache-2.0 license applies to original project source code and project-authored documentation, as scoped in NOTICE. It does not relicense third-party data, the supplied 65-role catalogue, model assets, dependencies, fonts, images, logos or challenge materials. The upstream redistribution license for the supplied 65-role catalogue was not provided and must be confirmed by its owner. Consult README, NOTICE, model notices and source attribution records before redistribution.

## 8. Authentication, Privacy and Security Boundaries

Demo password verification uses PBKDF2-HMAC-SHA256 with 600,000 iterations, a random 16-byte salt and a 32-byte derived hash. The runtime JSON account file contains the hash and salt, not a plaintext password. It is written atomically with restrictive file permissions where supported. The demo password is nevertheless public by design.

Sessions use random opaque tokens in HttpOnly cookies. The backend retains only a digest and expiry in memory; sessions expire after two hours and are invalidated by logout or backend restart. Account-cache files are local runtime data, not a durable production identity database.

Login attempts are rate-limited. Authentication mutations use an explicit request header and reject cross-site browser requests. Cookie policy accounts for HTTPS and preview proxy behaviour; the full implementation and limitations are in README.

Uploaded files, extracted resume text and resume vectors are processed transiently and are not retained by the application. Processing still sends data to the application backend; it is not browser-only offline computation.

Catalogue and analysis APIs intentionally remain public with their consent/resource checks. The shared demo UI gate is not authorization for private records. Production deployment with real users requires a separately designed identity, authorization, storage, privacy, abuse-prevention and operational-security programme.

## 9. Acceptance and Verification

- Upload a valid text-based DOCX or PDF, review extracted text, consent and receive genuine local-model results for all 65 roles.
- Inspect keyword evidence, select a career and receive courses associated with that career.
- Confirm all 65 occupations have SDG mappings and that English/Chinese display settings do not silently replace the scoring method.
- Check incorrect login, valid login, session restoration and logout with backend validation.
- Reject unsupported documents and missing-model states without fabricated scores.
- Follow README from a freshly extracted source archive with no Replit secrets: locked dependencies, fresh model download, index creation and local startup.
- Regenerate interfaces, run type checks and backend tests, build the frontend and exercise the HTTP upload → analysis → courses workflow.

Completed application checks include 65 backend regression tests, interface generation, workspace TypeScript checks, a production frontend build and browser checks of the changed primary flow. Independent source-archive verification also exercised a fresh dependency setup, public model download, index creation and the HTTP workflow.

These checks establish tested functionality in the documented environment. They do not establish recommendation accuracy, universal compatibility, production security, guaranteed uptime or measured social impact. The source package includes commands for repeating validation; internet access and compatible runtimes are required.

## 10. Delivery and Maintenance

- README.md: requirements, installation, demo credentials and authentication logic, data sources, limits and editing guide.
- docs/Product-Requirements-Document.en.md: maintained English source for this Word document.
- docs/Presentation-Outline.md: the approved ten-slide copy.
- artifacts/future-ready-presentation/: editable presentation source.
- docs/deliverables/: generated Word and PowerPoint copies included with the GitHub package.
- scripts/export_prd.py and scripts/export_github.py: reproducible document and source packaging.
- scripts/verify_release.py: independent extracted-package validation.

The Word document and slides describe the current implemented demo, explicitly distinguish reference data and synthetic pages, and preserve the demo-versus-production boundary.
