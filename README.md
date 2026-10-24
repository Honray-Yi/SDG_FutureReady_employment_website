# FutureReady

> **Live Prototype:** [Open the FutureReady demo](https://future-ready-demo.onrender.com/) — the hosted free instance is for synthetic profiles and career matching. Do not upload a real résumé. The full local résumé-embedding workflow needs the model download and at least 4 GB of memory; see [local setup](#本地启动).

[English PRD](docs/Product-Requirements-Document.en.md) · [Approved slide copy](docs/Presentation-Outline.md) · [算法与接口说明](docs/semantic-matching.md)

**面向职业探索的交互式 Web 项目：用本地多语言文本向量，将简历经历与 65 个职业进行语义匹配，再查看对应的基础学习课程。**

React + TypeScript 前端，FastAPI 后端；保留 WebGL 光球及 Canvas 粒子入场动画。分析使用开源 `multilingual-e5-small`，不调用 OpenAI 或其他外部推理 API，不需要分析 API Key。

> 当前是职业探索演示项目。上传个人简历前必须确认授权，建议去除联系方式等无关隐私。原文件、提取文本及简历向量不持久保存，不发送至外部分析服务。匹配百分比不是技能掌握率或录用概率。公开演示登录已接通，但不是真实用户认证；只使用下方演示凭据，请勿输入真实密码。

## 从 GitHub / 源码 ZIP 开始

这是完整的前后端 monorepo，不是只有页面截图或前端模板。源码包包含业务数据、Python 后端、OpenAPI 定义、生成客户端、React 前端、锁定依赖和启动/验证脚本。保持下面的文件夹结构，**不要只上传 `artifacts/future-ready`**。

- 在解压后的 `FutureReady/` 根目录运行命令；下载 GitHub ZIP 时，根目录名称可能为 `FutureReady-main/`。
- 基准环境：**Linux / macOS 或 Windows WSL；Node.js 22.12+、pnpm 10、Python 3.13、uv**。安装工具：[Node.js](https://nodejs.org/)、[pnpm](https://pnpm.io/installation)、[uv](https://docs.astral.sh/uv/getting-started/installation/)。
- 需要可访问 npm、PyPI 和 Hugging Face；首次下载约 135 MB 模型文件，建议至少 4 GB 可用内存、2 GB 可用磁盘。网络、防火墙及机器配置不是源码包能保证的条件。
- **无需 PostgreSQL、MySQL、OpenAI Key、Replit 账号或其他分析 API Key。** 本项目实际使用的“数据库”是包内 JSON/CSV 快照及本地派生索引，见下方完整来源表。`lib/db` 和 API 下旧 TypeScript 服务骨架不参与当前 FastAPI 运行，不需要设置 `DATABASE_URL`。
- 模型权重超过普通 GitHub 单文件大小限制，不放入源码仓库；下载脚本固定公开版本并校验 SHA-256，不会静默换成其他模型。

## Submission package

| Submission item | Status and location |
|---|---|
| Complete, functional repository | This repository contains the frontend, FastAPI backend, datasets, setup, and verification files. |
| Proof of Replit utilization | Upload evidence to `submission/evidence/replit/`. |
| Proof of RunPod utilization | Team to confirm; if applicable, upload to `submission/evidence/runpod/` and update the declaration. |
| Completed submission template | `submission/completed-submission-template.docx` and `.md`. Enter team identity fields before submission. |
| Completed tech tools declaration | `submission/tech-tools-declaration.docx` and `.md`. Confirm RunPod status and sign before submission. |
| Pitch deck slides | `docs/deliverables/FutureReady-Project-Presentation.pptx`. |
| YouTube product demo | Paste the URL into `submission/demo/youtube-demo-link.txt` after uploading the video. |
| Live prototype | https://future-ready-demo.onrender.com/ (synthetic-profile demo). |
| Product requirements document | `docs/deliverables/FutureReady-Product-Requirements-Document.docx` and `docs/Product-Requirements-Document.en.md`. |
| Apache License 2.0 | `LICENSE`; its scope and exclusions are described in `NOTICE`. |

The original source code and project-authored documentation are licensed under Apache-2.0. Third-party data and assets keep their own terms. In particular, the upstream redistribution license for the supplied 65-role catalogue was not provided; the Apache license does not grant rights to it.

## 功能与边界

- 经授权的简历文本粘贴、文字版 PDF / DOCX 后端文本提取，以及合成测试示例。
- 中英文文本向量，384 原生维度，CPU 本地推理。
- 65 个职业的真实余弦相似度排序、职业目录和详情。
- 语义匹配百分比（非概率）；所选职业的来源可追溯基础课程、推荐依据、官网链接和核验日期。
- 英文默认界面，可切换简体中文；65 个职业均有英文展示名称和摘要。界面偏好只保存于当前浏览器。
- 独立的关键词识别语言选择：默认英文词表，可切换中文词表。展示识别词和与所选职业描述的交集；关键词不改变语义分数，也不证明技能熟练度。
- 固定模型版本、SHA-256 校验、职业向量缓存一致性检查。
- 显式错误和资源限制；模型缺失不会返回虚构分数。
- 不保证完整覆盖每个职业的专科技能；真实登录与生产隐私合规仍是独立上线条件。

## Demo sign-in / 演示登录

The welcome-page form now performs a real **server-side demo credential check**, creates an HttpOnly session cookie and restores the signed-in UI after refresh. It is a **public shared demonstration**, not production authentication.

| Public demo credential | Value |
|---|---|
| Email | `demo@futureready.example` |
| Password | `FutureReadyDemo2026!` |

Click **Fill demo credentials**, then **Log in to demo**. Incorrect credentials are rejected; successful login plays the existing particle entrance and opens the resume explorer. **Log out** invalidates the server session, removes the cookie and unmounts the active analysis screen. Do not enter a real personal password. The password above is intentionally public and must never be reused for a private account.

### Login and session logic / 登录逻辑

1. The browser sends JSON to `POST /api/demo-auth/login` using same-origin `fetch`, `credentials: include` and `X-Demo-Action: 1`. Nothing authenticating is written to localStorage.
2. FastAPI validates bounded inputs, normalizes the email, recomputes the password hash and uses `hmac.compare_digest`. Unknown emails and wrong passwords receive the same generic 401; no password, salt or hash is returned to the browser.
3. On success the server generates a cryptographically random 256-bit opaque token. Only its SHA-256 digest and expiry are kept in backend memory. A prior session presented during login is invalidated (session rotation).
4. The application sets cookie `fr_demo_session` as `HttpOnly`, `SameSite=Lax`, `Path=/`, with a fixed **2-hour** maximum lifetime; `Secure` is enabled for HTTPS, including HTTPS forwarded by the preview proxy. HTTP localhost development does not use `Secure`. **Preview proxy caveat:** the external Replit preview response/browser was observed with `SameSite=None; Secure; HttpOnly`, although the backend sets `Lax`. Replit manages preview cookies through its proxy ([documentation](https://docs.replit.com/help/troubleshooting/auth)); verify the final browser attributes in each deployment. The mutation-header and cross-site checks below are required and do not rely solely on SameSite.
5. `GET /api/demo-auth/me` validates the cookie on page load and restores the app. The UI also checks once per minute and when the app regains focus. Expired or invalid sessions return to the login page.
6. `POST /api/demo-auth/logout` deletes the server record and expires the cookie. Auth responses use `Cache-Control: no-store`. Mutation requests require the custom header and reject `Sec-Fetch-Site: cross-site`; CORS is not opened for cross-origin login.
7. Login attempts are limited to **8 per 5 minutes per backend-visible client IP**, including successes, with at most 1,000 active sessions. A shared proxy may make this a shared demo limit. Backend restart immediately invalidates all sessions; login again.

### Password storage / 用户密码保存方式

Backend: `artifacts/api-server/backend/demo_auth.py`. On first login, if absent, it creates `.cache/futureready/demo-auth/users.json`, containing only the fixed demo account.

- Algorithm: **PBKDF2-HMAC-SHA256**, **600,000 iterations**, a fresh **16-byte cryptographic random salt**, and a **32-byte derived hash**.
- Stored fields: schema version, demo user ID/email/display name, algorithm, iteration count, salt (hex) and hash (hex). **No plaintext password or session token is stored in this JSON file.**
- The file is atomically written and uses owner-only `0600` permissions. Its directory is excluded from Git, published source files and the GitHub export. Corrupted account files cause an explicit error, not silent reseeding or a login bypass.
- The initial password is intentionally present in the source/UI/README **only because this is a public demo account**. Never extend this bootstrap pattern to private accounts.
- Existing hash/salt survive a local backend restart, but sessions do not. The local cache is **not a durable production user database**; redeploying/replacing a machine may recreate it.

**Security boundary:** this login demonstrates password verification and browser sessions. There is no real-user registration, email verification, password reset, MFA or per-user resume/history storage. The existing catalogue and analysis APIs intentionally remain public and retain their own consent/resource limits; signing in is an interface gate, **not authorization for private backend data**. Do not deploy this public shared account as protection for real user accounts or sensitive records. Production requires a real identity provider, backend authorization, durable account/session storage, correct TLS/proxy trust configuration and privacy review.

UI implementation: `src/demoAuth.ts`, `src/components/welcome/WelcomeGate.tsx` and the app's logout control. The default English interface and separate Chinese option remain unchanged.

## Career → SDG contribution mapping / 职业与 SDG

All **65 roles** include reviewed, explicit **potential** SDG alignments in the catalogue, semantic-ranking rows and role details. English is the default; Chinese interface mode translates the goal titles and rationale. Each detail links to the official UN goal and identifies the target (for example 9.5 for research capacity, 4.4 for job-relevant skills, or 3.8 for healthcare).

Mapping source: `artifacts/api-server/backend/sdg_mapping.py`; display: `src/components/explorer/SdgContributions.tsx`. Modify `GROUPS` for role assignments and `CATEGORIES` for the goal/target/conditional rationale. Coverage tests require all catalogue roles to have a mapping and prevent misspelled role assignments.

These are curated project interpretations, **not UN endorsement, measured impact or a claim that every application benefits society**. Rationale explicitly conditions contributions on responsible deployment, validation, inclusion or safety. Goal definitions: [UN Sustainable Development Goals](https://sdgs.un.org/goals). This metadata does **not** modify the embedding source, scores, rankings or course selection.

“本地”指应用后端：浏览器仍会把输入发送给你运行的 FastAPI 服务，不是浏览器离线计算。首次安装需要下载公共模型文件；推理不调用外部分析服务。

## 技术栈

| 部分 | 技术 |
|---|---|
| 页面及交互 | React、TypeScript、Vite |
| 布局 | CSS、Tailwind CSS |
| 动画 | WebGL / GLSL、Canvas 2D |
| 后端 | Python、FastAPI |
| 模型执行 | ONNX Runtime CPU、Hugging Face Tokenizers |
| 向量计算 | NumPy、余弦相似度 |
| 包管理 | pnpm workspace、uv |

## 本地启动

建议使用上述基准环境，并确保 `node --version`、`pnpm --version`、`python --version`、`uv --version` 都可执行。

在仓库根目录执行：

```bash
# 1. 安装依赖
pnpm install --frozen-lockfile
uv sync --frozen --no-dev --no-install-project

# 2. 首次下载公开、固定版本的模型；无需 Replit 或 API Key
uv run --no-sync python artifacts/api-server/backend/local_model_assets.py --from-hub

# 3. 生成 65 个职业的向量索引
uv run --no-sync python artifacts/api-server/backend/build_job_index.py

# 4. 启动前后端
uv run --no-sync python scripts/dev_local.py
```

打开 **http://localhost:5173**，点击 **Fill demo credentials**，再点击 **Log in to demo**。后端在 `8080` 端口；本地启动器为 Vite 启用 `/api` 与 `/intake` 开发代理，避免前后端跨域或请求落到错误服务。`Ctrl+C` 关闭两项服务。端口冲突时可使用：

```bash
uv run --no-sync python scripts/dev_local.py --frontend-port 5174 --backend-port 8082
```

安装完成后，模型保存在 `.cache/`，后续启动不需重新下载。没有 GPU 也能运行；仍会消耗服务器 CPU 和内存。网络无法访问模型库时，首次下载会明确失败，不会改用远程推理。

`--no-install-project` 是有意的：直接运行仓库脚本，不安装模板遗留的 Python CLI 包。`uv.lock` 锁定完整 Python 依赖；`requirements.lock` 是带哈希的等价第三方依赖导出，用于独立源码验证。不要使用无锁的 `pip install fastapi ...` 代替这套依赖。

### 在 Replit 中

继续使用现有托管 workflows，不要同时运行本地启动器。已配置 App Storage 的环境可执行：

```bash
python artifacts/api-server/backend/local_model_assets.py
python artifacts/api-server/backend/build_job_index.py
```

这条恢复路径依赖 Replit 资产存储配置；普通 GitHub 克隆请使用前面的 `--from-hub` 路径，无需这些平台配置。

## 测试与构建

```bash
# Python 回归与实际本地模型测试
uv run --no-sync python -m unittest discover -s artifacts/api-server/backend -p 'test_*.py' -q

# 前端检查
pnpm --filter @workspace/api-spec run codegen
pnpm run typecheck

# 前端生产构建（POSIX shell）
PORT=5173 BASE_PATH=/ NODE_ENV=production pnpm --filter @workspace/future-ready run build
```

实际模型测试会禁止 Python socket 外部连接，验证分析结果、重复性和完整目录排名。若尚未下载模型，该项测试会明确跳过，不能把跳过当作模型验证成功。部分测试会主动模拟缺失数据并输出告警，以最终测试汇总为准。

前端产物在 `artifacts/future-ready/dist/public/`。生产服务器还需运行 FastAPI，并将 `/api`、`/intake`、`/intake-static` 转发至后端；Vite 的开发代理不会进入静态构建。不要直接将这个全栈项目当作 GitHub Pages 静态站点部署。

### 验证真实启动与源码包

完成安装和索引构建后，可在另一终端运行下面的独立 HTTP 检查。它会使用临时空闲端口启动本地前后端，验证代理、演示登录/会话/退出、DOCX 上传、真实本地模型的 65 职业排名、SDG 和课程，然后关闭测试进程：

```bash
uv run --no-sync python scripts/smoke_local.py
```

要测试“源码 ZIP 本身是否完整”，运行：

```bash
python scripts/export_github.py
python scripts/verify_release.py
```

后者会解压到 `generated-artifacts/github-verification-*/FutureReady/`，独立安装 Node 依赖和带哈希的 Python 依赖（使用临时 `--target` 目录，不复用本项目 Python 包），重新从公开来源下载模型，构建索引、跑回归、重新生成接口、检查类型、构建前端并检查完整 HTTP 流程。还会检查 Slides 与确认文案一致、Word/PPTX 文件完整及 Slides 构建。它不复用当前工作区的模型缓存，也不需要平台 Secrets；需要联网及额外磁盘空间。结果写入 `generated-artifacts/GitHub-Verification.json`，只有所有步骤全部通过时 `complete` 才为 `true`。

GitHub 的 `.github/workflows/verify.yml` 会在 push / pull request 时运行对应安装、模型、测试、构建和 HTTP 检查。工作流需要能访问依赖下载站点；是否通过以你自己的 GitHub Actions 运行结果为准。

## 目录与修改位置

```text
artifacts/
  future-ready/             React 页面、动画、样式
  future-ready-presentation/ 独立的 10 页英文 Slides，可编辑源码
  api-server/
    backend/                FastAPI、文档解析、模型执行、测试
    catalogue/              职业文本目录
    data-package/           现有结构化演示数据及来源记录
    legacy-package/         历史演示所需数据，不是语义分析的备用结果
    module1-web/            现有 intake 页面
lib/                        接口规范、生成客户端及原有共享包
scripts/
  dev_local.py              普通电脑上的前后端启动器
  export_github.py          导出干净的 GitHub 源码 ZIP
  smoke_local.py            验证独立启动、代理、登录、上传、排名、SDG 与课程
  verify_release.py         从源码 ZIP 零缓存验证完整项目
docs/
  Product-Requirements-Document.en.md  当前英文 PRD
  Presentation-Outline.md   用户确认的逐页英文文案
  deliverables/            当前 Word 和 PowerPoint 成品
  semantic-matching.md      算法、数据流、限制及逐功能修改位置
  model-notice.md           模型来源、固定版本及 MIT 声明
.github/workflows/
  verify.yml                GitHub 自动安装、测试与构建检查
requirements.lock           带 SHA-256 哈希的完整 Python 第三方依赖
release-manifest.json       仅在导出的源码包中生成，记录逐文件大小与 SHA-256
```

**只改某个按钮或视觉效果：** 从 `artifacts/future-ready/src/components/ResumeExplorer.tsx`、`components/explorer/` 及对应 CSS 入手。  
**只改分析逻辑：** 修改 `backend/semantic_matching.py`；模型执行在 `local_encoder.py`，缓存和目录配置各自独立。  
**改接口：** 同步 `lib/api-spec/openapi.yaml`，再执行 `pnpm --filter @workspace/api-spec run codegen`。

更改职业文本、模型或向量处理规则后，重启后端并显式重建索引：

```bash
uv run --no-sync python artifacts/api-server/backend/build_job_index.py --rebuild
```

## 项目文档与 Slides

- [英文 Word PRD](docs/deliverables/FutureReady-Product-Requirements-Document.docx)：包含官方要求的 Problem、SDG Alignment、Target Users、Scope、Key Features，并补充架构、来源、隐私、验收和演示限制。
- [10 页英文 PowerPoint](docs/deliverables/FutureReady-Project-Presentation.pptx)：使用已确认的逐页文案；可直接用于项目展示。
- PRD 的维护源是 `docs/Product-Requirements-Document.en.md`。运行 `python scripts/export_prd.py` 会输出 `generated-artifacts/FutureReady-Product-Requirements-Document.docx`；更新交付时将其复制到 `docs/deliverables/`。
- `docs/Product-Requirements-Document.md` 是标明已归档的旧中文规划参考，不是当前演示范围的说明。
- Slides 的逐页文案在 `docs/Presentation-Outline.md`，视觉和页面在 `artifacts/future-ready-presentation/src/pages/slides/`，顺序在 `src/data/slides-manifest.json`。修改一页不需要修改主网站或后端。

安装 Node 依赖后，可单独启动 Slides，不需要 Python、模型或登录：

```bash
pnpm --filter @workspace/future-ready-presentation run dev
```

普通本机默认访问 `http://localhost:5174`。Slides 首页支持键盘导航；`/slide1` 至 `/slide10` 是单页，`/allslides` 是完整展示。平台预览通过配置的路径前缀访问。

```bash
python scripts/verify_presentation.py
pnpm --filter @workspace/future-ready-presentation run validate-slides
pnpm --filter @workspace/future-ready-presentation run build
```

Word/PPTX 成品不随源码修改自动刷新。更新源文案或版式后须重新生成对应成品，再运行文件与文案检查；Markdown PRD、Slides 源码和成品都在此次源码 ZIP 中。

## 上传到 GitHub

现有仓库可推送至你自己的 GitHub 仓库；不要盲目替换已有远程地址：

```bash
git init  # 从源码 ZIP 解压的新目录需要初始化；已有仓库无需重复执行
git remote -v
git status
# 确认忽略规则及待提交文件，不提交密码、密钥或用户资料
git add README.md docs scripts artifacts lib src package.json pnpm-lock.yaml \
  pnpm-workspace.yaml pyproject.toml uv.lock requirements.lock tsconfig.json \
  tsconfig.base.json .gitignore .npmrc .github
git diff --cached --stat
git commit -m "Prepare FutureReady for GitHub"
# 首次连接时，将下面地址替换为你创建的真实仓库地址
git remote add origin https://github.com/YOUR_USERNAME/FutureReady.git
git push -u origin HEAD
```

如果只需要干净的源码包：

```bash
python scripts/export_github.py
```

生成的 `generated-artifacts/FutureReady-GitHub.zip` 排除了模型缓存、依赖、构建产物、Git 历史、会话、代理记忆和旧实验归档，不会改动原项目。解压后的顶层目录就是仓库根目录。单纯 `git add` 的忽略规则不会删除以前已跟踪的文件；公开现有 Git 历史前仍需自行检查历史内容。

## 数据与许可

### 全部数据库 / 数据文件及来源

以下路径均相对于 `artifacts/api-server/`。所有运行必需的原始业务快照随源码包提供；外部来源保留官网链接，不要求启动时重新采集。快照不是实时招聘信息，也不是新增的 SQL 数据库。

| 文件 / 数据组 | 来源及用途 | 限制 / 许可 |
|---|---|---|
| `catalogue/job_list.csv`：65 个职业及中文描述 | 项目所有者提供的职业 CSV；当前 embedding 的唯一职业文本来源 | 上游作者/许可未随原文件提供，不冒充 O*NET 官方目录；对外再分发前由所有者确认使用权 |
| `catalogue/job_english.json` | 项目整理的 65 个英文名称和介绍摘要 | 仅展示/搜索，不替换向量原始语料，不是外部官方职业认证 |
| `data-package/data/courses.json`：22 条课程元数据；`evidence/course_content_verification.json` | 各课程提供者官网；标题、官网链接、费用条件及来源核验记录随数据提供 | 只提供元数据和跳转，不打包课程内容；证书、托管 API 或计算资源可能收费 |
| `data-package/data/roles.json`、`taxonomy_crosswalk.json` | [O*NET](https://www.onetcenter.org/database.html) 参考标题及项目人工映射；用于独立结构化演示 | 美国职业参考，不是当前 65 职业评分数据；参见 [O*NET 许可与署名](https://www.onetcenter.org/license_db.html) |
| `occupation_outlook.json` | [美国 BLS 职业预测](https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm) 的少量事实与引用 | 长期预测，不是已经发生的增长，不代表马来西亚市场 |
| `jobs_snapshot.json`、`evidence/jobs_*.json` | [Arbeitnow 公共招聘 API](https://www.arbeitnow.com/api/job-board-api) 历史快照/采集证据 | 欧洲导向便利样本，不是全球或马来西亚普查；保留职位原始链接并遵守来源当前条款 |
| `research_counts.json`、`evidence/research_*.json` | [arXiv API](https://info.arxiv.org/help/api/user-manual.html) 的公开元数据聚合计数 | 不打包论文全文或作者档案；研究关注度不等于劳动力需求 |
| `trend_signals.json`、`skills.json`、`skill_dictionary.json`、`scenarios.json` | 项目基于引用记录编写的技能分类、派生趋势和演示情景 | 含人工假设；与简历 embedding 排名分开，不能把旧结构化特征当作当前评分依据 |
| `demo_profiles.json`、`synthetic_profiles.json` | 项目编写的合成人物/技能情景，不来自真实简历 | 仅用于独立演示；不包含真实联系人或求职者数据库 |
| `malaysia_context.json` | [马来西亚 DOSM / data.gov.my](https://data.gov.my/data-catalogue/lfs_qtr_sru_age) 的劳动力背景聚合数据 | 来源声明 CC BY 4.0；技能相关就业不足不等于 AI 导致失业 |
| `malaysia_mycol.json` | [TalentCorp MyCOL](https://www.talentcorp.com.my/images/uploads/publication/204/MyMahir-Malaysia-Critical-Occupations-List-MyCOL20242025-1773385490.pdf) 的有限结构化摘录与核验记录 | 原报告及标识归来源所有；不是 AI 造成岗位增长的证明 |
| `malaysia_masco.json` | [MASCO 2020 官方职业分类](https://jtksm.mohr.gov.my/sites/default/files/2022-12/MASCO_2020_BI_Edaran.pdf) 的有限映射与来源记录 | 本地分类参考，不等同于开放职位 |
| `local_programmes.json` | 记录内所列本地教育/培训机构官网，保存参考项目元数据与来源 | 名额、费用、资格可能变化，报名前以官网为准 |
| `source_registry.json`、`MANIFEST.json`、`evidence/`、`reports/`、`ATTRIBUTION_AND_USE.md` | 完整来源登记、获取日期、原包文件哈希、核验与历史测试报告 | 历史报告不是本次源码验证结果；可选 Adzuna 仅登记，应用未调用，不需要它的密钥 |
| `legacy-package/data/*.json` | 较早的技能、职业、趋势、课程、合成档案和情景；独立的 `source_registry.json` 保留其原始来源 | 历史参考演示，不是模型不可用时的假分数回退；保留原有来源与使用限制 |
| `backend/sdg_mapping.py` | [联合国 SDG 目标与子目标](https://sdgs.un.org/goals) + 项目人工的职业应用解释 | 潜在贡献，不代表联合国认证或实测影响；不改变排名 |
| 模型权重与 tokenizer（首次下载） | [intfloat 原模型](https://huggingface.co/intfloat/multilingual-e5-small)、[Xenova ONNX 转换](https://huggingface.co/Xenova/multilingual-e5-small) | 固定版本、SHA-256 和 MIT 声明见 `docs/model-notice.md`；不提交约 135 MB 的二进制到 GitHub |
| `.cache/futureready/` 下的职业向量索引和演示账号 JSON（运行时创建） | 本地脚本从上述数据生成；演示密码仅保存加盐哈希 | 不随源码导出，不是丢失的必需数据库；按启动步骤自动创建。会话只在后端内存，简历不持久化 |

来源表中未写 `data-package/data/` 前缀的 JSON 行仍位于该目录。包内保留每条记录自身的 URL、日期和适用限制；不要将项目代码的许可推定为第三方数据或课程内容的许可。

- 模型、转换版本、校验和及模型 MIT 声明见 [model-notice.md](docs/model-notice.md)。
- 各类数据的来源记录保留在相应数据包中；公开和再分发前需确认自己的使用授权。模型 MIT 许可不自动覆盖所有数据或素材。
- 项目原创代码与项目原创文档按 Apache-2.0 授权，范围见根目录 `LICENSE` 和 `NOTICE`。原始 65 职业 CSV 的上游授权未随文件提供，对外分发前须由权利人确认；其他第三方数据与素材保留各自许可。
