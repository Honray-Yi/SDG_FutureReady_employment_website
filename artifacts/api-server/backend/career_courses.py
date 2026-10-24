"""Course suggestions from the existing, source-reviewed catalogue.

These are role-oriented learning foundations, NOT inferred personal skill gaps.
They never change the embedding ranking and do not reintroduce the old 80 features.
"""
from functools import lru_cache
import json
from pathlib import Path
import re

COURSES = Path(__file__).resolve().parents[1] / "data-package/data/courses.json"

# Rules bind a description's explicit topic to an existing course with reviewed
# access metadata. Narrow specialties are deliberately not claimed as covered.
RULES = [
    (r"Python|Scikit|PyTorch|TensorFlow|编程", "C01", "Python 编程基础", "职业描述明确涉及编程或 Python 生态。"),
    (r"SQL|数据分析|数据科学|经营分析|漏斗分析", "C02", "SQL 数据查询", "职业描述涉及 SQL 或结构化数据分析。"),
    (r"数据分析|数据科学|统计|A/B|AB实验|商业智能|增长分析|金融AI", "C03", "数据分析与统计入门", "职业描述涉及数据分析、实验或统计。"),
    (r"机器学习|分类|预测|特征工程|风控算法|推荐算法|AI研究", "C04", "机器学习基础", "职业描述涉及建模、分类、预测或机器学习研究。"),
    (r"深度学习|神经网络|PyTorch|TensorFlow|CNN|ResNet|计算机视觉|图像分类|图像分割|语音识别|多模态", "C05", "深度学习基础", "职业描述涉及神经网络或深度学习；不代表覆盖全部视觉/语音专项技能。"),
    (r"NLP|大模型算法|BERT|Transformer|LLM|SFT", "C06", "语言模型基础", "职业描述明确涉及语言模型或 NLP。"),
    (r"RAG|检索增强|向量检索|向量数据库|智能客服|知识库|Agent", "C07", "生成式 AI 与检索应用入门", "职业描述涉及检索、知识库或生成式 AI 应用。"),
    (r"Agent|智能体|Function Calling", "C09", "AI Agent 应用", "职业描述明确涉及 Agent 或工具调用。"),
    (r"MLOps|模型训练、部署|模型.*监控|模型服务|推理部署", "C10", "模型部署与运维基础", "职业描述涉及模型部署、服务或生命周期管理。"),
    (r"数据工程|大数据开发|ETL|数仓|数据仓库|Spark|Flink|Airflow", "C11", "数据工程基础", "职业描述涉及数据流水线或数仓。"),
    (r"Prompt|提示词|内容创作|视觉设计|视频制作|内容运营|技术文档|产品经理|产品设计|售前|销售|培训讲师", "C13", "生成式 AI 提示与应用基础", "只推荐提示与应用基础，不宣称覆盖设计软件、产品管理或行业专科训练。"),
    (r"安全|隐私|合规|治理|运维|基础设施", "C17", "安全与隐私基础", "职业描述涉及安全、隐私、治理或系统运维。"),
]


@lru_cache(maxsize=1)
def catalogue():
    records = json.loads(COURSES.read_text(encoding="utf-8"))
    return {c["course_id"]: c for c in records
            if c.get("default_recommendation_eligible") is True
            and c.get("link_check_status") == "retrieved"
            and c.get("source_url", "").startswith("https://")}


ENGLISH = {
    "C01": ("Python programming foundations", "The role description explicitly mentions programming or the Python ecosystem."),
    "C02": ("SQL and structured data", "The role involves SQL or structured data analysis."),
    "C03": ("Data analysis and statistics", "The role involves data analysis, experiments or statistics."),
    "C04": ("Machine learning foundations", "The role involves modeling, classification, prediction or machine learning research."),
    "C05": ("Deep learning foundations", "The role involves neural networks or deep learning; this does not cover every vision or speech specialty."),
    "C06": ("Language model foundations", "The role explicitly involves language models or natural language processing."),
    "C07": ("Generative AI and retrieval applications", "The role involves retrieval, knowledge bases or generative AI applications."),
    "C09": ("AI agent applications", "The role explicitly involves AI agents or tool calling."),
    "C10": ("Model deployment and operations", "The role involves model deployment, serving or lifecycle management."),
    "C11": ("Data engineering foundations", "The role involves data pipelines or warehousing."),
    "C13": ("Prompting and generative AI applications", "This covers prompting and application foundations, not specialist design software, product management or industry training."),
    "C17": ("Security and privacy foundations", "The role involves security, privacy, governance or system operations."),
    "C18": ("Responsible use of AI", "A general responsibility and safety foundation for AI-related roles, not specialist training for this position."),
}


def for_job(job,language="en"):
    records = catalogue()
    choices = []
    for pattern, course_id, topic, reason in RULES:
        evidence = re.search(pattern, job["job_text"], flags=re.IGNORECASE)
        if evidence and course_id in records and len(choices) < 3:
            choices.append((course_id, topic, reason, evidence.group(0)))
    # Responsible AI is a clearly labelled general foundation for these AI roles.
    if "C18" in records:
        choices.append(("C18", "负责任使用 AI", "该职业属于 AI 相关领域；这是通用责任与安全基础，不是该岗位的专项技能训练。", "AI 职业通用基础"))
    courses = []
    for course_id, topic, reason, excerpt in choices:
        c = records[course_id]
        if language=="en":
            topic,reason=ENGLISH[course_id]
            if re.search(r"[\u3400-\u9fff]",excerpt):
                excerpt=topic
        courses.append({
            "course_id": course_id, "title": c["title"], "provider": c["provider"],
            "url": c["url"], "source_url": c["source_url"],
            "checked_at": c["checked_at"], "topic": topic, "reason": reason,
            "job_evidence": excerpt, "access": c["price_scope"],
            "cost_note": c["extra_cost_note"], "level": c.get("difficulty_level", "See provider"),
        })
    return {
        "job_id": job["job_id"], "job_name": job["job_name"], "courses": courses,
        "basis": ("Source-reviewed learning resources selected from explicit topics in this role description. These are learning foundations, not inferred personal skill gaps." if language=="en" else "来自现有人工整理且有来源记录的课程目录；根据职业描述中的明确主题推荐基础学习内容，不是根据简历推断技能缺口。"),
        "coverage_note": ("Up to three relevant foundation courses and one responsible-AI course. This is not complete specialist coverage; confirm duration, prerequisites and current costs with the provider." if language=="en" else "最多 3 门相关基础课及 1 门责任 AI 基础课。未声称覆盖该职业全部技能；时长、前置条件及当前费用请以课程官网为准。"),
    }
