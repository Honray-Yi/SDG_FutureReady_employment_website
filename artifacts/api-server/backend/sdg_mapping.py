"""Curated potential SDG alignment, not UN endorsement or measured impact."""
from semantic_catalogue import normalize_text

GOALS = {
    3: ("Good Health and Well-being", "良好健康与福祉"),
    4: ("Quality Education", "优质教育"),
    7: ("Affordable and Clean Energy", "经济适用的清洁能源"),
    8: ("Decent Work and Economic Growth", "体面工作和经济增长"),
    9: ("Industry, Innovation and Infrastructure", "产业、创新和基础设施"),
    10: ("Reduced Inequalities", "减少不平等"),
    11: ("Sustainable Cities and Communities", "可持续城市和社区"),
    12: ("Responsible Consumption and Production", "负责任消费和生产"),
    16: ("Peace, Justice and Strong Institutions", "和平、正义与强大机构"),
}
# Each category links an actual application theme to a numbered UN target.
CATEGORIES = {
    "research": (9, "9.5", "Can support scientific research and technological capabilities when methods and results are evaluated responsibly.", "在负责任评估方法与结果的前提下，可支持科学研究与技术能力提升。"),
    "infrastructure": (9, "9.1", "Can improve reliable digital infrastructure when availability, accessibility and security are designed in.", "在兼顾可用性、可访问性与安全的前提下，可改善可靠的数字基础设施。"),
    "productivity": (8, "8.2", "Can improve productive workflows through technological innovation; decent work still requires responsible deployment and human oversight.", "可通过技术创新提高工作流程效率；体面工作仍需要负责任部署和人工监督。"),
    "safe_work": (8, "8.8", "Can reduce hazardous manual tasks or improve operational safety when worker protection guides deployment.", "在以劳动者保护为前提的应用中，可减少危险人工任务或改善作业安全。"),
    "skills": (4, "4.4", "Can improve access to technical learning and relevant job skills when educational content is accurate and accessible.", "在教学内容准确且可访问的前提下，可支持技术学习和就业相关技能提升。"),
    "health": (3, "3.8", "Can support healthcare research or service workflows, subject to clinical validation, privacy and equitable access.", "在临床验证、隐私保护和公平可及的前提下，可支持医疗研究或服务流程。"),
    "energy": (7, "7.3", "Can improve energy efficiency through efficient computation, forecasting or resource scheduling; actual savings must be measured.", "可通过高效计算、预测或资源调度改善能源效率；实际节能效果需要测量验证。"),
    "inclusion": (10, "10.2", "Can make information or digital services more inclusive when language, accessibility and unequal access are addressed.", "在解决语言、可访问性和获取机会差异的前提下，可促进信息和数字服务包容性。"),
    "fairness": (10, "10.3", "Can help identify discriminatory outcomes and improve equal opportunity when fairness is explicitly audited.", "在明确审计公平性的前提下，可帮助发现歧视性结果并改善机会平等。"),
    "mobility": (11, "11.2", "Can support accessible, safer transport or mobility systems when safety and public-interest requirements are validated.", "在验证安全与公共利益要求的前提下，可支持更便利、更安全的交通和出行系统。"),
    "resources": (12, "12.2", "Can improve resource planning and reduce avoidable consumption when sustainability is an explicit project objective.", "在将可持续性作为明确项目目标的前提下，可改善资源规划并减少可避免的消耗。"),
    "justice": (16, "16.3", "Can improve access to legal information and legal workflows when accuracy, rights and professional oversight are protected.", "在保障准确性、权利和专业监督的前提下，可改善法律信息获取和法律工作流程。"),
    "accountability": (16, "16.6", "Can strengthen transparency and accountable decision-making through documentation, audits or data governance.", "可通过文档、审计或数据治理，支持透明且可问责的决策。"),
}
GROUPS = {
    "research": ["机器学习工程师","深度学习工程师","大模型算法工程师","NLP算法工程师","计算机视觉工程师","语音识别算法工程师","多模态算法工程师","推荐算法工程师","搜索算法工程师","强化学习工程师","自动驾驶算法工程师","机器人算法工程师","知识图谱工程师","图算法工程师","风控算法工程师","量化交易算法工程师","时间序列预测工程师","生物信息算法工程师","AI研究科学家","数据科学家","AI芯片设计工程师","AI编译器优化工程师","AI推理部署工程师","计算摄影算法工程师","AR/VR算法工程师"],
    "infrastructure": ["数据工程师","大数据开发工程师","MLOps工程师","AIOps智能运维工程师","AI平台开发工程师","AI基础设施工程师","向量数据库工程师","AI解决方案架构师","AI+IoT工程师"],
    "productivity": ["机器学习工程师","推荐算法工程师","数据科学家","数据工程师","大数据开发工程师","MLOps工程师","AI平台开发工程师","提示词工程师","AI应用开发工程师","RPA智能自动化工程师","数据标注专家","AI训练师（模型调优）","AI产品经理","AI解决方案架构师","AI售前顾问","AI销售工程师","AI项目经理","数据分析师","商业智能分析师","用户增长分析师","AIGC内容创作者","AI视觉设计师","AI视频制作师","数字人设计师","AI游戏设计师","智能客服产品经理","智能硬件产品经理","工业AI工程师","金融AI分析师","AI内容运营专家","AI+IoT工程师"],
    "safe_work": ["机器人算法工程师","AI安全工程师","工业AI工程师","AIOps智能运维工程师"],
    "skills": ["AI培训讲师","AI教育产品设计师","AI技术文档工程师","AR/VR算法工程师","数字人设计师"],
    "health": ["生物信息算法工程师","医疗AI应用专家"],
    "energy": ["AI芯片设计工程师","AI编译器优化工程师","AI推理部署工程师","AI基础设施工程师","时间序列预测工程师"],
    "inclusion": ["NLP算法工程师","语音识别算法工程师","搜索算法工程师","AI教育产品设计师","智能客服产品经理"],
    "fairness": ["AI伦理与合规专家","AI测试工程师"],
    "mobility": ["自动驾驶算法工程师"],
    "resources": ["工业AI工程师","智能硬件产品经理"],
    "justice": ["法律科技AI专家"],
    "accountability": ["AI安全工程师","AI伦理与合规专家","AI测试工程师","AI数据治理专家","AI项目经理","AI技术文档工程师","风控算法工程师","金融AI分析师","数据标注专家","AI训练师（模型调优）"],
}


def sdgs_for_job(job):
    records = []
    for category, roles in GROUPS.items():
        if job["job_name"] not in {normalize_text(name) for name in roles}:
            continue
        goal, target, en, zh = CATEGORIES[category]
        records.append({
            "goal": goal, "title_en": GOALS[goal][0], "title_zh": GOALS[goal][1], "target": target,
            "reason_en": en, "reason_zh": zh, "url": f"https://sdgs.un.org/goals/goal{goal}",
        })
    return records
