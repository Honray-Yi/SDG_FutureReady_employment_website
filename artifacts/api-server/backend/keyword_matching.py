"""Transparent bilingual keyword evidence, never a replacement ranking score."""
import re

# Concept, English label, Chinese label, English aliases, Chinese aliases.
TERMS = [
    ("python", "Python", "Python", ["python"], ["python"]),
    ("sql", "SQL", "SQL", ["sql"], ["sql"]),
    ("pytorch", "PyTorch", "PyTorch", ["pytorch"], ["pytorch"]),
    ("tensorflow", "TensorFlow", "TensorFlow", ["tensorflow"], ["tensorflow"]),
    ("sklearn", "scikit-learn", "scikit-learn", ["scikit-learn", "sklearn"], ["scikit-learn", "sklearn"]),
    ("ml", "Machine learning", "机器学习", ["machine learning"], ["机器学习"]),
    ("dl", "Deep learning", "深度学习", ["deep learning"], ["深度学习"]),
    ("nn", "Neural networks", "神经网络", ["neural network", "neural networks"], ["神经网络"]),
    ("nlp", "Natural language processing", "自然语言处理", ["nlp", "natural language processing"], ["nlp", "自然语言处理"]),
    ("vision", "Computer vision", "计算机视觉", ["computer vision"], ["计算机视觉"]),
    ("llm", "Large language models", "大语言模型", ["llm", "llms", "large language model", "large language models"], ["llm", "大语言模型", "大模型"]),
    ("genai", "Generative AI", "生成式 AI", ["generative ai", "generative artificial intelligence", "aigc"], ["生成式", "aigc"]),
    ("rag", "Retrieval-augmented generation", "检索增强生成", ["rag", "retrieval-augmented generation", "retrieval augmented generation"], ["rag", "检索增强"]),
    ("prompt", "Prompt engineering", "提示词工程", ["prompt engineering", "prompt design", "prompt"], ["prompt", "提示词"]),
    ("agent", "AI agents", "智能体", ["agent", "agents", "agentic"], ["agent", "智能体"]),
    ("transformer", "Transformers", "Transformer", ["transformer", "transformers"], ["transformer"]),
    ("bert", "BERT", "BERT", ["bert"], ["bert"]),
    ("xgboost", "XGBoost", "XGBoost", ["xgboost"], ["xgboost"]),
    ("features", "Feature engineering", "特征工程", ["feature engineering"], ["特征工程"]),
    ("evaluation", "Model evaluation", "模型评估", ["model evaluation", "model eval", "evaluation", "cross validation", "cross-validation"], ["模型评估", "模型评测", "交叉验证", "评测"]),
    ("testing", "Automated testing", "自动化测试", ["automated testing", "regression tests", "regression testing", "unit tests"], ["自动化测试", "回归测试"]),
    ("stats", "Statistics", "统计分析", ["statistics", "statistical analysis"], ["统计分析", "统计"]),
    ("ab", "A/B testing", "A/B 测试", ["a/b testing", "a/b tests", "ab testing", "ab experiment"], ["a/b测试", "a/b实验", "ab实验"]),
    ("visualization", "Data visualization", "数据可视化", ["data visualization", "data visualisation", "visualization", "visualisation"], ["数据可视化", "可视化"]),
    ("etl", "ETL", "ETL", ["etl"], ["etl"]),
    ("warehouse", "Data warehousing", "数据仓库", ["data warehouse", "data warehousing"], ["数据仓库", "数仓"]),
    ("spark", "Spark", "Spark", ["spark"], ["spark"]),
    ("airflow", "Airflow", "Airflow", ["airflow"], ["airflow"]),
    ("kafka", "Kafka", "Kafka", ["kafka"], ["kafka"]),
    ("kubernetes", "Kubernetes", "Kubernetes", ["kubernetes", "k8s"], ["kubernetes", "k8s"]),
    ("docker", "Docker", "Docker", ["docker"], ["docker"]),
    ("mlops", "MLOps", "MLOps", ["mlops"], ["mlops"]),
    ("mlflow", "MLflow", "MLflow", ["mlflow"], ["mlflow"]),
    ("cuda", "CUDA", "CUDA", ["cuda"], ["cuda"]),
    ("onnx", "ONNX", "ONNX", ["onnx"], ["onnx"]),
    ("quantization", "Model quantization", "模型量化", ["quantization", "quantisation"], ["量化", "模型量化"]),
    ("vector", "Vector retrieval", "向量检索", ["vector search", "vector retrieval", "vector database", "faiss", "milvus"], ["向量检索", "向量数据库", "向量召回", "faiss", "milvus"]),
    ("graph", "Graph methods", "图方法", ["knowledge graph", "graph neural network", "gnn", "neo4j"], ["知识图谱", "图神经网络", "gnn", "neo4j"]),
    ("rl", "Reinforcement learning", "强化学习", ["reinforcement learning", "ppo", "dqn"], ["强化学习", "ppo", "dqn"]),
    ("ros", "ROS", "ROS", ["ros"], ["ros"]),
    ("opencv", "OpenCV", "OpenCV", ["opencv"], ["opencv"]),
    ("yolo", "YOLO", "YOLO", ["yolo"], ["yolo"]),
    ("ocr", "OCR", "OCR", ["ocr", "optical character recognition"], ["ocr", "文字识别"]),
    ("speech", "Speech recognition", "语音识别", ["speech recognition", "asr", "tts"], ["语音识别", "asr", "tts"]),
    ("diffusion", "Stable Diffusion", "Stable Diffusion", ["stable diffusion", "diffusion"], ["stable diffusion", "扩散模型", "diffusion"]),
    ("midjourney", "Midjourney", "Midjourney", ["midjourney"], ["midjourney"]),
    ("photoshop", "Photoshop", "Photoshop", ["photoshop"], ["photoshop"]),
    ("design", "Visual design", "视觉设计", ["visual design", "brand visuals", "illustration", "illustrations"], ["视觉设计", "品牌视觉", "插画"]),
    ("product", "Product design", "产品设计", ["product design", "product management", "product manager"], ["产品设计", "产品经理"]),
    ("research", "User research", "用户研究", ["user research"], ["用户研究"]),
    ("privacy", "Data privacy", "数据隐私", ["data privacy", "differential privacy", "privacy"], ["隐私", "差分隐私"]),
    ("security", "Security", "安全", ["security", "red teaming", "red team"], ["安全", "红队测试"]),
    ("ethics", "AI ethics", "AI 伦理", ["ai ethics", "algorithmic fairness", "fairness"], ["伦理", "公平性"]),
    ("compliance", "Compliance", "合规", ["compliance", "governance"], ["合规", "治理"]),
    ("annotation", "Data annotation", "数据标注", ["annotation", "labeling", "labelling"], ["标注"]),
    ("rlhf", "RLHF", "RLHF", ["rlhf"], ["rlhf"]),
    ("project", "Project management", "项目管理", ["project management", "agile"], ["项目管理", "敏捷"]),
    ("writing", "Technical writing", "技术写作", ["technical writing", "api documentation", "model cards"], ["技术写作", "api文档", "模型卡片"]),
    ("training", "Curriculum design", "课程设计", ["curriculum design", "instructional design"], ["课程设计"]),
    ("iot", "Internet of Things", "物联网", ["iot", "internet of things"], ["iot", "物联网"]),
    ("excel", "Excel", "Excel", ["excel"], ["excel"]),
    ("tableau", "Tableau", "Tableau", ["tableau"], ["tableau"]),
    ("powerbi", "Power BI", "Power BI", ["power bi", "powerbi"], ["power bi", "powerbi"]),
    ("figma", "Figma", "Figma", ["figma"], ["figma"]),
    ("cpp", "C++", "C++", ["c++"], ["c++"]),
    ("java", "Java", "Java", ["java"], ["java"]),
    ("javascript", "JavaScript", "JavaScript", ["javascript", "typescript"], ["javascript", "typescript"]),
    ("cloud", "Cloud computing", "云计算", ["cloud computing", "aws", "azure", "cloud services"], ["云计算", "云服务", "aws", "azure"]),
    ("forecast", "Time-series forecasting", "时间序列预测", ["time series", "time-series", "forecasting"], ["时间序列", "时序", "预测"]),
]


