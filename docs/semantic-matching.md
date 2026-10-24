# FutureReady：本地文本向量匹配

## 当前路径

页面独立读取服务状态、65 职业目录、5 个合成示例。用户确认处理授权后粘贴简历或上传文字版 PDF/DOCX，检查提取文本后点击分析。后端本地分词、生成向量、计算余弦相似度并排序；选中职业只查询对应课程，不会再次进行简历推理。

模型为 **intfloat/multilingual-e5-small，原生 384 维**，使用固定版本的量化 ONNX 权重，由 CPU 推理。不是插件，不使用 OpenAI 或其他外部分析 API，也不需要 API Key。旧 128 维缓存不复用。

## 安装与恢复

模型及分词器约 135 MB，保存在 App Storage；开发和运行时读取经过校验的 `.cache/futureready/models/`。大文件不进 Git，也不作为部署源文件提交。

安装/构建时恢复：

```bash
python artifacts/api-server/backend/local_model_assets.py
python artifacts/api-server/backend/build_job_index.py
```

只有初次配置维护者需要从公共模型库下载并保存：

```bash
python artifacts/api-server/backend/local_model_assets.py --from-hub --store
```

模型下载只传输公共模型文件，不传输简历或经历。运行时分词/推理不会触发下载；缺少模型时明确报错，不偷偷改用远程 API。

修改职业文本、模型、分块规则或权重后需重启后端并显式重建：

```bash
python artifacts/api-server/backend/build_job_index.py --rebuild
```

生产构建和合并后设置已包含恢复模型、校验和预生成目录步骤。模型加载和 CPU 分析仍消耗服务器资源；“无需外部 API”不等于“服务器运行免费”。

## 模型处理

### 界面语言与关键词依据

界面默认英文，可切换中文。职业英文名称和摘要只用于展示和目录搜索，不修改原始职业向量文档、稳定 ID 或缓存哈希。职业向量仍使用同一份原始描述，通过多语言模型与英文/中文经历比较。

关键词识别使用 `keyword_matching.py` 中有明确中英别名的词表，默认 `keyword_language=en`，可选 `zh`。英文短语按大小写不敏感、单词边界与常见空格/连字符匹配；中文模式匹配中文别名并支持 Python、SQL 等共用技术名称。返回原文依据及位置，并展示与职业描述的词表概念交集。它不是开放域技能抽取，不保证识别任意新关键词，不计入余弦分数或作为旧 80 特征方案的替代评分。

界面语言与关键词语言独立；两种偏好保存在浏览器本地存储，不保存简历内容。切换界面不重新推理；切换词表清除过期结果并要求重新分析。课程接口支持 `?language=en|zh`，查询缓存按职业 ID 和语言区分。

- 文本先做 NFKC 与空白规范化。职业文档为名称与描述拼接。
- 中英文使用同一模型、分词器、384 维输出。
- 按模型卡对称语义相似度建议，职业和经历两端统一 `query: ` 前缀。
- 内容每块最多 384 token，另加前缀/特殊 token，严格低于模型 512 token 上限；单份输入上限 12,000 token，超限拒绝而非静默截断。
- 每块做 attention-mask mean pooling 和 L2 归一化；长文按块的内容 token 数加权平均，再单位化。
- 使用原始余弦相似度排序；展示百分比为 `max(0, cosine) × 100`，保留一位小数，并展示原始值。它不是准确率、技能掌握率或录用概率；E5 分数通常偏高，各职业百分比不要求合计为 100%。
- 同一模型配置和输入可复现同一排名。仍需人工标注的职业相关性数据才能评估推荐质量；冒烟测试不等于准确率评估。

## 缓存

`.cache/futureready/local_e5_job_embeddings.npz` 只存职业向量与配置。配置绑定职业稳定 ID、文本/目录哈希、顺序、模型版本、权重/分词器 SHA-256、维度、前缀、pooling 和分块规则。单个原子文件与矩阵校验和避免映射错配。拒绝损坏、非有限、非单位化和不兼容缓存。

不持久保存简历原文、文件或简历向量；刷新页面会丢失当前输入与结果，除非用户主动下载结果 JSON。

## 单独修改的位置

| 目标 | 文件 |
|---|---|
| 光球、粒子入口 | `artifacts/future-ready/src/components/welcome/` |
| 输入、按钮、状态 | `artifacts/future-ready/src/components/ResumeExplorer.tsx` |
| 排名、目录、详情 | `artifacts/future-ready/src/components/explorer/` |
| 分析页面样式 | `artifacts/future-ready/src/components/resume-explorer.css` |
| 模型/维度/规范化/目录 | `artifacts/api-server/backend/semantic_catalogue.py` |
| ONNX 加载、前缀、pooling | `artifacts/api-server/backend/local_encoder.py` |
| 资产恢复和校验 | `artifacts/api-server/backend/local_model_assets.py` |
| 分块聚合、排序、资源限制 | `artifacts/api-server/backend/semantic_matching.py` |
| 缓存读写与一致性 | `artifacts/api-server/backend/semantic_cache.py` |
| 请求与处理授权校验、上传 | `artifacts/api-server/backend/explorer_api.py` |

接口变更同步 `lib/api-spec/openapi.yaml`，再运行 codegen。保留独立历史演示页面，不将旧结果混入新匹配。文本向量的维度不代表单项技能，也不自动提供技能缺口与课程证据。

## 限制与测试

个人简历须确认处理授权；真实认证和生产隐私合规不是本功能的完成声明。8MB/20页文件限制、解析超时、512 KiB 分析请求体限制继续有效。扫描件没有 OCR，会明确拒绝而非虚构文本。推理批次最多 4 块，CPU 两线程；请求最多两个并发、每进程每小时 30 次，不能替代真实认证和跨实例资源配额。

课程推荐位于 `career_courses.py`，接口 `/api/explorer/jobs/{job_id}/courses`，前端组件 `CourseSuggestions.tsx`。它只使用现有课程目录中 `default_recommendation_eligible=true` 且有读取来源记录的条目。规则关联职业描述中的明确主题，不参与职业匹配向量，也不等于旧 80 特征方法。推荐最多 3 门相关基础课及 1 门责任 AI 基础课；不推断个人技能缺口，不保证覆盖全部专科技能。核验日期和费用范围来自来源记录，当前条件须在课程官网确认。

自动测试包含原有演示回归、缓存与数学单元测试、合成资料校验、文档解析，以及实际本地 ONNX 模型测试。实际模型测试禁止 Python socket 建立外部连接，验证不同经历的排名变化、重复输入结果一致和 65 职业完整返回。缺少模型的轻量 CI 会明确跳过实际模型测试，部署前应恢复资产后运行它。
