# 来源署名与使用范围

本包是多来源数据整理，**不把所有第三方材料统一重新许可**。JSON 中事实/元数据与代码可用于本次原型；若公开再分发，请保留来源并按各源站当前条款处理。没有打包论文全文、课程全文、真实 CV 或第三方站点的完整 HTML。

- arXiv：元数据计数和题目/链接示例。API 文档：https://info.arxiv.org/help/api/user-manual.html 。论文自身可能有不同许可；本包未包含论文正文。
- Arbeitnow：公开 Job Board API，https://www.arbeitnow.com/blog/job-board-api 。展示职位时保留“Source: Arbeitnow”和每条原链接。公开可访问不等于无条件再许可。
- O*NET：职业标题与页面背景参考。数据库许可页：https://www.onetcenter.org/license_db.html 。本包职业技能等级和 AI 方向是团队派生设计，不是官方 O*NET 评分，不表示美国劳工部背书。
- Department of Statistics Malaysia / data.gov.my：全国聚合技能相关就业不足记录，CC BY 4.0；https://data.gov.my/data-catalogue/lfs_qtr_sru_age 。本包只选 `age=overall`，未保存个人调查记录。
- TalentCorp：MyMahir Malaysia Critical Occupations List 2024/2025，Table 7 相关职业事实子集。https://www.talentcorp.com.my/mycol/ 。不包含完整报告；团队近似职业对应关系应单独标识。
- U.S. Bureau of Labor Statistics：Table 1.2，2025–2035 职业预测。https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm 。复制的是少量事实数值，未把预测当作已发生结果。
- United Nations SDGs：https://sdgs.un.org/goals 。目标连接仅用于说明团队设计依据，不宣称 UN 认证。
- 课程：归各自提供者所有。`courses.json` 保存标题、链接、费用条件和课程路线所需元数据；需在提供者平台学习。免费内容不保证免费证书或计算资源。
- 合成档案：针对四种抽象演示情景从零编写，没有从真实 CV、联系人或人员数据库改写。

准备工具：Codex 辅助资料整理和代码编写。采集和匹配脚本没有 LLM 依赖。后续增加生成式解释时，应记录实际模型标识，始终引用本包可验证记录，并允许人类用户自行判断。