def pattern(alias):
    escaped = re.escape(alias).replace(r"\ ", r"[\s\-]+")
    if re.search(r"[\u3400-\u9fff]", alias):
        return re.compile(escaped, re.I)
    return re.compile(r"(?<![a-zA-Z0-9_])" + escaped + r"(?![a-zA-Z0-9_])", re.I)


PATTERNS = {(term[0], language): [pattern(a) for a in term[3 if language == "en" else 4]]
            for term in TERMS for language in ("en", "zh")}


def recognize(text, language="en"):
    found = []
    for concept, en, zh, *_ in TERMS:
        matches = [m for p in PATTERNS[concept, language] if (m := p.search(text))]
        if matches:
            match = min(matches, key=lambda m: (m.start(), -(m.end() - m.start())))
            found.append({"keyword_id": concept, "label_en": en, "label_zh": zh,
                          "evidence": match.group(), "start": match.start(), "end": match.end()})
    return sorted(found, key=lambda item: (item["start"], item["keyword_id"]))


def enrich(result, text, language="en"):
    from job_localization import public_job
    keywords = recognize(text, language)
    ids = {item["keyword_id"] for item in keywords}
    for row in result["rankings"]:
        row.update(public_job(row))
        role = row["job_name"] + " " + row["job_text"]
        role_ids = {item["keyword_id"] for lang in ("en", "zh") for item in recognize(role, lang)}
        row["matched_keyword_ids"] = sorted(ids & role_ids)
    return {**result, "keyword_language": language, "keywords": keywords}
